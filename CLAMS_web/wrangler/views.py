from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.http import Http404


def homepage_view(request):
    return render(request, 'home.html')
