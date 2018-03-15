from flask import Flask, request, make_response
import json
import sys, os

from coze_utilities import CozeUtilities

app = Flask(__name__)
cu = CozeUtilities()

cu.setup_next_coze()

print("Next Coze: " + str(cu.next_coze))

# Just a default route
@app.route("/", methods=["GET", "POST"])
def root():
    return "Coze Backend Online!"

# Manually trigger a Coze in 5 seconds (for testing)
@app.route("/trigger_coze", methods=["GET"])
def trigger_coze():
    print("enter trigger_coze")
    delay = 5
    data = request.args
    if "delay" in data:
        delay = int(data["delay"])

    cu.trigger_coze(delay=delay)

    print("Next Coze: " + str(cu.next_coze))
    return json.dumps({"success":True}), 200, {'ContentType':'application/json'}


# Return next coze time to clients
@app.route("/get_next_coze_time", methods=["GET"])
def get_next_coze_time():
    print("enter get_next_coze_time")

    retval = {'coze_state':cu.get_state(), 'next_coze_time':cu.next_coze_utc.astimezone().isoformat()}
    print(retval)
    return json.dumps(retval), 200, {'ContentType':'application/json'}

# Client tells Server it is ready for Coze
@app.route("/ready_for_coze", methods=["GET"])
def ready_for_coze():
    print("enter ready_for_coze")

    user_data = request.args
    cu.add_user(user_data["webrtc_id"])
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

# Client requests their partner's ID
# Only one client per coze will receive the partner ID to make the call
# to save some time and avoid 2 users calling each other simultaneously
@app.route("/get_match", methods=["GET"])
def get_match():
    print("enter get_match")

    user_data = request.args
    user_id = user_data["webrtc_id"]
    partner_id = cu.get_match(user_id)

    retval = {'coze_state':cu.get_state(), 'partner_id':partner_id}
    return json.dumps(retval), 200, {'ContentType':'application/json'}


if __name__ == "__main__":
    port = 5000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(host="0.0.0.0", port=port, debug=True)
