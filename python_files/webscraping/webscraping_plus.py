#a common package to work with data in Python
import pandas as pd
#used to do stuff with regex (for recognizing the product id)
import re

import requests
import bs4

def clean_hit(group_name):
    """
    Get as input a soup list and return a list with clean prices
    group_name: soup list
    hits: list with found prices
    """
    hits=[re.sub('[^0-9a-zA-Z %,.-]','',i.get_text()) for i in group_name]
    return hits

def discount(d):
    price=False
    if re.match(r'\d{3}',d[-3:]):
        d=d[:-2]+'.'+d[-2:]
    weight=[[match.start(),match.end()] for match in re.finditer('gram',d.lower())]
    if weight:
        d=d[match.end():]
    if re.match(r'(\d+?).\d{2}',d):
        price=True
    return d,price


def scrape(links):
    for i in range(len(links)):
        response=requests.get(links.urls.loc[i])
        soup=bs4.BeautifulSoup(response.text,"html.parser")
        items=soup.findAll("div", { "class" : "description" })
        sort=soup.findAll("div", { "class" : "variant" })
        disc=soup.findAll("div", {"class": "shape-clover-red clover-size-s"})
        info=soup.findAll("div",{"class":"ish-productTileKlik"})
        brands=[k["data-brand"] for k in info]
        categories=[k["data-category"] for k in info]
        if items:
            links.title.loc[i]=', '.join(clean_hit(items))
        if sort:
            links.title.loc[i]=links.title.loc[i]+', '.join(clean_hit(sort))
        if brands:
            links.brand.loc[i]=', '.join(set(brands))
        if categories:
            links.category.loc[i]=', '.join(set(categories))
        disc,price=discount(' '.join(set(clean_hit(disc))))

        if price:
            links.price.loc[i]=disc
            if soup.findAll("div",{"class":"highest-price"}):
                o=clean_hit(soup.findAll("div",{"class":"highest-price"}))[0]
            elif soup.findAll("div",{"class":"lowest-price"}):
                o=clean_hit(soup.findAll("div",{"class":"lowest-price"}))[0]
            old_price=o[:-2]+'.'+o[-2:]
            links.discount.loc[i]=str(int((1-float(disc)/float(old_price))*100))+'%'
        else:
            links.persuasion.loc[i]=disc
    return links
