import json
import datetime

##this is the number of character tbat will be used in making the filename
##the larger this number, the more overall files you will have, but the smaller each file will be
##this could lead to faster read times with smaller files, to a certain extent
NUMBER_OF_FILE_LETTERS = 3

##this function takes in a hash, the number of times it occers in a given ntoe or situation and an id number assoiated with it
##the number of occerences is then added to the database along with the id number and the time if enabled.
def update_database_json(hash, add_count, id):
    filename = str(hash)[:NUMBER_OF_FILE_LETTERS]+'.json'
    try:
        with open(filename, 'r+') as f:
            data = json.load(f)

            try:
                data[hash]['COUNT'] = data[hash]['COUNT'] + add_count
                times = (data[hash]['TIMES'])
                times.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                data[hash]['TIMES'] = times
                ids = set(data['IDs'])
                ids.add(id)
                data['IDs'] = list(ids)
                ##  This was taken out to reduce database size
                # locations = (data[hash]['LOCATIONS'])
                # locations.append(this_site)
                # data[hash]['LOCATIONS'] = locations

            except KeyError:
                data[hash] = {"HASH": hash, "COUNT": add_count, "TIMES": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")], "IDs": [id]}
                # "LOCATIONS" : this_site

            f.seek(0)
            json.dump(data, fp=f, indent=4)

    except FileNotFoundError:
        with open(filename, 'w') as f:
            data = dict()
            data[hash] = {"HASH": hash, "COUNT": add_count, "TIMES": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")], "IDs": [id]}
            # "LOCATIONS" : this_site
            f.seek(0)
            json.dump(data, fp=f, indent=4)