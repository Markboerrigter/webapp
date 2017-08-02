
import xlsxwriter
import pandas as pd
import json
from tagging_from_xml_Mark import tags_from_xml
from xml_to_db import update_database
from get_click_data import *
from pymongo import MongoClient
import os

def write_to_excel(data, file_name):
    #workbook = xlsxwriter.Workbook('chart_line.xlsx')
    #worksheet = workbook.add_worksheet()
    #data = [10, 40, 50, 20, 10, 50]
    workbook = xlsxwriter.Workbook(file_name + '.xlsx')
    worksheet = workbook.add_worksheet()

    worksheet.write('A1', 'views')

    if True: # write Row D

        worksheet.write('D3', 'Score Basis',
                    workbook.add_format({'bold': True,'top': True, 'bottom': True ,'bg_color': '#819FF7','center_across': True}))
        worksheet.write('D4', 'Visits',
                    workbook.add_format({'bg_color': '#ECF6CE','center_across': True}))
        worksheet.write('D5', 'Clicks',
                    workbook.add_format({'bg_color': '#ECF6CE','center_across': True}))
        worksheet.write('D6', 'CTR',
                    workbook.add_format({'bg_color': '#CEF6D8','center_across': True}))
        worksheet.write('D7', 'Score',
                    workbook.add_format({'top': True, 'bottom': True,'center_across': True}))
        worksheet.write('D9', 'Score interactiviteit',
                    workbook.add_format({'bold': True, 'bottom': True,'center_across': True}))
        worksheet.write('D10', 'Links in folder',
                    workbook.add_format({'bg_color': '#819FF7','center_across': True}))
        worksheet.write('D11', 'Clicks per link',
                    workbook.add_format({'bg_color': '#CEF6D8','center_across': True}))
        worksheet.write('D12', 'Score',
                    workbook.add_format({'top': True, 'bottom': True,'center_across': True}))
        worksheet.write('D14', 'Score betrokkenheid',
                    workbook.add_format({'bold': True, 'bottom': True,'center_across': True}))
        worksheet.write('D15', "Pagina's",
                    workbook.add_format({'bg_color': '#819FF7','center_across': True}))
        worksheet.write('D16', '% tot laatste pagina',
                        workbook.add_format({'bg_color': '#ECF6CE','center_across': True}))
        worksheet.write('D17', 'Score',
                    workbook.add_format({'top': True, 'bottom': True,'center_across': True}))
        worksheet.write('D20', 'Score inspiratie',
                    workbook.add_format({'bold': True, 'bottom': True,'center_across': True}))
        worksheet.write('D21', 'Visits',
                        workbook.add_format({'bg_color': '#ECF6CE','center_across': True}))
        worksheet.write('D22', 'Views',
                        workbook.add_format({'bg_color': '#ECF6CE','center_across': True}))
        worksheet.write('D23', "Pagina's",
                    workbook.add_format({'bg_color': '#819FF7','center_across': True}))
        worksheet.write('D24', 'Views per visit',
                    workbook.add_format({'bg_color': '#CEF6D8','center_across': True}))
        worksheet.write('D25', 'Views per pagina',
                        workbook.add_format({'bg_color': '#F6D8CE','center_across': True}))
        worksheet.write('D26', "% gelezen pagina's per visit")
        worksheet.write('D27', 'Score',
                    workbook.add_format({'top': True, 'bottom': True,'center_across': True}))
        worksheet.write('D30', 'Score',
                    workbook.add_format({'bold': True, 'center_across': True}))
        worksheet.write('D31', 'Visit',
                        workbook.add_format({'bg_color': '#ECF6CE','center_across': True}))
        worksheet.write('D32', 'Tijd',
                        workbook.add_format({'bg_color': '#ECF6CE','center_across': True}))
        worksheet.write('D33', 'Pagina',
                    workbook.add_format({'bg_color': '#819FF7','center_across': True}))
        worksheet.write('D34', 'Tijd per visit',
                    workbook.add_format({'bg_color': '#CEF6D8','center_across': True}))
        worksheet.write('D35', 'Tijd per pagina',
                    workbook.add_format({'bg_color': '#CEF6D8','center_across': True}))
        worksheet.write('D36', 'Score',
                    workbook.add_format({'top': True, 'bottom': True,'center_across': True}))
        worksheet.set_column('D:D', 30,
                    workbook.add_format({'center_across': True}))
    if True: # write Row E with the data
        worksheet.write('E3', 'folder wk 30',
                    workbook.add_format({'right': True,'bold': True,'top': True, 'bottom': True ,'bg_color': '#819FF7','center_across': True}))
        worksheet.write('E4', data['total_visits'],
                    workbook.add_format({'right': True}))
        worksheet.write('E5', data['total_clicks'],
                    workbook.add_format({'right': True}))
        worksheet.write('E6', str(float(data['clicks'])/float(data['views'])*100) +'%',
                    workbook.add_format({'right': True}))
        worksheet.write('E7', str(float(data['total_clicks'])/float(data['total_visits'])*50),
                    workbook.add_format({'bold': True, 'right': True,'top': True, 'bottom': True,'center_across': True}))
        worksheet.write('E9', '',
                    workbook.add_format({'bold': True, 'bottom': True,'center_across': True}))
        links_in_folder = len(data['link_clicks'])
        worksheet.write('E10', str(links_in_folder),
                    workbook.add_format({'right': True}))
        clicks_per_link = data['clicks']/links_in_folder
        worksheet.write('E11', str(clicks_per_link),
                    workbook.add_format({'right': True}))
        worksheet.write('E12', str(clicks_per_link/links_in_folder),
                    workbook.add_format({'right': True, 'top': True, 'bottom': True,'center_across': True}))
        worksheet.write('E14', '',
                    workbook.add_format({'bold': True, 'bottom': True,'center_across': True}))
        ## DEZE DATA IS KUT
        aantal_pagina = ''
        worksheet.write('E15', "Pagina's",
                    workbook.add_format({'right': True, 'bg_color': '#819FF7','center_across': True}))
        worksheet.write('E16', '% tot laatste pagina',
                        workbook.add_format({'right': True, 'bg_color': '#ECF6CE','center_across': True}))
        worksheet.write('E17', 'Score',
                    workbook.add_format({'right': True, 'top': True, 'bottom': True,'center_across': True}))
        worksheet.write('E20', '',
                    workbook.add_format({'bold': True, 'bottom': True,'center_across': True}))
        worksheet.write('E21', 'Visits',
                        workbook.add_format({'bg_color': '#ECF6CE','center_across': True}))
        worksheet.write('E22', 'Views',
                        workbook.add_format({'bg_color': '#ECF6CE','center_across': True}))
        worksheet.write('E23', "Pagina's",
                    workbook.add_format({'bg_color': '#819FF7','center_across': True}))
        worksheet.write('E24', 'Views per visit',
                    workbook.add_format({'bg_color': '#CEF6E8','center_across': True}))
        worksheet.write('E25', 'Views per pagina',
                        workbook.add_format({'bg_color': '#F6E8CE','center_across': True}))
        worksheet.write('E26', "% gelezen pagina's per visit")
        worksheet.write('E27', 'Score',
                    workbook.add_format({'top': True, 'bottom': True,'center_across': True}))
        worksheet.write('E30', 'Score',
                    workbook.add_format({'bold': True, 'center_across': True}))
        worksheet.write('E31', 'Visit',
                        workbook.add_format({'bg_color': '#ECF6CE','center_across': True}))
        worksheet.write('E32', 'Tijd',
                        workbook.add_format({'bg_color': '#ECF6CE','center_across': True}))
        worksheet.write('E33', 'Pagina',
                    workbook.add_format({'bg_color': '#819FF7','center_across': True}))
        worksheet.write('E34', 'Tijd per visit',
                    workbook.add_format({'bg_color': '#CEF6E8','center_across': True}))
        worksheet.write('E35', 'Tijd per pagina',
                    workbook.add_format({'bg_color': '#CEF6E8','center_across': True}))
        worksheet.write('E36', 'Score',
                    workbook.add_format({'top': True, 'bottom': True,'center_across': True}))
        worksheet.set_column('D:D', 30,
                    workbook.add_format({'center_across': True}))


    # worksheet.set_column('A:G',
    #             workbook.add_format({'center_across': True}))

    # Create a Pandas Excel writer using XlsxWriter as the engine.

    # Convert the dataframe to an XlsxWriter Excel object.
    # cat_values.to_excel(writer, sheet_name='Sheet1',index=False)
    #workbook  = writer.book
    #worksheet = writer.sheets['Shfile_directoryeet1']
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({'values': '=Sheet1!$D$2:$D$8'})
    worksheet.insert_chart('J2', chart)
    # workbook.close()
    # writer.save()

def get_data():
    client = MongoClient('95.85.15.95', 27017)
    db = client['datatrics']
    collection = db.scorecards
    folder_id = int(2000548)
    traffic_coming_from = get_coming_from(collection,folder_id)
    link_clicks = merge_clicks_tags(get_link_clicks(collection, 'prenatal'), 'trek.csv')
    print(link_clicks)
    device = get_device_visits(collection,folder_id)
    views = total_views(collection, folder_id)
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

def main():

    json_data=open('data.json').read()

    data = get_data()

    """
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
    """
    # data = [10, 40, 50, 20, 10, 50]
    write_to_excel(data, 'try')

if __name__== '__main__':
    main()
