#!/usr/bin/env python3
import logging
import time
import datetime

import pymongo

from utils import json_from_file, json_to_file
import json
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return o.strftime("%d.%m.%Y")
        return json.JSONEncoder.default(self, o)


config_file_name = 'config.json'
config = {}

try:
    config = json_from_file(config_file_name, "Can't open ss-config file.")
except RuntimeError as e:
    print(e)
    exit()

formatter = logging.Formatter(config['logging.format'])
# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(config['logging.file'])

# Create formatters and add it to handlers
c_handler.setFormatter(formatter)
f_handler.setFormatter(formatter)

logging_level = config["logging.level"] if 'logging.level' in config else 20
print("Selecting logging level", logging_level)
print("Selecting logging format", config["logging.format"])
print("Selecting logging file \"%s\"" % config['logging.file'])

logging.basicConfig(format=config["logging.format"], handlers=[c_handler, f_handler])
logger = logging.getLogger(config["logging.name"])
logger.setLevel(logging_level)



db_records = []


while True:
    try:
        myclient = pymongo.MongoClient(config["db.url"])

        with myclient:
            dienasgramata = myclient.school.dienasgramata

            db_records = list(dienasgramata.find({"kind": "exercise"}, {'_id': 0}))

            # db_records = list(dienasgramata.aggregate( [
            # {"$project": {"kind":"$kind", "day":"$day", "subject":"$subject", "exercise":"$exercise",
            #                "date": {
            #                     "$dateFromString": {
            #                         "dateString": '$date',
            #                         "format": "%d.%m.%Y"
            #                     }
            #                 }
            #             }
            # } ] ))
            #, {'$match': {'date': {'$gte': datetime.datetime.utcnow()}}}
            for i in db_records:
                print(i)
            json_to_file(config['export.file.path'], JSONEncoder().encode(db_records))


    except RuntimeError as e:
        logger.error(e)

    if 'restart' in config and config['restart'] > 0:
        logger.info("Waiting %s seconds.", config['restart'])
        time.sleep(config['restart'])
    else:
        break
