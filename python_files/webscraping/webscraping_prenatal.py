#a common package to work with data in Python
import pandas as pd
#used to do stuff with regex (for recognizing the product id)
import re
import csv
import json
import requests
import ast
import bs4
from slimit.parser import Parser
from tagging_from_xml_Mark import tags_from_xml

def clean_hit(group_name):
    """
    Get as input a soup list and return a list with clean prices
    group_name: soup list
    hits: list with found prices
    """
    #vraag me af of die sub wel nodig is of dat get_text genoeg is, moet ik testen
    #hits=[re.sub('[^0-9a-zA-Z %&+,.-]','',i.get_text()) for i in group_name]
    hits=[i.get_text().strip(' ') for i in group_name]
    return hits


def remove_counts(item):
    item=[re.sub(r'\d+$', '', i) for i in item]
    return item


def scrape(links):
    name_categories=['category','category2','category3','category4','category5','category6']
    for i in range(len(links)):
        pro = False
        if links.urls.loc[i]=="-":
            continue
        response=requests.get(links.urls.loc[i])
        soup=bs4.BeautifulSoup(response.text,"lxml")
        scripts=soup.findAll("script")
        for script in scripts:
            if script.text.startswith('var product = {\nid'):
                pro = True
                form = script.contents[0].split('\n')
                title = form[2][5:-2]
                price = form[5][8:-2]
                price_old = form[6][9:-2]
                brand = form[4][8:-2]
                category = form[3][11:-1]
                if title:
                    links.title.loc[i]=((title))
                if price:
                    if price != '0.00':
                        links.price.loc[i]=(price)
                    else:
                        links.price.loc[i]=(price_old)
                if brand:
                    links.brand.loc[i]=brand

                discount = str(int((1-float(price)/float(price_old))*100))+'%'
                if discount and discount !='100%':
                    links.discount.loc[i]=discount
                try:
                    category = ast.literal_eval(category)
                    subcategory=category[1:]
                    category=category[0]
                    if category:
                        links.category.loc[i]=category
                    if subcategory:
                        links.loc[i,name_categories[1:]]=subcategory+[None]*(len(name_categories[1:])-len(subcategory))
                except:
                    pass
        if not pro:
            products = soup.findAll("li", {"id": re.compile('product_')})
            for x in products:
                title = x.find_all('a', {"title":'Meer info'})
                price = x.find_all('', {"class":'web_price'})
                title = clean_hit(title)
                price = clean_hit(price)
                if title:
                    links.title.loc[i]=', '.join((title))
                    pro=True
                if price:
                    links.price.loc[i]=re.sub('[^0-9.,]','',', '.join(price))
    return links

    # links = 'http://www.prenatal.nl/shop/verzorging-Badcapes/Pr%C3%A9natal-Prenatal-badcape-sterren-117178.htm?startValue=24&rangeValue=6&prevVisit=true&id=117178&utm_medium=folder&utm_campaign=augustus-folder-2017&utm_source=overige'
    # scrape(links)
