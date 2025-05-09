from django.db import models

class VideoInfo(models.Model):
    video_id = models.CharField('video_id', max_length=100)
    video_title = models.CharField('動画タイトル', max_length=100)
    video_url = models.CharField('動画URL', max_length=100)
    published_date = models.DateField('配信日')

    def __str__(self):
        return f"{self.video_title}({self.published_date})"

class ChapterInfo(models.Model):
    video_id = models.CharField('video_id', max_length=100)
    video_title = models.CharField('動画タイトル', max_length=100)
    chapter_title = models.CharField('チャプタータイトル', max_length=100)
    chapter_url = models.CharField('チャプターURL', max_length=100)
    published_date = models.DateField('配信日')
    chapter_start = models.CharField('チャプター開始時間', max_length=100)

    def __str__(self):
        return f"{self.chapter_title}({self.published_date})"