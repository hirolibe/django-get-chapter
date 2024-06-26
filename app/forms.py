from django import forms

class KeywordForm(forms.Form):
  keyword = forms.CharField(max_length=100, label='キーワード')
  search_start = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}), label='いつから')
  search_end = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}), label='いつまで')
  items_count = forms.IntegerField(label='検索数')
