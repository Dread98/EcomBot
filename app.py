from flask import Flask, render_template, request, jsonify
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
    # if intent == "tracking":
    #     trackingConvoStage = 1
    #     return "of course what is your order tracking number?"
    # else if intent == "review":
    #     reviewConvoStage = 1
    #     return "of course what is your order tracking number?"
    #
    response = get_response(text)
    message = {"answer": response}
    # message = {"answer": intent}

    return jsonify(message)


if __name__ == "__main__":
    app.run(debug=True)
