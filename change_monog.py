from pymongo import MongoClient

client = MongoClient('95.85.15.95', 27017)
db = client['datatrics']
collection = db.scorecards
folder = collection.find({})

for x in folder:
    # print(x)
    if isinstance(x['page_info']['page_views'],dict):
        print('failed')
#         print('next mistake')
#         # print(x['page_info']['page_cart_popups'].items())
#         # print(True)
#         # print(x['page_info']['page_views'])
#         l = {int(k) : v for k,v in x['page_info']['page_views'].items()}
#         x['page_info']['page_views'] = [x['page_info']['page_views'][str(y)] for y in sorted(l.keys())]
#         l = {int(k) : v for k,v in x['page_info']['page_exits'].items()}
#         x['page_info']['page_exits'] = [x['page_info']['page_exits'][str(y)] for y in sorted(l.keys())]
#         l = {int(k) : v for k,v in x['page_info']['page_video_popups'].items()}
#         x['page_info']['page_video_popups'] = [x['page_info']['page_video_popups'][str(y)] for y in sorted(l.keys())]
#         l = {int(k) : v for k,v in x['page_info']['page_cart_popups'].items()}
#         x['page_info']['page_cart_popups'] = [x['page_info']['page_cart_popups'][str(y)] for y in sorted(l.keys())]
#         l = {int(k) : v for k,v in x['page_info']['page_next'].items()}
#         x['page_info']['next'] = [x['page_info']['page_next'][str(y)] for y in sorted(l.keys())]
#         l = {int(k) : v for k,v in x['page_info']['page_prev'].items()}
#         x['page_info']['page_prev'] = [x['page_info']['page_prev'][str(y)] for y in sorted(l.keys())]
#         # l = {int(k) : v for k,v in x['page_info']['page_cart_popups'].items()}
#         # x['page_info']['page_cart_popups'] = [x['page_info']['page_cart_popups'][str(y)] for y in sorted(l.keys())]
#         l = {int(k) : v for k,v in x['page_info']['page_popup_cart_order'].items()}
#         x['page_info']['page_popup_cart_order'] = [x['page_info']['page_popup_cart_order'][str(y)] for y in sorted(l.keys())]
#         l = {int(k) : v for k,v in x['page_info']['autoplay_video'].items()}
#         x['page_info']['autoplay_video'] = [x['page_info']['autoplay_video'][str(y)] for y in sorted(l.keys())]
#         l = {int(k) : v for k,v in x['page_info']['time_spent_on_page'].items()}
#         x['page_info']['time_spent_on_page'] = [x['page_info']['time_spent_on_page'][str(y)] for y in sorted(l.keys())]
#
#         # print(x['page_info']['page_views'])
#         print(type(x))
#         collection.update_one({'_id':x['_id']}, {"$set": x}, upsert=False)
# print('finished')
