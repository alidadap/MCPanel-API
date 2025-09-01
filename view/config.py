import json

conf_file = open("config.json","r")
storage = dict(json.load(conf_file))
conf_file.close()