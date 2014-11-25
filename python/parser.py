# -*- coding: utf-8 -*-
import re, os, sys

from lxml import etree

import robotparser #for check a wbe page can be fetched or not
from urlparse import urljoin #for combine the link
import urllib, urllib2, httplib, socket
from urllib2 import urlopen,Request
import urlparse
import time  

import json


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

    with open('output/done_lists.txt', 'a+') as f:
        f.write(key_string + '\n')


def parseHTML(data):
    tree = etree.HTML(data)


    # get east total record
    east_elements = tree.xpath('//*/div[@id="east"]/table[@class="main "]/tr')
    #east_elements = tree.cssselect('div.east table.main')

    print len(east_elements)
    for x in east_elements:
        print x


    # get west total record
    # west_element = tree.xpath('//*/div[@id="west"]')

    return True

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
        #saveToFile(data)
        parseHTML(data)

        print 'Here has queues =>', len(queues)
        print '-' * 20

print '===== Done ====='
