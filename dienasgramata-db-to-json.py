#!/usr/bin/env python3
import logging
import time
import datetime

import pymongo

from utils import json_from_file, json_to_file


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

now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
left_border = now - datetime.timedelta(days = 7 + datetime.datetime.today().weekday()) - datetime.timedelta(seconds=1)
right_border = now + datetime.timedelta(days = 7 - datetime.datetime.today().weekday() + 7) - datetime.timedelta(seconds=1)

while True:
    try:
        myclient = pymongo.MongoClient(config["db.url"])
        with myclient:
            dienasgramata = myclient.school.dienasgramata
            db_records = list(dienasgramata.find(
                 {"$and": [
                     {"kind": "exercise"},
                     {"date": {"$gt": left_border}},
                     {"date": {"$lt": right_border}}
                       ]
                 },
                {'_id': 0}).sort("date"))
            print("Seeking for records from %s to %s" % (left_border, right_border))
            for i in db_records:
                print(i)
            json_to_file(config['export.file.path'], db_records)

    except RuntimeError as e:
        logger.error(e)

    if 'restart' in config and config['restart'] > 0:
        logger.info("Waiting %s seconds.", config['restart'])
        time.sleep(config['restart'])
    else:
        break
