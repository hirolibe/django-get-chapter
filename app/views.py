from django.shortcuts import render, redirect
from django.views.generic import View
from apiclient.discovery import build
from datetime import datetime, timedelta, date
from django.conf import settings
from .forms import KeywordForm
import pandas as pd

class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "app/index.html")