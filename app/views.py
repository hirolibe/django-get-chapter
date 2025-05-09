from django.shortcuts import render, redirect
from django.views.generic import View
from apiclient.discovery import build
import datetime as dt
from django.conf import settings
from .models import VideoInfo, ChapterInfo
import re
from .forms import KeywordForm
from django.core.paginator import Paginator
import pandas as pd



'''---------------------------------------
動画検索画面
---------------------------------------'''
class IndexView(View):
    def get(self, request, *args, **kwargs):
        # キーワードはデフォルトでNone（フィルターなし）
        keyword = None

        # 検索ロジックを実行
        video_all_list = VideoInfo.objects.order_by('-published_date').distinct().values_list('video_id', 'video_title', 'published_date', 'video_url')

        # キーワードがない場合はフィルタリングなし
        filtered_video = video_all_list

        paginator = Paginator(filtered_video, 15)
        page_str = request.GET.get('page')
        page = int(page_str) if page_str else 1
        page_data = paginator.page(page)
        max_page_number = max(page_data.paginator.page_range)

        return render(request, 'app/index.html', {
            'keyword': keyword,
            'hit_number': len(filtered_video),
            'page': page,
            'page_data': page_data,
            'max_page_number': max_page_number,
        })

    def post(self, request, *args, **kwargs):
        keyword = request.POST['keyword']

        video_all_list = VideoInfo.objects.order_by('-published_date').distinct().values_list('video_id', 'video_title', 'published_date', 'video_url')

        # キーワードがある場合のみフィルタリング
        if keyword:
            filtered_video = video_all_list.filter(video_title__icontains=keyword)
        else:
            # キーワードが空の場合はすべて表示
            filtered_video = video_all_list

        paginator = Paginator(filtered_video, 15)
        page_str = request.GET.get('page')
        page = int(page_str) if page_str else 1
        page_data = paginator.page(page)
        max_page_number = max(page_data.paginator.page_range)

        return render(request, 'app/index.html', {
            'keyword': keyword,
            'hit_number': len(filtered_video),
            'page': page,
            'page_data': page_data,
            'max_page_number': max_page_number,
        })



'''---------------------------------------
チャプター検索画面
---------------------------------------'''
class ChapterView(View):
    def get(self, request, *args, **kwargs):
        # キーワードはデフォルトでNone（フィルターなし）
        keyword = None

        # 検索ロジックを実行
        chapter_all_list = ChapterInfo.objects.order_by('-published_date').distinct().values_list('video_id', 'video_title', 'chapter_title', 'chapter_url', 'published_date', 'chapter_start')

        # キーワードがない場合はフィルタリングなし
        filtered_chapter = chapter_all_list

        paginator = Paginator(filtered_chapter, 15)
        page_str = request.GET.get('page')
        page = int(page_str) if page_str else 1
        page_data = paginator.page(page)
        max_page_number = max(page_data.paginator.page_range)

        return render(request, 'app/chapter.html', {
            'keyword': keyword,
            'hit_number': len(filtered_chapter),
            'page': page,
            'page_data': page_data,
            'max_page_number': max_page_number,
        })

    def post(self, request, *args, **kwargs):
        keyword = request.POST['keyword']

        chapter_all_list = ChapterInfo.objects.order_by('-published_date').distinct().values_list('video_id', 'video_title', 'chapter_title', 'chapter_url', 'published_date', 'chapter_start')

        # キーワードがある場合のみフィルタリング
        if keyword:
            filtered_chapter = chapter_all_list.filter(chapter_title__icontains=keyword)
        else:
            # キーワードが空の場合はすべて表示
            filtered_chapter = chapter_all_list

        paginator = Paginator(filtered_chapter, 15)
        page_str = request.GET.get('page')
        page = int(page_str) if page_str else 1
        page_data = paginator.page(page)
        max_page_number = max(page_data.paginator.page_range)

        return render(request, 'app/chapter.html', {
            'keyword': keyword,
            'hit_number': len(filtered_chapter),
            'page': page,
            'page_data': page_data,
            'max_page_number': max_page_number,
        })



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
VIDEOIDリストで得た'description'から動画情報(ID、動画タイトル、配信日)を一つずつ抽出し、動画URLを生成
'''
def get_video_data(videoinfo_list):
    data = []
    for videoinfo in videoinfo_list: # videoinfo_list = [[videoId, publishedAt, title], [videoId, publishedAt, title], ...]
        published_date = videoinfo[1]
        # ISO 8601形式の日付文字列をdatetimeオブジェクトに変換
        published_date_jp = dt.datetime.fromisoformat(published_date.replace('Z', '+00:00'))+dt.timedelta(hours=9)
        # 必要な形式の文字列に変換
        formatted_date = published_date_jp.strftime('%Y-%m-%d')
        video_url = f'https://www.youtube.com/embed/{videoinfo[0]}'
        data.append([videoinfo[0], videoinfo[2], formatted_date, video_url])
    df_data = pd.DataFrame(data, columns=['ID', '動画タイトル', '配信日', '動画URL'])
    return df_data

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
        chapterinfo_dicts[videoinfo[0]] = [videoinfo[1], chapterinfo_dict, videoinfo[2]] # chapterinfo_dicts = {id: [配信日, {チャプタータイトル: 秒数, ...}, 動画タイトル], ...}
    return chapterinfo_dicts

'''
チャプターの開始時間を抽出して動画URLとチャプター動画URLを作成
'''
def get_chapter_data(chapterinfo_dicts):
    data = []
    for id, chapterinfo in chapterinfo_dicts.items(): # chapterinfo_dicts = {id: [配信日, {チャプタータイトル: 秒数, ...}, 動画タイトル], ...}
        for chapter_title, time in chapterinfo[1].items(): # chapterinfo = [配信日, {チャプタータイトル: 秒数, ...}, 動画タイトル]
            published_date = chapterinfo[0]
            # ISO 8601形式の日付文字列をdatetimeオブジェクトに変換
            published_date_jp = dt.datetime.fromisoformat(published_date.replace('Z', '+00:00'))+dt.timedelta(hours=9)
            # 必要な形式の文字列に変換
            formatted_date = published_date_jp.strftime('%Y-%m-%d')
            chapter_url = f'https://www.youtube.com/embed/{id}?start={time}'
            video_url = f'https://www.youtube.com/embed/{id}'
            data.append([id, chapterinfo[2], chapter_title, chapter_url, formatted_date, time, video_url])
    df_data = pd.DataFrame(data, columns=['ID', '動画タイトル', 'チャプタータイトル', 'チャプターURL', '配信日', 'チャプター開始時間', '動画URL'])
    return df_data

'''
データベースをアップデート
'''
def add_video_database(df_data):
    for index, row in df_data.iterrows():
        if not VideoInfo.objects.filter(video_id=row['ID']).exists():
            video_data = VideoInfo()
            video_data.video_id = row['ID']
            video_data.video_title = row['動画タイトル']
            video_data.video_url = row['動画URL']
            video_data.published_date = row['配信日']
            video_data.save()

def add_chapter_database(df_data):
    for index, row in df_data.iterrows():
        if not ChapterInfo.objects.filter(video_id=row['ID']).exists():
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

        df_video_data = get_video_data(videoinfo_list)
        add_video_database(df_video_data)

        chapterinfo_dicts = get_chapter_info(videoinfo_list)
        df_chapter_data = get_chapter_data(chapterinfo_dicts)
        add_chapter_database(df_chapter_data)

        return redirect('index')