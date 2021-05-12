import os
import sys
import json
from argparse import ArgumentParser
import pandas as pd
import xmltodict

XML = 1
CSV = 2
JSON = 3
UNDEF = None
FMTS = {1: 'xml',
        2: 'csv',
        3: 'json'}

def type_autodetect(file):
    '''
    TODO auto detect the file type
    '''
    return None

class BaseFile(object):
    def __init__(self, file, format=None):
        #note that file can be either path or list of path
        self.file = file
        if type(self.file)==str:
            # verify that file exists
            if self.file==None:
                raise Exception("file can't be none")
            elif not self.__exists__():
                raise Exception("file doesn't exist, make sure your provide full path to the file\n")
            # determine file format
            if not format==None:
                self.format = format
            else:
                fmt = self.file.split('.')[-1]
                if fmt==FMTS[XML]:
                    self.format = XML
                elif fmt==FMTS[CSV]:
                    self.format = CSV
                elif fmt==FMTS[JSON]:
                    self.format = JSON
                else:
                    self.format = type_autodetect(self.file)
            self.file_name = os.path.join(FMTS[self.format], os.path.split(self.file)[-1])
        elif type(self.file)==list:
            # verify that file exists
            if self.file==None:
                raise Exception("file can't be none")
            elif not len(self.file)==2:
                raise Exception("you need to provide exactly two files customers, and vehicle files on the command line instead {} are give".format(len(self.file)))
            elif not self.__all_exists__():
                raise Exception("file doesn't exist, make sure your provide full path to the file\n")
            self.format=format
            self.file_name = [os.path.join(FMTS[self.format], os.path.split(f)[-1]) for f in self.file]
        self.json = {}
        self.df=None
    def __exists__(self):
        if  not os.path.exists(self.file):
            self.file = os.path.join(os.path.abspath(__file__), self.file)
            if  not os.path.exists(self.file):
                return False
        return True
    def __all_exists__(self):
        for idx, f in enumerate(self.file):
            if  not os.path.exists(f):
                self.file[idx] = os.path.join(os.path.abspath(__file__), f)
                if  not os.path.exists(self.file[idx]):
                    return False
        return True
    def to_json(self):
        '''
        virtual function implemented in the adapter.
        '''
        pass
    def view(self):
        print(self.df.head())
    def save(self):
        with open('./data/parsing_result/sample.json', 'w') as outfile:
            json.dump(self.json, outfile)
        #save file to the output dir.

class XMLFileAdapter(BaseFile):
    def __init__(self, file):
        super().__init__(file, XML)
        # verify try to open XML file
    def to_json(self):
        # open file
        if not super().__exists__():
            raise Exception("the file {} no longer exists!".format(self.file))
        self.buff=open(self.file, 'r').read()
        #
        self.json = xmltodict.parse(self.buff)

        self.json = json.loads(json.dumps(self.json))
        self.json['file_name'] = self.file_name
        self.df = pd.DataFrame([self.json])
        #self.df = pd.DataFrame.from_dict(self.json)
        self.df = pd.json_normalize(self.json['Transaction'])

class CSVFileAdapter(BaseFile):
    def __init__(self, files):
        '''
        the csv file is divided into halves
        '''
        super().__init__(files, CSV)
        self.l = self.file[0]
        self.r = self.file[1]
        self.l_df = pd.read_csv(self.l)
        self.r_df = pd.read_csv(self.r)
        if 'owner_id' in self.r_df.columns:
            self.df=pd.merge(self.l_df, self.r_df, how='outer', left_on=['id'], right_on=['owner_id'])
        else:
            self.df=pd.merge(self.l_df, self.r_df, how='outer', right_on=['id'], left_on=['owner_id'])
        self.tbls=[]
    def to_json(self):
        for index, row in self.df.iterrows():
            # create tbl dict
            tbl = {}
            tbl['transaction'] = {}
            # date
            tbl['transaction']['date'] = row['date']
            # customer
            tbl['transaction']['customer'] = {}
            tbl['transaction']['customer']['id'] = row['id_x']
            tbl['transaction']['customer']['name'] = row['name']
            tbl['transaction']['customer']['address'] = row['address']
            tbl['transaction']['customer']['phone'] = row['phone']
            # vehicles
            if tbl['transaction'].get('vehicle')==None:
                tbl['transaction']['vehicle'] = []
            veh = {}
            veh['id'] = row['id_y']
            veh['make'] = row['make']
            veh['vin_number'] = row['vin_number']
            tbl['transaction']['vehicle'].append(veh)
            # add transaction
            # if the customer made any previous purchase, append the purcahse to the case customer
            appended=False
            for idx, prev_tbl in enumerate(self.tbls):
                if prev_tbl['transaction']['customer']['id'] == row['id_x']:
                    self.tbls[idx]['transaction']['vehicle'].append(veh)
                    appended=True
            if not appended:
                self.tbls.append(tbl)
        self.json = {}
        self.json['file_name'] = self.file_name
        self.json['transactions'] = self.tbls
        #self.json=json.loads(json.dumps(self.tbls))



parser = ArgumentParser()
parser.add_argument('-fmt', '--format', type=str, default=None)
parser.add_argument('file', type=str, nargs='+')
args = parser.parse_args()
force_format = args.format
file_name = args.file
print("format:{}, file: {}".format(force_format, file_name))
if file_name==None:
    file_name=sys.argv[-1]
if force_format == FMTS[XML]:
    reader=XMLFileAdapter(*file_name)
elif force_format == FMTS[CSV]:
    reader = CSVFileAdapter(file_name)
reader.to_json()
reader.view()
reader.save()
