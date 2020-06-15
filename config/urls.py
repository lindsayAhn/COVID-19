from django.contrib import admin
from django.urls import path
from chart import views

urlpatterns = [
    path('covid/',
         views.covid19, name='covid19'),
    path('world-population/',
         views.world_population, name='world_population'),
    path('titanic/',
         views.titanic, name='titanic'),
    path('admin/', admin.site.urls),
]
