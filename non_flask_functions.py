from python_files.tagging_from_xml_Mark import tags_from_xml
from python_files.xml_to_db import update_database
from python_files.get_click_data import *
from pymongo import MongoClient
import os

basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir,'uploads')
ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def retrieve_tags(session):
    filepath = UPLOAD_FOLDER + '/' + session['filename']
    # click.echo(session['Foldernaam'])
    # click.echo(filepath)
    links, csv_name = tags_from_xml(session['Foldernaam'], session['fid'],filepath)
    return links, csv_name

def updateXMLdatabase(session):
    update_database(session['Foldernaam'])
    return

def generateClickData(session):
    client = MongoClient('95.85.15.95', 27017)
    db = client['datatrics']
    collection = db.scorecards
    folder_id = int(session['fid'])
    print(folder_id)

    traffic_coming_from = get_coming_from(collection,folder_id)
    link_clicks = merge_clicks_tags(get_link_clicks(collection, session['Foldernaam']), os.path.join(basedir,'csv_output/tags_' + session['Foldernaam'] + '_' + session['fid'] + '.csv'))
    device = get_device_visits(collection,folder_id)
    views = total_views(collection, folder_id)
    print(views)
    visits = total_visits(collection,folder_id)
    time = total_time(collection,folder_id)
    bounce = total_bounce(collection,folder_id)
    views_per_page = page_views(collection,folder_id)
    exits_per_page = page_exits(collection,folder_id)
    best_cat=performance_value(link_clicks,'category')
    # best_page=performance_value(mlink_clicks,'page')
    price_bins=performance_value_prices(link_clicks)
    disc_bins=performance_value_bins(link_clicks,'discount')

    data = {
                'link_clicks' : link_clicks,
                'total_visits':visits,
                'total_time': time,
                'total_bounce': bounce,
                "device": device,
                'traffic': traffic_coming_from,
                'total_views': views,
                'page_views': views_per_page,
                'page_exits': exits_per_page,
                'best_cat': best_cat,
                'best_page': best_page,
                'price_bins': price_bins,
                'disc_bins': disc_bins
                }
    return data


def get_retailers():
    client = MongoClient('ds119533.mlab.com', 19533)
    db = client['tagging']
    db.authenticate('hahamark','hahamark')
    collection = db.variables_retailers
    retailers = [x['retailer'] for x in collection.find({})]
    return retailers
