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
    hits=[re.sub('[\n\r\t]','',i.getText(separator=' ')).strip() for i in group_name]
    return hits

def scrape(links):
    cat_names=['category','category2','category3','category4','category5','category6']
    for i in range(len(links)):
        links.brand.loc[i]=None
        response=requests.get(links.urls.loc[i])
        soup=bs4.BeautifulSoup(response.text,"lxml")
        #get tags if product not found in xml
        if not links.title.loc[i]:
            if soup.find_all("ol",{"class":"breadcrumb"}):
                cat=clean_hit(soup.find_all("ol",{"class":"breadcrumb"}))[0].split("  ")
                links.loc[i,cat_names]=cat[:-1]+[None]*(len(cat_names)-len(cat[:-1]))
                links.title.loc[i]=cat[-1]
        if not links.brand.loc[i]:
            links.brand.loc[i]=soup.find("meta",{"itemprop":"brand"})['content']
        if not links.price.loc[i]:
            prod=soup.find("div",{"class":"product__offer"})
            price=clean_hit(prod.find_all("span",{"itemprop":"price"}))
            price=re.sub('[^0-9.,-]','',price[0])
            price=price.replace('-','00').replace(',','.')
            links.price.loc[i]=price

        #find old price and calculate discount. Always by scraping, not in xml
        if links.price.loc[i]:
            prod=soup.find("div",{"class":"product__offer"})
            price_old=clean_hit(prod.find_all("span",{"class":"price price-old"}))
            if price_old:
                price_old=re.sub('[^0-9.,-]','',price_old[0])
                price_old=price_old.replace('-','00').replace(',','.')
                if '.' in price_old[:-3]:
                    price_old=price_old.replace('.','',1)
                links.discount.loc[i]=str(int(round((1-float(links.price.loc[i])/float(price_old))*100)))+'%'
    print('Webscraping finished')
    return links
