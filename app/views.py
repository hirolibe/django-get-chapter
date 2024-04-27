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
    videoinfo_list = ['4XxBfq1ZQro', 'HQfluGiUNDQ', 'GDxzly7zOVc', 'kqa8HPF5ykI', 'wOgMMXzZk1g', 'l6puojXPXaY', 'SLJcuWUnO5M', '4WNvQ64xqPc', 'V-kdzDmCdxo', 'UWvx89Tf1aI', 'Hft_pOHSX8I', 'EsJq5l-RLns', 'LhfVPo_ojqo', 'jtl1SuWrv10', '4vl6nVMpYnk', 'mPbnk6CpBOo', '7c7pfYl_V-0', 'Q4aGjML1F3Y', 'HHvakrk0ShU', 'vjCxxN9uroE', 'eIsDBSzjSbk', 'UpL3oJtYg0s', 'HzhwiMKnTPE', 'rg72vpxYr0M', 'm0WSX1TES8c', 'RbUk5ssns8A', 'Zj_76eddRe4', 'BaCWJsnZsOE', 'RZsa_cBif40', 'urfJoLoIQBk', '9QtnXd06hvc', 'MRt4niabo4c', '6roxtwZwzFk', '4jrKDTT8iiQ', 'GbvXFtdUp2M', 'MFEznGHWlnI', 'xgtNWiuEqYA', 'yrSqkz57u9w', 'tLiorU0EgxE', '8JI42sXl-M4', 'URrejyFhiDI', 'uGblfw4SVBI', 'RW0beH-_8jg', 'uhQtn05BEAs', 'yrMbdYllTWA', 't1OpmVfcbX4', 'RmHr3daI2No', 'QDf3u0aEziw', '3NmM5hxxNTs', 'CzPo5enC73Y', '4ayIB8hPfeU', 'p2ryGnJoRUw', 'zWi2H8aFuog', 'GEP65Gvedqc', 'skPH5U-fKjw', 'W6QKp82LlVA', 'WJEFJFmqwlw', '9v4kAuU9PjI', 'INns-ftvzzU', 'E3D5DrSHtE4', 'ufI2SRk4S9I', 'pRrTIaopq0M', '0GoTz3_hSH8', 'BIWx3-mkRyw', '5iG5hAw7qds', 'xNyX-OKajqo', 'oCAaxHcM1nA', 'cWPi6Xf8-fY', '11slW4gG2LU', 'TSMi11gtbQw', 'EN8tkJp-8pU', 'eNl1rGami7Y', 'xMgQfLSBB2g', 'ymp_qFPw8ZM', 'HvKJW54vrHI', 'YbT8ts7N1tY', 'vPxBOtcdFk0', 'AvEycgKuPH8', 'fBpxUXb8AmQ', '4-hKKbTwtFA', 'QmY9i_ha-o0', 'TX__hRWB5CY', 'UV8ak1o5YeA', 'UNVw6T9yumo', 'pjQWRYlkGOk', 'JYcJjyFEFsA', 'AcnS3kopzww', 'Mv_YX8Slabc', 'XMaTE9P7cdA', 'aphH0_Ce1SA', 'bEbsdoh1CvA', 'f4n3mvkOI1I', '49k_tXaZsmI', 'ZSHSTj6DvXI', '4sowsCQOoKg', '9-24ACcU9Ts', 'jwJe3ouGPtc', '3xhWX50TF5g', 'JeqIBamvYpM', 'yTLCASxLX34', 'Qf0WlUy8-Bc', 'kWohRsrsKqM', 'dCALjaWUkJA', 'jUX5BPc4Dlg', 'iTd1qruS_os', '-T4kcG2T03E', '2g4_BllBuo8', 'UFW7XdMvdOc', '7paaXBrt3qs', 'DlkOHnB6doA', 'wTRcpOyi01Q', '2wYHlBF93K4', 'CcCPAE6gdkE', 'rDL6EDBdzVk', 'xhBhKBaO-jg', 'YzPZ1K_Uxh4', 'zVUJ29EU5LI', 'QFvkj_vozBA', 'xE2ZPOy_ntw', 'wCaS4wzWO44', '_x2gBgWFhzY', '9nAopQCGmAA', 'vbZIPBqj7jU', 'rA-8SSZPO54', 'pyhP_3kNntw', 'epsGsinWEGI', 'kQQlzr_qn7s', '9haZc-UBF50', 'aOPa5qJv_6Y', 'cKW4l_oqOdE', 'YSzfu6Xvn5c', 'T6gsGo4uFfI', 'yFzqkck4yXw', 'cb0tqSkKn3c', 'iTfklR3dPZ8', '0sSlWNMcrwE', '27lMMdYFOwE', 'ZEGn_KlmV1Q', 'zT3hVxRWyzU', 'DoiFrArIuj0', '8FSO4VVQ_tk', 'MA0YCtVf0iI', 'ucCu1wVJ0-c', 'Rp2G_nWfe20', 'szSS1HOe534', 'k2cc3nBq5kc', 'VubqdjOK4TY', 'qyKC5Ftv8Vk', 'KaBtnQ-ogOo', 'uUuAtMafMYA', 'E165zQ3JirQ', 'pP198XKp8Ts', '6V9PEEEonRs', 'w0NH6C8MIvc', 'VAo01Fwc6Lw', 'fuml2lsYW7E', 'JFs-MnjSXQA', '18cAPPFPKxI', 'SgvbvCpylYk', 'XfeQcnRBzPQ', '0SSckGzTk_c', 'eyb1dnt5zME', 'N-Id6X73gcY', 'zJaJSnJOHqk', 'dqbfMp_nvVM', 'm-4wcFl67jM', 'r9fQQYvLSzk', 'aMYlAsQ9VXo', 'zmulq35s1K0', 'PwkUTZkXFps', 'ePXT3sbgH1s', '5t9ZFKQBdlQ', 'tUaLumN--rc', 'U6PKth3F_9o', 'IW_6FG8ZjIk', 'v8sQ31T73DA', 'whexEXQW_I8', 'tobtVkOEOBc', 'uMps1aLrHkA', 'bAwoXkzvwdU', 'DlA9lZq81DQ', 'nmh_EzLjQQ4', 'RBzmP4AzH2k', 'NNqutEu3ias', 'G3y98A3V7Tc', 'y5npgntC6OY', '15Jk7dYoyvo', 'aFwiAVqOI1w', 'PYDDCkcGl34', '_v8KKldmULk', 'jrVONkG2YG8', 'HmrEifDfnLE', 'hIUgF7v10rI', 'p-9KOg_O3HE', 'CcFjtpJeEWI', '8WdabhjIQiM', 'N9zUQJkxwtY', 'k__R0Uqhfek', 'FpFP3DxCZFs', 'AhbNkIq_mEY', 'ZnUJCHLVUwY', 'dceBWWXyE68', 'cfv_9gp7h_M', 'FtVRv2D12nQ', 'RC6PAXpysCk', '0ie2KzWm75c', 'WTU3YDwRf6o', 'q9tkPLw6sEU', 'yfeVaI57fGE', 'HVSuab0m018', 'dneQII4ItpE', 'tL6UIHndWRs', 'C8cgiitb1nk', 'E4uHGijpCNM', 'yLjefWe221o', 's8rTOpsLajk', 'VYqDFGDYEaI', 'DyhVhORTucQ', 'GwoNtIt85hY', 'ee4yuSSYljs', '7SvnkeFzLE4', 'HXFpcQDEW10', 'bwmvUyqQ3eo', 'g4xezBtEOL0', 'hxOVHljKQ_w', 'p-Rx-T2tl6c', 'us7CsLFmDeM', 'uSwLgZs1l6g', 'YzfMjHOh8dM', 'rHlw1zdVFxw', 'tZRRpuXZCYM', 'dnjCQWXUNUk', '3kHkwFmFotk', 'JlauJgLZMG0', '11wBAJoJ7sQ', 'ofimWFb3Yeg', 'EPvap4h3Ghs', 'Nxi3x9QMI9c', 'R5HNRKxc39U', '6zXIBB7pH7s', 'X49rBLcd9bk', 'ClNenGtcUmI', 'WcV0pCIjnzY', '993ym4tkIYg', 'hLlot_iJU-I', '-fWKZC8OHIg', 'M4UzCrFyS3o', 'CWjNQjRbVWw', 'a0hjwFWH99w', 'YvwLePHyyfQ', '1WUvE54GY10', 'NdlSwO8N-5c', '2dsN0n2w8aQ', 'aoBmdoOeBYc', 'LvSHDIRU9ow', 'DSZs2zyfIp8', 'CaGV2AqJ0_8', 'ArxYqP7Uh9k', 'eoHieTFpN1Y', '5c1Hh-GexL0', 'VX0I73A4rrc', 'zmA5phRaltE', 'MXQj2qeugjQ', 'Zl9cI_0tZtQ', '3baYoUB-vIQ', 'a-6fxIMALq4', 'mkQ2EIAFcSY', 'vn8RdqwepN0', 'lPgGU5fR5rs', 'lfWCVTj28nM', 'XekUT7SHQZ8', 'i6n-1XvopYM', 'hxl25iJnqkM', 'D-vYn6hfdvw', 'M83xOFCZE3E', 'va1XdcSZ4qk', 'LdQ3ZhKBwUk', 'v7mdERpzfIM', 'jSjcXM0EkjA', 'F29DTP8Aulg', 'J7ZdOAuaFBA', 'Sz05P0HedjE', '-Bh0SA37Krw', 'TGSp-gF30yA', '0lHzcGoe1KQ', 'P0bB-ysp8Ko', 'Rw7D9nkKMBc', 'ukfKaMkQlUc', 'mBa_2bn-J-I', '2HINaOEPgGg', '8XjNQJERmRY', 'Fx5lzEDSDs0', 'sEoFCLDmsX0', 'v03ONJrQOPo', 'Ie1OZJrjRT0', 'm_JYLI0VcTU', 'VRIXgDPhhUw', 'JE3GtK3jKnY', 'n5W2OCg2urM', 'wg9WpDuC89c', '_vdGQXdK4K4', 'c_bCt9xMufU', 'Z2VouBlwrmc', '7ME9pEG37e8', 'YetjxYoJo6k', 'owW38Ps3qT8', 'Y0S_LJQAvvM', 'qxPsEEYQ6qg', 'in0GDXJfX4c', 'Wupf7C9up4I', 'G0QaAvikZ-I', 'gnsgEjx7Hco', 'o-RwO6r-xEM', 'eD6SK3cTygU', 'W5sANNsnoVU', 'cPJg_c1CPE0', 'fJHQeBGodDU', '_OKjVF_CUk0', 'uiVgfnFEFx0', '5Cm2E2N0bQ4', 'Jk-VxUGOgzA', '4iwE02CTFVg', 'iSqMw-Ccq_o', 'DhqF-IHKpuM', 'svMYx5wTCfM', 'GRzE-TB0-hw', 'FMiYOX3wvZw', 'ewuoMV3HlTM', 'kAQOHX0fVNQ', 'IgGq0Me2rXM', 'WgIb2Sg1Mso', 'XUc-Av0_JOQ', 'NDbxQ6qUJV0', '_XdOoy4H5cM', 'XmOAqgZQOS8', 'Sf5v91X6zfE', 'fFcZdmMo3no', 'zt05uor6cOE', 'O3AuC_8QUKg', 'WuRjklugLhw', 'vVydAh3Tyzw', 'Ff5TWKmQ6eI', 'wnUynxpxJS4', 'u6XNCAIfK74', 'c-k-jYDbToY', '-dE5xRYIhNA', '8vJilhFM5UE', 'LADna3GFCI8', 'IyuXUK3_4BQ', 'GfKoSuJvOCQ', 'L1j8oRWfF2U', 'qlOK3MkVeg4', '46Mo1Emcs80', 'QQ6svn2absQ', 'pDxouzp9nbc', 'CUJsMWLow6s', 'iES96tY4svQ', 'AtvH8l1M8KI', 'zaErWxZ8pns', '_rapuzUYTdo', 'YRkpqCrQoC8', '9pGfe9j-_JI', 'NNaxNp7K8Nw', 'Mr_ykmzIdVA', 'KFs7ZWGXYBk', 'Sb30bWtUPmI', 'EwWfXepnZ_k', 'vnJXpaUjz4I', 'Dgn5h16iL_4', 'J_LcEDzQkEA', '7slS9xr8Ur4', 'QzhXrjkiGCc', '7X9O7VtzScQ', 'hn6SceU_XK8', 'NeOptmENvaI', 'zovs04G0_Dw', 'hRosT9rtIS8', '4BVO5loM7bw', '2-klAtULnzk', '4vLjTcsbJz8', 'GHm7uex64nM', '7g2FrwLhs1E', 'nOiOcEEgFhM', 'SYtU1TE_hKA', 'hReGDOiTNAU', 'N5e9cwKzGAM', 'JMzTXen2FcE', 'nAmc5FXa8mo', '6nZLCtS1viY', 'oFAR7PXbZVE', 'PJv0cDJoLQI', 'USbfymHPM4w', 'OvjNFbHK1lM', 'gtgWJtVScsM', '_MoGCHU0uPE', 'nij7Rnagl2g', 'gM_nvMd0Lnw', 'l3fFdrXWxBw', 'YNXmhItgMNw', 'KZ_geJdtc7Y', 'yQv4pdfig6s', 'HIjoU7fWrCY', 'QfRN2I4F9a4', 'TXlQ_coPjv0', '8rV9hiNxxXc', 'bmKUfMelslw', 'aqrobDrCxeY', 'L643SU3qFdU', 'Rw1V1pkHH_w', '4aysQCooku4', '4CCy3Wjzi1g', 'G1tsq1rqkhM', 'tnIVoJsCD2g', '7pzv8tMeNvo', 'YuKeN3Sa0_A', 'mTkcOipYcRE', 'BcOZomprWqI', 'ak9_m0YpDBw', '_HvNq1X_w6I', 'mZnahVIurFM', 'm_6gxLm-zRs', '3LL-OvGTiD0', '82c988PMbyk', '6A-lzCCwcvc', 'jGxj9YLYpYc', 'dUtaic9_B0s', 'fPDL_uJuc0E', 'F8gceTKvCv4', '37lPey51lnQ', 'y54qIBqrECk', 'I2MUpVR0qRw', 'tfB4ZyomwwQ', 'MB-V_T-iUHs', 'iKtN8GlCLyc', 'znnZ1c1Ta4w', '_OTP6AhLx-o', 'E3lhjae5T6A', 'yK4u-dQI_rg', 'akTuhIUtrxo', 'UKsEOncRSLY', 'IXbrNAo6Wjg', '2Yu0SynkvP8', 'YeKxiDorAAo', 'VgLRsSPczag', 'zG2-a5_PXow', 's4f0Jf057wI', 'qP7IosD-ByY', 'VLa9gUCsJHY', '2ssYzcOziww', 'BGcvo9QWy2M', 'f0wIDpNqBO4', 'tYCWN2UIlo8', 'YAGnkIDw1JA', '-VuOIZgUXgU', 'ug4DmGuotWU', 'O-1bgZWR2Gs', 'YY3AI5Wx3sI', 'bFw0g2Th7tM', 'RwqFdI02xro', 'tCJagmTM-VE', 'mcraR0NjWGE', '-Q7wFGSheug', '1dwNUmg2hMY', 'dLU6mC89xao', 'uSJy02dn9Rk', 'Tym3wB4HYE0', 'FyUzQ-m8H0A', 'jp3N39HKDEM', 'krtSwRPGP9s', 'kL9eSaKTSYk', 'VdA_jhe547s', 'lRTElygyy9U', 'E1M34YYzVPE', 'l5wo4YaIMbM', 'mV95O-Xfe28', 'Zr_GeWkZyv4', 'FmyEB8Praa8', 'UuKvuoPAu4g', 'zsGqfn5wUwc', 'pe-ObmiFKjk', 'YA95F3E8CKA', '1n3wRsQ0NvY', 'gSWDwPZcEZQ', 'YvHP2ivDLPo', 'QKjYjii5FEM', 'g30mh_2WETE', '96SIZ1Lw5SU', 'xI-HrJazEX0', 'LDM2BU8Ihuc', '6oBCKMRHTl0', 'fGk3YgC5DXk', 'WDlV7nHelFo', 'uWeuLGJfkVg', 'sixcS3ZFeaQ', '8kk-cOGG1qk', '4_qnl14xItI', 'EzD0OJw5rC0', '1dyLfENvWrA', 'CsrjR6LpToc', 'URiq9Z22VZU', 'E5usEJcZwdU', 'AYfAHfBNJzw', 'epTlbUWWnEQ', 'W-oKkWrVH48', 'dVSh9U_viEU', 'GMoOR00XDtY', 'ZcQklZ8oko4', 'kSU0e-TyDY8', 'd8Q2v5dkxi0', 'QOEBy1GgeHA', '2v-BO_x_FAc', 'sBeJ_qcbh2M', 'ZcnenrhiXmY', 'spKt59uJur8', 'xJJnyyCTQdg', 'WKxHVs0NM-0', 'mT7WcChJHvY', 'HkKBtkjO3xw', 'X7DxjDFTbtM', 'THER_AxNZuw', 'oXBQ0rg_ffA', 'qTG7D88HO74', 'qxL3QUSqgWI', 'zkLUdikuvs4', 'qUCxs78c8hM', 'BF-8uNb-pkM', 'y8srVGnIP-E', 'YpV-i4uEY1Y', 'kGZSjZRqznI', 'a9gKykLsFYo', 't9oXoQgYI9E', 'cys92_O3Mpw', 'WM6whFeGKYU', 'cBcFF1fw5OY', 'De1HFNwh12c', 'lKSn5E-J9kE', 'zmXmITXj-vM', '3c68rFMvxVE', 'j6DthdxdJyU', 'Jnhlv2RqqmM', 'EJIB7O1Y7Vw', 'sqpM5TTPlZY', 'RWteD50zKZ8', 'FIzdXuzO0LY', '6tbROuyj3q0', 'd_X43MgQUKM', '-YI6cDwVaDM', '05Pm0gFsY5U', '00IFNGThtbE', '_M1cv_JFqnM', 'h44CqDNLw1A', 'F0KuSKAf8T4', '44G8GBkRR28', '9aNKvBzRg14', 'r_UGh3fcEJ0', 'iGcyFwCBKws', 'dirTp9PTS28', 'k7Yc7QCCboA', 'dkM-nnms44w', 'cCM3uqz9lGQ', '4SKTSbxxnlQ', 'VAjLYemxHpE', 'ENMw5e74UDw', 'F4YZzzTTzuc', 'nQopxphOHdo', 't6_WqSQ6mH4', 'nPh8VJSORuo', '8pXpwUnMP58', 'wj8jkXiY6r0', 'KeADnRZGOik', 'sPCMKJd1bI4', 'zQMSxSGymU8', 'nn8S-vZawnY', 'wkjH54obnA4', 'p7KuGqgZH2E', 'tjnuwv07O1c', 'VfTLjPxsfaU', 'OTPLvnPN7z0', 'lNUby7a88k0', 'TYWCNKSkanE', 'E3vSwgZ57ng', '28yVgxjClow', 'djOehl1OhbI', 'ZLFSPL9ust4', 'G8VsgwVpoYg', '4Le_tunjkDY', '98ziWu3oVk8', 'bk1ZEYSS-sk', 'zhA88qwb5_0', '7QwqHB-ntBw', 'aszFfp3J6Fg', 'O7ITBpzMrUo', 'yvMZxKaCCLo', 'Wu0CZdFka3A', '_2FfbBViEXg', 'NRrjsFTEjZo']
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
