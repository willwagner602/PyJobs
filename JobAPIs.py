__author__ = 'wwagner'

import urllib
import json
import configparser

import requests


class JobAPI(object):

    def __init__(self, search):
        self.jobs = []
        self.avoid_terms = search['avoid_terms']

    def audit_job(self, job):
        if any(term.upper() in job['name'].upper() for term in self.avoid_terms):
            return False
        else:
            self.jobs.append(job)


class GitHubJobs(JobAPI):

    def __init__(self, search, desired_jobs=100, page=1):
        self.source_link = '<div class="github_jobs"><a class="github_jobs_logo" href="http://jobs.github.com">GitHub Jobs</a></div>'
        self.jobs = []
        self.site = 'https://jobs.github.com/positions.json?'
        self.desired_jobs = desired_jobs
        self.avoid_terms = search['avoid_terms']
        self.end_job = 24
        self.page = page
        self.args = (
            ("search", search['terms'][0]),
            # GitHub jobs API says that location should be valid, but never returns results if used
            ("location", search['zip_code']),
            # ("full_time", "true"),
            # ("page", self.page)
        )

    def get_jobs(self):
        while self.end_job <= self.desired_jobs:
            self.end_job += 50
            indeed_query = requests.get(self.site + urllib.parse.urlencode(self.args))
            results = json.loads(indeed_query.text)
            for job_info in results:
                try:
                    this_job = {
                        'name': job_info['title'],
                        'company': job_info['company'],
                        'url': job_info['url'],
                        'location': job_info['location'],
                        'date_posted': job_info['created_at'],
                        'source': self.source_link,
                    }
                except UnicodeEncodeError:
                    this_job = {
                        'name': job_info['jobtitle'].encode('utf-8'),
                        'company': job_info['company'].encode('utf-8'),
                        'url': job_info['url'].encode('utf-8'),
                        'location': job_info['formattedLocation'].encode('utf-8'),
                        'date_posted': job_info['formattedRelativeTime'].encode('utf-8'),
                        'source': self.source_link,
                    }
                self.audit_job(this_job)
            self.page += 1
        return self.jobs


class IndeedJobs(JobAPI):

    def __init__(self, search, desired_jobs=1000, page=1):
        self.source_link = """<span id=indeed_at><a href="http://www.indeed.com/" title="Job Search"><img src="http://www.indeed.com/p/jobsearch.gif" style="border: 0; vertical-align: middle;" alt="Indeed job search"></a></span>"""
        self.jobs = []
        self.site = 'http://api.indeed.com/ads/apisearch?'
        self.desired_jobs = desired_jobs
        self.avoid_terms = search['avoid_terms']
        self.end_job = 24
        self.args = {
                "publisher": "9397654515414817",
                "v": "2",
                'format': "json",
                'callback': "",
                "q": '+or+'.join(search['terms']),
                "l": search['zip_code'],
                'limit': '25',
                "radius": '25',
                "userip": '50.185.23.24',
                "useragent": 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
                "start": str(self.end_job - 24),
                "end": str(self.end_job),
                "fromage": "1",

            # stuff that should work with advanced search but doesn't
            #     "as_any":'+'.join(search['terms']),
            #     "as_not": '+'.join(search['terms_to_avoid']),
            #     "psf": "advsrch"
            #     "as_and": "",
            }

    def get_jobs(self):
        while self.end_job <= self.desired_jobs:
            self.end_job += 25
            indeed_query = requests.get(self.site + urllib.parse.urlencode(self.args, safe="+"))
            results = json.loads(indeed_query.text)['results']
            for indeed_job in results:
                this_job = {
                    'name': indeed_job['jobtitle'],
                    'company': indeed_job['company'],
                    'url': indeed_job['url'],
                    'location': indeed_job['formattedLocation'],
                    'date_posted': indeed_job['formattedRelativeTime'],
                    'source': self.source_link,
                }
                self.audit_job(this_job)
        return self.jobs


class DiceJobs(JobAPI):

    def __init__(self, search, desired_jobs=1000, page=1):
        self.source_link = '<a class="dice_logo" href="http://www.dice.com">Dice</a>'
        self.jobs = []
        self.site = 'http://service.dice.com/api/rest/jobsearch/v1/simple.json?'
        self.avoid_terms = search['avoid_terms']
        self.desired_jobs = desired_jobs
        self.args = {
            "direct": "0",
            "city": search['zip_code'],
            # "areacode": "",
            # "country": "",
            # "state": "",
            "skill": ' '.join(search['terms']),
            # "text": "",
            # "ip": "",
            "age": "1",
            # "diceid": "",
            "page": page,
            # "pgcnt": "",
            "sort": "1",
            "sd": "d"
            }

    def get_jobs(self):
        while int(self.args['page']) <= (self.desired_jobs/50):
            dice_query = requests.get(self.site + urllib.parse.urlencode(self.args))
            results = json.loads(dice_query.text)['resultItemList']
            for dice_job in results:
                this_job = {
                    'name': dice_job['jobTitle'],
                    'company': dice_job['company'],
                    'url': dice_job['detailUrl'],
                    'location': dice_job['location'],
                    'date_posted': dice_job['date'],
                    'source': self.source_link,
                }
                self.audit_job(this_job)
            self.args['page'] = str(int(self.args['page']) + 1)

        return self.jobs


class GlassdoorJobs(JobAPI):
    """ It doesn't appear that GlassDoor's API supports jobs, but this might be useful to pull in employer data """

    def __init__(self, search, desired_jobs=1000, page=1):
        partnerid, key = self.load_glassdoor_config()
        self.source_link = "<a href='https://www.glassdoor.com/index.htm'>" \
                + "<img src='https://www.glassdoor.com/static/img/api/glassdoor_logo_80.png' title='Job Search'/></a>"
        self.jobs = []
        self.site = 'http://api.glassdoor.com/api/api.htm?'
        self.avoid_terms = search['avoid_terms']
        self.desired_jobs = desired_jobs
        self.args = {
            'v': 1.1,
            'format': 'json',
            't.p': partnerid,
            't.k': key,
            'userip': '50.185.23.24',
            "useragent": 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            'action': 'jobs',
            'q': '+'.join(search['terms']),
            'page': 0,
            }

    def get_jobs(self):
        while int(self.args['page']) <= (self.desired_jobs/50):
            glassdoor_query = requests.get(self.site + urllib.parse.urlencode(self.args))
            results = json.loads(glassdoor_query.text)['resultItemList']
            for glassdoor_job in results:
                this_job = {
                    'name': glassdoor_job['jobTitle'],
                    'company': glassdoor_job['company'],
                    'url': glassdoor_job['detailUrl'],
                    'location': glassdoor_job['location'],
                    'date_posted': glassdoor_job['date'],
                    'source': self.source_link,
                }
                self.audit_job(this_job)
            self.args['page'] = str(int(self.args['page']) + 1)

        return self.jobs

    def load_glassdoor_config(self):
        config = configparser.ConfigParser()
        config.read('keys.ini')
        return config['glassdoor.com']['partnerid'], config['glassdoor.com']['key']
