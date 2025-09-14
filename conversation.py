from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
# Import your existing game logic
from level import register_client, get_client_info, get_messages, get_streaks, get_target, ID, __clients
from llama import check_action, handle_client, daily_quiz, daily_ask_if_done_saving

app = Flask(__name__)

# --- Initialize one test client (like in developer_play) ---
clientId = ID
register_client(clientId)


@app.route("/reply_whatsapp", methods=['POST'])
def reply_whatsapp():
    """Handle incoming WhatsApp messages from Twilio"""
    incoming_msg = request.form.get("Body", "").strip()
    user_number = request.form.get("From")  # Useful if you want to track multiple users

    resp = MessagingResponse()

    # Exit condition (for dev testing)
    if incoming_msg.lower() in ["exit", "quit", "q"]:
        resp.message("You have exited the session. Type START to rejoin.")
        return Response(str(resp), mimetype='text/xml')

    # Info command
    if incoming_msg.lower() == "info":
        info = get_client_info(clientId)
        resp.message(f"Client Info: {info}")
        return Response(str(resp), mimetype='text/xml')
    
    if "leaderboard" in incoming_msg.lower():
        leaderboard = f"🏆 Leaderboard:\n1. John Doe (Level: {__clients[ID]['Level']}) \n2. Daniel (Level: 1)"
        resp.message(leaderboard)
        return Response(str(resp), mimetype='text/xml')

    # Store user message
    messages = get_messages(clientId)
    messages.append({"role": "user", "content": incoming_msg})

    # Get AI response (calls your llama handler)
    ai_response = handle_client(clientId, resp)

    # Send back Twilio message
    if ai_response:
        resp.message(ai_response)
    else:
        resp.message("Hmm, I didn’t quite get that. Try again!")

    return Response(str(resp), mimetype='text/xml')


# --- Daily routines (can be triggered manually or via cron/apscheduler) ---
@app.route("/daily_quiz", methods=["GET"])
def run_quiz():
    resp = MessagingResponse()
    ai_response = daily_quiz(clientId)
    resp.message(ai_response if ai_response else "No quiz today.")
    return Response(str(resp), mimetype="text/xml")


@app.route("/daily_check", methods=["GET"])
def run_check():
    resp = MessagingResponse()
    ai_response = daily_ask_if_done_saving(clientId)
    resp.message(ai_response if ai_response else "No check today.")
    return Response(str(resp), mimetype="text/xml")


if __name__ == "__main__":
    app.run(port=3000, debug=True)
