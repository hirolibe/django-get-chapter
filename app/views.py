from django.shortcuts import render, redirect
from django.views.generic import View
from apiclient.discovery import build
import datetime as dt
from django.conf import settings
import pandas as pd
from .models import ChapterInfo
import re
from django.db import models
from .forms import KeywordForm
import os
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import Flow


'''---------------------------------------
データベースに最新の動画のチャプター情報を追加
---------------------------------------'''

'''
変数の設定
'''
channel_id = "UC67Wr_9pA4I0glIxDt_Cpyw" # 両学長 リベラルアーツ大学
fromtime = (dt.datetime.now(dt.timezone.utc)-dt.timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ') # 24時間以内にアップされた動画から検索

'''
認証情報の設定
'''
YOUTUBE_API = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)

'''
チャンネルIDからVIDEOIDリストを取得する
'''
def get_videoid_list(YOUTUBE_API, channel_id):
    videoinfo_list = []
    nextpagetoken = ''
    while True:
        # チャンネルIDから24時間以内にアップされた動画情報をリスト化
        request = YOUTUBE_API.search().list(
            part='snippet', # 必須パラメータ
            channelId=channel_id, # チャンネルIDを指定
            maxResults=50, # 1回の試行における最大の取得数
            publishedAfter=fromtime, # 動画がアップされた期間
            type='video', # 動画タイプ
            regionCode='JP', # 地域コード
            order='date', # 日付の新しい順
            pageToken=nextpagetoken, #ページ送りのトークンの設定
        )
        result = request.execute()
        print(result['items'])

        # もしも動画数が50件より少ないならば、dataに情報を追加してbreak
        if len(result['items']) < 50:
            for i in result['items']:
                videoinfo_list.append([i['id']['videoId'], i['snippet']['publishedAt'], i['snippet']['title']]) # videoinfo_list = [[videoId, publishedAt, title], [videoId, publishedAt, title], ...]
            break
        # もしも動画数が50件より多い場合はページ送りのトークン(result['nextPageToken']を変数nextpagetokenに設定する
        else:
            for i in result['items']:
                videoinfo_list.append([i['id']['videoId'], i['snippet']['publishedAt'], i['snippet']['title']]) # videoinfo_list = [[videoId, publishedAt, title], [videoId, publishedAt, title], ...]
            nextpagetoken = result['nextPageToken']
    return videoinfo_list

'''
VIDEOIDリストで得た'description'からチャプター情報(配信日、開始時間、タイトル)を一つずつ抽出
'''
'''
def get_chapter_info(videoinfo_list):
    chapterinfo_dicts = {}
    # 'description'の文字列を取得
    for videoinfo in videoinfo_list:
        request = YOUTUBE_API.videos().list(
            part='snippet',
            id=videoinfo[0],
        )
        response = request.execute()
        # print(response)
        chapterinfo = response['items'][0]['snippet']['description']
        # 'description'から開始時間とタイトルを抽出
        pattern = r"(\d{1,2}:\d{2}(?::\d{2})?)\s(.+?)(?=\s|$)" # 開始時間とタイトルを抽出する正規表現パターン
        matches = re.findall(pattern, chapterinfo) # 正規表現でマッチした'description'内の開始時間とタイトルを全て取得
        chapterinfo_dict = {}
        for match in matches: # matches = [(00:00, チャプタータイトル), (0:00:00, チャプタータイトル), ...]
            title = match[1]
            time = match[0]
            time_parts = time.split(':') # 文字列を時と分と秒に分割
            time_length = len(time_parts)
            if time_length == 2: # 分と秒のみの場合(00:00)
                time_value = int(time_parts[0])*60 + int(time_parts[1]) # 秒数に変換
            else: # 時と分と秒の場合(0:00:00)
                time_value = int(time_parts[0])*3600 + int(time_parts[1])*60 + int(time_parts[2]) # 秒数に変換
            time_str = str(time_value) # int型から文字列に変換
            chapterinfo_dict[title] = time_str # chapterinfo_dict = {チャプタータイトル: 秒数, チャプタータイトル: 秒数, ...}
        chapterinfo_dicts[videoinfo[0]] =[videoinfo[1], chapterinfo_dict, videoinfo[2]] # chapterinfo_dicts = {id: [配信日, {チャプタータイトル: 秒数, ...}, 動画タイトル], ...}
    return chapterinfo_dicts
'''

def get_chapter_info():
    chapterinfo_dicts = {}
    videoinfo_list = ['F1fSllK0-uU', 'M4YjVaZQ1uo', 'wTxHqW8TeC8', 'H1833LNDtqo', 'oYmdhvLYdrY', 'Fgl6hqnlIy4', '3FTXE5qWrwI', 'TskDMq079gE', 'MFZglEo0dC8', 'ufX_dEZodnY', '1NE-JzfpZyY', '3j4kGNaj0n4', 'Hs-iaW6ThXU', 'bQ7Vr6dgTLM', '8N96qzaImio', '_y_6FYlNfpU', 'I7uyCRC4qkA', 'LHzhdpLtmyI', 'SMpaTY7-6EI', 'iglACLas2m4', 'cymB46EbbPM', '1SNL0dKh2Qc', '-tA_XfnI4XA', 'Jd18DNCiDtg', 'UPTIBIJl8Q8', 'CwB7jn_JWQM', '0mxdCf439_Q', 'm1fIl0rWyVo', 'xg3o4e5IoTM', 'lyDxTBRDxcg', 'BIf8n_scP1A', 'ry2UBq69xS8', 'xUbfj7q_iLY', 'Rg2c7TMbWuI', '8vdaGArGDCY', '2nnlWM3DB40', 'OdfQwsHHNac', 'qo2qCVN-nj8', 'GNRb-yXcI9o', 'UxH4MLOqTrg', 'tRfeJXImhpo', 'Mx12uqlmqp4', 'fltsarxiAbI', 'sqJBWOD1jss', 'zgqLcy4UEmY', 'dBhtyFZ0fKQ', 'wvSPFC5iLZI', 'nywRfcyTjoE', 'OgoR-CSvsbo', 'XUWkbqC8_GU', '69u-pE8VbXM', 'ijCysVPNbxg', '1XOBW-foQoA', 'gYgCeBhRXEs', 'QOOU8TCIGA0', 'gMPo8Uu2IxY', '1L3noQGcy1I', 'CVjJpZiwFQg', 'fhd0dd-m49U', 'dPtl6JYXJ0', 'QHHZFm_E7Ts', 'b21YoiJGsGE', '2LkfEZZYk2g', 'jRX77MJSkaQ', 'dg0wzt0Hask', 'FtnzKYJ6R-4', 'qQSnzPwZZfc', 'qUC5FkKcahs', 'yknkX-PZWJ4', 'uu2P00q6ouk', 'jYwK6Njt1uE', 'x9rSO4dJTmo', 'r-XJAwnNNco', 'JZ-8cKcWjBQ', 'P5vj6y2x-UE', 'eqwcrhi95Io', 'rijSPBCvkcc', 'bV2AfB3Qg6k', 'zA7vhqwZHKs', 's-3xcSFHguM', 'O3CvGnTbGJM', 'd3wtd0yFBUA', '80_L_07Uvzg', 'tm42zumaYm8', '2BGTXUXZA7s', 'V4CyiMTLhrk', '09HT4ED8jog', 'vpiVXQ5JJUE', 'Qh9JeCuTth8', '2Tx5UCcacgs', 'c_0HAe8h7ag', 'Ts_Kz0ukc8w', 'zcfHt9RS0oY', 'Yk89ER9yr80', 'JaSko2ika3Q', 'MCdVD54HjdY', 'uiObbqI7Hdw', 'RV2e94YG2xc', 'dZBPAsMXLJo', 'xg0xOu3RyDE', 'ReeNHrmCCU4', '6dWZuF30J8Q', 'cEby5nl49uo', 'QokEo5bTz1Q', 'SnXl7F47E5E', 'm96mCOjMGGE', '05cU-setvWI', 'l-dj0ESUyoQ', '4zEMw5dhWzo', 'a-Lo6AfkFbo', '5Q6Iu8WhaHo', 'XS8m9ZcSh-g', 'JfmWQ6dCEFw', 'DGHqPghpnT0', '77hJVNt7EM0', 'MZOCPjW6moE', 'dJBAY7nDxxQ', 'j6Z3tKyIoKQ', 'okXiJOCwUSc', '6AIvwugmg4I', 'c9ETOniWeYg', 'MJq6flrBffQ', 'i5wHNbMPvOE', '-tf5en5qWgk', 'T5Z1ZdtI9ms', 'KKT3VDeUeQo', 'jintLg-8_PU', 'INbyO6FU11Q', '2Ky9VO-8TzE', 'lagvX4mgyAo', 'HBAzsLIuoNo', 'l-KJlm9nekc', 'Ai29o8ekd5w', '7Ur_epUiI94', '25FmpWFoUIo', 'WCQKX6UwMU4', 's7hhi5H-m2Y', 'fMo-WI3Ukr0', 'kPvWoHKcR_k', 'eY6XHeOEnfc', 'W7yQRFaCCFQ', 'g_h_4QGHHoE', 'yCzvrNFHIYs', '2B8NdAZY5Y4', 'wodj3Rt73cM', 'QhhfEiVkGtM', 'Mz8lvEYNpBU', 'tqgW1tX1nRw', 't2kKEU-JA8Q', 'Sd6ZbjIPydY', 'j9FJTXW5njE', 'p0J4pY4B4nc', 'd2N6F9egOb8', 'LTijn12lBOg', 'r9n9jk6Fna8', 'dFjGU1_HLhs', 'VnwpgU-fAiU', 'uet-AP7bJLE', '4vmkCcsSXgs', 'kkeJyPr_c6E', '7DadsS3ipDA', 'JhIGYkSjp64', 'ChA21RKXeE0', 'gP-ZHf3S10Y', 'JBefXUYNuto', 'YNFUpJ_RKpQ', 'JMnDQJF2oLk', 'Q-m6Cd93mz4', 'DzBPVRO0Dyc', 'V93BklfRGq0', '0cavSp_ilFw', 'x3Wi7ScawsE', 'Doqg7l1RmPU', 'kHOE6qkqLko', 'sKmU_FAqFeo', 'edZ8YR_x4sE', 'cEpRW4oQZqE', 'hgHuZmaQqB0', 'hY-1yuT0Tvo', 'YVB2OqRw04A', 'I3crSTaBIiI', '0jUBk55NotI', '8W4pZLh1IAQ', 'OAQ_n4mKpBM', '4sXmJUZcDHA', 'rdiUa2EssXU', 'GFPLMOtuAjo', '6M5eCkozBDE', 'xLQp0FDMRvM', 'k02UmZJ1L6c', '7gmoWZC-vWo', 'LnqKFedEDrE', 'sGK55X44VXQ', 'qRXkeKIdQJ8', 'fIUi1P9-63Y', 'R3-YdScvDX8', 'KyLSaU0k49w', 'LH5rb8w72-o', 'hKVbFnjfkAk', 'w93YAuHiTzM', '9jdSHjUluCA', 'qiTTlIp5r-o', 'wctwpaybghg', 'UDCVz4hzTYw', '5aAewZfVORE', 'R4fk4GfY63U', 'NPZX3AFVVc4', 'rzaU9f4TEP8', 'uh9jC9fNsak', 'GWCky9RrHqk', '8S7osyQL9io', 'qD8RogYuj1s', 'FJNarEVTNGI', 'c_qQkuvlipc', 'BPvUX3AK_kI', 'Ng3dJ5A1pho', 'kmOKE28mWHo', 'RQ6_CnZqQ2s', '911RMzG6mJk', '7Wcv7GZLkXw', 'UfYJmAQ6klA', 'H9QzzActRuM', 'x-j7oH9JtGI', '1ditHW0njvM', 'om9kjCcUnQA', 'vEhZpTmmj3Q', 'YXA-wQ4klnY', 'zBvkz2yoG6k', 'bE7rM4C25nA', '8t3aqIDTM54', 'aZHfw7gyAVU', 'VK3n_XHMMZc', 'sxaRbw2V9DM', 'JqDUTCFZwDI', 'VbZkjmMYpuw', 'Ewva0SaQgtw', 'tAgSI8_Ox1o', 'Qty2aQDz198', 'dQ2fOgJdMyg', 'H5nhcE_A7lQ', 'ohQY-Uhck9k', 'w-NRdAuCTs0', 'Xpe5wVHoHTA', 'Tmib6AStTxU', 'hapkxvPNQGI', 'Y2HbJijIprA', 'u9QylntFfdY', '7NJBiq5jiHQ', 'O5HXXLJCqIk', 'vVNRazY66XE', 'U1vTpfMBA5Q', '3ZgsyOL7G_c', 'myhvGtVvMto', 'qkSf6_XdZug', '89irzNLkMGg', 'W8wQP4UqcCw', 'Sev0nq4HR0M', 'hw-QU-0RDN8', '04jtbLfGr6o', '4dakScl_V20', 'm1pfNDhLMKw', 'HviLag1AC1U', 'jyld3SoY6uw', 'tul6DZT5vkw', 'Q0KbfaGuVxY', 'mvM6S2orKPg', 'RI4jGWKl_lk', 'ACLynAsRd58', 'CbUni7wo1cE', 'XKcfvNYBLaM', '2rVancfwJ78', 'hMH1ZpGSylM', '3HjTGupbNNQ', 'aWv3U4FfoiQ', 'zGq90aDgXws', 'XGzCZoXIOCo', '9kEwTgf5KKw', 'yf5m4zmkC4g', '3FRTcg1Z9pk', 'hAhzmx5WfcQ', 'b4QjHsUpcqo', 'np_QEe4AD5M', '3u1vFjcwT_A', 'liJ_IT1rY9c', 'VhSmCUB4UYg', 'g4dNSDrgRBA', '8FYQ9hzLhdc', 'sWiz_PTylmc', 'XLEq1-kS2w8', 'R98T86zicTQ', '13nRJH-LJRM', '2LiMs00-upo', 'S7ycURDm7jM', 'ry_14xW-QwU', 'OFjNR6pmieg', 'HRead--srTA', 'iok_XyEJOLA', 'oIIcjnW0gKY', 'LfxwsFa-3jI', 'pCQrL4EuahU', 'XAH5ibRXTdY', 'WEhCZ0uPBKI', 'VUtYs47xK4U', 'tSB3M5x2elQ', 'E_F5UD7s2hE', 'bpMzr4SI2TY', 'ZLZa-RiUbms', '1upX-qw71Mk', 'N6rTcqWSLo0', 'l9C5G8QDIrw', 'NpSm5_ioszU', 'WDP91SglCrs', 'E8M3nAdgokU', 'vyI7ed0DH4M', 'WDWGwNkrc-I', 'dmMQGhIV_yw', 'jHeq2iRGTz8', 'uGAN-uPyynA', 'E53vR9CUrc8', 't1a5eTfSKsw', 'oZhBWA3HNhA', 'VIxp0b6rDZ8', 'Z27ZP4QCYkg', 'RT2DzUzQY5k', 'l6emTng5io0', 'tnWiMYYux3U', 'yB8Cg_4ABKk', '2dP8SH23htc', 'E-JzWjohews', '6eETHdrpBPo', 'ymtQ9fOKddI', 'G_7sBX6-ADA', 'YJ1i-JGSXK0', 'hkeyPZhI7Do', 'MTATSdiVbPk', 'PDET6ACgKa0', '5kgl6ZNL4zM', 'BkIf6Sl6Pqk', 'b3Uow6rq4vU', 'HiJvep7qicE', '2uLoz-7JSeI', 'RpjEN8yRick', 'Q87oxhkCAQ4', 'In2eWB9I3NM', 'mWvbB1_XDIo', 'qQ0r9grSEH0', 'GnFs7yzrr54', '4RM0px8Lmrs', 'qJaAvrZCOZc', '0rMewA8b8Oc', 'SgakPnYuwY0', 'o3d073xbWvY', 'U2VuEutZAvs', 'R1rpKrF8igI', 'JS11vR-c9-c', 'oFDY_IrYBR0', 'HTabN_kdCXA', 'v-JylINFCU8', 'avZgcFhBWOE', 'uGRTByvpZqE', 'udMJP28kM5o', 'afyVrcrlzwg', 'HygrxZH7k6g', 'Vn-ET78dF78', 'LcBPBju8TdU', 'bdCbHC5qlgQ', 'hgtT6w56VDw', 'GfqMAA9uDOU', 'i_YMGETs3No', 'eeJLk6BQaCE', 'vikTx4rrv9Y', 'QrmAtAOx5qk', '7YCI8PGfDIM', 'hIvMkM6y21M', 'Xq9pXQaz4yw', 'mv7_c557_RI', 'Ned1zW4J0-4', '28PgQ1lDS4w', 'JDsCDETUJwo', 'C-76_s7Uj3U', 'CmpbQDrHfJg', 'O6n5ce2ws_8', 'YarzJGBwrVc', 'XjdnIJkIDJo', 'BqJp9oZomUo', 'sZMBvgvI7B4', 'A51WVDSU4CM', 'XuJti6Y7fU8', 'dxJj81uVnck', 'gUYkIcGrmpQ', '295yCiyih0c', 'dJmcdt_eH-Y', 'S-LqMGZ2Mn0', 'DedNCDcZFXU', 'E4SA4xmcq44', 'Fs6d94lnyjQ', 'UVKshfW-Cis', '995Skk_jvTQ', 'ULXXjh3sIJ0', 'VO71cAGk-Qk', 'krAwZT95vaY', 'QKuHDc13Blk', 'KwqvqriFUGU', '0wGxu0hZ_pE', 'IQ-to3vrTR8', 's6N0afL81YY', 'wFFLgNMj1Wc', '6E9egsXcaO8', 'yR07fs5ODfY', 'GxN_UUyea0g', 'n4QtoHN6qYk', 'cI1k0ZNwoK8', 'b4Eb8_cUWZQ', '5khJ7_wPH4g', 'sZltlZHQ6GA', '7frekM7HLC4', 'Vv9OVURjluk', 'Ipn6fihZ3pg', 'XJJ2cOa4cFA', 'cIa3i6SurKA', 'kMC1ngLO-n4', '70IMrSQSMoA', 'GKMxz2uILMc', 'hbNsElknMBA', '4SQOlLo1Kv4', 'UZ5NfCU839Y', 't4Y_BwKSd2Y', 'Lo65gMbqBt8', 'FzoqaujQHNk', 'HzSzfO7nezA', 'ls7e3qrpSyA', 'ZUBYyPVymHk', 'yeCxg2UOfbk', 's7p5Z52Rw18', 'vI8-SJPMJj0', 'nw7LMMkp02U', 'f3wpwlkfY3w', 'K0MCNzGe_dA', 'lZaz_9OC8-U', 'r_CseE36cGw', 'iD242qMnMqA', '7PyJV3Ew3a0', 'm_Zn7LDZCg', '7-UKDKA1Up4', 'Na8hbacGglg', 'aX_dZj7YfpU', 'W7ackdumhP4', 'rKqk9LDP29M', 'l4JyQCJUe-M', 'NQiW-S7v7Jo', 'fgMGyowbvuc', '74EzFuW8HIc', 'k1TB7bUPVEk', 'xlLw5vj_oow', 'ql0OnWgGvO0', 'W2udiX7WhS4', 'bYeRe8JEbDE', 'qV-eDdaYk98', 'bEpN6Dc_cdQ', 'nJP_d5TVkbY', 'joZlW0tvtJg', 'x6O4ZSFiXlc', 'hYOyVHsPesM', 'MFLTzBxA7dM', 'Gnwry2WhvDI', 'BACkv8c8dGc', 'sqRwUD-nqlw', 'JOdzi1ZJJ8c', 'g5UBEwvtiHs', 'cLm0cTopax4', 'PAchrH52Aus', 'LIeShGmirYA', 'RLIFJHzmNJ8', '1rlhuuXiqf8', '8rx17Xt0mBk', 'Z_48rH-BwNo', 'zth8eUx41Ro', 'dayY6T8yUTM', 'ziSp0U-JhMU', 'mVQotz-3a2Q', 'i_6BUe7dIdI', 'CfAea6EQia4', 'gfsIKyKhHww', '8N9r1f1lAWs', 'cnJDTnj1PtE', 'Bh2qm6shJfE', 'MwOdeSf1At4', 'BudqjfeWQLw', 'mKMHCak9JQ8', 'vw62kF_j9c8', '837Oi6WSZsw', 'KsVRr9VbDB0', '_tJM-2GEKLo', 'q48TbeHz3Hk', 'PHNSe60smxY', 'gIO5Skf39NA', 'kbRPUlQpT8s', 'JcA5FM0ZBtc', '1WjJkDI6z2w', 'OhyODohDdCk', 'BncUNN4J_Sk', 'XG4uEGKFgGU', 'XpCaiVzPc6g', '2NAVXXCdg_A', '9CWub6YQCv8', 'Xr8ptUTbRFM', 'our3O934Kuo', 'rpf4dIB7_Js', 'JwIYtLmdRZI', '_WaBcSCYvOk', '9YO0k-sbuOA', 'PATC0m2YShw', 'HYQXENuekx8', 'I3N9Rv8aTww', 'yevotIPWsQU', 'XfS66uekspg', 'PnDpsnbwPGI', 'XaChkFR76JI', '9hLcq-vIPyY', 'JotuzG8t83c', 'yO-mWA-I1J8', 'nboOw8GFzJQ', 'kZ5Y34HG4co', 'cHSj_3o7RjI', 'Sp_I-N8dXHY', 'njRnuWiEJSc', 'QfNZ2HUAFVg', 'NuoNMmkWA_k', 'jRC8NRnBaiI', 'EY9ZXaktHvs', 'Y0x6fzH1iuc', 'xlBUvbllmFU', 'ZYHC8NPNTpc', 'd-Q-ujiqmA4', 'TTc_EnVLM-o', 'a0ic4H_QLt8', 'ez4Nrj_qC-Y', '2NPRXSFeXuE', 'rXJtvcM_zIM', 'gjrpcy6hDeo', 'AS8-AmOJEZc', 'B69hLmmjC-w', 'iGWrvjX4ZwA', 'QiMioZkp2Fw', '9zjZQLKuaPE', '-LWRuW5_piw', 'nskwK27L62Y', '3C7hjghqiqA', 'govIt4ATPd4', 'd-KNzJOlaHs', 'yRv5Yn8nkxg', 'gVTJAF8jGdg', 't5g4M38Qmn0', 'QQUYQJ7l1HM', '5DuO6j5n6kw', 'pK7TSHArAXc', '51suEFqrfgA', 'rEIm2KVpYI8', 'yanxI8CRNLQ', '0P2hJZ7SWIY', '1lkh7O9KApQ', 'PtDQzwsijLA', '6hfTtfNG-MY', 'r3147RhA64g', 'ptX_sYDlDL4', 'T5EKchaKTdo', 'bgVIrPuJU2E', 'H1txlq8FQfk', 'obHl6RCdDxU', '0s0YrjSCwpE', 'K_IQlWUfLnE', 'tEpUr9mmSGA', 'zDiFYM8pBMI', 'T9ZrUzVBq2s', 'hDKvE-BgovA', 'pWQzOfMFnVY', 'JzIIhzLu_nU', '7CyPhUIWlK0', 'kpM67Brc4ik', 'F_aASWUjOSk', 'C4Dc-tvj8Y4', 'k9Hcvh02a8o', '6fcvnKOm11I', 'Ot3_SRZKGBs', '_X_u-nBE7H0', '0Enrv15vd1s', 'x2lcHCmNl0A', 'YcgPCjl_cVg', 'SYBD7oY4res', 'YFty8Q6cGwg', 'De1eg-ErkpI', '4Yu21BkK1vI', 'qsaSSqdOfU0', 'E77VH0hCCfU', 'qbQdQaEzvGk', 'OUUt998DVWE']
    for videoinfo in videoinfo_list:
        request = YOUTUBE_API.videos().list(
            part='snippet',
            id=videoinfo,
        )
        # print(videoinfo)

        response = request.execute()
        # print(response)
        if response['items']:
            chapterinfo = response['items'][0]['snippet']['description']
            publish_date = response['items'][0]['snippet']['publishedAt']
            video_title = response['items'][0]['snippet']['title']
            # 'description'から開始時間とタイトルを抽出
            pattern = r"(\d{1,2}:\d{2}(?::\d{2})?)\s(.+?)(?=\s|$)" # 開始時間とタイトルを抽出する正規表現パターン
            matches = re.findall(pattern, chapterinfo) # 正規表現でマッチした'description'内の開始時間とタイトルを全て取得
            chapterinfo_dict = {}
            for match in matches: # matches = [(00:00, チャプタータイトル), (0:00:00, チャプタータイトル), ...]
                title = match[1]
                time = match[0]
                time_parts = time.split(':') # 文字列を時と分と秒に分割
                time_length = len(time_parts)
                if time_length == 2: # 分と秒のみの場合(00:00)
                    time_value = int(time_parts[0])*60 + int(time_parts[1]) # 秒数に変換
                else: # 時と分と秒の場合(0:00:00)
                    time_value = int(time_parts[0])*3600 + int(time_parts[1])*60 + int(time_parts[2]) # 秒数に変換
                time_str = str(time_value) # int型から文字列に変換
                chapterinfo_dict[title] = time_str # chapterinfo_dict = {チャプタータイトル: 秒数, チャプタータイトル: 秒数, ...}
            chapterinfo_dicts[videoinfo] = [publish_date, chapterinfo_dict, video_title] # chapterinfo_dicts = {id: [配信日, {チャプタータイトル: 秒数, ...}, 動画タイトル], ...}
        else:
            pass
    return chapterinfo_dicts

'''
チャプターの開始時間を抽出して動画URLを作成
'''
def get_chapter_url(chapterinfo_dicts):
    data = []
    for id, chapterinfo in chapterinfo_dicts.items(): # chapterinfo_dicts = {id: [配信日, {チャプタータイトル: 秒数, ...}, 動画タイトル], ...}
        for chapter_title, time in chapterinfo[1].items(): # chapterinfo = [配信日, {チャプタータイトル: 秒数, ...}, 動画タイトル]
            published_date = chapterinfo[0]
            # ISO 8601形式の日付文字列をdatetimeオブジェクトに変換
            published_date_jp = dt.datetime.fromisoformat(published_date.replace('Z', '+00:00'))+dt.timedelta(hours=9)
            # 必要な形式の文字列に変換
            formatted_date = published_date_jp.strftime('%Y-%m-%d')
            url = f'https://www.youtube.com/embed/{id}?start={time}'
            data.append([id, chapterinfo[2], chapter_title, url, formatted_date, time])
    df_data = pd.DataFrame(data, columns=['ID', '動画タイトル', 'チャプタータイトル', 'チャプターURL', '配信日', 'チャプター開始時間'])
    return df_data

'''
データベースをアップデート
'''
def add_database(df_data):
    for index, row in df_data.iterrows():
        chapter_data = ChapterInfo()
        chapter_data.video_id = row['ID']
        chapter_data.video_title = row['動画タイトル']
        chapter_data.chapter_title = row['チャプタータイトル']
        chapter_data.chapter_url = row['チャプターURL']
        chapter_data.published_date = row['配信日']
        chapter_data.chapter_start = row['チャプター開始時間']
        chapter_data.save()

'''
メインコード
'''
class UpdateView(View):
    def get(self, request, *args, **kwargs):
        # videoinfo_list = get_videoid_list(YOUTUBE_API, channel_id)
        # chapterinfo_dicts = get_chapter_info(videoinfo_list)
        chapterinfo_dicts = get_chapter_info() # video_id直接入力
        df_data = get_chapter_url(chapterinfo_dicts)
        add_database(df_data)

        return redirect('index')


'''---------------------------------------
データベースからチャプタータイトルをキーワード検索
---------------------------------------'''
class IndexView(View):
    def get(self, request, *args, **kwargs):
        form = KeywordForm(
            request.POST or None,
            initial={
                'search_start': dt.datetime(2021, 11, 8),
                'search_end': dt.datetime.today(),
                'items_count': 30,
            }
        )

        return render(request, 'app/index.html', {
            'form': form
        })

    def post(self, request, *args, **kwargs):
        form = KeywordForm(request.POST or None)

        if form.is_valid():
            keyword = form.cleaned_data['keyword']
            search_start = form.cleaned_data['search_start']
            search_end = form.cleaned_data['search_end']
            items_count = form.cleaned_data['items_count']

            chapter_all_list = ChapterInfo.objects.order_by('-published_date')
            chapter_search_list = []
            count = min(len(chapter_all_list), items_count)
            for i in chapter_all_list:
                if count > 0:
                    if search_start <= i.published_date <= search_end:
                        if keyword in i.chapter_title:
                            chapter_search_list.append([
                                i.video_id,
                                i.video_title,
                                i.chapter_title,
                                i.chapter_url,
                                i.published_date,
                                i.chapter_start,
                            ])
                            count -= 1
                else:
                    break
            chapter_search_df = pd.DataFrame(chapter_search_list, columns=[
                'video_id',
                'video_title',
                'chapter_title',
                'chapter_url',
                'published_date',
                'chapter_start',
            ])

            data = chapter_search_df.to_dict(orient='records')

            return render(request, 'app/keyword.html', {
                'keyword': keyword,
                'data': data,
                'keyword': keyword,
                'search_start': search_start,
                'search_end': search_end,
                'items_count': items_count,
            })

        else:
            return redirect('index')


'''---------------------------------------
プレイリスト作成
---------------------------------------'''
'''
メインコード
'''
class KeywordView(View):
    def post(self, request, *args, **kwargs):
        form = KeywordForm(request.POST or None)
        if form.is_valid():
            keyword = form.cleaned_data['keyword']
            search_start = form.cleaned_data['search_start']
            search_end = form.cleaned_data['search_end']
            items_count = form.cleaned_data['items_count']
            my_channel_id = form.cleaned_data['my_channel_id']

            chapter_all_list = ChapterInfo.objects.order_by('-published_date')
            chapter_search_list = []
            count = min(len(chapter_all_list), items_count)
            for i in chapter_all_list:
                if count > 0:
                    if search_start <= i.published_date <= search_end:
                        if keyword in i.chapter_title:
                            chapter_search_list.append([
                                i.video_id,
                                i.video_title,
                                i.chapter_title,
                                i.chapter_url,
                                i.published_date,
                                i.chapter_start,
                            ])
                            count -= 1
                else:
                    break
            chapter_search_df = pd.DataFrame(chapter_search_list, columns=[
                'video_id',
                'video_title',
                'chapter_title',
                'chapter_url',
                'published_date',
                'chapter_start',
            ])
            data = chapter_search_df.to_dict(orient='records')

            # 認証情報の設定
            flow = Flow.from_client_secrets_file(
                settings.CLIENT_SECRETS_FILE,
                scopes=['https://www.googleapis.com/auth/youtube']
                )
            # 認証コードを受け取るためにリダイレクトされるポートを指定して、認証フローを実行
            authorization_url, state = flow.authorization_url(
            access_type='offline', prompt='consent', include_granted_scopes='true')
            # ユーザーに認証してもらう
            print("Go to the following URL and authorize access:")
            print(authorization_url)
            # ユーザーが認証した後、リダイレクトURIで提供された認証コードを取得して認証フローを完了
            flow.fetch_token(authorization_response=input("Enter the authorization code: "))
            credentials = flow.credentials
            youtube = build('youtube', 'v3', credentials=credentials)

            # プレイリストの作成
            request = youtube.playlists().insert(
                part="snippet",
                body={
                "snippet": {
                    "channelId": my_channel_id,
                    "title": keyword,
                }
                }
            )
            response = request.execute()
            playlist_id = response['id']

            for row in data:
                #プレイリストに検索した動画を登録
                request = youtube.playlistItems().insert(
                    part="snippet",
                    body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                        "kind": "youtube#video",
                        "videoId": row.video_id,
                        }
                    }
                    }
                )
                request.execute()

            return redirect('keyword')

        else:
            # フォームのエラーをここで処理する
            pass
