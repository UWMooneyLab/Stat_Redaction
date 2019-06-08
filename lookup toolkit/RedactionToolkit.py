"""
'Don't be bad'
    -Samir Yhann 2018
"""
import hashlib
import requests
import json

phrase_length = 3

def hash(phrase):
    """
    :param phrase: the phrase that is going to be hased
    :return: a hash of the phrase using sha256
    """
    m = hashlib.sha256()
    m.update(phrase.encode('utf-8'))
    output = m.hexdigest()
    return output

def _concat_words(words):
    phrase = ""
    for x in words:
        phrase = phrase + " " + str(x)
    return phrase.strip()

def chunk_file(filename):
    """
    :param filename: the name of the file in the current dir that is going to be read and chunked.
    :return: a list of 3 word chunks from the file passed. Goes line by line.
    """

    '''I'm going to break this up into for each sentece '''
    with open(filename) as fp:
        data = fp.read()
        phrases = []
        words = data.split()
        if words:
            phrases = [' '.join(words[i:i + phrase_length]) for i in range(len(words) - phrase_length + 1)]
        return phrases

def lookup_phrase(phrase):
    """ NONE FUNCTIONAL
        Sends a phrase to the web service to be looked up on the database.
        :return: a dictionary of jsons which contain the sentence hash,
        occurrences, sites the phrase has been seen at, and the time at
        which the phrase was added to the database.
        :param phrase: the phrase being looked up (this should be unhashed)
        :param key: an authentication key
    """
    url = 'http://test-env.wuiqyva5ew.us-east-2.elasticbeanstalk.com/lookup'
    #url  = 'http://localhost:8000/lookup'
    hashed = hash(phrase)
    querystring = {'PHRASE': hashed}
    response = requests.post(url,data = querystring)
    return json.loads(response.text)

