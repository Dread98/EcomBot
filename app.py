from flask import Flask, render_template, request, jsonify, make_response
from utils import get_response
from intentIdentifier import identify_intent_from_message

app = Flask(__name__)


@app.get("/")
def index_get():
    return render_template("base.html")


@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    intent = identify_intent_from_message(text)
    response = "There seems to have been an error. My apologies"
    conversation_tracking_cookie = request.cookies.get("conversationStage")
    print(conversation_tracking_cookie)
    print(intent)
    if intent == "['cancel']":
        conversation_tracking_cookie = ""
        response = "task cancelled, what would you like to do next?"
    elif conversation_tracking_cookie is not None:
        print("placeholder")
        # continue_conversation(conversation_tracking_cookie)
    else:
        match intent:
            case "['question']":
                conversation_tracking_cookie = ""
                response = get_response(text)
            case "['tracking']":
                conversation_tracking_cookie = "t1"
                response = "Lets find your package, what is your order tracking number?"
            case "['complaint']":
                conversation_tracking_cookie = "c1"
                response = "I'm sorry to hear that you have had a problem with our product, if you have a question " \
                           "that you think I could help with type '"'question'"', if you want me to raise a support " \
                           "ticket for you type '"'ticket'"'"
            case "['review']":
                conversation_tracking_cookie = "r1"
                response = "Excellent lets start writing your review, what is your first name"
    re = make_response(response)
    re.set_cookie("conversationStage", conversation_tracking_cookie)
    return re


if __name__ == "__main__":
    app.run(debug=True)
