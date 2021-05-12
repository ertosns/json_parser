import numpy as np
import pandas as pd
import matplotlib as plt
import seaborn as sb
import xml.etree.ElementTree as ET
import xmltodict
import json
import os
import sys
from argparse import ArgumentParser

XML = 1
CSV = 2
JSON = 3
UNDEF = None
FMTS = {1: 'xml', 2: 'csv', 3: 'json'}


def type_autodetect(file):
    '''
    def try_xml():
        pass
    def try_csv():
        pass
    def try_json():
        pass
    # try possible types
    if try_xml():
        return XML
    elif try_csv():
        return CSV
    elif try_json():
        return JSON
    else:
        return UNDEF
    '''
    pass

class BaseFile(object):
    def __init__(self, file, format=None):
        self.file = file
        # verify that file exists
        if self.file==None:
            raise Exception("file can't be none")
        elif not self.__exists__():
            raise Exception("file doesn't exist, make sure your provide full path to the file\n")
        # determine file format
        fmt = self.file.split('.')[-1]
        if fmt==FMTS[XML]:
            self.format = XML
        elif fmt==FMTS[CSV]:
            self.format = CSV
        elif fmt==FMTS[JSON]:
            self.format = JSON
        else:
            self.format = type_autodetect(self.file)
            #self.format = UNDEF
        # set local variables
        print('fmt: {}, file: {}, filename: {}'.format(self.format, self.file, os.path.split(self.file)[-1]))
        self.file_name = os.path.join(FMTS[self.format], os.path.split(self.file)[-1])
        self.json = {}
        self.df=None
    def __exists__(self):
        if  not os.path.exists(self.file):
            self.file = os.path.join(os.path.abspath(__file__), self.file)
            if  not os.path.exists(self.file):
                return False
        return True

    def open(self):
        if not self.__exists__():
            raise Exception("the file {} no longer exists!".format(self.file))
        self.buff=open(self.file, 'r').read()
    def to_json(self):
        '''
        virtual function implemented in the adapter.
        '''
        pass
    def view(self):
        print(self.df.head())
    def save(self):
        with open('out.json', 'w') as outfile:
            json.dump(self.json, outfile)
        #save file to the output dir.

class XMLFileAdapter(BaseFile):
    def __init__(self, file):
        super().__init__(file, XML)
        # verify try to open XML file
    def to_json(self):
        super().open()
        self.json = xmltodict.parse(self.buff)

        self.json = json.loads(json.dumps(self.json))
        self.json['file_name'] = self.file_name
        self.df = pd.DataFrame([self.json])
        #self.df = pd.DataFrame.from_dict(self.json)
        self.df = pd.json_normalize(self.json['Transaction'])

class CSVFileAdapter(BaseFile):
    def __init__(self, file):
        super().__init__(file, CSV)
    def to_json(self):
        self.df = pd.read_csv(self.file)
        self.json = self.df.json
        self.json['file_name'] = self.file_name


parser = ArgumentParser()
parser.add_argument('-fmt', '--format', type=str, default=None)
parser.add_argument('-f', '--file', type=str, default=None)
args = parser.parse_args()
print('args: {}, of type {}'.format(args, type(args)))
force_format = args.format
file_name = args.file

if force_format == FMTS[XML]:
            reader=XMLFileAdapter(file_name)
elif force_format == FMTS[CSV]:
            reader = CSVFileAdapter(file_name)
reader.to_json()
reader.view()
reader.save()
