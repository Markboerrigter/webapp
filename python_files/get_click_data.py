import pandas as pd
#used to do stuff with regex (for recognizing the product id)
import re
#used to read data from sql database
from pymongo import MongoClient
from collections import defaultdict
import time
import math
import numpy as np

def get_coming_from(collection,folder_id):
    folder = collection.find({"publicationid": folder_id})
    traffic = [x['performance_metrics']['traffic'] for x in folder]
    c = defaultdict(int)
    for d in traffic:
        c[d.keys()[0]] += d[d.keys()[0]]
    c = dict(c)
    return c

def sum_clicks(links):
    total_clicks=sum([d['clicks'] for d in links])
    return(total_clicks)

def merge_clicks_tags(links,tags_name):
    tags=pd.read_csv(tags_name)
    tags['linkid']=tags['urls'].str.extract("(linkid=\d{8})",expand=True)
    links=pd.DataFrame(links)
    links['linkid']=links['_id'].str.extract("(linkid=\d{8})",expand=True)
    clicks=links.groupby('linkid').sum()
    clicks['linkid'] = clicks.index
    #met inner neemt hij alleen de linkids die in beide dataframes voorkomen
    merged=pd.merge(clicks,tags,on='linkid',how='inner')
    return merged

def performance_value(merged,value):
    f={'sum','mean','count'}
    df_mean=merged.groupby(value).agg(f)
    df_mean=df_mean['clicks']
    df_mean=df_mean.sort_values('mean',ascending=False)
    df_mean.reset_index(inplace=True)
    if not any(df_mean['mean'].isnull()):
        df_mean['mean']=df_mean['mean'].astype(int)
    return df_mean

def performance_value_bins(merged,value):
    num_bin=6
    mer_notnan=merged[merged[value].notnull()]
    mer_notnan[value]=mer_notnan[value].astype(float)
    bins=np.histogram(mer_notnan[value],bins=6)[1]
    mer_notnan[value+'_bins'] = pd.cut(mer_notnan[value].astype(float), bins,include_lowest=True)
    val_bins=performance_value(mer_notnan,value+'_bins')
    val_bins=val_bins.sort_values(value+'_bins')
    return val_bins

def performance_value_prices(merged):
    print(merged['price'])
    print(merged)
    merged['price']=merged['price'].str.replace('[^0-9.,-]','')
    merged['price']=merged['price'].str.replace(',','.')
    merged['price']=merged['price'].astype(float)
    return performance_value_bins(merged,'price')

def get_link_clicks(collection, foldernaam):
    regex = re.compile(foldernaam)
    links = collection.aggregate(
            	[
            		{
            			 "$match": {
            			    "date": {"$gte": "2017-07-16", "$lt": "2017-07-22"}
            			}
            		},
            		{
            			"$unwind": {
            			    "path" : "$links",
            			    "includeArrayIndex" : "arrayIndex",
            			    "preserveNullAndEmptyArrays" : False
            			}
            		},
            		{
            			"$match": {"links.url" : regex}
            		},
            		{
            			"$group": {
            			    "_id": "$links.url",
            			    "clicks": {"$sum": "$links.count"},
            			}
            		},
            		{
            			"$sort": {
            			    "clicks": -1
            			}
            		},
            	]
            );
    return [x for x in links]

def get_device_visits(collection,folder_id):
    bla=collection.aggregate(
    [
    {
    "$match":{"publicationid":folder_id}
    },
    {"$group":
        {"_id":"$config_device_type"
        ,"visits":
            {"$sum":'$performance_metrics.visits'},
            },
        },
    ]
    )
    return [x for x in bla]

def total_views(collection,folder_id):
    bla=collection.aggregate(
    [
    {
    "$match":{"publicationid":folder_id}
    },
    {"$group":
        {"_id":"$config_device_type"
        ,"visits":
            {"$sum":'$performance_metrics.views'},
            },
        },
    ]
    )
    return sum([x['visits'] for x in bla])

def total_visits(collection,folder_id):
    bla=collection.aggregate(
    [
    {
    "$match":{"publicationid":folder_id}
    },
    {"$group":
        {"_id":"$config_device_type"
        ,"visits":
            {"$sum":'$performance_metrics.visits'},
            },
        },
    ]
    )
    return sum([x['visits'] for x in bla])

def total_time(collection,folder_id):
    bla=collection.aggregate(
    [
    {
    "$match":{"publicationid":folder_id}
    },
    {"$group":
        {"_id":"$config_device_type"
        ,"visits":
            {"$sum":'$performance_metrics.time'},
            },
        },
    ]
    )
    return sum([x['visits'] for x in bla])
    # views = [x['performance_metrics']['time'] for x in folderbla]
    #
    # return sum(views)

def total_bounce(collection,folder_id):
    bla=collection.aggregate(
    [
    {
    "$match":{"publicationid":folder_id}
    },
    {"$group":
        {"_id":"$config_device_type"
        ,"visits":
            {"$sum":'$performance_metrics.bounce'},
            },
        },
    ]
    )
    return sum([x['visits'] for x in bla])
    # views = [x['performance_metrics']['bounce'] for x in folderbla]
    # return sum(views)

def page_views(collection, folder_id):
    bla=collection.aggregate(
    [
		{
			"$match": {
			    "publicationid": folder_id
			}
		},
		{
			"$unwind": {
			    "path" : "$page_info.page_views",
			    "includeArrayIndex" : "arrayIndex",
			}
		},
		{
			"$project": {
			    "first": {"$arrayElemAt":["$page_info.page_views",0]},
			    "last":{"$arrayElemAt":["$page_info.page_views",1]}
			}
		},
		{
			"$group": {
				"_id":"$first",
				"views":{"$sum":"$last"}

			}
		},
		{
			"$match": {
			    "views":{"$gt":0}
			}
		},
		{
			"$sort": {
			    "_id": 1
			}
		},
	],
    )

    # for x in bla:
    #     print(x)
    return {x['_id']:x['views'] for x in bla}
    # return page_views_final

def page_exits(collection, folder_id):
    bla=collection.aggregate(
    [
		{
			"$match": {
			    "publicationid": folder_id
			}
		},
		{
			"$unwind": {
			    "path" : "$page_info.page_exits",
			    "includeArrayIndex" : "arrayIndex",
			}
		},
		{
			"$project": {
			    "first": {"$arrayElemAt":["$page_info.page_exits",0]},
			    "last":{"$arrayElemAt":["$page_info.page_exits",1]}
			}
		},
		{
			"$group": {
				"_id":"$first",
				"exits":{"$sum":"$last"}

			}
		},
		{
			"$match": {
			    "exits":{"$gt":0}
			}
		},
		{
			"$sort": {
			    "_id": 1
			}
		},
	],
    )
    return {x['_id']:x['exits'] for x in bla}
    # page_exits = [x['page_info']['page_exits'] for x in folder]
    # page_exits = [[x,y] for z in page_exits if isinstance(z,list) for [x,y] in z]
    #
    # page_exits_final = {}
    # for x in page_exits:
    #     if x[0] not in page_exits_final:
    #         page_exits_final[x[0]] = x[1]
    #     else:
    #         page_exits_final[x[0]] += x[1]
    # return page_exits_final

# def main(folder_id):
#     client = MongoClient('95.85.15.95', 27017)
#     db = client['datatrics']
#     collection = db.scorecards
#     folder = collection.find({"publicationid": folder_id})
#     starttime = time.time()
#     # link_clicks = get_link_clicks(collection)
#     # print(link_clicks)
#     # views = total_views(collection, folder_id)
#     # print(views)
#     x = page_views(collection, folder_id)
#     print(x)
#     l = page_exits(collection, folder_id)
#     print(l)
#     # print('coming from timer: ' + str(time.time() - starttime))
#     # folder = collection.find({"publicationid": folder_id})
#     # starttime = time.time()
#     # traffic = get_coming_from(folder)
#     # print(traffic)
#     # print('link clicks timer: ' + str(time.time() - starttime))
#     # folder = collection.find({"publicationid": folder_id})
#     # starttime = time.time()
#     # views = total_views(folder)
#     # print(views)
#     # print('total views timer: ' + str(time.time() - starttime))
#     # folder = collection.find({"publicationid": folder_id})
#     # starttime = time.time()
#     # bounce = total_bounce(folder)
#     # print(bounce)
#     # print('total bounce timer: ' + str(time.time() - starttime))
#     # folder = collection.find({"publicationid": folder_id})
#     # starttime = time.time()
#     # page_views1 = page_views(folder)
#     # print(page_views1)
#     # print('total views per page timer: ' + str(time.time() - starttime))
#     #
#     # folder = collection.find({"publicationid": folder_id})
#     # starttime = time.time()
#     # page_exits1 = page_exits(folder)
#     # print(page_exits1)
#     # print('total exits per page timer: ' + str(time.time() - starttime))
#     # return
#
# if __name__ == '__main__':
#     main(1058298)
