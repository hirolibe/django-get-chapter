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
fromtime = (dt.datetime.now(dt.timezone.utc)-dt.timedelta(hours=43800)).strftime('%Y-%m-%dT%H:%M:%SZ') # 24時間以内にアップされた動画から検索

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
def get_chapter_info(videoinfo_list):
    chapterinfo_dicts = {}
    # 'description'の文字列を取得
    for videoinfo in videoinfo_list:
        request = YOUTUBE_API.videos().list(
            part='snippet',
            id=videoinfo[0],
        )
        response = request.execute()
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
        videoinfo_list = get_videoid_list(YOUTUBE_API, channel_id)
        chapterinfo_dicts = get_chapter_info(videoinfo_list)
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
                'search_start': dt.datetime.today() - dt.timedelta(days=30),
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
