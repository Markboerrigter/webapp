#import the needed packages

#a common package to work with data in Python
import pandas as pd
#used to do stuff with regex (for recognizing the product id)
import re
#used to read data from sql database
from pymongo import MongoClient
import importlib

def retrieve_links(csv_path,col_names,split_name):
    """
    Gets a dataframe with links from a database table
    links_db: name of the database which contains links
    links_table: the name of the table in the database which contains the needed links
    col_names: a list with all the column names you want in the dataframe (except urls)
    split_name: string with from where on to cut the url
    links: a dataframe which contains the links of the folder (urls)
    """

    #import the csv by pandas
    links=pd.read_csv(csv_path,encoding='utf-8')
    #have to change this if you change column name in database
    #change column name, just for ease of rest of proces
    links.columns=['urls']
    #THIS MIGHT HAVE TO BE CHANGED, DEPENDING ON THE FORMAT OF THE URLS WE GET
    #only get the first part of the link
    links.urls=[i[:int(i.find(split_name))] if split_name and i.find(split_name)!=-1 else i for i in links.urls]
    #initialize all the columns
    for i in col_names:
        links[i]=None
    return links


def retrieve_vars(db,ret):
    """
    Retrieve the retailer specific information from the database and return a dictionary with this information
    ret: the name of the retailer
    retail_var: a dictionary with the information from the retailer
    """


    #select all information
    collection = db.variables_retailers
    retail_var=dict(collection.find_one({"retailer":ret}))
    print("retail_vars loaded")
    return retail_var


def split_cat(delimiter,links,main_category,all_categories):
    #split the name into categories from main to sub-bers
    for idx,cat in enumerate(links[main_category]):
        if links.loc[idx,main_category]:
            category_split=cat.split(delimiter)
            attr=category_split+[None]*(len(all_categories)-len(category_split))
            links.loc[idx,all_categories]=attr
    return links

def fill_tags(xml_db,retail_var,links,col_names):
    """
    Loop through the links and check if there is an entry in the xml file that contains this link.
    If so, get the values of the given categories of that product and write them to the dataframe.
    xml_db: name of database containing the xml
    table_name: the name of the table containing the xml
    retail_var: dictionary with retailer specific information
    links (in): dataframe with the links in the folder
    links (out): dataframe with the links in the folder and the found tags that belong to each links
    """
    all_categories=['category','category2','category3','category4','category5','category6']
    collect_name='xml_'+retail_var['retailer']
    try:
        collection = xml_db[collect_name]
    except Exception as e:
        print(e)
        print("you should first initialize a xml database")
    print('collection initialized')
    #loop over all urls
    for idx,start in enumerate(links.urls):
        #select the information from the row of the xml database where the link is like the link from the folder
        query={}
        query["link"]={'$regex':".*"+start+".*"}
        hit=collection.find_one(query)

        #if there is a link like the one from the folder
        if hit:
            hit={your_key: hit[your_key] for your_key in hit.keys() if your_key not in ['link','_id']}
            #set those values in the dataframe
            #links.loc[idx,col_names]=vals[0]
            for k in hit.keys():
                links.loc[idx,k]=hit[k]
                if links.loc[idx,'category'] and retail_var['delimiter']:
                        if type(links.loc[idx,'category']) ==list:
                            links.loc[idx,'category']=''.join(links.loc[idx,'category'])
                        category_split=links.loc[idx,'category'].split(retail_var['delimiter'])
                        links.loc[idx,all_categories]=category_split+[None]*(len(all_categories)-len(category_split))
            #if there is no current price but there is an old price, set the old price as current price
            #this because some retailers have a price and a sale price.
            if not links.price.loc[idx] and 'price_old' in col_names:
                links.price.loc[idx]=links.price_old.loc[idx]
            #if a price is found
            #HAVE TO TEST IF THIS ALWAYS WORKS
            for k in ['price','price_old']:
                if links.loc[idx,k]:
                    #remove all none currency related characters
                    links.loc[idx,k]=re.sub('[^0-9.,-]','',links.loc[idx,k])
                    #make it in a general format
                    links.loc[idx,k]=links.loc[idx,k].replace('-','00').replace(',','.')
            #calculate the discount
            p=links.price.loc[idx]
            o=links.price_old.loc[idx]
            if p!=None and o!=None and p!=o:
                links.discount.loc[idx]=str(int(round((1-float(p)/float(o))*100)))+'%'

    #price_old is only for computing purposes so can be deleted
    del links['price_old']
    print('tags filled')
    return links

def save_to_csv(links,csv_out):
    """
    save the dataframe with links and tags to a database
    links (in):dataframe with links and tags
    table_out: the name of the table the tags should be saved in
    links (out): the dataframe with links and tags
    """


    #write the results to a csv
    links.to_csv(csv_out,index=False,encoding='utf-8')
    #not fully necessary but might come in handy
    return links


def tags_from_xml(ret, week,csv_name):
    client = MongoClient('ds119533.mlab.com', 19533)
    db = client['tagging']
    db.authenticate('hahamark','hahamark')

    csv_out='tags_'+ret+'_'+week+'.csv'

    #table=ret+'_week'+week
    xml_table='xml_'+ret

    col_names=['title','brand','price','price_old','discount','category','category2','category3','category4','category5','category6','category7','persuasion']

    retail_var=retrieve_vars(db,ret)
    links=retrieve_links(csv_name,col_names,retail_var['split_name'])
    #get the tags from the xml
    if retail_var['xml']:
        links=fill_tags(db,retail_var,links,col_names)
    if 'price_old' in links.columns:
        del links['price_old']
    links=save_to_csv(links,'csv_output/beforescrape'+ csv_out)
    if retail_var['scrape']==True:
        module_name='webscraping_'+ret
        module = importlib.import_module('python_files.webscraping.' + module_name)
        links=module.scrape(links)
    download_path = 'csv_output/'+ csv_out
    links=save_to_csv(links,'csv_output/'+ csv_out)
    print('links saved to csv')
    return links, download_path
