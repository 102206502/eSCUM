#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import requests
from requests_html import HTML
import pandas as pd
import re
import urllib.parse
import threading



class PttBoardCrawleer(object):
    """docstring for PttBoardCrawleer"""
    def __init__(self):
        self.domain = 'https://www.ptt.cc/'
        self.key_words = [r'折扣', r'打折', r'優惠', r'特賣', r'特價', r'降價', r'免運']
        self.Life_key_words = [r'']
        self.block_words = [r'特賣會']
        self.month_period = 2 # 間隔?個月
        # self.max_post = 30

    def crawl_discount_info(self, boards, df_name):
        board_collected_meta = []
        for board_name in boards:
            start_url = 'https://www.ptt.cc/bbs/' + board_name + '/index.html'
            num_pages = 300
            board_collected_meta += self.get_paged_meta(start_url, num_pages)
        article_df = pd.DataFrame(board_collected_meta)
        article_df.to_csv(df_name+'.csv')
        # print(article_df)
        

    def fetch(self, url):
        response = requests.get(url)
        # response = requests.get(url, cookies={'over18': '1'})  # 一直向 server 回答滿 18 歲了 !
        return response

    def parse_article_meta(self, ent):
        ''' Step-3 (revised): parse the metadata in article entry '''
        # 基本要素都還在
        meta = {
            'title': ent.find('div.title', first=True).text,
            'push': ent.find('div.nrec', first=True).text,
            'date': ent.find('div.date', first=True).text,
        }

        try:
            # 正常狀況取得資料
            meta['author'] = ent.find('div.author', first=True).text
            meta['link'] = ent.find('div.title > a', first=True).attrs['href']
        except AttributeError:
            # 但碰上文章被刪除時，就沒有辦法像原本的方法取得 作者 跟 連結
            if '(本文已被刪除)' in meta['title']:
                # e.g., "(本文已被刪除) [haudai]"
                match_author = re.search(r'\[(\w*)\]', meta['title'])
                if match_author:
                    meta['author'] = match_author.group(1)
            elif re.search(r'已被\w*刪除', meta['title']):
                # e.g., "(已被cappa刪除) <edisonchu> op"
                match_author = re.search(r'\<(\w*)\>', meta['title'])
                if match_author:
                    meta['author'] = match_author.group(1)
        return meta

    def get_metadata_from(self, url):

        def parse_next_link(doc):
            html = HTML(html=doc)
            # print('html type:', type(html))
            controls = html.find('.action-bar a.btn.wide')
            link = controls[1].attrs.get('href')
            return urllib.parse.urljoin(self.domain, link)

        def check_month(date_str):
            now_time = datetime.datetime.now()
            # print('today:', now_time.month)
            date_arr = date_str.split('/')
            post_month = int(date_arr[0])
            post_day = int(date_arr[1])
            # print(date_str)
            too_old = False
            if self.month_period <=1:
                too_old = now_time.day - post_day > 31
                if now_time.month > post_month:
                    too_old = (now_time.day > post_day)
                else:
                    too_old = post_day - now_time.day > 30
            elif now_time.month >= post_month:
                too_old = (now_time.month - post_month >= self.month_period)
            else:
                too_old = now_time.month + 12 - now_time.month >= self.month_period
            # print('too old?', too_old)
            if too_old:
                return True
            else:
                return False

        resp = self.fetch(url)
        post_entries = self.parse_article_entries(resp.text)
        next_link = parse_next_link(resp.text)
        metadata = []
        old_counter = 0
        for entry in post_entries:
            meta = self.parse_article_meta(entry)
            # print(meta)
            for key_word in self.key_words:
                key_word = r'\[情報\].*' + key_word
                match = re.search(key_word, meta['title'])
                if re.search(r'Re:.*\[', meta['title']) or re.search(r'已結束', meta['title']):
                    match = None
                if match :
                    # print(meta['title'])
                    # print('折扣通知!')
                    metadata.append(meta)
            if check_month(meta['date']):
                old_counter+=1
            if old_counter >= 10:
                next_link = None
                print('stop crawling becausse information too old.')
                break
                
        return metadata, next_link

    def parse_article_entries(self, doc):
        html = HTML(html=doc)
        post_entries = html.find('div.r-ent')
        return post_entries

    def get_paged_meta(self, url, max_pages):

        collected_meta = []

        for page in range(max_pages):
            print('parsing page', page)
            print('page url:', url)
            posts, link = self.get_metadata_from(url)
            collected_meta += posts
            if not link:
                break
            url = urllib.parse.urljoin(self.domain, link)

        return collected_meta

    def crawl_all_info(self):
        eshop_boards = ['e-shopping']
        pc_boards = ['PC_Shopping', 'nb-shopping']
        life_boards = ['Lifeismoney']
        self.month_period = 1
        crawl_thread = threading.Thread(target=self.crawl_discount_info, args=(eshop_boards, 'discount info'))
        crawl_thread.start()
        crawl_thread2 = threading.Thread(target=self.crawl_discount_info, args=(pc_boards, 'discount info pc'))
        crawl_thread2.start()
        crawl_thread3 = threading.Thread(target=self.crawl_discount_info, args=(life_boards, 'discount info life'))
        crawl_thread3.start()
        print('mainthread jump out....')

if __name__ == "__main__":
    # ptt_boards = ['e-shopping', 'Lifeismoney', 'PC_Shopping', 'nb-shopping']
    crawler = PttBoardCrawleer()
    crawler.crawl_all_info()




