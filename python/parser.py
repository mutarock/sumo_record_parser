# -*- coding: utf-8 -*-
import re, os, sys

from lxml import etree

import robotparser #for check a wbe page can be fetched or not
from urlparse import urljoin #for combine the link
import urllib, urllib2, httplib, socket
from urllib2 import urlopen,Request
import urlparse
import time  

from collections import OrderedDict

#from bson import json_util
import json

retr_text = lambda nodes, pipe='': pipe.join([''.join(i.itertext()) for i in nodes])
retr_one = lambda nodes: nodes.text if len(nodes)==0 else nodes[0].text
retr_list = lambda nodes : filter(None, [i.strip() for i in nodes.itertext()])


amazon_url = 'http://www.sumo.or.jp/'
base_url = 'http://www.sumo.or.jp/honbasho/main/hoshitori#east'
# headers = {
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#     'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36',
#     'Accept-Encoding': 'gzip,deflate,sdch',
#     'Accept-Language': 'ja,zh-TW;q=0.8,zh;q=0.6,en;q=0.4,en-US;q=0.2',
#     'Cache-Control': 'no-cache',
#     'Connection': 'keep-alive',
#     'Host': 'www.amazon.co.jp',
#     'Pragma': 'no-cache',
# }

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Host': 'www.sumo.or.jp',
    'Pragma': 'no-cache',
}

done_dict = []


def add_into_done_list(key_string):

    global done_dict
    done_dict.append(key_string)

    with open('output/done_lists.txt', 'w+') as f:
        f.write(key_string + '\n')

def save_total_record_json(data):
    ## save info into json
    with open('output/docs.json', 'w+') as f:
        doc_str = json.dumps(data)
        f.write(doc_str)


def parseHTML(data):
    tree = etree.HTML(data)

    # get east total record
    east_elements = tree.xpath('//*/div[@id="east"]/table[@class="main "]/tr')
    # print len(east_elements)


    #totalPlayer = {}
    totalPlayer = OrderedDict()

    # get EAST player name, rank, and total record with competitor
    for index in xrange(0, len(east_elements), 2):

        singlePlayer = {}

        playerInfo = east_elements[index].xpath('td[@class="player bBnone"]/div/dl')
        recordInfo = east_elements[index].xpath('td/img')
        competitorInfo = east_elements[index+1].xpath('td')


        if len(playerInfo) == 1:
            info = retr_list(playerInfo[0])
            singlePlayer['rank'] = info[0]
            singlePlayer['name'] = info[1]
            singlePlayer['record'] = info[2]
            # print info[0], info[1], info[2]

        #print singlePlayer

        # wbRecord = [i.get('alt') for i in recordInfo]
        # 白丸unicode = u'\u767d\u4e38'
        wbRecord = ['O' if i.get('alt') == u'\u767d\u4e38' else 'X' for i in recordInfo]
        singlePlayer['win_lose_list'] = wbRecord
        #print wbRecord


        # get competitor info and order
        comRecord = [i.text for i in competitorInfo]
        singlePlayer['competitor_list'] = comRecord
        #print comRecord


        totalPlayer["E" + str(index/2 + 1)] = singlePlayer



    # get west total record
    west_elements = tree.xpath('//*/div[@id="west"]/table[@class="main "]/tr')
    # print len(west_elements)


    # get WEST player name, rank, and total record with competitor
    for index in xrange(0, len(west_elements), 2):

        singlePlayer = {}

        playerInfo = west_elements[index].xpath('td[@class="player bBnone"]/div/dl')
        recordInfo = west_elements[index].xpath('td/img')
        competitorInfo = west_elements[index+1].xpath('td')


        if len(playerInfo) == 1:
            info = retr_list(playerInfo[0])
            singlePlayer['rank'] = info[0]
            singlePlayer['name'] = info[1]
            singlePlayer['record'] = info[2]
            # print info[0], info[1], info[2]

        #print singlePlayer

        # 白丸unicode = u'\u767d\u4e38'
        wbRecord = ['O' if i.get('alt') == u'\u767d\u4e38' else 'X' for i in recordInfo]
        singlePlayer['win_lose_list'] = wbRecord
        #print wbRecord


        # get competitor info and order
        comRecord = [i.text for i in competitorInfo]
        singlePlayer['competitor_list'] = comRecord
        #print comRecord


        totalPlayer["W" + str(index/2 + 1)] = singlePlayer


    # for keys, values in totalPlayer.items():
    #     print keys, values
    #     print "=" * 20

    # print len(totalPlayer)

    # print json.dumps(totalPlayer)
    return totalPlayer

def saveToFile(data):

    global done_dict
    filename = done_dict[-1]+'.html'

    print filename

    with open('output/' + filename, 'a+') as f:
        f.write(data)


def q(url):
    req = urllib2.Request(url, None, headers)
    resp = urllib2.urlopen(req)
    data = ungzip(resp)
    return data


def getData(url):
    req = urllib2.Request(url, None, headers)
    page = urllib2.urlopen(req) 
    return page.read()



######## Main Start ########

if __name__=="__main__":
    #reload(sys)
    #sys.setdefaultencoding('utf-8')

    ## set init
    queues = {
        'total' : 'http://www.sumo.or.jp/honbasho/main/hoshitori'
    }


    while len(queues) > 0:
        time.sleep(5)


        key, value = queues.popitem()
        print key, value


        add_into_done_list(key)
        data = getData(value)

        resultData = parseHTML(data)
        save_total_record_json(resultData)


        print 'Here has queues =>', len(queues)
        print '-' * 20

print '===== Done ====='
