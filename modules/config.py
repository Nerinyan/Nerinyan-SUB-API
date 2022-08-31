import os
import configparser
import sys

from common import glob

class config:
    def __init__(self, file):
        self.config = configparser.ConfigParser()
        self.default = True
        self.fileName = file
        if os.path.isfile(self.fileName):
            self.config.read(self.fileName, encoding="utf-8")
            self.default = False
        else:
            self.generateConfig()
            self.default = True

    def checkConfig(self, parsedConfig=None):
        if parsedConfig is None:
            parsedConfig = self.config
        
        try:
            parsedConfig.get("root", "beatmaps")
            parsedConfig.get("root", "unzip")
            parsedConfig.get("root", "rebuild")
            return True
        except configparser.Error:
            return False
    
    def generateConfig(self):
        f = open(self.fileName, "w", encoding="utf-8")

        self.config.add_section("root")
        self.config.set("root", "beatmaps", "CHANGE_HERE")
        self.config.set("root", "unzip", "CHANGE_HERE")
        self.config.set("root", "rebuild", "CHANGE_HERE")

        self.config.write(f)
        
        f.close()

def CONFIG_LOADER():
    conf = config(str(glob.BASEROOT) + "/config.ini")
    if conf.default:
        print("config.ini is not found. A default one has been generated.")
        sys.exit()
    if not conf.checkConfig():
        print("Invaild config.ini. Please configure it properly")
        print("Delete config.ini to generate a default one.")
        sys.exit()

    glob.ROOT_BEATMAP = conf.config['root']['beatmaps']
    glob.ROOT_UNZIP = conf.config['root']['unzip']
    glob.ROOT_REBUILD = conf.config['root']['rebuild']

    if any(i == "CHANGE_HERE" for i in [glob.ROOT_BEATMAP, glob.ROOT_UNZIP, glob.ROOT_REBUILD]):
        print("Config load Failed.")
        sys.exit()