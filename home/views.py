from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Article, Parvandeh


# Create your views here.


class HomeView(View) :
    def get(self, request) :
        articles = Article.objects.all()
        parvandeh = Parvandeh.objects.all()
        paginator = Paginator(articles, 6)
        paginatorr = Paginator(parvandeh, 3)
        page_number = request.GET.get("page")
        page_numberr = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        page_objj = paginatorr.get_page(page_numberr)
        return render(request, 'home/home.html', context = {"page_obj": page_obj,'page_objj':page_objj})

class ArticleDetail(View):
    def get(self,request,id):
        article = get_object_or_404(Article, id=id)
        return render(request, 'home/post_detail.html', {'article' : article})

class ParvandeDetailView(View) :
    def get(self, request,id) :
        parvandeh = get_object_or_404(Parvandeh, id=id)
        return render(request, 'home/parvandeh_detail.html', context = {'parvandeh' : parvandeh})