import json
import pickle
import nltk
import numpy as np

from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

nltk.download('punkt')
nltk.download('wordnet')

lemmatazier = WordNetLemmatizer()   # reduces words to their stem (walking walks walker walk all become walk)
intents = json.loads(open('intents.json').read())

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))

model = load_model('my_model.keras')


def process_input(sentence): # tokenize and process the input data
    input_words = nltk.word_tokenize(sentence)
    input_words = [lemmatazier.lemmatize(word) for word in input_words]
    return input_words


def make_bag(sentence):  # if a word from the input matches the one in the bag indicate that with a 1
    sentence_words = process_input(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence):
    bag = make_bag(sentence)
    result = model.predict(np.array([bag]))[0]  # predict using the bag of words
    error_threshold_percentage = 0.25  # 25% uncertainty
    results = [[i, r] for i, r in enumerate(result) if r > error_threshold_percentage]
    results.sort(key=lambda x: x[1], reverse=True)
    predicted_class = []
    for r in results:
        predicted_class.append({'intent': classes[r[0]], 'probability': str(r[1])})
        # returns the highest probability case that is above 25% and displays its probability
    return predicted_class


def identify_intent(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = i['responses'] # returns the response for the correct tag
            break
    return result


def identify_intent_from_message(msg):
    predicted_class = predict_class(msg)
    result = identify_intent(predicted_class, intents)
    return str(result)

