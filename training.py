import random
import json
import pickle
import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer
import tensorflow as tf

nltk.download('punkt')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()  # reduces words to their stem (walking walks walker walk all become walk)

intents = json.loads(open('intents.json').read())

words_list = []
classes = []
documents = []
ignored_letters = ['?', '!', '.', ',']

for intent in intents['intents']:
    for pattern in intent['patterns']:
        tokenized_words = nltk.word_tokenize(pattern)
        words_list.extend(tokenized_words)
        # tokenize splits sentences into their component parts (hello I am happy becomes "hello" "I" "am" "happy").
        documents.append((tokenized_words, intent['tag']))  # associates the tokenized words with the intent tag
        if intent['tag'] not in classes:  # adds new intent to classes if not already in there
            classes.append(intent['tag'])

words_list = [lemmatizer.lemmatize(word) for word in words_list if word not in ignored_letters]
words_list = sorted(set(words_list))  # converting to set eliminates duplicates
classes = sorted(set(classes))

pickle.dump(words_list, open('words.pkl', 'wb'))  # save to pickle files
pickle.dump(classes, open('classes.pkl', 'wb'))

training = []
empty_output = [0] * len(classes)    # sets up empty numerical representation

for document in documents:
    bag = []
    word_patterns = document[0]
    word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
    # lowercases all words in a given document
    for word in words_list:
        bag.append(1) if word in word_patterns else bag.append(0)   # adds words to list

    output_row = list(empty_output)
    output_row[classes.index(document[1])] = 1
    training.append(bag + output_row)    # populates the training data with the bag of words and its corresponding row

random.shuffle(training)
training = np.array(training)   # convert to numpy array

train_x = training[:, :len(words_list)]
train_y = training[:, len(words_list):]

model = tf.keras.Sequential()   # explicit import due to errors
model.add(tf.keras.layers.Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
# Im aware this setup works, but I struggle to explain the individual components
model.add(tf.keras.layers.Dropout(0.5))
model.add(tf.keras.layers.Dense(64, activation='relu'))
model.add(tf.keras.layers.Dropout(0.5))
model.add(tf.keras.layers.Dense(len(train_y[0]), activation='softmax'))
# softmax scales % allocations of all outputs so that they total 100%

sgd = tf.keras.optimizers.SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
# SGD stands for stochastic gradient descent and is an optimisation algorithm to find the best fit

model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)
# Epochs refer to how many times the data is run through the algorithm
model.save('my_model.keras')
print('Training done')
