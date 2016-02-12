
# coding: utf-8

# Create the parse lines function

# In[102]:

def parse_lines(file_name):
    import os
    import re
    import sys
    import nltk.data
    import numpy as np
    import pandas as pd
    import math
    from scipy import stats
    import random
    
    data = open(file_name).read()
    
    #cut off metadata at top of the file
    
    #extract list of members present
    try:
        present = "".join(re.findall('(?s)(?<=[Pp]resent:)(.+?\.)',data))
        members = re.findall('([^, ]+)(?=,|\.| and)',present)
        members = list(set(members))
        to_remove = ["\band\b","\n","Representatives","Senator","(ex officio)"]
        for i in to_remove:
            members = [w.replace(i,"") for w in members]
        members = [w.lstrip() for w in members] 
    except IndexError:
        try:
            present = re.findall('(?s)(?<=C O N T E N T S)(.+)(?=Witnesses)',data)[0]
            members = re.findall('(?s)(?<=Statement of )(.+?)(?=\.)',present)
            to_remove = ["\band\b","\n","Representatives","Senator","(ex officio)"]
            for i in to_remove:
                members = [w.replace(i,"") for w in members]
            members = [w.lstrip() for w in members]
        except IndexError:
            pass
   
    if members:
        #cut off metadata at the top using the list of present members as the wedge. note: this will break if the file has transcripts of several hearings in it.
        match = None
        #find last match of the list of present members. this is often the last thing before the actual body of text begins.
        for match in re.finditer('(?s)(?<=[Pp]resent:)(.+?\.)', data):
            pass
        top_of_file = re.split(match.group(), data)[0]
        body = re.split(match.group(), data)[1]
    
        #cut off additional material at the bottom
        match = None
        for match in re.finditer('[Aa]djourn', body):
            pass
        bottom_of_file = re.split(match.group(), body)[1]
        body = re.split(match.group(), body)[0]
      
    else:
        #try to split on the last instance of the date before the body begins
        date_temp = re.split('_',file_name)[3]
        date = re.split('\.', date_temp)[1]
        date = date.upper()
        match = None
        for match in re.finditer(date,data):
            pass
        top_of_file = re.split(match.group(), data)[0]
        body = re.split(match.group(), data)[1]
        
       #split the bottom the same way as before
        match = None
        for match in re.finditer('[Aa]djourn', body):
            pass
        bottom_of_file = re.split(match.group(), body)[1]
        body = re.split(match.group(), body)[0]

#break text file into lines
    lines = re.split('\\n',body)
    df = pd.DataFrame({"line":lines})    
   
#assess whether each line begins with the beginning of a speech
    for index, row in df.iterrows():        
        if bool(re.match("^\s\s\s\s",row['line'])) is False:
            df.ix[index, "speech_start"] = 'False'
        elif re.match("^\s*STATEMENT OF ",row["line"]):
            df.ix[index, "speech_start"] = "False"
        elif re.match("^\s*Senator \S+\s?\S*\. |^\s*Mr?s?\. \S+\s?\S*\. |^\s*Dr\. \S+\s?\S*\. |^\s*Chairman \S+\s?\S*\. |^\s*(?:[A-Z][A-Za-z]+ ){1,2}[A-Z][A-Za-z]+\. |^\s*\[",row['line']):
             df.ix[index, "speech_start"] = 'True'
        else:
            df.ix[index, "speech_start"] = 'False'
   
   #a machine learning pipeline to perfect the above process would go here   
   
   #tag lines to the first line to which they belong
    current_index = 0    
    for index, row in df.iterrows():
        if row["speech_start"] == 'True':
            df.ix[index, "speech_index"] = index
            current_index = index
        if row["speech_start"] == 'False':
            df.ix[index, "speech_index"] = current_index
    
   #group by speech
    df_speech = df.groupby("speech_index")["line"].apply(lambda x: ' '.join(x))
    df_speech = df_speech.reset_index(drop=True)
    df_speech = pd.DataFrame({"speech":df_speech})
    
   #drop speeches that are definitely not speeches
    df_speech = df_speech[~df_speech.speech.str.contains("^\s*\[")]
    df_speech = df_speech.reset_index(drop=True)
   
#add metadata to each speech
   #look for the speaker's surname
    def strip_surname(text):
        text_begin = " ".join(text.split()[:4])
        poss_surnames = re.findall('[A-Z]\w*',text_begin)
        for i in poss_surnames:
             if i in members:
                 return i
        try:
            surname = poss_surnames[1]
            return surname
        except IndexError:
            pass
   
    thread = 0
    for index, row in df_speech.iterrows():
        df_speech.ix[index, "surname"] = strip_surname(row["speech"])
        #check if speaker is senator        
        df_speech.ix[index, "is_senator"] = df_speech.ix[index, "surname"] in members
        
        #assess sequence
        df_speech.ix[index,"thread"] = index
        try:
            prior_surname = df_speech.ix[index-1,"surname"]
        except KeyError:
            prior_surname = None
        if index>0 and isinstance(prior_surname, basestring) and prior_surname in row["speech"]:
            df_speech.ix[index, "responding"] = 'True'
            df_speech.ix[index, "thread"] = df_speech.ix[index-1,"thread"]
        else:
           df_speech.ix[index, "responding"] = 'False' 
   
   #get congress name
    df_speech['congress'] = file_name.split('_')[0]
   #get date        
    date_temp = re.split('Monday, |Tuesday, |Wednesday, |Thursday, |Friday, |Saturday, |Sunday, ',file_name)[1]    
    df_speech['date'] = date_temp.split('.')[0]
   #get committee    
    df_speech["committee"] = file_name.split('_')[2]
   #get hearing name     
    df_speech["hearing_name"] = re.findall('(?<=\<title\>).*(?=\<\/title\>)',data)[0]
    df_speech["file_name"] = file_name   
   
    return df_speech
    


# Practice using it

# In[103]:

import os
os.chdir("C:\Users\Jeff\Documents\hearings\docs")
#choose a file
file_name = "111th Congress (2009 - 2010)_Senate Hearings_Committee on Commerce, Science, and Transportation_General. Wednesday, May 13, 2009..txt"
d = parse_lines(file_name)
d

