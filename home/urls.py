from django.urls import path
from .views import HomeView,ArticleDetail


app_name = 'home'

urlpatterns = [

    path('', HomeView.as_view(), name = 'home'),
    path('article/<int:id>', ArticleDetail.as_view(), name = "post_detail"),
]