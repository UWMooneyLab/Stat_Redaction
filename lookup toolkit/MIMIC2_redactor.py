##Samir Yhann
## Don't be evil


PHRASE_LENGTH = 2
##this is build for phrase length 2

import re
import hashlib
import datetime
import json
import io
import pandas as pd
clock = datetime.datetime

##this is code that is build specifially for mimic 2 since the files in it are of a particular format
##this is the main method for redacting a file in mimic ii
def redact(dir, filename, threshold, dbs):
    #print(filename)
    redactions = pd.DataFrame()
    with open(dir +'\\'+ filename + '.text', encoding="utf8", errors='ignore') as fl:
        file_info = filename.split('_')
        sub_id = file_info[0]
        note_id = file_info[1]
        text = fl.read()
        #lines = fl.readlines()
        #for text in lines:
        phrases = create_phrases(text)
        #print(phrases)
        phrase_table = make_phrase_hash_table(phrases)
        count_table = get_counts(set(phrase_table.values()), dbs)
        #print(count_table)
        output = min_blackout(phrases, phrase_table, count_table, threshold, redactions, filename, sub_id, note_id, dir, text)
        #save(filename, output)

##this themod is for redacting on a specific raw text
##THIS METHOD WAS NOT USED FOR MIMIC 2
def redact_on_text(file_text, row_num, threshold):
    buf = io.StringIO(file_text)
    lines = buf.readlines()
    for text in lines:
        phrases = create_phrases(text)
        phrase_table = make_phrase_hash_table(phrases)
        count_table = get_counts(list(phrase_table.values()))
        #print(count_table)
        output = min_blackout(phrases, phrase_table, count_table, threshold)
        save(row_num, output)

##this is the minimum balckout method that redacts the max ammount based upon the threshold
##if one of the phrases a word is involved in
def min_blackout(chunked_note, hash_table, count_table, threshold, df ,fn, sub_id, note_id, dir, text):
    output = ''
    ind = 0
    note_index = 0

    ##this method iterates over all the different lsit of phrases within a note
    ##if any hrase does not meet the reqirements for being left, ie the threshold, then both words are removed
    ##this part of the method has been hard coded for 2 word long, but with a for loop it could be changed so that it
    ##  can work for any phrase length

    ##this method is done by adding thier a redaction symbol or the first word in a phrase to a note.
    while ind in range(len(chunked_note)-1):
        phrase = chunked_note[ind]
        # print(phrase)
        # redact_symbol = '#' * len(phrase)
        redact_symbol = '|' + phrase.upper() + '|'
        hash = hash_table[phrase]
        add = str(phrase.split()[0])
        if count_table[hash]['COUNT'] >= threshold:
            ind = ind + 1
            #print(str(note_index) + " " + add)
            note_index = note_index + len(add) + 1
            output = output + " " + add
        else:
            ##here just do a search around the current note_index and endex  to see if anything is cloes by  +- 10
            output = output + " " + redact_symbol
            endex = note_index + len(phrase.split()[0]) + 1
            try:
                note_index = text.index(phrase.split()[0], note_index -10, endex + 10)
                endex = note_index + len(phrase.split()[0]) + 1
            except:
                pass
            redacted_word_1 = {'SUB_ID': sub_id, 'NOTE_ID': note_id, 'Index Start': note_index, 'Index End': endex - 1, 'word': add}
            add = str(phrase.split()[1])
            note_index = endex
            endex = note_index + len(add) +1
            try:
                note_index = text.index(phrase.split()[1], note_index - 10, endex + 10)
                endex = note_index + len(phrase.split()[1]) + 1
            except:
                pass
            redacted_word_2 = {'SUB_ID':sub_id ,'NOTE_ID':note_id, 'Index Start': note_index, 'Index End': endex-1, 'word': add}
            df = df.append(redacted_word_1, ignore_index=True)
            df = df.append(redacted_word_2, ignore_index=True)
            note_index = endex
            ind = ind + PHRASE_LENGTH
    end = len(chunked_note)

    ##edge case catching
    if end > ind:
        phrase = chunked_note[end-1]
        #print(str(phrase.split()))
        redact_symbol = '|' + phrase.upper() + '|'
        #redact_symbol = '#' * len(phrase)
        hash = hash_table[phrase]
        add = str(phrase.split()[0])
        if count_table[hash]['COUNT'] >= threshold:
            output = output + " " + phrase
        else:
            endex = note_index + len(phrase) + 1
            redacted = {'SUB_ID': sub_id, 'NOTE_ID': note_id, 'Index Start': note_index,'Index End': endex-1, 'word': add}
            df = df.append(redacted, ignore_index=True)
            output = output + " " + redact_symbol
    elif end == ind and chunked_note:
        #print(chunked_note)
        phrase = chunked_note[end-1]
        #print(str(phrase.split()))
        add = str(phrase.split()[1])
        redact_symbol = '|' + add.upper() + '|'
        #redact_symbol = '#' * len(phrase.split()[1])
        hash = hash_table[phrase]
        if count_table[hash]['COUNT'] >= threshold:
            output = output + " " + str(add)

        else:
            end = note_index + len(phrase) + 1
            redacted = {'Index Start': note_index,'Index End': endex-1, 'word': add}
            df = df.append(redacted, ignore_index=True)
            output = output + " " + redact_symbol
    df.to_csv(dir + '\\redactions\\' + str(threshold) + '\\' + fn + '_redacted.csv')
    return output

##makes a dict that where the phrases are the key and the counts are the value
def get_counts(hashes, dbs):
    data_dict = {}
    for h in hashes:
        data_dict[h] = lookup(h, dbs)
    return data_dict


##lookup the counts from across all the serperate databases
def lookup(hash, dbs):
    info = dict()
    info['COUNT'] = 0
    info['TIMES'] = 0
    info['IDs'] = 0
    for db in dbs:
        filename = hash[:3]
        filename = filename + '.json'
        location  = str(db) +'\\mimicii_db\\'+filename

        try:
            with open(location, 'r') as f:
                data = json.load(f)
                try:
                    info['COUNT'] = info['COUNT'] + data[hash]['COUNT']
                    info['TIMES'] = info['TIMES'] + data[hash]['TIMES']
                    info['IDs'] = info['IDs'] + data[hash]['IDs']
                except KeyError:
                    pass
                    # info['COUNT'] = 0
                    # info['TIMES'] = 0
                    # info['IDs'] = 0
                    # "LOCATIONS" : this_site

        except FileNotFoundError:
            pass
            # info['COUNT'] = -1
            # info['TIMES'] = -1
            # info['IDs'] = -1

    return info

## saves the redacted text into a new file
def save (og_filename, redacted):
    save_file = (og_filename + '_redacted')
    with open(save_file + '.txt', 'a+', encoding='utf8') as out_file:
        out_file.write(redacted.strip() + "\r\n")

################################################VESTIGL######################

##removes punctuation and sends all characters to lowwer case.
def remove_punct(note):
    data = note.lower()
    data = re.sub(r'(?<!\d)\.(?!\d)', '', data)
    data = re.sub('[!@#$,:^&]', '', data)
    data = data.strip()
    return data

def hash(phrase):
    """
    :param phrase: the phrase that is going to be hased
    :return: a hash of the phrase using sha256
    """
    phrase = remove_punct(phrase)
    m = hashlib.sha256()
    m.update(phrase.encode('utf-8'))
    output = m.hexdigest()
    return output


#returns a dict of phrases and thier hashes for a given note
def create_phrases(data):
    phrases = []
    words = data.split()
    if words:
        index = 0
        while index < len(words) - PHRASE_LENGTH:
            phrases.append(concat_words(words[index: index + PHRASE_LENGTH]))
            index = index + 1
        phrases.append(concat_words(words[index:]))
    return phrases

##takes in a list of words in order that create a note and puts them together to create 2 word long phrases
def concat_words(words):
    phrase = ""
    for x in words:
        phrase = phrase + " " + str(x)
    #return phrase.strip()
    return phrase

##makes a dict with phrases as the key and thier hash as the value
def make_phrase_hash_table(phrases):
    hashed = {}
    for p in phrases:
        hashed[p] = hash(p)
    return hashed