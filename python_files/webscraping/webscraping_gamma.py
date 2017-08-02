#import the needed packages
#a common package to work with data in Python
import pandas as pd
#used to do stuff with regex (for recognizing the product id)
import re

import requests
import bs4

import time

import ast


def clean_hit(group_name):
    """
    Get as input a soup list and return a list with clean prices
    group_name: soup list
    hits: list with found prices
    """
    #vraag me af of die sub wel nodig is of dat get_text genoeg is, moet ik testen
    #hits=[re.sub('[^0-9a-zA-Z %&+,.-]','',i.get_text()) for i in group_name]
    hits=[re.sub('\n','',i.get_text().strip(' ')) for i in group_name]
    return hits


def remove_counts(item):
    item=[re.sub(r'\d+$', '', i) for i in item]
    return item

def scrape(links):
    category_names=['category','category2','category3','category4','category5','category6']
    for i in range(10):
        response=requests.get(links.urls.loc[i])
        soup=bs4.BeautifulSoup(response.text,"lxml")

        product=soup.find("div", {"id":"product-data"})

        if product:
            script_text=soup.find_all('script',text = re.compile("(.+)var stqVarsObj(.+)"))[0].string
            var_text=[script_text[match.end():-45]+'}' for match in re.finditer('var stqVarsObj = ',script_text)]
            var_text=re.sub('\s+', '', var_text[0])
            var_dict=ast.literal_eval(var_text)
            title=var_dict['productName']
            category=var_dict['productCategory']
            brand=var_dict['productBrand']
            price=var_dict['productPrice']
            price_old_gen=soup.find("div", {"class":re.compile("price-block(.+)")})
            price_old=price_old_gen.find("span",{"class":"pricing__old-price"})
            if price_old:
                price_old=price_old.text.strip()
                discount=str(int((1-float(price)/float(price_old))*100))+'%'
            if title:
                links.title.loc[i]=str(title)
            links.loc[i,category_names]=category.split('/')+[None]*(len(category_names)-len(category.split('/')))
            if discount:
                links.discount.loc[i]=discount
            if brand:
                links.brand.loc[i]=brand
            if price:
                links.price.loc[i]=price

        else:
            brand=[]
            cats=[]
            old_prices=[]
            prices=[]
            discount=[]
            cat_split=[]
            info=soup.findAll("article",{"class":re.compile("(.+)promotie-actie(.+)")})

            if not info:
                info=soup.findAll("article")
            for k in info:
                brand.append(k["data-brand"])
                cat=clean_hit(k.find_all("p", {"class":"hidden category"}))
                if not cat:
                    cat=set([k["data-category"]])

                cat_split=[g.split('/') for g in set(cat)]
                cats.extend(cat_split)

                old_price=clean_hit(k.find_all("span", {"class":"pricing__old-price"}))
                old_price=[float(re.sub('[^\d\.]','',o)) for o in old_price]
                old_prices.extend(old_price)
                price=clean_hit(k.find_all("span",{"class":"current-price"}))
                price=[float(re.sub('[^\d\.]','',o)) for o in price]
                prices.extend(price)
                disc=[str(int(round((1-float(p)/float(o))*100)))+'%' for o,p in zip(old_price,price)]
                discount.extend(disc)

            if len(set(prices))==1:
                links.price.loc[i]=prices[0]
            if discount and len(set(discount))==1:
                links.discount.loc[i]=discount[0]
            brand = [x for x in brand if x!='Geen merk']
            if brand:
                links.brand.loc[i]=', '.join(set(brand)).encode('utf-8')
            if cats:
                cat_split=[]
                for item in zip(*cats):
                    cat_split.append(list(set(item)))
                cats_uni=[', '.join(f).encode('utf-8') for f in cat_split]
                links.loc[i,category_names]=cats_uni+[None]*(len(category_names)-len(cats_uni))

        pers=clean_hit(soup.find_all('p',{"class":"offer-explanation"}))
        if pers:
            links.persuasion.loc[i]=', '.join(set(pers)).encode('utf-8')
        if not links.title.loc[i] and (brand or cat_split):
            links.title.loc[i]=(brand or [""])[0]+' '+(cat_split or [[""]])[-1][0]
            if links.title.loc[i]:
                links.title.loc[i].encode('utf-8')
    return links
