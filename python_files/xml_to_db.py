
# coding: utf-8

# In[ ]:

#import the needed packages

#used to read data from sql database
from pymongo import MongoClient
import time
import xmltodict
import requests
from collections import OrderedDict

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

def listRecursive (d, key):
    for k, v in d.items ():
        if isinstance (v, OrderedDict):
            for found in listRecursive (v, key):
                yield found
        if k == key:
            yield v

def xml_to_sql(db,retail_var,prod_name,xml_cols):
    """
    write the xml feed to a database
    cur: cursor of the database
    conn: connector of the database
    retail_var: dictionary with retailer specific information
    table_name: name of the database table
    prod_name: string which indicates a new product in the xml
    """
    collect_name='xml_'+retail_var['retailer']

    try:
        collection = db[collect_name]
        collection.remove({})
    except:
        db.createCollection(collect_name)
        collection=db[collect_name]

    #from the stated categories, select only the ones for which for this retailer a value is defined
    col_names=[k for k in xml_cols if retail_var[k]]
    ret_cols=[retail_var[col] for col in col_names]

    r = requests.get(retail_var['xml'])

    dic=xmltodict.parse(r.content)
    producten=next(listRecursive(dic,retail_var['select_first']))
    producten_new=[]
    for p in producten:
        if p:
            d={}
            for i in range(len(ret_cols)):
                if ret_cols[i] in p.keys():
                    d.update({col_names[i]:p[ret_cols[i]]})
                else:
                    d.update({col_names[i]:None})
            producten_new.append(d)
    collection.insert(producten_new)
    print("xml inserted in mongo")

def update_database(ret):
    client = MongoClient('ds119533.mlab.com', 19533)
    db = client['tagging']
    db.authenticate('hahamark','hahamark')
    xml_cols=['title','brand','price','category','price_old','link']
    retail_var=retrieve_vars(db,ret)
    if retail_var['xml']:
        xml_to_sql(db,retail_var,retail_var['select_first'],xml_cols)
