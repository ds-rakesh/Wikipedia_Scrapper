#importing all necessary library
import json
from wikiscrapping import wikipedia_scrapper
from summarizing import summarizzing
from flask import Flask
from flask import Flask, render_template, request, jsonify, Response, url_for, redirect
from flask_cors import CORS, cross_origin
from mongoDBOperations import MongoDBManagement
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from urllib.request import urlopen 
import base64
from logger_class import getLog

db_name= "wikidb"       # Name of the DataBase

logger = getLog('app.py')

app = Flask(__name__)  #an instance of flask

#For selenium driver implementation on heroku
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("disable-dev-shm-usage")

@app.route('/', methods=['GET', 'POST']) # To render Homepage
@cross_origin()
def home_page():
    return render_template('index.html')

@app.route('/scrap',methods = ["POST"])
def index():

    if(request.method == "POST"):
        
        searchString = request.form['content'].lower()  # obtaining the search string entered in the form    
        searchString_html = searchString.upper()        # used for heading in the result.html
        try:
            mongo_object = MongoDBManagement(username="rakesh", password="rk123")  #instance of the MongoDBManagement Class
            mongo_object.createDatabase(db_name)  #creating the DB                  

            #******************* To check if Collection is present or not *******************************
            if(mongo_object.isCollectionPresent(collection_name=searchString, db_name=db_name) == True):
                logger.info("Database Already Present") 
                response = mongo_object.findAllRecords(db_name=db_name, collection_name=searchString)
                reviews = [i for i in response]
                if len(reviews) > 0:       # If present then check if is empty or not
                    for i in reviews:
                        Summary = (i["Summary"])  # show the Summary to user if collection has data
                        Ref_link = (i["Ref_link"])  # show the Ref_link to user if collection has data
                        Image_link = (i["Image_link"])  # show the Image_link to user if collection has data
                    return render_template('results.html',heading = searchString_html,Summary=Summary,Ref_link = Ref_link,Image_link =Image_link )  

                #******************* if Collection is present and it is empty *******************************
                else:
                    summarized_text = "" 
                    paragraph_nobrac = []
                    imgtob64_converted = []

                    find = wikipedia_scrapper("https://www.wikipedia.org/")
                    logger.info("Url hitted")

                    logger.info(f"Search begins for {searchString}")
                    lst = find.search(searchString) 
                    logger.info("Searching completed")  
                    
                    for text in lst:
                        text_nobrac = find.bracketremoval(text)         #Scrapping the paragraphs from the wiki
                        paragraph_nobrac.append(text_nobrac)
                                       
                    summarized_paragraph2 = summarizzing()      #instance of the summarizzing class
                    
                    #print("************************** >>>> Inner Else BLOCK <<<< ************************************")
                   
                    for text in paragraph_nobrac:
                        text = text.replace('"','')  # Removing "" from the text
                        summarized_text = summarized_text + summarized_paragraph2.summarizer(text)  #Summarizing the paragraphs
                    logger.info("Summarization Done") 

                    ref_links = find.ref()              #scrapping the Ref Links
                    logger.info("Ref_links Fetched")

                    image_links = find.image()          #scrapping the Image Links
                    logger.info("Image_links Fetched")

                    for url in image_links:             #Converting the images to base64 format
                        mybs64 = base64.b64encode(urlopen(url).read())
                        imgtob64_converted.append(mybs64)
                    logger.info("imgtob64 Done")

                    result = {"Summary" : summarized_text,
                              "Ref_link" : ref_links,
                              "Image_link" : image_links,
                              "Imgtob64" : imgtob64_converted}  #Converting to dict
                                

                    mongo_object.insertRecord(db_name=db_name, collection_name=searchString, record = result) # Insert the dict to DB
                    logger.info("Data saved in MongoDB")
                    
                    return render_template('results.html',heading = searchString_html,Summary=result["Summary"],Ref_link = result["Ref_link"],Image_link =result["Image_link"])

            #******************* If Collection is not present *******************************
            else:
    
                mongo_object.createCollection(collection_name=searchString, db_name=db_name) #Creating a collection
                
                paragraph_nobrac = []    
                summarized_text = ""
                imgtob64_converted = []

                find = wikipedia_scrapper("https://www.wikipedia.org/")
                logger.info("Url hitted")

                logger.info(f"Search begins for {searchString}")
                lst = find.search(searchString) 
                logger.info("Searching completed") 
                
                for text in lst:
                        text_nobrac = find.bracketremoval(text)         #Scrapping
                        paragraph_nobrac.append(text_nobrac)
                
                summarized_paragraph2 = summarizzing()

                #print("************************** >>>> Outer Else BLOCK <<<< ************************************")
                for text in paragraph_nobrac:
                    text = text.replace('"','')     # Removing "" from the text
                    summarized_text = summarized_text +"\n\n\t"+ summarized_paragraph2.summarizer(text)
                
                logger.info("Summarization Done") 
                
                
                ref_links = find.ref()              #scrapping the Ref Links
                logger.info("Ref_links Fetched")

                
                image_links = find.image()          #scrapping the Image Links
                logger.info("Image_links Fetched")

                for url in image_links:                 #Converting the images to base64 format
                        mybs64 = base64.b64encode(urlopen(url).read())
                        imgtob64_converted.append(mybs64)
                logger.info("imgtob64 Done")
           
                
                result = {"Summary" : summarized_text,
                              "Ref_link" : ref_links,
                              "Image_link" : image_links,
                              "Imgtob64" : imgtob64_converted}  #Converting to dict

                                       
                mongo_object.insertRecord(db_name=db_name, collection_name=searchString, record = result)
                logger.info("Data saved in MongoDB")
      
                return render_template('results.html',heading = searchString_html,Summary=result["Summary"],Ref_link = result["Ref_link"],Image_link =result["Image_link"])
                
        except Exception as e:
            raise Exception("(app.py) - Something went wrong while rendering all the details of product.\n" + str(e))
        
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run()