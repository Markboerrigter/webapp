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
    hits=[re.sub('[\n\r\t]','',i.get_text().strip(' ')) for i in group_name]
    return hits


def scrape(links):
    #loop through all links
    for i in range(len(links)):
        #get soup of url
        response=requests.get(links.urls.loc[i])
        soup=bs4.BeautifulSoup(response.text,"lxml")

        #if no price has been found yet
        if not links.price.loc[i]:
            #prodPrice contains current prices if there are several products on the page
            prices=clean_hit(soup.find_all("span",{"class":"prodPrice"}))
            prices=[re.search('\d+(\.|,)\d*',p).group() for p in prices]
            if not prices:
                #only occurs if there is one product on the page
                prices=soup.find_all("meta",{"name":"price"})
                prices=[k['content'] for k in prices]
            #if something is found and all prices are the same
            if prices and prices.count(prices[0])==len(prices):
                links.price.loc[i]=re.sub('[^0-9.,-]','',prices[0])

        if not links.title.loc[i]:
            #prodName prodNameTro occurs when there are several products on the page
            titles=clean_hit(soup.find_all("span",{"class":"prodName prodNameTro"}))
            if not titles:
                #only occurs if there is one product on the page
                titles=clean_hit(soup.find_all("div",{"class":"productName"}))
            if titles and titles.count(titles[0])==len(titles):
                links.title.loc[i]=titles[0]
            #when there are several products, there is sometimes a short description that gives a bit more info
            desc=clean_hit(soup.find_all("span",{"class":"prodDesc"}))
            if desc and desc.count(desc[0])==len(desc):
                links.title.loc[i]=links.title.loc[i]+' '+desc[0]

        if not links.category.loc[i]:
            #only occurs when there is only one product on the page
            cat=soup.find_all("meta",{"name":"category_name"})
            cat=[k['content'] for k in cat]
            if cat and cat.count(cat[0])==len(cat):
                links.category.loc[i]=cat[0]

        if links.brand.loc[i]==None:
            #only occurs if there is one product
            brand=clean_hit(soup.find_all("SPAN",{"itemprop":"brand"}))
            if brand and brand.count(brand[0])==len(brand):
                links.brand.loc[i]=brand[0]

        if links.price.loc[i] and not links.discount.loc[i]:
            vars_prod=clean_hit(soup.find_all("script",{"type":"text/javascript","language":"JavaScript"}))
            #find all keys and values from dictionaries in the gotten script
            pattern = re.compile('"(\w+)":"(.*?)"')
            #convert those to a dictionary
            fields = dict(re.findall(pattern, ' '.join(vars_prod)))
            #indicates an old price
            if 'previousprice' in fields:
                price_old=re.search('\d+(\.|,)\d*',fields['previousprice']).group()
                price_old=price_old.replace('-','00').replace(',','.')
                links.discount.loc[i]=str(int(round((1-float(links.price.loc[i])/float(price_old))*100)))+'%'
    return links
