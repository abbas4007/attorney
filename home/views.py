from django.shortcuts import render
from django.views import View
from .models import Article, Parvandeh


# Create your views here.


class HomeView(View) :
    def get(self, request) :
        articles = Article.objects.all()
        return render(request, 'home/home.html', context = {'articles' : articles})


class ParvandeView(View) :
    def get(self, request) :
        parvandeh = Parvandeh.objects.all()
        return render(request, 'home/home.html', context = {'parvandeh' : parvandeh})