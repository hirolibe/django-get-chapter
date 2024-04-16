from django import forms

class KeywordForm(forms.Form):
  keyword = forms.CharField(max_length=100, label='キーワード')
  items_count = forms.IntegerField(label='検索数')
  viewcount = forms.IntegerField(label='再生回数')
  order = forms.ChoiceField(label='並び順', widget=forms.Select, choices=(('date', '日付'),),)
  search_start = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}), label='検索開始日')
  search_end = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}), label='検索終了日')