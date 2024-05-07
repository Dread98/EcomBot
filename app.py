from flask import Flask, render_template, request, jsonify, make_response
from utils import get_response, continue_conversation
from intentIdentifier import identify_intent_from_message

app = Flask(__name__)


@app.get("/")
def index_get():
    return render_template("base.html")


@app.post("/predict")
def predict():
    user_message = request.get_json().get("message")
    predicted_user_intent = identify_intent_from_message(user_message)
    response_text = "There seems to have been an error. My apologies"
    current_conversation_stage = request.cookies.get("conversationStage")
    chat_history = request.cookies.get("chatHistory")
    spam_tracker = request.cookies.get("spamTracker")
    if spam_tracker:
        spam_tracker = str(int(spam_tracker) + 1)
    else:
        spam_tracker = "1"

    if int(spam_tracker) >= 3:
        response_text = "You have spammed the chatbot, slow down or your messages won't be processed"

    elif predicted_user_intent == "['cancel']":
        current_conversation_stage = ""
        response_text = "task cancelled, what would you like to do next?"

    elif current_conversation_stage:
        continued_conversation = continue_conversation(user_message, current_conversation_stage, chat_history)
        current_conversation_stage = continued_conversation[1]
        response_text = continued_conversation[0]

    else:
        match predicted_user_intent:
            case "['question']":
                current_conversation_stage = ""
                response_text = get_response(user_message)
            case "['tracking']":
                current_conversation_stage = "t1"
                response_text = "Lets find your package, what is your order tracking number?"
            case "['complaint']":
                current_conversation_stage = "c1"
                response_text = "I'm sorry to hear that you have had a problem with our product, if you have a " \
                                   "question that you think I could help with type '"'question'"', if you want me to " \
                                   "raise a support ticket for you type '"'ticket'"'"
            case "['review']":
                current_conversation_stage = "r1"
                response_text = "Excellent lets start writing your review, what is your first name"
            case "['thanks']":
                current_conversation_stage = ""
                response_text = "You're welcome, have a nice day!"
            case "['greeting']":
                current_conversation_stage = ""
                response_text = "Hello, what can I help you with today?"

    chatbot_response_with_cookies = make_response(response_text)
    chatbot_response_with_cookies.set_cookie("conversationStage", current_conversation_stage)
    chatbot_response_with_cookies.set_cookie("spamTracker", spam_tracker, max_age=3)

    if chat_history:
        updated_history = chat_history + "|" + user_message
        chatbot_response_with_cookies.set_cookie("chatHistory", updated_history)
    else:
        chatbot_response_with_cookies.set_cookie("chatHistory", user_message)
    return chatbot_response_with_cookies


@app.route("/trackingStubEndpoint/<tracking_number>")
def track(tracking_number):
    royal_mail_stub_api_response = {
                                    "orderStatus": "in transit",
                                    "shippedOn": "2024-03-24T14:15:22Z",
                                    "shippingDetails": {
                                      "trackingNumber": tracking_number,
                                      "shippingTrackingStatus": "string",
                                      "serviceCode": "string",
                                      "shippingService": "string",
                                      "shippingCarrier": "Royal Mail",
                                      "receiveEmailNotification": True,
                                      "receiveSmsNotification": True,
                                      "guaranteedSaturdayDelivery": True,
                                      "requestSignatureUponDelivery": True,
                                      "isLocalCollect": True
                                    }
                                  }

    valid_order_numbers = ["JV620553954GB",
                           "050111C31F4",
                           "32048619500001B3A6F40",
                           "0210DAD9015248A2",
                           "0B0480284000010307090"]

    if tracking_number in valid_order_numbers:
        return jsonify(royal_mail_stub_api_response), 200
    else:
        return "", 404


@app.route("/reviewStubEndpoint", methods=["POST"])
def save_review():  # This is a stub API representing the review being successfully uploaded to the reviews database/spreadsheet
    data = request.data
    print(data)
    return "review created", 200


@app.route("/supportStubEndpoint", methods=["POST"])
def raise_ticket():  # This is a stub API representing the ticket being successfully uploaded to the support database
    data = request.data
    print(data)
    return "ticket raised", 200


if __name__ == "__main__":
    app.run(debug=True)
