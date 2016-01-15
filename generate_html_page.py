__author__ = 'wwagner'

import os
import webbrowser
from datetime import datetime
import logging
from urllib.request import pathname2url
from multiprocessing import Process, Queue

from MainServer import settings
from PyJobsDjango.JobAPIs import DiceJobs, IndeedJobs, GitHubJobs


class JobListPage(object):

    def __init__(self, search, css_location, filename="Job_Report.html", job_count=100):
        self.search = search
        self.jobs_list = []
        self.file_name = "templates/PyJobsDjango/" + filename
        self.locations = {}
        if css_location == 'static':
            self.css_location = '/static/PyJobsDjango/job_page.css'
        else:
            self.css_location = css_location + "job_page.css"
        self.job_count = job_count
        month = datetime.now().strftime('%A, %B')
        day = datetime.now().day
        self.page = """
      <html>
        <head>
            <title>Job Report for {} {}</title>
            <link type='text/css' rel='stylesheet' href="{}"/>
            <link type='text/css' rel='stylesheet' href="https://cdnjs.cloudflare.com/ajax/libs/materialize/0.97.5/css/materialize.min.css">
        </head>
        <body>
          <div class="title">
          <h1>
           Job Report for {} {}
          </h1>
          </div>
          <p>""".format(month, day,self.css_location, month, day)

    html_tail = """
          </p>
          <script type="text/javascript" src="https://code.jquery.com/jquery-2.1.1.min.js"></script>
          <script type="text/javascript" src="js/materialize.min.js">
        </body>
      </html>"""

    @staticmethod
    def validate_filename(filename):
        if filename[:-5] == '.html':
            return filename
        else:
            raise ValueError('Invalid filename supplied: ' + filename)

    def execute(self):
        logging.debug('Building job page ' + self.file_name)
        self.retrieve_jobs()
        self.get_locations()
        self.create_page()

    def retrieve_jobs(self):
        indeed = IndeedJobs(self.search, self.job_count)
        github = GitHubJobs(self.search, self.job_count)
        dice = DiceJobs(self.search, self.job_count)
        job_list = Queue()
        indeed_jobs = Process(target=indeed.get_jobs, args={job_list})
        dice_jobs = Process(target=dice.get_jobs, args={job_list})
        github_jobs = Process(target=github.get_jobs, args={job_list})
        indeed_jobs.start()
        dice_jobs.start()
        github_jobs.start()
        for i in range(3):
            self.jobs_list += job_list.get()


    def get_locations(self):
        for job in self.jobs_list:
            if job["location"].upper() not in self.locations:
                self.locations[job["location"].upper()] = []

    @staticmethod
    def format_job_to_html(job):
        return job['date_posted'] + ' - ' + job['name'] + ' - <a href="' + job['url'] + '">Link</a>    ' \
               + job['source'] +'<br>\n'

    def format_jobs_to_page(self):
        """
        Formats lists of jobs in HTML for display to humans. self.jobs must be dict of jobs as dicts,
        each job needs values for "name", "date_posted", "location", "url", "company"
        :return: Jobs formatted into HTML page
        """
        jobs_html = ""
        for location in self.locations:
            jobs_html += '<div class="card-panel teal lighten-2"><br><h3>' + location.upper() + '</h3>'
            for job in self.jobs_list:
                if job['location'].upper() == location and job['name'] not in jobs_html:
                    jobs_html += self.format_job_to_html(job)
            jobs_html += '</div>'
        self.page += jobs_html

    def create_page(self):
        self.format_jobs_to_page()
        try:
            with open(self.file_name, 'w') as file:
                file.write(self.page)
        except FileNotFoundError:
            file = open(settings.BASE_DIR + '/PyJobsDjango/' + self.file_name, 'w+', encoding='utf-8')
            file.write(self.page)
            file.close()

    def open_page(self):
        url = 'file:{}'.format(pathname2url(os.path.abspath(self.file_name)))
        webbrowser.open(url)


if __name__ == "__main__":

    origin = os.getcwd()

    logging.basicConfig(filename='log.log', level=logging.INFO)

    search = {
        "terms": ["python", "junior", "engineer", "developer", "entry", "django"],
        # "terms": ["project", "program", "manager", "entry", "junior"],
        "avoid_terms": ["senior", "sr", "ios", "scala", "architect", "lead", "principal"],
        "required_terms": [],
        "zip_code": "95126"
    }
    
    search_test = {'terms': ["python", "developer"],
                  'zip_code': 95126,
                  "avoid_terms": '',
                  "required_terms": '',
                  }

    job_page = JobListPage(search_test, origin + '/static/PyJobsDjango/', 'python_developer.html')
    job_page.execute()
    job_page.open_page()