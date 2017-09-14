#! /usr/bin/python3
#coding:utf-8

#  修改自：
#  免登录下载微博图片 爬虫 Download Weibo Images without Logging-in
#  https://github.com/yAnXImIN/weiboPicDownloader

import os
import requests
import json

NICKNAMES_FILE = 'weibo_nicknames.txt'

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

def get(url,stream=False,allow_redirects=True):
    print(url)
    return requests.get(url=url,headers=HEADERS,allow_redirects=allow_redirects)

def save_image(nickname,url):
    save_path = os.path.join('WeiboAlbum',"WeiboAlbum_" + nickname)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    image_path = os.path.join(save_path,nickname+'_'+url.split('/')[-1])
    if os.path.isfile(image_path):
        print("File already exists: " + image_path)
        return
    response = get(url=url, stream=True)
    image = response.content
    try:
        with open(image_path, "wb") as image_object:
            image_object.write(image)
            return
    except IOError:
        print("IO Error\n")
        return

def get_urls(containerid,page):
    url = "https://m.weibo.cn/api/container/getIndex?count=25&page={}&containerid={}".format(page,containerid);
    resp_text = get(url=url).text
    json_data = json.loads(resp_text)
    cards = json_data['cards']
    if not cards:
        return None
    photos = []
    for card in cards:
        mblog = card.get('mblog')
        if mblog:
            pics = mblog.get('pics')
            if pics:
                photos.extend([pic.get('large').get('url') for pic in pics])
    return photos

def nickname_to_containerid(nickname):
    url = "http://m.weibo.com/n/{}".format(nickname)
    resp = get(url,allow_redirects=False)
    cid = resp.headers['Location'][27:]
    return '107603{}'.format(cid)

def read_nicknames():
    nicknames = []
    with open(NICKNAMES_FILE,'r',encoding='utf-8') as f:
        for line in f:
            nicknames.extend(line.split(' '))
    return nicknames

def handle_user(nickname):
    cid = nickname_to_containerid(nickname)
    if not cid:
        return
    all = []
    page = 0
    has_more = True
    while has_more:
        page += 1
        urls = get_urls(containerid=cid,page=page)
        has_more = bool(urls)
        if has_more:
            all.extend(urls)
    count = len(all)
    index = 0
    for url in all:
        index += 1
        print('{} {}/{}'.format(nickname,index,count))
        save_image(nickname,url)
    pass

def main():
    for nickname in read_nicknames():
        handle_user(nickname)

if __name__ == '__main__':
    main()