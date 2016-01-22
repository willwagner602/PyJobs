__author__ = 'wwagner'

from django.conf.urls import url
from PyJobsDjango import PyJobsDjango

urlpatterns = [
        url(r"^$", PyJobsDjango.get_jobs_page, ),
		url(r"^.*_.*", PyJobsDjango.get_existing_page, ),
]