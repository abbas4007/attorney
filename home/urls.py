from django.urls import path
from .views import HomeView

app_name = 'home'

urlpatterns = [

    path('', HomeView.as_view(), name = 'home'),
    # path('parvandeh/', ParvandeView.as_view(), name = 'parvandeh'),
]