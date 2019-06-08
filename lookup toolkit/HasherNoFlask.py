
##this is VERY OLD AND EARLY
#this is specifially for the admins use only
##if you feed this in files and it will send hashes directly to the sever. It's really not the best way to do this, but it is a way
import hashlib
import boto3
import decimal
import datetime



dynamodb = boto3.resource('dynamodb', region_name='us-east-2', endpoint_url="https://dynamodb.us-east-2.amazonaws.com")

table = dynamodb.Table('HASH_LOOKUP')


clock = datetime.datetime
##hashes
def hash(phrase):
    """
    :param phrase: the phrase that is going to be hased
    :return: a hash of the phrase using sha256
    """
    m = hashlib.sha256()
    m.update(phrase.encode('utf-8'))
    output = m.hexdigest()
    return output

##makes the phrases
def _concat_words(words):
    phrase = ""
    for x in words:
        phrase = phrase + " " + str(x)
    return phrase.strip()

##reads in a file and gets hashes and whatnot
def read_file(filename):
    with open(filename) as fp:
        data = fp.readline()
        #output = (tokenizer.tokenize(data))
        output = []
        while data != "":
            words = data.split()
            index = 0
            while index < len(words)-3:
                output.append(words[index: index + 3])
                del words[index]
            output.append(words[index:])
            print(data)
            data = fp.readline()

        print(output)
        return output

##finds all the hases and 
def hash_note(filename, site):
    hashes = dict()
    if site == None:
        site = 'ANON'
    for s in read_file(filename):
        words =""
        for w in s:
            words = words + " " + w
        hashed = hash(words.strip())
        if hashed not in hashes.keys():
            hashes[hashed] = {'COUNTS': 1, 'SITE': site, 'TIMES': [str(clock.utcnow())]}
        else:
            hashes[hashed]['COUNTS'] += 1
            hashes[hashed] ['TIMES' ].append(str(clock.utcnow()))

    print (hashes)
    return hashes

#this is the important one
##looks up the phrase
def phrase_lookup(h):
    response = table.get_item(
        Key=
        {
            'SENTENCE_HASH': h
        }
    )
    try: item = response['Item']
    except KeyError:
       item  = {'SENTENCE_HASH' : h, 'COUNTS' : 0, 'TIMES':[]}
    print(item)
    return item

##this will update the databases with the new information about the hash that is found in the note that is being currently examined.
def update_hashes(filename, site):
    hashcounts = hash_note(filename, site).items()
    #count = 0
    for h, v in hashcounts:
        #if count == 10:
         #   break
        item = phrase_lookup(h)
        curcount = item.get('COUNTS')
        curtimes = item.get('TIMES')
        curtimes.extend(v['TIMES'])
        if curcount == 0:
            table.put_item(
                Item={
                    'SENTENCE_HASH': h,
                    'COUNTS' : v['COUNTS'],
                    'SITE' : v['SITE'],
                    'TIMES': v['TIMES']
                }
            )
        else:
            table.update_item(
                Key={
                    'SENTENCE_HASH': h
                },
            UpdateExpression = 'SET COUNTS = :val1 , TIMES = :val2',
                               ExpressionAttributeValues = {
                ':val1': v['COUNTS'] + curcount,
                ':val2': curtimes
            }
            )
       # count += 1
    return 'updated'


##decimal formating
def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

##this is the manual way to have people upload files
if __name__ == '__main__':


    f = input("What is the name of the file you wnat to add?")
    s = input("Which site are you?")
    try:
        update_hashes(f, s)
        print('Done Updating')
    except FileNotFoundError:
        print('File not found')
