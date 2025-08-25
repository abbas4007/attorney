from django.urls import path
from .views import HomeView,ArticleDetail,ParvandeDetailView


app_name = 'home'

urlpatterns = [

    path('', HomeView.as_view(), name = 'home'),
    path('article/<int:id>', ArticleDetail.as_view(), name = "post_detail"),
    path('parvandeh/<int:id>', ParvandeDetailView.as_view(), name = 'parvandeh_detail'),
]