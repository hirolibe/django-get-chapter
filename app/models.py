from django.db import models

# Create your models here.
class ChapterInfo(models.Model):
    video_id = models.CharField(max_length=255, unique=True)  # 動画ID
    title = models.CharField(max_length=100)  # 動画タイトル
    chapter_title = models.CharField(max_length=100)  # チャプタータイトル
    published_at = models.DateTimeField()  # 公開日時
    list

    def __str__(self):
        return self.chapter_title