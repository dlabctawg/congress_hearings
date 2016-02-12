# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 13:23:47 2015

@author: Jeff
"""
import os
import urllib
from selenium import webdriver

os.chdir("C:\Users\Jeff\Documents\hearings\demo")

#to prevent download dialog
profile = webdriver.FirefoxProfile()
profile.set_preference('browser.download.folderList', 2) # custom location
profile.set_preference('browser.download.manager.showWhenStarting', False)
profile.set_preference('browser.download.dir', os.getcwd())
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

#open browser driver
browser = webdriver.Firefox(profile)
browser.implicitly_wait(10)
browser.get("http://www.gpo.gov/fdsys/browse/collection.action?collectionCode=CHRG")

#find the elements by congress
congressElements = browser.find_elements_by_xpath(".//div[@class='level1 browse-level']/a")

#loop through congresses
counter = 0
for counter in range(counter, len(congressElements)):
    
    #re-establish the element locations    
    congressElements = browser.find_elements_by_xpath(".//div[@class='level1 browse-level']/a")    
    
    #save the name of the congress   
    congress_name = congressElements[counter].text    
    
    #click on the chosen congress
    congressElements[counter].click()

    #record chamber element locations   
    chamberElements = browser.find_elements_by_xpath(".//div[@class='level2 browse-level']/a")
    
    #loop through chambers
    chamber_counter = 0
    for chamber_counter in range(chamber_counter, len(chamberElements)):
        
        #re-establish the chamber element locations        
        chamberElements = browser.find_elements_by_xpath(".//div[@class='level2 browse-level']/a")
        
        #save the name of the chamber        
        chamber_name = chamberElements[chamber_counter].text        
        
        #click the chosen chamber        
        chamberElements[chamber_counter].click()
        
        #record committee element locations        
        committeeElements = browser.find_elements_by_partial_link_text("Committee")
        
        #it is picking up an erroneous committee name from a sidebar
        committeeElements.pop(0)
        
        #loop through committees
        committee_counter = 0
        for committee_counter in range(committee_counter, len(committeeElements)):
            committeeElements = browser.find_elements_by_partial_link_text("Committee")
            committeeElements.pop(0)
            committee_name = committeeElements[committee_counter].text
            committeeElements[committee_counter].click()
            #record hearing element locations
            hearingElements = browser.find_elements_by_xpath(".//tr[td[span[@class='results-line2']]]")
            
            #loop through hearings
            hearing_counter = 0
            for hearing_counter in range(hearing_counter, len(hearingElements)):
                
                #re-establish hearing element locations                
                hearingElements = browser.find_elements_by_xpath(".//tr[td[span[@class='results-line2']]]")
                
                #navigate to the line with the hearing elements                
                hearing_line =  hearingElements[hearing_counter]               
                
                #save the hearing date                
                hearing_date = hearing_line.find_element_by_xpath(".//span[@class='results-line2']").text
                
                #find the "Text" part of the element and extract the link                
                hearing_text_link = hearing_line.find_element_by_partial_link_text("Text").get_attribute('href')
                
                #download the text file 
                file_name_elements = [congress_name, chamber_name, committee_name, hearing_date]
                file_name = "_".join(file_name_elements)
                file_name += ".txt"
                urllib.urlretrieve(hearing_text_link, file_name)
            
            browser.back()
       
        browser.back()
    
    browser.back()
    #for chamber in chamberElements:
        
    