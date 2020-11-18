import os, subprocess
from datetime import datetime, timedelta, date
import time
import argparse
import logging
import json
import math

data = "";

log = logging.getLogger("File Purge System")

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def loadConfig():
    global data
    confpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Config.json")
    if os.path.exists(confpath):
        with open("Config.json") as json_data_file:
            data = json.load(json_data_file)
    else:
        print("No Config file found")
        exit(0)

def parse_args():
    parser = argparse.ArgumentParser(description="File removal system")
    parser.add_argument("-d", action='store_true', help="Dry run no files will be deleted")
    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = parse_args()
    loadConfig()
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y-%H%M%S")
    log.setLevel(logging.INFO)
    hdlr = logging.FileHandler('%s.log' % (dt_string))
    formatter = logging.Formatter("%(asctime)-15s  %(message)s")
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
    total = 0;
    files = 0;
    if args.d:
        print ("Dry run mode - Files to be Deleted")
        for val in data['folders']:
            print("\n%s" % val)
            entries = os.listdir(val)
            for entry in entries:
                creation_date = datetime.fromtimestamp(os.stat(os.path.join(val, entry)).st_atime)
                if creation_date < datetime.now() - timedelta(days=int(data['days'])):
                    filesize = os.path.getsize(os.path.join(val, entry))
                    total = filesize + total
                    files += 1
                    log.info("%s\%s to be Deleted" % (val, entry))

            print("Total File size to be deleted would be %s over %s files" % (convert_size(total),files))
        print("\nDry Run Log file stored %s.log" % (dt_string))
    else:
        delete = input("Are you sure you wish to delete all files older than %s? (Y/N): " % (data['days']))
        if delete == "y":
            print("Well here we go")
            for val in data['folders']:
                print(val)
                entries = os.listdir(val)
                for entry in entries:
                    creation_date = datetime.fromtimestamp(os.stat(os.path.join(val, entry)).st_atime)
                    if creation_date < datetime.now() - timedelta(days=int(data['days'])):
                        filesize = os.path.getsize(os.path.join(val, entry))
                        os.remove(os.path.join(val, entry))
                        total = filesize + total
                        files += 1
                        log.info("%s\%s Deleted" % (val,entry))

                print("Total File size %s over %s files" % (convert_size(total), files))
            print("\nLog file stored %s.log" % (dt_string))