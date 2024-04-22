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
