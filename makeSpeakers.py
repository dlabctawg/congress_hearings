#!/usr/bin/python
import sys, re, json

## filename = sys.argv[1]

## we'll try and make this as 'stateless' as is possible,
## by which we mean that the result of one lines read
## effects subsequent lines reads as minimally as possible.
## in addition, this will be a 'streaming' implementation
## where we only take one pass at the document,
## and collect all data along the way
## (as  might be expected of a reader).

peoplematch = re.compile("(([A-Z \.\,\'\`]+),[ ]+(Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming)(?=[ ][ ]+|\n|,))+")

def parse_file(filename):

    speaker = ""
    surname = ""
    chains = []
    speeches = [{'surname': "", 'speech': "", 'speaker': "", 'previous_surname': "", "previous_speaker": ""}]
    speakers = {}
    junk = []
    inspeech = 0
    inbody = 0
    newspeaker = 0
    contentsTop = 0
    contentsBottom = 0
    contents = ""
    f = open(filename,"r")
    for line in f:
        newspeaker = 0

        ## Now that we know all participants, we can look for records beginning with the surnames,
        ## which will indicate the transitions from one speaker to the next
        if contentsBottom:
            ## speechstarts = re.findall("(?is)    ((?:Senator|Representative|Mr.|Ms.|Mrs.) (?:"+allsurnames+"))\. (.*?)$", line)
            speechstarts = re.findall("(?is)^    ((?:Senator|Representative|Congressman|Congresswoman|Commissioner|Ambassador|Secretary|Admiral|General|Commander|Chief|Colonel|Sergeant|Major|Captain|Governor|The Clerk|Mayor|Minister|Judge|Justice|Chair|Mr.|Ms.|Mrs.|Dr.|Chairman|Chairwoman|Speaker) (?:.*?))\. (.*?)$", line)
            if len(speechstarts):
                previous_surname = surname
                previous_speaker = speaker
                for speaker, speech in speechstarts:
                    nameparts = re.split(" ", speaker)
                    surname = nameparts[-1].lower()
                    if speeches[-1]['speech'] == "":
                        speeches[-1]['surname'] = surname
                        speeches[-1]['speech'] = "    "+speech+"\n"
                        speeches[-1]['speaker'] = speaker
                        speeches[-1]['previous_speaker'] = previous_speaker
                        speeches[-1]['previous_surname'] = previous_surname
                    else:
                        speeches.append({
                            'surname': surname,
                            'speech': "    "+speech+"\n",
                            'speaker': speaker,
                            'previous_surname': previous_surname,
                            "previous_speaker": previous_speaker
                        })
                    inspeech = 1
                    newspeaker = 1
            else:
                speechstarts = re.findall("(?is)^    ((?:The Chairman\.|The Chairwoman\.)) (.*?)$", line)
                if len(speechstarts):
                    previous_surname = surname
                    previous_speaker = speaker
                    for speaker, speech in speechstarts:
                        nameparts = re.split(" ", speaker)
                        surname = nameparts[-1].lower()
                        if speeches[-1]['speech'] == "":
                            speeches[-1]['surname'] = surname
                            speeches[-1]['speech'] = "    "+speech+"\n"
                            speeches[-1]['speaker'] = speaker
                            speeches[-1]['previous_speaker'] = previous_speaker
                            speeches[-1]['previous_surname'] = previous_surname
                        else:
                            speeches.append({
                                'surname': surname,
                                'speech': "    "+speech+"\n",
                                'speaker': speaker,
                                'previous_surname': previous_surname,
                                "previous_speaker": previous_speaker
                            })
                        inspeech = 1
                        newspeaker = 1
                else:
                    ## speechstarts  = re.findall("(?is)^\s*prepared Statement of (.*?(?:"+allsurnames+"))\s*$", line)
                    speechstarts  = re.findall("(?is)^\s*prepared Statement of (.*?(?:.+?))\s*$", line)
                    if len(speechstarts):
                        previous_surname = surname
                        previous_speaker = speaker
                        for speaker in speechstarts:
                            nameparts = re.split(" ", speaker)
                            surname = nameparts[-1].lower()
                            if speeches[-1]['speech'] == "":
                                speeches[-1]['surname'] = surname
                                speeches[-1]['speech'] = ""
                                speeches[-1]['speaker'] = speaker
                                speeches[-1]['previous_speaker'] = previous_speaker
                                speeches[-1]['previous_surname'] = previous_surname
                            else:
                                speeches.append({
                                    'surname': surname,
                                    'speech': "",
                                    'speaker': speaker,
                                    'previous_surname': previous_surname,
                                    "previous_speaker": previous_speaker
                                })
                            inspeech = 1
                            newspeaker = 1
                            
                    else:
                        dubCaps = re.findall("(?s)^    ((?:[A-Z][a-z]+) (?:[A-Za-z\'\-0-9]+){1,3})\. (.*?)$", line)
                        if len(dubCaps):
                            for speaker, speech in dubCaps:
                                print speaker+". \n\n"+speech+"\n\n\n"

        ## speech ends are defined when a new speeches start,
        ## when a total whitespace lines are observed,
        ## or when a single block (not applause or laughter) of bracketed text appears
        ## if newspeaker is active, then we have already processed this line and should just pass
        if not newspeaker:
            if inspeech:
                ## take total whitespace line as an indicator for a speech conclusion
                if re.search("^\s*\n$",line) or re.search("^\s*\[[^\[\]]*\]\s*$",line):
                    if not re.search("(?si)^\s*\[(?:applause\.|laughter\.)]*\]\s*$",line):
                        inspeech = 0
                    keepers = []
                    for ix in range(len(speeches)):
                        speeches[ix]['speech'] = re.sub("^\n+","",speeches[ix]['speech'])
                        speeches[ix]['speech'] = re.sub("\.[A-Z\.\,\s\n]+$",".",speeches[ix]['speech'])
                        speeches[ix]['speech'] = re.sub("\n+$","",speeches[ix]['speech'])

                        if not speeches[ix]['speech'] == "" and not speeches[ix]['speech'] == "\n" and not re.match("(?is)^\s+prepared statement",speeches[ix]['speech']) and not re.match("(?is)^\s+(?:prepared statement|summary statement of|introduction of|opening remarks of|impact of)",speeches[ix]['speech']):
                            keepers.append(speeches[ix])
                        else:
                            junk.append(speeches[ix]['speech'])
                    if len(keepers):
                        chains.append(keepers)                    
                    speeches = [{'surname': "", 'speech': "", 'speaker': "", 'previous_surname': "", "previous_speaker": ""}]

                if inspeech:
                    ## need indicators for an acceptable line
                    if re.search("(?si)^(?:\s*[^\[\]]*(?:\[(?:laughter\.|applause\.)\])?\s*$)",line):
                        speeches[-1]['speech'] = speeches[-1]['speech']+line
                    else:
                        junk.append(line)
            elif surname != "" and speaker != "" and re.search("(?si)^(?:\s*[^\[\]]*(?:\[(?:laughter\.|applause\.)\])?\s*$)",line):
                inspeech = 1
                if speeches[-1]['speech'] == "":
                    speeches[-1]['surname'] = ""
                    speeches[-1]['speech'] = line
                    speeches[-1]['speaker'] = ""
                    speeches[-1]['previous_surname'] = surname
                    speeches[-1]['previous_speaker'] = speaker
                else:
                    speeches.append({
                        'surname': "",
                        'speech': line,
                        'speaker': "",
                        'previous_surname': surname,
                        "previous_speaker": speaker
                    })
            else:
                junk.append(line)

        ## find members present, according to names preceded by states
        present = peoplematch.findall(line)

        if len(present):
            for members in present:
                member = members[1].strip()
                nameparts = re.split(" ", member)
                surname = nameparts[-1].lower()
                state = re.sub("\s+"+member+",\s+", "", members[0])
                speakers.setdefault(surname, [])
                speakers[surname].append([member,state])

        ## once we hit the "c o n t e n t s," we are in the body and can create our
        ## search for speaches with the names we have collected
        if re.search("(?i)c o n t e n t s", line):
            inbody = 1

        ## grab the table of contents and process here
        if contentsTop and re.match("^\s+\-+\s+$",line) and not contentsBottom:
            contentsBottom = 1
            ## process table of contents here
            contents = re.sub("[ ]+\n[ ]+"," ",contents)
            contents = re.sub("\n+","\n",contents)
            table = re.split("\n",contents)
            for entry in table:
                mentions = re.findall("(?is).*?statement of ([^,]+), (.*?[^\.])\.+\s+\d+$", entry)
                for speaker,affiliation in mentions:
                    nameparts = re.split(" ", speaker)
                    surname = nameparts[-1].lower()
                    speakers.setdefault(surname, [])
                    speakers[surname].append([member,affiliation])
            allsurnames = "|".join(speakers.keys())
            ## flush surname and speaker for later
            surname = ""
            speaker = ""

        if contentsTop and not contentsBottom:
            contents = contents + line
        if inbody and not contentsTop and re.match("^\s+\-+\s+$",line):
            contentsTop = 1

    f.close()
    ## process and store speeches one more time,
    ## just in case the last batch of speeches
    ## didn't make it to the output gate in the loop
    keepers = []
    for ix in range(len(speeches)):
        speeches[ix]['speech'] = re.sub("^\n+","",speeches[ix]['speech'])
        speeches[ix]['speech'] = re.sub("\.[A-Z\.\,\s\n]+$",".",speeches[ix]['speech'])
        speeches[ix]['speech'] = re.sub("\n+$","",speeches[ix]['speech'])

        if not speeches[ix]['speech'] == "" and not speeches[ix]['speech'] == "\n" and not re.match("(?is)^\s+prepared statement",speeches[ix]['speech']) and not re.match("(?is)^\s+(?:prepared statement|summary statement of|introduction of|opening remarks of|impact of)",speeches[ix]['speech']):
            keepers.append(speeches[ix])
        else:
            junk.append(speeches[ix]['speech'])
        if len(keepers):
            chains.append(keepers)
    
    ## pass the data back to the function call
    return speakers, chains, junk
