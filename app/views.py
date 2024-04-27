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
    videoinfo_list = ['rbg3CyTpyUA', 'pFoNvWd-h-c', 'oXPWp7kdjIw', 'jdThmrwWHtQ', 'E5lUqqXRINc', 'n2ke-NCJ4PM', 'sBQuBlmwXAA', 'eQM1gHF-olo', '-pgyKzqqSMg', 'l5ZHAtk9fSQ', 'Z2xskiiuyAA', 'X9yvsN9mOgI', 'IHB1mYftdww', 'ym6e7iaRS7Y', 'Gog1u82CpyE', 'dIT1Zd4mAGY', 'pY_QOwpnIWw', '2YfytpztR7o', 'A24QVPDuAtk', '95PO4mcYAZ8', '3da5mIYelVE', 'NMOY2evqaVo', '2CKF5uwLqxw', '0UCsHegUxAY', 'SchAuHzpPDY', '2pFSRxqjFrk', 'LxipEVGwZsA', 'VDAO5jYwCj8', 'tX3L5ll4n3s', 'v7zXtr2NXDw', 'dOiFlRehg5E', 'a_fmaXqXqK0', 'WW-ElJzeHD0', 'j9oL2PuUPAw', 'cTWARMPElak', 'r9lRCeBV0SY', 'PHMKnjA3Mok', 'gZ8YwTpgACA', 'FhmfrPd0U4k', '9N_HIbwg_g8', '7N0N8Elj9AQ', '9xdSLGzUQzg', 'JOjEWY3nttY', 'ORDcVpRbklQ', 'spTge9Ww4uw', 'uxLr-RupKmg', 'HV-uJZVlLeQ', '6DiPBtmFL0E', 'u62E9DAzDHU', '7Fbq7t5l9N4', 'Sskeu9YVpXc', 'KTbUmUh5l-k', 'x4BguGnlIqE', 'A-63yOiKL4c', 'BqUVjyB19Ro', 'Dm0r51qJCg8', '1uMJmeeB-ik', 'JSRUoLjICgw', 'oVqKe4pbQCU', 'fZi822V1h48', 'oVatxIKEF-k', '368pK7hcMz8', 'SBZBkdkIBBY', 'zYO8KJvxmZ0', 'aN8ghtSrKDk', 'o9Ay35tPQ70', 'ceYfbRuADuU', '-d2YfSsXff4', 'NN7qVw3c6v0', 'tw4fygeHCGo', 'PZfJXquT-yo', 'OAaJ_OyCjD8', '822FFyjco1w', '322IpCSbhlE', 'gLdPcTgWrPQ', '3ojSHoXGFzA', 'dQq_4x02Lxw', 'nkhU8eGV15M', 'tNKKMpizWKo', '3a5d7gH7gAU', 'CrLqO6oYNFQ', 'EBO6Vgwtl-8', '5OfV3dYsF3U', 'Vw0eHZNX-qE', 'JPPxGV8fRAc', 'TJo45_mcMm4', 'B5vfNIs9-Ek', 'Y0Ctr01nQRI', 'K36df1X9who', 'gQ-IQFelbzI', 'PtJF0IWxFJE', '2r6RhfZ3SSs', 'vjQ3KkfRh04', 'QWIKr3OpDZ8', 'PhxfA9L7mdY', '3mdIaws2CnY', 'A66-j0z-gfA', '5Gq2eG1HnHg', 'MjmTLSOcUwU', 'zTzB8hoPnRI', 'mjfhFUaojgk', 'pyMIRGJwpM0', 'wQfDKpdllJs', 'hEEPiTaM0aE', 'uxw1ZxggZo4', 'E1Dx_wBd06E', 'HkqwXYm64R4', 'mw53JE6bysE', 'YMbXZsUm3wM', 'tQucqttXt_s', 'vtcDAXzW56A', 'MH-_cSck_Lo', 'guYWHR2-_P8', 'TR-CV9_-RMU', '63au-GYx2_M', '3PXFwoFsKM4', 'bfghGc9JkgA', 'uTNSgWuNnxc', 'OhDcDSfSDXA', 'bnuvoZ5C4LE', 'uQZhlc1a4og', 'SnjsvlVSu2Q', 'OVjraMT09MM', '9N84AlI6jjY', 'UljngsWpuos', 'VIyRUXKLYck', 'kv8oITYYw50', 'tW3L5KIVgUM', 'CBFJvSgO7yw', '0_i4d0_J1SM', 'EY9u5CDKT7E', 'yXuQ9qkT-T8', 'hsssnni7y8A', 'gqibcL8vSgA', 'iO3ris90w5s', 'kWrttsYIj74', 'ilQeeMwn0u4', 'ceuwJ-_U_oo', 'fG5VWKr04n0', 'hSLYVE0XFIo', 'rC11zJ9_VFo', 'nM62SVD5wXM', 'zk2G0hVr1rc', 'KLnjnnkpA1s', 'd2_xBm3vPkI', 'asLPu9_lifQ', '_BFlhwSbaPM', 'E3uvprJyVHY', 'wmB0eWecx7w', 'frK127n29E8', '3QuRWLE50vg', 'dHzSbz3-Dgo', 'VgxIqCQOy6g', '1HBQUukiOrE', 'jxANYFMHGCY', '0H2jZnaTtOM', 'hJ5wFgS-Py4', '6ruvMYAe8cQ', 'KsU7FJQMkU4', '-2coJUh7I3M', 'NjW60d9L-y0', 'kQGa-Efgbv0', 'SS8B8m_VYOY', 'j3hQfMfUf6E', 'sh1DiGrH_wE', 'EiZmEMIpCOA', '21DSp2IsZw4', 'fEa-8gEqi14', 'WC5y9FSzyCU', 'qOdiw9IF6U0', 'sM7958Hx4Yg', 'Ll-ORcTqR4A', 'GFX9pUCM_8I', 'bJvpsS1L_tg', '1blbKLDgMhk', 'ZncNtIBufTA', 'YoxD1G3ulqE', 'VGI2n9jCV2Q', 't5F9y8_Qfs0', 'OuWKwvl1_ZU', 'LNwKGuuQ9JA', 'tkaMZWe3vxU', 'XoAV7A-TSVg', 'bYCl0kOq9Eg', '0d3reYJ_V98', 'oHcGxz1gSvU', 'oJnfQPKxNUo', 'XmQlL_lS4Sc', 'Ft0GLbHDooM', 'QJUbkEA4qGc', 'NE5jd2HEO7A', 'TRe50CZSWfw', 'hZLzo0GhfDE', 'Sqt2kap6ra8', '-Im27CNgjD0', 'sJ9HSLgiiyE', 'x72vIQgN8qw', 'nzo36aM5WQk', '7Stnnnnhi_I', 'ugYu70sgNxo', '3jb6J84ZEzk', 'CjofGBuU5so', 'LD09UmHrVp4', '7MEx-1WoOH0', 'b36vE8m00hM', 'i78PmTXABRw', '61RwkiC67Y8', 'bmP0paSWf3U', 'WrBDj902QKs', 'Cwe8C69jm9E', 'uMgA2bqnxOA', 'HZ_oZyAyW0M', 'pi-jhd6NB_s', 'pOiCZCgiQD4', 'ke3Hu7hC50o', 'ErpqCfqMDbw', 'Ar-mfyVSQbg', 'BleKU04nCnY', 'I5luHcMOGGQ', 'ihhwdZrMk7E', 'dj77lPhOs-Y', 'QJ2Sc6jib1s', 'bnwMc3DHiIY', 'UPQeF-pbPXM', 'UXwNl9T-_4o', 'onrPaOuTjxo', 'niYWQjkOPN8', 'LMCBubdkhNw', 'JeSg0zstHC0', 'oRei15CZG14', 'GF2ih_5q_tY', 'Ce3qAfXy18Y', 'BdbyDb-XIYc', 'IDUE2aNycMo', 'AVuCtleBnRI', 'ojQAA8reNZc', 'EYNkJFA2MeY', 'kw1ccK0Cjtg', 'qhU2nVLIdjs', '0kBCVFvkbzA', '6kj5E_oSWTU', '2ezxRks_kPc', 'SWsq9BD2vwI', 'ysiIJ01fdYM', '6EYmiXxQSDE', 'ZyVaPduofbE', 'TQlVNVuU6Iw', 'BEKS--gLsE0', 'vVUI_RKQtZI', '9Bilku6YZpY', 'dc5nYFtJRCg', 'kWb1lTM8n28', 'sKegdAY6Ieg', 'TovP0QjoLkk', '5Un_rzeCrwQ', 't4CPWD-ugPQ', 'lGgEeAPl_bk', 'lkPhWzNHonY', '-rHYyb3_TV8', 'EUzqPNBuGWA', 'YmBVQeGJofM', 'lo4llzEYdEY', 'fNBPIR46m_8', '1Rb5F6L5EqY', 'TAUIyGJ_2aI', '6Zf2vuXeYy0', 'QcWqfCxOT_s', 'JKzntV4uuw8', 'pHNzhUaiuLI', 'slmeFjIBVyY', '04-XHmIIRpE', 'cq5qEu68Jek', 'jWt9CV7vDnw', 'c8f7V9FdAVI', 'XMW05IasNcU', '7b701AVD--A', 'sFDnQgyDQIU', '1COSzke5vxw', 'lLAZQtjRmXA', 'iim8YocZhMo', 'FkQ9Xh2w2WY', 'e2V2QcaF8UI', '9RVUu4ZOcI0', '2cOwgFU6cZs', 'GAbshPLGdYg', 'Mu9nqXe19tA', 'FIIAdb0NMms', 'erYGy1ZPRsY', 'kXmv3TVDq8s', 'OOrFT6rJVY4', 'BB95BIroGGo', 'ThMwv9f1WCM', '4p79-wmcSvM', 'HCYOQamxJ3o', 'WtQv5t4_6Js', 'fCx7k6LnhFM', 'vIF9qDz_5xw', 'tWBreJI2KAM', 'kLHfOxB22I8', 'n4fDPA5VqmQ', 'KIvepXnOu30', 'EoHOnd-psko', 'WbwenzbmzCE', 'fY1m-mtxsBU', 'rcoNGRc-NQU', 'fIFyCWH5pj0', 'weABbrTjtZY', 'olJUniYSpcw', 'wlHrG1LT9mo', 'DYX5yNk3HyM', '0aPzv7FlwVs', '6xiWPkq5vBc', 'apH9oC7fQFU', 'J0s8czVKcVE', 'bqFnIlzJIc8', 'p35wMJIHRuQ', 'WixO0rhkrOU', 'P9PMGmQhsq0', 'TS3cWkiA2iY', 'OlHrvXixR2U', 'K9So1pC0ZDg', '5QVG_acjFSE', 'v5DwRdUr0d8', 'uC1N37XPWrE', 'd-Aw-xtW6gw', 'Gd7WQE2YjYI', 'eRlWSYrjSpg', 'cBBK2_wdjrQ', '6T3ViOL4K2Y', 'CZY3DzgmECM', 'Vh167mbf3ME', '0xdj_Eqxc8o', '12xnXZjo-yw', '1ULGLZ7WlVI', 'qJQYRaozh7Y', 'J_8Ob8IxPDM', 'FwIq9n00B3A', 'vkNcrviTI9o', 'Hy39nmJlB_o', 'KxIqN6fgb_o', 'FIwNeHPHmwg', 'WxjwY7cHigU', 'w-_LdRJjM2k', 'zKXgdJkYONU', '893Q1wcwthg', 'BfZV03rlhDE', 'IBXqKVYrV6I', 'ZWyH0f8gvK0', '7wwQgEXB2hM', '1QTUm_cJjco', 'ezQLr4uqoFg', '4ngi_2AWr0E', 'd8jlydTkivM', 'IsGJKTLLHpA', '42i2GXQ2Bvw', 'Mv5IyvemkR0', 'QXd_x4hg4kU', '4vgpc0zb02g', 'b5-m-JLLVk0', '4ool-J29C0o', '7W21nHOmuLc', 'OIWHEAjJ2ls', 'Q7RflKP75xg', 'R_MG5ws_pv0', 'RxY2Wcjl3_Q', 'no_I95ag9jA', 'b0ATSC18Zd8', 'jAGPtSzfBEg', 'vP-2XBCitYw', 'y-2AGWX9MWM', 'jB_5NIVLHAw', 'Bqj5qaI_UPQ', 'he24r2Le5kI', '0p9lSoR4DHc', 'aSMxza_PnZM', 'XdI9wCLNEho', '6SKlyluDx78', '7JETUAX7Vic', '7n-w6NHx1Nc', 'l-xtje2E0sc', 'RIaMvVGDT8c', 'CnCZFQ74LFM', '0YxPERPoalY', 'tU9Ue4iyGAY', 'HEzyeMzoLbk', 'bPzhPHR7HAI', 'exRruUMUboI', '5sSz-wzjXwI', 'pVw1Pme95uM', '8p2eHs8w6Wg', 'vjh-RsgVXeo', 'Cy84vkHicBg', 'qS4EWM2uGT8', 'g4pPIZJjhi0', '6bHV479to4M', 'Pwu6Oj6l3RM', 'etWUd2D-o1g', 'wnhJI-5xjGw', 'PxEN5D6iWlw', '6qL3W9Qmnqk', 'E4Ev1k9hTrs', 'cFpv1Zitt2c', 'JYKHLMg8fno', 'pll3QQUCHyc', '6JEOjFIjQz8', 'WoFFpt0UHb0', '8jyyhsemfHQ', 'QMkyAS4IKuA', 'yTl8QwjuSvA', 'nVy36PZLACo', 'ZIKPc5G9t6I', 'jBX3pc1Bde0', 'iJl6wh0AKjw', 'c9tEYJd7mtw', '_XcgyGJP_pA', 'McUmn6Mkl_I', 'lAAHyntHENk', 'Rryna5r-Ocw', '5cPixdsAWUI', 'TinAojki5zs', 'RrTiyi0jdOI', 'cC0X1jCJKAM', 'cW0CHO33y20', 'bHnPZ2mQa_M', 'Cqd1OFwi0Ik', 'mUN8FjkFzaE', 'p0n_N1T8lSs', 'ak7eWVRtBKg', 'JSrI_VFNhPA', 'cgTzna5_vKU', 'Y1hBJyam8C8', 'aLqhrecOVaw', 'cgVTQGLVMJE', 'RzOJLycXO6o', 'IoHG6ZJ8BO0', 'PPGtUNUAUVQ', '50uq87q4yy8', 'XsUydesjejw', '2VV8BVlpSDE', 'net2FClXDx0', 'KY1jtI75keU', 'sJRKIck2gGg', 'eHTtxaXx5wI', '9vU3J4YCKjQ', 'P8olnrGMxEQ', '77PTNJkMHEE', 'rirB2LdZueE', 'x1JIV6OzF_U', 'wJMInwVHc-A', 'AAIyQxRC_AM', '5GaeaGRdFpU', 'Im55eBda4zc', 'ERWMch_YtYk', 'K1zInd495ec', 'En9ZHw0YVqc', 'ix_BOlp5Gy4', 'uAu5lYvwqo0', 'M2uB2E3KYBw', 'NnO6_11Hlho', 'F7fRUmb1dBI', 'p-kC1YcScrs', '6KLUlGNiZps', 'PfAbpJGta8o', 'x1E-KfuQkL0', 'KyanlIxPKGQ', 'yiFm2F6QsOE', 'n1wdu39Bioc', 'qbPdID0vljM', '6UfffEKxFyM', '2mt2b7FfBIs', '-FwOSviP_jk', 'BEWyUVmx4rE', 'aii_Xy1pBUI', 'oHMg9opZ5GY', 'hPcBU-iojMM', 'BN2nGtwAH5I', '25DfwHHnKDg', 'IoeWqnq31G0', 'AoGKs9d2ypQ', 'IKX5q_zDtlc', 'NXemvVxtQa4', '5N1r7NAfuqE', '46BmjpnN2RU', 'vuTQyk75pjc', 'RgE-l3isCA8', 'NTBSkBkQ-vk', 'R2c6g55U1LE', 'QO7j9Dj6E4A', 'c88Ev0H2t_o', 'nDC3juGf5G8', 'fg7ZMuRp5D4']
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
                'search_start': dt.datetime(2018, 10, 6),
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

            chapter_all_list = ChapterInfo.objects.order_by('-published_date').distinct().values_list('video_id', 'video_title', 'chapter_title', 'chapter_url', 'published_date', 'chapter_start')
            print(chapter_all_list)
            chapter_search_list = []
            count = min(len(chapter_all_list), items_count)
            for i in chapter_all_list:
                if count > 0:
                    if search_start <= i[4] <= search_end:
                        if keyword in i[2]:
                            chapter_search_list.append([
                                i[0],
                                i[1],
                                i[2],
                                i[3],
                                i[4],
                                i[5],
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
