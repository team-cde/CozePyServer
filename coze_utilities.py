import time
from threading import Timer
import random
from datetime import datetime, timezone, timedelta


class CozeUtilities:

    def __init__(self):
        self.active_users = []
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

    def add_user(self, user_id):
        self.active_users.append(user_id)

    def start_coze(self):
        print("enter CozeUtilites::start_coze")

        self.coze_state = "matching"
        self.match_users()

    # Match ID's
    def match_users(self):
        self.active_users = list(set(self.active_users))
        print("Active Users:")
        print(self.active_users)
        random.shuffle(self.active_users)
        num_users = len(self.active_users)

        # If there is an odd number of people, someone needs to get shafted
        if num_users % 2 > 0:
            num_users -= 1
            self.matched_users[self.active_users[-1]] = -1

        for i in range(0, num_users, 2):
            self.matched_users[self.active_users[i]] = self.active_users[i+1]

        self.coze_state = "matched"
        print(self.matched_users)

    def get_match(self, user_id):
        partner_id = -1
        if user_id in self.matched_users:
            partner_id = self.matched_users[user_id]
        return partner_id

    def get_state(self):
        return self.coze_state

    def end_coze(self):
        print("enter CozeUtilites::end_coze")
        self.active_users = []
        self.matched_users = {}
        self.coze_state = "waiting"
        self.setup_next_coze()

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
        coze_end_delay = coze_sched_time + self.coze_duration_minutes * 60 - tnow + 1

        self.coze_start_event = Timer(coze_start_delay, self.start_coze, ()).start()
        self.coze_end_event = Timer(coze_end_delay, self.end_coze, ()).start()
