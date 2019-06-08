#Samir Yhann
#Be good to others

##this is used to create json databases on a local server, this way you don't have to hammer the server 
import time
import re
import hashlib
import json
import pandas as pd
import glob

##can be any length
NUMBER_OF_FILE_LETTERS = 3
PHRASE_LENGTH = 2

##I don't know
database = 0

##same as in lookup
def concat_words(words):
    phrase = ""
    for x in words:
        phrase = phrase + " " + str(x)
    return phrase.strip()

##same as in lookup
def create_phrases(data,phrase_length):
    phrases = []
    words = data.split()
    if words:
        index = 0
        while index < len(words) - PHRASE_LENGTH:
            phrases.append(concat_words(words[index: index + PHRASE_LENGTH]))
            index = index + 1
        phrases.append(concat_words(words[index:]))
    hashed = []
    for p in phrases:
        hashed.append(hash(p))
    return hashed

def per_subject(sub_id, PHRASE_LENGTH,mimic):
    print(sub_id)
    subject_notes = mimic.get_group(sub_id)
    # subject_notes_inds = mimic.get_group(sub_id).index
    #print(subject_notes)
    subject_phrase_dict = dict()
    for ind in subject_notes.iterrows():
        phrase_count_list = tally_note(ind[1]['TEXT'], PHRASE_LENGTH)
        #print(phrase_count_list)
        for dictionary in phrase_count_list:
            cur_phrase = dictionary['PHRASE']
            #print(cur_phrase)
            cur_count = dictionary['COUNTS']
            try:
                subject_phrase_dict[cur_phrase]['COUNT'] = subject_phrase_dict[cur_phrase]['COUNT'] + cur_count
                subject_phrase_dict[cur_phrase]['NOTES'] = subject_phrase_dict[cur_phrase]['NOTES'] + 1
            except KeyError:
                subject_phrase_dict[cur_phrase] = {'COUNT': cur_count, 'NOTES': 1}

    keys = subject_phrase_dict.keys()
    [update_database_json(phrase, subject_phrase_dict[phrase]) for phrase in keys]

##Chunks the note into phrases using create_phrases then counts how many occurances of each phrase are found are found per note.
## The phrases are already hahsed once they are sent to be updated.
##then will update the database
def tally_note(text, length):
    note = text

    phrases = create_phrases(note, length)
    raw_phrases = list()
    [raw_phrases.append(phrase)for phrase in phrases]
    phrase_set = set(raw_phrases)

    phrase_counts_list = [{'PHRASE': phrase, 'COUNTS': raw_phrases.count(phrase)} for phrase in phrase_set]
    return phrase_counts_list
    ##now a list instead of a dict and we will update using the new alogrithm
    #this might encounter a pipleine slowdown due to the size of the phrase but it should be fine

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

def remove_punct(note):
    data = note.lower()
    data = re.sub(r'(?<!\d)\.(?!\d)', '', data)
    data = re.sub('[!@#$,:^&]', '', data)
    data = data.strip()
    return data

##This is what the will find or create file that will need to be altered.
##This also update the database with the new data
def update_database_json(hash, stats):
    filename = str(hash)[:NUMBER_OF_FILE_LETTERS]+'.json'
    add_count = stats['COUNT']
    add_notes = stats['NOTES']
    try:
        with open(str(database) +'\\mimicii_db\\' + filename, 'r+') as f:
            data = json.load(f)

            try:
                data[hash]['COUNT'] = data[hash]['COUNT'] + add_count
                times = (data[hash]['TIMES']) + add_notes
                #times.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                data[hash]['TIMES'] = times
                #ids = set(data[hash]['IDs'])
                #ids.add(str(id))
                data[hash]['IDs'] = data[hash]['IDs'] + 1
                # locations = (data[hash]['LOCATIONS'])
                # locations.append(this_site)
                # data[hash]['LOCATIONS'] = locations

            except KeyError:
                data[hash] = {"HASH": hash, "COUNT": add_count, "TIMES": add_notes, "IDs": 1}
                # "LOCATIONS" : this_site

            f.seek(0)
            json.dump(data, fp=f, indent=4)

    except FileNotFoundError:
        with open(str(database) +'\\mimicii_db\\' + filename, 'w') as f:
            data = dict()
            data[hash] = {"HASH": hash, "COUNT": add_count, "TIMES": add_notes, "IDs": 1}
            # "LOCATIONS" : this_site
            f.seek(0)
            json.dump(data, fp=f, indent=4)

    #print(filename + ", " + hash + " updated")

if __name__ == '__main__':
    print('running')
    start = time.time()
    for db in range(5,6):
        mimic = pd.DataFrame()
        database = db
        for file_dir in glob.glob(str(db) + '\\*.text'):
            filename = file_dir[2:]
            filename = filename[:len(filename)-5]
            broken_filename = filename.split('_')
            patient_id = broken_filename[0]
            note_id = broken_filename[1]
            with open(file_dir, encoding="utf8", errors='ignore') as d:
                text = d.read()
            info = {'SUBJECT_ID': [patient_id], 'TEXT': [text]}
            df = pd.DataFrame(info)
            mimic = mimic.append(df)
        sub_ids = mimic['SUBJECT_ID']
        sub_ids = set(sub_ids)
        mimic = mimic.groupby('SUBJECT_ID')
        print('total number of sub ids = ' + str(len(sub_ids)))
        [per_subject(sub_id, PHRASE_LENGTH,mimic) for sub_id in sub_ids]
        #pool.close()
        #pool.join()
        print('done')
        end = time.time()
        print(end-start)
        ##indead i want select distinct subject id, then for each subic, select text text from noteevents where subid = subid
