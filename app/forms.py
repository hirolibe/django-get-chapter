from django import forms

class KeywordForm(forms.Form):
  keyword = forms.CharField(max_length=100, label='キーワード')
  search_start = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}), label='検索開始日')
  search_end = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}), label='検索終了日')
  items_count = forms.IntegerField(label='検索数')
  my_channel_id = forms.CharField(max_length=100, label='自分のチャンネルID')
