from flask import Flask, render_template, request, jsonify, make_response
from utils import get_response, continue_conversation
from intentIdentifier import identify_intent_from_message

app = Flask(__name__)


@app.get("/")
def index_get():
    return render_template("base.html")


@app.post("/predict")
def predict():
    input_message = request.get_json().get("message")
    predicted_user_intent = identify_intent_from_message(input_message)
    chatbot_response = "There seems to have been an error. My apologies"
    conversation_tracking_cookie = request.cookies.get("conversationStage")
    print(conversation_tracking_cookie)
    print(predicted_user_intent)
    if predicted_user_intent == "['cancel']":
        conversation_tracking_cookie = ""
        chatbot_response = "task cancelled, what would you like to do next?"

    elif conversation_tracking_cookie is not None:
        chatbot_response = continue_conversation(input_message, conversation_tracking_cookie)

    else:
        match predicted_user_intent:
            case "['question']":
                conversation_tracking_cookie = ""
                chatbot_response = get_response(input_message)
            case "['tracking']":
                conversation_tracking_cookie = "t1"
                chatbot_response = "Lets find your package, what is your order tracking number?"
            case "['complaint']":
                conversation_tracking_cookie = "c1"
                chatbot_response = "I'm sorry to hear that you have had a problem with our product, if you have a question " \
                           "that you think I could help with type '"'question'"', if you want me to raise a support " \
                           "ticket for you type '"'ticket'"'"
            case "['review']":
                conversation_tracking_cookie = "r1"
                chatbot_response = "Excellent lets start writing your review, what is your first name"
    re = make_response(chatbot_response)
    re.set_cookie("conversationStage", conversation_tracking_cookie)
    return re


@app.route("/trackingStubEndpoint/<tracking_number>")
def track(tracking_number):
    royal_mail_stub_api_response = {
        "orderStatus": "string",
        "shippedOn": "2019-08-24T14:15:22Z",
        "shippingDetails": {
          "trackingNumber": tracking_number,
          "shippingTrackingStatus": "string",
          "serviceCode": "string",
          "shippingService": "string",
          "shippingCarrier": "string",
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
    data = request.get_json()
    print("Review raised for " + data.name
          + " for product " + data.product
          + " with a review of " + data.stars
          + " stars and content: " + data.content)


@app.route("/supportStubEndpoint", methods=["POST"])
def raise_ticket():  # This is a stub API representing the ticket being successfully uploaded to the support database
    data = request.get_json()
    print("Support Ticket raised for " + data.name
          + " with contact details: " + data.email
          + " with content: " + data.content)


if __name__ == "__main__":
    app.run(debug=True)
