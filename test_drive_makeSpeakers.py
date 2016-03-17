#!/usr/bin/python

from makeSpeakers import parse_file
import os

files = os.listdir("./sub_sample/")
for filename in files[1:len(files)+1]:

    speakers, chains, junk = parse_file("./sub_sample/"+filename)

## filename = "sample/105th Congress (1997 - 1998)_Senate Hearings_Committee on Energy and Natural Resources_General. Thursday, May 28, 1998..txt"
## filename = "testSpeakers.txt"
## speakers, chains, junk = parse_file(filename)

## print chains
