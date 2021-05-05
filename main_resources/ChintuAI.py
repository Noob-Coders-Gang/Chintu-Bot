import json
import pickle
import random

import nltk
import numpy as np
from keras.models import load_model
from nltk.stem import WordNetLemmatizer

nltk.download('punkt')
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

# --------------------------------Importing ChatModels--------------------------------#
model = load_model('./Chintu-Chat-Model/ChintuChat.h5')
intents = json.loads(open('./Chintu-Chat-Model/intents.json').read())
words = pickle.load(open('./Chintu-Chat-Model/words.pkl', 'rb'))
classes = pickle.load(open('./Chintu-Chat-Model/classes.pkl', 'rb'))


# --------------------------------Tokenizing the sentence--------------------------------#


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(
        word.lower()) for word in sentence_words]
    return sentence_words


# --------------------------------Storing Tokenised Data in Bag of words--------------------------------#


def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return (np.array(bag))


# --------------------------------Predicting Class--------------------------------#


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


# --------------------------------Getting random response from the Intense--------------------------------#


def getResponse(ints, intents_json):
    result = random.choice(
        ["I'm confused. Could you tell me clearly?", 'Sorry I dont get you', 'Dont talk bullsh*t, I cant understand',
         'Say it Clearly', 'I\'m sorry, I don\'t understand. Could you say it again?'])
    tag = ints[0]['intent']
    # print(tag)
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if (i['tag'] == tag):
            result = random.choice(i['responses'])
            break
    return result, tag


# --------------------------------  prediction from model --------------------------------#


def prediction(msg):
    ints = predict_class(msg, model)
    res, tag = getResponse(ints, intents)
    if float(ints[0]['probability']) > 0.95:
        result = {"response": res,
                  "tag": tag
                  }
    else:
        result = {"response": "Dont talk bullsh*t, I cant understand",
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


# opening intents
with open("./Chintu-Chat-Model/intents.json") as file:
    data = json.load(file)


def converttostring(list):
    res = str(", ".join(map(str, list)))
    return res


# --------------------------------get response--------------------------------#
def AskChintu(query):
    try:
        Bot_Response = prediction(query)
        tag = Bot_Response.get('tag')

    except Exception as e:
        Bot_Response = {'response': e, 'tag': "error"}
        # print(e)

    return Bot_Response
