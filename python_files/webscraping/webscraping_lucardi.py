
# coding: utf-8

# In[1]:

#import the needed packages
#a common package to work with data in Python
import pandas as pd
#used to do stuff with regex (for recognizing the product id)
import re
#used to parse websites
import requests
import bs4


# In[2]:

# def get_xml_tags(tag_db,tag_table):
#     eng_links=create_engine('sqlite:///'+tag_db)
#     #import the database by pandas
#     links=pd.read_sql_table(tag_table,eng_links)
#     return links


# In[3]:

# links=get_xml_tags('tag_results.db','lucardi_week29')


# In[4]:

def clean_hit(group_name):
    """
    Get as input a soup list and return a list with clean prices
    group_name: soup list
    hits: list with found prices
    """
    hits=[re.sub('[\n\r\t]','',i.get_text()).strip() for i in group_name]
    return hits


# In[5]:

def scrape(links):
    for i in range(len(links)):

        response=requests.get(links.urls.loc[i])
        soup=bs4.BeautifulSoup(response.text,"lxml")

        vars_prod=soup.find("div",{"class":"c-product-detail"})
        links.brand.loc[i]=vars_prod['data-brand']
        links.category.loc[i]=vars_prod['data-category']
        if links.title.loc[i]==None:
            links.title.loc[i]=vars_prod['data-name']
        if links.price.loc[i]==None:
            links.price.loc[i]=vars_prod['data-price'].replace('-','00').replace(',','.')
        if links.discount.loc[i]==None and links.price.loc[i]!=None and soup.find("div", {"class":"vanprijs"}):
            price_old=re.sub('[^0-9.,]','',soup.find("div", {"class":"vanprijs"}).text)
            price_old=price_old.replace('-','00').replace(',','.')
            links.discount.loc[i]=str(int(round((1-float(links.price.loc[i])/float(price_old))*100)))+'%'
    print('Webscraping finished')
    return links
