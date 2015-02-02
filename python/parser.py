# -*- coding: utf-8 -*-
import re, os, sys

from lxml import etree

import robotparser #for check a wbe page can be fetched or not
from urlparse import urljoin #for combine the link
import urllib, urllib2, httplib, socket
from urllib2 import urlopen, Request
import urlparse
import datetime, time  

from collections import OrderedDict

#from bson import json_util
import json

retr_text = lambda nodes, pipe='': pipe.join([''.join(i.itertext()) for i in nodes])
retr_one = lambda nodes: nodes.text if len(nodes)==0 else nodes[0].text
retr_list = lambda nodes : filter(None, [i.strip() for i in nodes.itertext()])


base_url = 'http://www.sumo.or.jp/'
year_schedule_url = 'http://www.sumo.or.jp/ticket/year_schedule'
sumo_hoshitori_url = 'http://www.sumo.or.jp/honbasho/main/hoshitori#east'
# headers = {
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#     'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36',
#     'Accept-Encoding': 'gzip,deflate,sdch',
#     'Accept-Language': 'ja,zh-TW;q=0.8,zh;q=0.6,en;q=0.4,en-US;q=0.2',
#     'Cache-Control': 'no-cache',
#     'Connection': 'keep-alive',
#     'Host': 'www.sumo.or.jp',
#     'Pragma': 'no-cache',
# }

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36',
#     'Accept-Encoding': 'gzip,deflate,sdch',
#     'Accept-Language': 'ja,zh-TW;q=0.8,zh;q=0.6,en;q=0.4,en-US;q=0.2',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Host': 'www.sumo.or.jp',
    'Pragma': 'no-cache',
}

win_lose_type = {
    u'\u767d\u4e38' : 0,         # 白丸
    u'\u9ED2\u4E38' : 1,         # 黑丸
    u'\u4E0D\u6226\u52DD' : 2,   # 不戰勝
    u'\u4E0D\u6226\u6557' : 3,   # 不戰敗
    u'\u4F11\u307F' : 4,         # 休み
    u'\u5F15\u5206' : 5,         # 引分
    u'\u75DB\u5206' : 6          # 痛分

}


def add_into_done_list(key_string):
    check_output_folder_exist('output/')
    with open('output/done_lists.txt', 'a+') as f:
        f.write(key_string + '\n')


##############################################################################################

def get_url_response_with_encoding(url):
    req = urllib2.Request(url, None, headers)
    resp = urllib2.urlopen(req)
    data = ungzip(resp)
    return data


def generate_url_request(url):
    request = urllib2.Request(url, None, headers)
    return request


def send_url_request(request):
    page = urllib2.urlopen(request) 
    return page.read()


def parse_html_data_to_json(html_data):

    total_record = OrderedDict()

    tree = etree.HTML(html_data)

    # get date
    date = tree.xpath('//*/div[@id="content"]/div[@id="mainContent"]/p[@class="mdDate"]')
    total_record['date'] = date[0].text.strip()

    e_path = '//*/div[@id="east"]/table[@class="main "]/tr'
    get_total_record_by_path(total_record, tree, e_path, "E")

    w_path = '//*/div[@id="west"]/table[@class="main "]/tr'
    get_total_record_by_path(total_record, tree, w_path, "W")

    return total_record


def get_total_record_by_path(total_record, tree, path, tag):

    # get east total record
    elements = tree.xpath(path)

    # get EAST player name, rank, and total record with competitor
    for index in xrange(0, len(elements), 2):

        single_player = {}

        player_info = elements[index].xpath('td[@class="player bBnone"]/div/dl')
        record_info = elements[index].xpath('td/img')
        competitor_info = elements[index+1].xpath('td')


        if len(player_info) == 1:
            info = retr_list(player_info[0])
            single_player['rank'] = info[0]
            single_player['name'] = info[1]
            single_player['record'] = info[2]


        win_lose_record = [win_lose_type.get(i.get('alt')) for i in record_info]
        single_player['win_lose_list'] = win_lose_record


        # get competitor info and order
        competitor_record = [i.text if i.text else "" for i in competitor_info]
        single_player['competitor_list'] = competitor_record

        total_record[tag + str(index/2 + 1)] = single_player


def check_output_folder_exist(folder_name):
    try:
        os.makedirs(folder_name)
    except OSError:
        pass


def save_to_file(data):
    check_output_folder_exist('output/')
    ## save info into json
    dateStr = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    with open('output/' + dateStr + '.json', 'w+') as f:
        doc_str = json.dumps(data)
        f.write(doc_str)


def update_data_to_server(data):
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    connection.connect()
    connection.request('POST', '/1/classes/TotalRecord', json.dumps(data), 
        {
            "X-Parse-Application-Id": "APP-ID",
            "X-Parse-REST-API-Key": "REST-API-Key",
            "Content-Type": "application/json"
        })

    result = json.loads(connection.getresponse().read())
    print result



######## Main Start ########

if __name__=="__main__":
    #reload(sys)
    #sys.setdefaultencoding('utf-8')

    ## set init
    queues = {
        'total' : 'http://www.sumo.or.jp/honbasho/main/hoshitori',
        'singleDay' : 'http://www.sumo.or.jp/honbasho/main/torikumi?day=%d&rank=1'
    }

    print '===== START ====='

    while len(queues) > 0:
        time.sleep(5)

        key, value = queues.popitem()
        print key, value

        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        add_into_done_list(current_date)

        if key == 'total':
            add_into_done_list(key + " : " + value)

            request = generate_url_request(value)
            
            data = send_url_request(request)

            result_data = parse_html_data_to_json(data)

            save_to_file(result_data)
            
            #update_data_to_server(result_data)

        else:
            for x in xrange(1, 16):
                time.sleep(5)
                print value % x
                add_into_done_list(key + " : " + (value % x))




        print 'Here has queues =>', len(queues)
        print '-' * 20

    add_into_done_list('-' * 20)

    print '===== Done ====='
