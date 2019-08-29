from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import re
import pandas as pd
import pttcrawler
import urllib.parse
import datetime

app = Flask(__name__)

# load your 'channel access token', 'channel secret'
line_bot_api = LineBotApi('channel access token')
handler = WebhookHandler('channel secret')
crawler = pttcrawler.PttBoardCrawleer()
last_crawl = datetime.datetime.now()
# global max_lines

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    is_crawling = check_crawl()
    query_type = check_message(event.message.text)
    discount_df = None
    if query_type == 'pc':
        discount_df = pd.read_csv('discount info pc.csv')
        re_msg = get_discount_infoes(discount_df)
    elif query_type == 'e-shop':
        discount_df = pd.read_csv('discount info.csv')
        re_msg = get_discount_infoes(discount_df)
    elif query_type == 'track':
        re_msg = event.message.text
    else:
        discount_df = pd.read_csv('discount info life.csv')
        re_msg = get_discount_infoes(discount_df)

    if is_crawling:
        re_msg += '新訊更新中...'

    line_bot_api.reply_message(
        event.reply_token, 
        TextSendMessage(text=str(re_msg))
        # TextSendMessage(text=event.message.text)
    )

def check_message(message):
    pc_info = r'(電腦|PC|pc|Pc|筆電|桌電)'
    life_info = r'(附近|超商|省錢)'
    match = re.search(pc_info, message)
    if match:
        return 'pc'
    elif re.search(life_info, message):
        return 'life'
    elif re.search(r'http', message):
        return 'track'
    else:
        return 'e-shop' 

def check_crawl():
    re_crawl = True
    cur_time = datetime.datetime.now()
    global last_crawl
    if cur_time.date() != last_crawl.date():
        crawler.crawl_all_info()
        last_crawl = cur_time
    elif cur_time.minute - last_crawl.minute > 4:
        crawler.crawl_all_info()
        last_crawl = cur_time
    else:
        re_crawl = False
    print(last_crawl)
    print(cur_time)
    print('重爬嗎?', re_crawl)
    return re_crawl

def get_discount_infoes(discount_df):
    discount_info = discount_df[['date','title','link']]
    re_msg = ''
    max_lines = 20
    for i in range(len(discount_info)):
        info_meta = discount_info.iloc[i,:]
        link_str = urllib.parse.urljoin(crawler.domain, info_meta['link'])
        re_msg += info_meta['date']+'\n'+info_meta['title']+'\n'+link_str+'\n'
        if i > max_lines:
            break
    print(re_msg)
    return re_msg

if __name__ == "__main__":
    max_lines = 10
    # discount_df = pd.read_csv('./discount info life.csv')
    # re_msg = get_discount_infoes(discount_df)
    cur_time = datetime.datetime.now()
    crawler.crawl_all_info()
    last_crawl = cur_time
    app.run()

