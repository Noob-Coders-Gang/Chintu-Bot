import json
import random

import numpy as np
import pickle
import nltk
import requests
from nltk.stem import WordNetLemmatizer

nltk.download('punkt')
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()


# --------------------------------Importing ChatModels--------------------------------#

intents = json.loads(open('./Chintu-Chat-Model/intents.json',
                          encoding='utf-8', errors='ignore').read())
words = pickle.load(open('./Chintu-Chat-Model/words.pkl', 'rb'))
classes = pickle.load(open('./Chintu-Chat-Model/classes.pkl', 'rb'))


url = 'https://chintu-ai.herokuapp.com/v1/models/chintuchat:predict'


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(
        word.lower()) for word in sentence_words]
    return sentence_words


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
    return np.array(bag)


def make_arr(sentence):
    p = bow(sentence, words, show_details=False)
    return np.array([p])


def create_return_list(res):
    ERROR_THRESHOLD = 0.9
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
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


def docker_ask(sentence):
    instances = make_arr(sentence)
    data = json.dumps({"signature_name": "serving_default",
                       "instances": instances.tolist()})
    headers = {"content-type": "application/json"}
    json_response = requests.post(url, data=data, headers=headers)
    predictions = json.loads(json_response.text)['predictions'][0]
    return_list = create_return_list(predictions)
    return return_list


def getResponse(ints, intents_json):
    result = random.choice(
        ["I'm confused. Could you tell me clearly?", 'Sorry I dont get you',
         'Say it Clearly', 'I\'m sorry, I don\'t understand. Could you say it again?'])
    tag = ints[0]['intent']
    # print(tag)
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result, tag


def prediction(msg):
    ints = docker_ask(msg)
    res, tag = getResponse(ints, intents)
    if float(ints[0]['probability']) > 0.97:
        result = {"response": res,
                  "tag": tag
                  }
    else:
        result = {"response": "Dont talk bullsh*t, I cant understand",
                  "tag": "couldnotunderstand"
                  }
    return result


# --------------------------------get response--------------------------------#
def AskChintu(query):
    try:
        if query == None or query.strip() == "":
            return {'response':  random.choice(['what?', "Hey ssup! 🙋‍♂️", "what⁉️", "what you want?", "why did you ping me sir?"]), 'tag': "nonemsg"}

        Bot_Response = prediction(query)

    except Exception as e:
        Bot_Response = {
            'response': 'I have headache I cant understand', 'tag': "error"}
        # print(e)

    return Bot_Response
