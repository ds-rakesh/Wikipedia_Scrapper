from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException


class wikipedia_scrapper():
    def __init__(self,url):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.url = url
        self.driver.maximize_window() # For maximizing window

    def bracketremoval(self,text):   # To remove the [],() from the scrapped text
        self.text = text
        
        ret = ''
        skip1c = 0
        skip2c = 0
        for i in self.text:
            if i == '[':
                skip1c += 1
            elif i == '(':
                skip2c += 1
            elif i == ']' and skip1c > 0:
                skip1c -= 1
            elif i == ')'and skip2c > 0:
                skip2c -= 1
            elif skip1c == 0 and skip2c == 0:
                ret += i
        return(ret)


    def search(self,searchString):   #To search and Scrap the data for the given topic
        self.searchString = searchString
        self.driver.get(self.url)
        self.driver.maximize_window()
        self.driver.implicitly_wait(20) # gives an implicit wait for 20 seconds

        search_box = self.driver.find_element_by_xpath("//input[@name='search']")  #To target the search box
        search_box.send_keys(self.searchString)     #To enter search string in the search box
        

        search_results = self.driver.find_elements_by_xpath("//p[@class='suggestion-description']") #To target the suggestion list
        

        for result in search_results: #To target the relevant suggestion from the suggestion list
            if result.text != "Topics referred to by the same term": 
                result.click()
                break       #when the relevant suggestion is found break from loop

        total_ptag = (len(self.driver.find_elements_by_xpath(f"//div[@class='mw-parser-output']/p")))  #To find all the paragraphs on the page

        lst = [] 
        for i in range(1,total_ptag+1):     #To find all the texts from each paragraphs on the page
            try:
                paragraph = self.driver.find_element_by_xpath(f"//div[@class='mw-parser-output']/p[{i}]").text 
                if(len(paragraph) != 0):
                    lst.append(paragraph)

            except NoSuchElementException as e:
                raise Exception("(wikiscrapping.py) - Something went wrong while rendering all the details of product.\n" + str(e))
        return lst    

    def ref(self):     #To find all the ref. links on the page
        link_lst = []
        find_href = self.driver.find_elements_by_xpath("//span[@class='reference-text']/cite/a")
        for my_href in find_href:
            link_lst.append(my_href.get_attribute("href"))
        return link_lst
    
    def image(self):    #To find all the IMAGE links on the page
        image_lst = []
        find_image = self.driver.find_elements_by_xpath("//a[@class='image']/img")
        #find_image = self.driver.find_elements_by_xpath('//a[@class="image"]')
        for my_image in find_image:
            image_lst.append(my_image.get_attribute("src"))
            #image_lst.append(my_image.get_attribute("href"))
        return image_lst



