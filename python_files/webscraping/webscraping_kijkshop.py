#import the needed packages
#a common package to work with data in Python
import pandas as pd
#used to do stuff with regex (for recognizing the product id)
import re
#used to parse websites
import requests
import bs4



def clean_hit(group_name):
    """
    Get as input a soup list and return a list with clean prices
    group_name: soup list
    hits: list with found prices
    """
    #vraag me af of die sub wel nodig is of dat get_text genoeg is, moet ik testen
    #hits=[re.sub('[^0-9a-zA-Z %&+,.-]','',i.get_text()) for i in group_name]
    hits=[re.sub('[\n\r\t]','',i.get_text()).strip() for i in group_name]
    return hits


def scrape(links):
    for i in range(len(links)):
        response=requests.get(links.urls.loc[i])
        soup=bs4.BeautifulSoup(response.text,"lxml")
        nav=soup.find("div",{"class":"navbar-inner"})
        if not links.brand.loc[i] and nav:
            head_brand=nav.find('h2',text=re.compile('Merk')).parent
            if head_brand:
                brand=clean_hit(head_brand.find_all("li",{"class":" actief tw-checkbox"}))
                links.loc[i,'brand']=', '.join(brand)
        if not links.category.loc[i] and nav:
            head_cat=nav.find("h2",text=re.compile("Categorie(.+)")).parent
            if head_cat:
                cat=clean_hit(head_cat.find_all("li",{"class":" actief"}))
                cat=[re.sub('[^a-zA-Z]','',c) for c in cat]
                links.category.loc[i]=', '.join(cat)
        #if the column has a price tag

        if links.price.loc[i] and not links.discount.loc[i]:
            #find all classes that have the value that indicates the old price
            price_old=soup.find_all(class_="vanprijs")
            price_old=clean_hit(price_old)
            print(price_old)
            if price_old and len(set(price_old))==1:
                price_old=price_old[0].replace('-','00').replace(',','.')
                #calculate the discount percentage by comparing the old and new price
                links.discount.loc[i]=str(int((1-float(links.price.loc[i])/float(price_old))*100))+'%'
    return links
