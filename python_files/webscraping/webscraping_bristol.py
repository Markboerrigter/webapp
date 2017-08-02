#import the needed packages
#a common package to work with data in Python
import pandas as pd
#used to do stuff with regex (for recognizing the product id)
import re
#used to parse websites
import requests
import bs4

def scrape(links):
    links['price_old']=None
    for i in range(len(links)):
        response=requests.get(links.urls.loc[i])
        soup=bs4.BeautifulSoup(response.text,"lxml")
        #get all dictionary like values from the kega-ddl script
        script_text=soup.find('script',{"class":"kega-ddl-script"}).text
        pattern = re.compile('"(\w+)":"(.*?)"')
        #write them to a dictionary
        fields = dict(re.findall(pattern, script_text))
        #retrieve the brand and categories from the dictionary
        if 'brand' in fields:
            links.brand.loc[i]=fields['brand']
        if 'primaryCategory' in fields:
            links.category.loc[i]=fields['primaryCategory']
        subs=['subCategory2','subCategory3','subCategory4']
        links.loc[i,['category2','category3','category4']]=[fields[val] if val in fields else None for val in subs]

        #if no title has been found yet it can be in the name field
        if not links.title.loc[i] and 'name' in fields:
            links.title.loc[i]=fields['name']
        #fiels price contains the old price if there is one
        if not links.price_old.loc[i] and 'price' in fields:
            links.price_old.loc[i]=round(float(fields['price']),2)
        if not links.price.loc[i]:
            #priceDiscount contains the amount of discount. Only exists if there is a discount
            if 'priceDiscount' in fields:
                links.price.loc[i]=round(float(fields['price'])-float(fields['priceDiscount']),2)
            elif 'price' in fields:
                links.price.loc[i]=round(float(fields['price']),2)
        if links.price_old.loc[i]!=links.price.loc[i] and links.price_old.loc[i] and links.price.loc[i]:
            p=links.price.loc[i]
            o=links.price_old.loc[i]
            links.discount.loc[i]=str(int(round((1-float(p)/float(o))*100)))+'%'
    del links['price_old']
    return links
