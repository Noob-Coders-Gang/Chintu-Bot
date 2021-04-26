from copy import Error
from nltk.stem import WordNetLemmatizer
import nltk
import os
from os.path import join
from urllib.request import urlopen
import json
import numpy as np
import keras
import pickle
import random
from keras.models import load_model

nltk.download('punkt')
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()


model = load_model('ChintuChat.h5')
intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(
        word.lower()) for word in sentence_words]
    return sentence_words


def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return(np.array(bag))


def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.9
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    # print(results)
    return_list = []
#     for r in results:
#         return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    try:
        if results[0]:
            for r in results:
                return_list.append(
                    {"intent": classes[r[0]], "probability": str(r[1])})
        else:
            return_list.append({"intent": 'noanswer', "probability": '1'})
    except:
        return_list.append({"intent": 'noanswer', "probability": '1'})
    # print(return_list)
    return return_list


def getResponse(ints, intents_json):
    result = 'sorry i could not understand'
    tag = ints[0]['intent']
    # print(tag)
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag'] == tag):
            result = random.choice(i['responses'])
            break
    return result, tag


def prediction(msg):
    ints = predict_class(msg, model)
    res, tag = getResponse(ints, intents)
    if float(ints[0]['probability']) > 0.95:
        result = {"response": res,
                  "tag": tag
                  }
    else:
        result = {"response": "sorry i could not understand what you are saying",
                  "tag": "couldnotunderstand"
                  }
    return result
# text to response


def to_json(response, tag=None):
    response = {
        "response": response,
        "tag": tag,
    }

    return response


# taking command from response
def takeCommand(cmd):

    return cmd


# opening intents
with open("intents.json") as file:
    data = json.load(file)


def converttostring(list):
    res = str(", ".join(map(str, list)))
    return res


##### response #####
def ChatBot(query):

    try:
        Bot_Response = prediction(query)
        tag = Bot_Response.get('tag')

    except Exception as e:
        Bot_Response = {'response': e, 'tag': "error"}
        # print(e)

    return Bot_Response


os.system('cls')
while True:
    x = input('user : ')
    if x.lower() in ['exit', 'quit', 'close']:
        exit()
    print('Bot : ' + ChatBot(takeCommand(x).lower())['response'])
