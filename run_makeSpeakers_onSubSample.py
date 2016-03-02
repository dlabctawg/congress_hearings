#!/usr/bin/python
import os, json, re
from makeSpeakers import parse_file

files = os.listdir("./sub_sample/")
outdir = "./sub_sample_processed/"
for filename in files[1:len(files)+1]:
    metadata = re.split("_",re.sub("\.\.txt","",filename))
    print metadata
    speakers, chains, junk = parse_file("./sub_sample/"+filename)
    outfile = outdir+filename
    outfile = re.sub("\.\.txt","\.csv",outfile)
    f = open(outfile,"w")
    f.writelines(",".join(["surname","speaker","previous_surname","previous_speaker", "speech"])+"\n")
    for chain in chains:
        f.writelines(",".join(["break","break","break","break", "break"])+"\n")
        for speech in chain:
            data = [
                json.dumps(speech["surname"]),
                json.dumps(speech["speaker"]),
                json.dumps(speech["previous_surname"]),
                json.dumps(speech["previous_speaker"]),
                json.dumps(speech["speech"])
            ]
            f.writelines(",".join(data)+"\n")
    f.close()
    
