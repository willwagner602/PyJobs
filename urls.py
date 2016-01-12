__author__ = 'wwagner'

from django.conf.urls import url
from django.views.generic import TemplateView
from PyJobsDjango import PyJobsDjango

urlpatterns = [
        url(r"^$", PyJobsDjango.get_jobs_page, ),
]