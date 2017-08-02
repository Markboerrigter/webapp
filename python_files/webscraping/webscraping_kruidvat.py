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
    #vraag me af of die sub wel nodig is of dat get_text genoeg is, moet ik testen
    #hits=[re.sub('[^0-9a-zA-Z %&+,.-]','',i.get_text()) for i in group_name]
    hits=[i.get_text().strip(' ') for i in group_name]
    return hits


def remove_counts(item):
    item=[re.sub(r'\d+$', '', i) for i in item]
    return item


def scrape(links):
    name_categories=['category','category2','category3','category4','category5','category6']
    for i in range(25,len(links)):
        if links.urls.loc[i]=="-":
            continue
        response=requests.get(links.urls.loc[i])
        soup=bs4.BeautifulSoup(response.text,"lxml")
        product=soup.findAll("div",{"class":"c-product-summary__wrp"})
        if product:
            for div in product:
                title = div.find_all("div", {"class": "c-product-summary__title-wrp"})
                if title:
                    links.title.loc[i]=', '.join(clean_hit(title))
                price_old= div.find_all("span", {"class": "c-pricetag__from"})
                price_old_clean=[re.sub("[^0-9.,-]","",p) for p in clean_hit(price_old)]
                price= div.find_all("span", {"class": "c-pricetag__current-price"})
                price_clean=clean_hit(price)
                if price_clean:
                    links.price.loc[i]=', '.join(price_clean)
                if re.match("(.+)\d{2}",price_old_clean[0]):
                    discount=str(int((1-float(price_clean[0])/float(price_old_clean[0]))*100))+'%'
                    if discount:
                        links.discount.loc[i]=discount
                cat=soup.findAll("ol",{"class":"c-breadcrumbs c-breadcrumbs--transform-xxs"})
                for c in cat:
                    category=c.findAll("a",{"class":"c-breadcrumbs__label"})
                    category=clean_hit(category)
                    category.remove("Home")
                    subcategory=category[1:]
                    category=category[0]
                    if category:
                        links.category.loc[i]=category
                    if subcategory:
                        links.loc[i,name_categories[1:]]=subcategory+[None]*(len(name_categories[1:])-len(subcategory))

        else:
            brand=soup.findAll("span", { "data-for" : re.compile("masterBrandName(.+)") })
            brand=remove_counts(clean_hit(brand))
            if brand:
                links.brand.loc[i]=', '.join(brand)
            category=soup.findAll("span", { "data-for" : re.compile("categoryCodeLevel1(.+)") })
            category=remove_counts(clean_hit(category))
            if category:
                links.category.loc[i]=', '.join(category)
            subcategory=soup.findAll("span", { "data-for" : re.compile("categoryCodeLevel2(.+)") })
            subcategory=remove_counts(clean_hit(subcategory))
            if subcategory:
                links.category2.loc[i]=', '.join(subcategory)
            disc=soup.findAll("span",{"data-for":re.compile("promotionName(.+)")})


            if not remove_counts(clean_hit(disc)):
                price=soup.findAll("span",{"class":re.compile("c-pricetag__current-price")})
                price_clean=clean_hit(price)
                if len(set(price_clean))==1:
                    links.price.loc[i]=price_clean[0]
                    price_old=soup.findAll("span",{"class":re.compile("c-pricetag__from")})
                    price_old_clean=clean_hit(price_old)
                    price_old_clean=[re.sub("[A-Za-z]","",p) for p in price_old_clean]
                    if len(set(price_old_clean))==1 and re.match("(.+)\d{2}",price_old_clean[0]):
                        discount=str(int((1-float(price_clean[0])/float(price_old_clean[0]))*100))+'%'
                        links.discount.loc[i]=discount
            else:
                pers=remove_counts(clean_hit(disc))
                if pers:
                    links.persuasion.loc[i]=', '.join(pers)

            if not links.title.loc[i] and (links.brand.loc[i] or links.category.loc[i]):
                links.title.loc[i]=(brand or [""])[0]+' '+(subcategory or category or [""])[0]
    return links
