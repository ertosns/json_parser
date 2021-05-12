# json adapter

A specific json adapter parses xml, and csv into unified json

# XMLAdapter

- please note the adapter built using xmltodict library, note that ids are preceded with '@' sign, also that, and keys are case sensitive.
- you can execute it as:
```console
python3 parser.py -fmt xml path/to/file.xml
```


# CSVAdapter

- it accepts two files customers, and vehicles files, merge on customer id, then convert them to json
- it accepts files at any order
- you can execute it as:
```console
python3 parser.py -fmt csv path/to/first.csv /path/to/second.csv
```


# installation

- to install requirement run the following:
```console
pip install -r ./requirements.txt
```
