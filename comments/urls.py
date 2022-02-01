from django.urls import path

from . import views

app_name = 'comments'
urlpatterns = [
    path('comments/<int:pk>', views.comment, name='comment'),
]