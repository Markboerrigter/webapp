#import the needed packages
#a common package to work with data in Python
import pandas as pd
#used to do stuff with regex (for recognizing the product id)
import re


import requests
import bs4
from pymongo import MongoClient

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


def remove_counts(item):
    item=[re.sub(r'\d+$', '', i) for i in item]
    return item

def scrape(links):
    client = MongoClient('ds119533.mlab.com', 19533)
    db = client['tagging']
    db.authenticate('hahamark','hahamark')
    collection = db['xml_dio']
    brands_list=collection.distinct('brand')
    for i in range(len(links)):
        response=requests.get(links.urls.loc[i])
        soup=bs4.BeautifulSoup(response.text,"html.parser")


        if not links.title.loc[i]:
            keywords=soup.find("meta", {"name":"keywords"})['content']
            if keywords!="":
                disc=soup.find_all("div", {"class":"label label-promotion"})
                promotions=[]
                for d in disc:
                    prom=d.find("span",{"class":"label-promotion-header"}).text+' '+d.find("span",{"class":"label-promotion-content"}).text
                    promotions.append(prom)
                pers=[]
                for p in set(promotions):
                    if re.search(re.escape(p),keywords):
                        pers.append(re.search(re.escape(p),keywords).group())
                if pers:
                    links.persuasion.loc[i]=', '.join(pers)
                for d in pers:
                    keywords=keywords.replace(d,"")
                links.title.loc[i]=keywords
            elif soup.find("div", {"class":"product-name"}):
                links.title.loc[i]=' '.join(clean_hit(soup.find_all("div", {"class":"product-name"})))

        if not links.brand.loc[i] and links.title.loc[i]:
            brand=remove_counts(clean_hit(soup.find_all("a" ,{"href":re.compile("https://www.diodrogist.nl/aanbiedingen/merk/(.+)")})))
            # if brand:
            #     links.brand.loc[i]=', '.join(brand)
            # elif links.title.loc[i]:# and [b for b in brands_list if b in links.title.loc[i]]:
            #     for b in brands_list:
            #         print(b)
            #         if b in links.title.loc[i]:
            #             print("woop")
                #print([b for b in brands_list if b in links.title.loc[i]])
            links.brand.loc[i]=', '.join([b for b in brands_list if b and b in links.title.loc[i]])

        if links.price.loc[i]==None:
            if soup.find("meta", {"itemprop":"price"}):
                price=soup.find("meta", {"itemprop":"price"})['content']
                links.price.loc[i]=re.sub('[^0-9\.,-]','',price)
            if soup.find_all("div", {"class":"price-box"}):
                all_prices=soup.find_all("div", {"class":"price-box"})
                reg=set()
                sale=set()
                old=set()
                for a in all_prices:
                    r=a.find("span",{"class":"regular-price"})
                    s=a.find("p",{"class":"special-price"})
                    o=a.find("p",{"class":"old-price"})
                    if r:
                        reg.add(re.sub('[^0-9,.-]','',r.text).replace('-','00').replace(',','.'))
                    if s:
                        sale.add(re.sub('[^0-9,.-]','',s.text).replace('-','00').replace(',','.'))
                    if o:
                        old.add(re.sub('[^0-9,.-]','',o.text).replace('-','00').replace(',','.'))
                if len(reg)==1 and len(sale)==0:
                    links.price.loc[i]=' '.join(reg)
                if len(reg)==1 and len(sale)==1 and reg[0]==sale[0]:
                    links.price.loc[i]=' '.join(reg)
                if len(reg)==0 and len(sale)==1:
                    links.price.loc[i]=' '.join(sale)
                    if len(old)==1:
                        o=list(old)[0].replace('-','00').replace(',','.')
                        p=list(sale)[0].replace('-','00').replace(',','.')
                        links.discount.loc[i]=str(int(round((1-float(p)/float(o))*100)))+'%'
        if links.price.loc[i] and not links.discount.loc[i]:
            prod=soup.find("div", {"class":"product-view row"})
            spec=prod.find("p",{"class":"special-price"})
            o=links.price.loc[i]
            if spec:
                p=re.sub('[^0-9,.-]','',spec.text).replace('-','00').replace(',','.')
                if float(p)<float(o):
                    links.price.loc[i]=p
                    links.discount.loc[i]=str(int(round((1-float(p)/float(o))*100)))+'%'
            elif prod.find("span",{"class":"label-promotion-header"}):
                prom=prod.find("span",{"class":"label-promotion-header"})
                p=prom.find("span",{"class":"price"})
                if p:
                    p=re.sub('[^0-9,.-]','',p.text).replace('-','00').replace(',','.')
                    if float(p)<float(o):
                        links.price.loc[i]=p
                        links.discount.loc[i]=str(int(round((1-float(p)/float(o))*100)))+'%'


        if links.category.loc[i]=='Aanbiedingen ':
            links.loc[i,['category','category2','category3','category4','category5','category6']]=None
    return links
