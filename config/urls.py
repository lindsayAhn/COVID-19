from django.contrib import admin
from django.urls import path
from chart import views                                     # !!!

urlpatterns = [
    path('covid/',
         views.covid19, name='covid19'),  # !!!
    path('admin/', admin.site.urls),
]