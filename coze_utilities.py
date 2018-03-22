import time
from threading import Timer
import random
from datetime import datetime, timezone, timedelta


class CozeUtilities:

    def __init__(self):
        self.active_users = {}
        self.matched_users = {}
        self.coze_state = "waiting"
        self.coze_start_event = None
        self.coze_end_event = None
        self.coze_hour = 20
        self.coze_minute = 0
        self.coze_timezone = timezone(-timedelta(hours=5), "EST")
        self.coze_duration_minutes = 1
        self.next_coze = None
        self.next_coze_utc = None

    def add_user(self, webrtc_id, user_id):
        self.active_users[user_id] = webrtc_id

    def start_coze(self):
        print("enter CozeUtilites::start_coze")

        self.coze_state = "matching"
        self.match_users()

    # Match ID's
    # TODO: This can probably be done a lot smarter eventually
    def match_users(self):
        #self.active_users = list(set(self.active_users))
        print("Active Users:")
        print(self.active_users)
        active_user_ids = list(self.active_users.keys())
        random.shuffle(active_user_ids)

        num_users = len(active_user_ids)

        # If there is an odd number of people, someone needs to get shafted
        # TODO: Can we make this better?
        if num_users % 2 > 0:
            num_users -= 1
            self.matched_users[active_user_ids[-1]] = {}

        for i in range(0, num_users, 2):
            a_user_id = active_user_ids[i]
            b_user_id = active_user_ids[i+1]
            a_webrtc_id = self.active_users[a_user_id]
            b_webrtc_id = self.active_users[b_user_id]
            self.matched_users[a_user_id] = {"is_caller":1,
                "partner_user_id":b_user_id, "partner_webrtc_id":b_webrtc_id}
            self.matched_users[b_user_id] = {"is_caller":0,
                "partner_user_id":a_user_id, "partner_webrtc_id":a_webrtc_id}

        self.coze_state = "matched"
        print(self.matched_users)

    def get_match(self, user_id):
        match = {}
        if user_id in self.matched_users:
            match = self.matched_users[user_id]
        match['coze_state'] = self.coze_state
        return match

    def get_state(self):
        return self.coze_state

    def end_coze(self):
        print("enter CozeUtilites::end_coze")
        self.active_users = {}
        self.matched_users = {}
        self.setup_next_coze()
        self.coze_state = "waiting"

    def setup_next_coze(self):
        now = datetime.now()
        now.replace(tzinfo=self.coze_timezone)
        self.next_coze = now.replace(hour=self.coze_hour, minute=self.coze_minute, second=0)

        if now > self.next_coze:
            self.next_coze += timedelta(days=1)

        self.next_coze_utc = self.next_coze
        self.next_coze_utc.replace(tzinfo=timezone.utc)

        self.set_coze_timers(self.next_coze)

    def trigger_coze(self, delay=10):
        now = datetime.now()
        self.next_coze = now + timedelta(seconds=delay)
        self.next_coze_utc = self.next_coze
        self.next_coze_utc.replace(tzinfo=timezone.utc)

        self.set_coze_timers(self.next_coze)

    def set_coze_timers(self, start_time):
        # TODO: Fix this - it doesn't actually work/cancel timers
        if self.coze_start_event:
            print("Cancelling START Timer")
            self.coze_start_event.cancel()
        if self.coze_end_event:
            print("Cancelling END Timer")
            self.coze_end_event.cancel()

        tnow = time.time()
        coze_sched_time = time.mktime(start_time.timetuple())
        coze_start_delay = coze_sched_time - tnow + 1
        #coze_end_delay = coze_sched_time + self.coze_duration_minutes * 60 - tnow + 1
        # This signals the end of the matching period, not the call. This should
        # really be pub-sub or something but it works for now
        # 10 seconds should be enough time for all matchings to happen and calls to start
        coze_end_delay = coze_start_delay + 10

        self.coze_start_event = Timer(coze_start_delay, self.start_coze, ())
        self.coze_start_event.daemon = True
        self.coze_end_event = Timer(coze_end_delay, self.end_coze, ())
        self.coze_end_event.daemon = True

        self.coze_start_event.start()
        self.coze_end_event.start()
