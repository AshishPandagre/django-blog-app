from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='index'),
    path('blog/', views.PostList.as_view(), name='blog'),
    path('post/<slug:slug>', views.post_detail, name='post'),
    path('subscribe', views.subscribe, name='subscribe'),
    path('comment/', views.comment, name='add comment'),
]
