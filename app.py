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
    response = "There seems to have been an error. My apologies"
    print(intent)
    if intent == "['cancel']":
        conversation_stage_tracker = ""
        response = "task cancelled, what would you like to do next?"

    # continue_conversation(conversation_stage_tracker)

    match intent:
        case "['question']":
            conversation_stage_tracker = ""
            response = get_response(text)
        case "['tracking']":
            conversation_stage_tracker = "t1"
            response = "Lets find your package, what is your order tracking number?"
        case "['complaint']":
            conversation_stage_tracker = "c1"
            response = "I'm sorry to hear that you have had a problem with our product, if you have a question that " \
                       "you think I could help with type '"'question'"', if you want me to raise a support ticket " \
                       "for you type '"'ticket'"'"
        case "['review']":
            conversation_stage_tracker = "r1"
            response = "Excellent lets start writing your review, what is your first name"
    message = {"answer": response}
    return jsonify(message)


if __name__ == "__main__":
    app.run(debug=True)
