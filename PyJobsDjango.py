import logging

from MainServer.settings import BASE_DIR
from django.shortcuts import render

from .generate_html_page import JobListPage


def get_jobs_page(request):
    if request.method == 'POST':
        keywords = request.POST['keywords']
        logging.debug('Received Jobs POST ' + keywords)
        zip = request.POST['zipcode']
        filename = keywords.replace(' ', '_') + '.html'

        search = {'terms': ' '.split(keywords),
                  'zip_code': zip,
                  "avoid_terms": '',
                  "required_terms": '',
                  }

        # setup and build the page of results for the search
        job_page = JobListPage(search, 'static', filename)
        job_page.execute()

        return render(request, 'PyJobsDjango/' + filename, )

    elif request.method == 'GET':
        return render(request, 'PyJobsDjango/search_page.html', )

def get_existing_page(request):
	path = request.path[6:]
	return render(request, 'PyJobsDjango/' + path + '.html',)