"""yandex_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from promotion.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('imports/', post_import),
    path('imports/<int:import_id>/citizens/<int:citizen_id>', patch_citizen),
    path('imports/<int:import_id>/citizens', get_import),
    path('imports/<int:import_id>/citizens/birthdays', get_birthdays),
    path('imports/<int:import_id>/towns/stat/percentile/age', get_percentile)
]
