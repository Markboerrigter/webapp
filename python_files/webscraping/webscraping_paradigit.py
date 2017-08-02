
#a common package to work with data in Python
import pandas as pd
#used to do stuff with regex (for recognizing the product id)
import re
#used to read data from sql database
import sqlite3 as lite
from sqlalchemy import create_engine
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
    hits=[re.sub('[\n\r\t]','',i.get_text().strip(' ')) for i in group_name]
    return hits

def scrape(links):
    for i in range(len(links)):
        response=requests.get(links.urls.loc[i])
        soup=bs4.BeautifulSoup(response.text,"lxml")
        script_text=clean_hit(soup.find_all('script',{"type":"text/javascript"}))
        #print(script_text)
        if 'product' in links.urls.loc[i]:
            if script_text and not links.brand.loc[i]:
                pattern = re.compile('brand: "(.*?)"')
                brand = [re.findall(pattern, s) for s in script_text]
                brand=[item for sublist in brand for item in sublist]
                if len(set(brand))==1:
                    links.brand.loc[i]=brand[0]
            if script_text and not links.title.loc[i]:
                pattern = re.compile('name: "(.*?)"')
                title = [re.findall(pattern, s) for s in script_text]
                title=[item for sublist in title for item in sublist]
                if len(set(title))==1:
                    links.title.loc[i]=title[0]
            if script_text and not links.category.loc[i]:
                pattern = re.compile('category: "(.*?)"')
                cat = [re.findall(pattern, s) for s in script_text]
                cat=[item for sublist in cat for item in sublist]
                if len(set(cat))==1:
                    all_categories=['category','category2','category3','category4','category5','category6']
                    category_split=cat[0].split('/')
                    links.loc[i,all_categories]=category_split+[None]*(len(all_categories)-len(category_split))
            if not links.price.loc[i]:
                price=soup.find("span", {"itemprop":"price"})['content']
                price=re.sub("[^0-9.,-]","",price)
                if price:
                    price=price.replace('-','00').replace(',','.')
                    links.price.loc[i]=price
            if links.price.loc[i] and not links.discount.loc[i]:
                price_old=soup.find("div",{"class":"productdetail_product_advice"})
                if price_old:
                    price_old=re.sub("[^0-9.,-]","",price_old.text)
                    if price_old:
                        price_old=price_old.replace('-','00').replace(',','.')
                        links.discount.loc[i]=str(int(round((1-float(links.price.loc[i])/float(price_old))*100)))+'%'
        else:
            if not links.title.loc[i]:
                title=clean_hit(soup.find_all("h1", {"id":"productlist-title"}))
                if not title:
                    title=soup.find("title").text
                    title=[title[:title.find('|')]]
                if title:
                    links.title.loc[i]=', '.join(title)
            if not links.brand.loc[i] :
                brand=[s["content"] for s in soup.find_all("span",{"itemprop":"manufacturer"})]
                if not brand and script_text:
                    pattern = re.compile('brand: "(.*?)"')
                    brand = [re.findall(pattern, s) for s in script_text]
                    print("one",brand)
                    brand=[item for sublist in brand for item in sublist]
                    print("two",brand)
                if brand:
                    links.brand.loc[i]=', '.join(set(brand))
            if not links.category.loc[i] and script_text:
                pattern = re.compile('list: "categorie -(.*?)"')
                cat = [re.findall(pattern, s) for s in script_text]
                cat=[item for sublist in cat for item in sublist]
                if len(set(cat))==1:
                    all_categories=['category','category2','category3','category4','category5','category6']
                    category_split=cat[0].split('/')
                    links.loc[i,all_categories]=category_split+[None]*(len(all_categories)-len(category_split))
            if not links.price.loc[i]:
                prices=clean_hit(soup.find_all("div",{"class":"productlist-huidigeprijs"}))
                if prices:
                    prices=[re.sub("[^0-9.,-]","",p) for p in set(prices)]
                    if len(prices)==1:
                        links.price.loc[i]=prices[0].replace('-','00').replace(',','.')
            if links.price.loc[i] and not links.discount.loc[i]:
                prices_old=clean_hit(soup.find_all("div",{"class":"productlist-oudeprijs"}))
                if prices_old:
                    prices_old=[re.sub("[^0-9.,-]","",p) for p in set(prices_old)]
                    if len(prices_old)==1:
                        price_old=prices_old[0].replace('-','00').replace(',','.')
                        links.discount.loc[i]=str(int(round((1-float(links.price.loc[i])/float(price_old))*100)))+'%'
    return links
