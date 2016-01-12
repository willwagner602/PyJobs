__author__ = 'wwagner'

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

import scrapers
import smart_dropbox_path

user = ''
password = ''

config_file = smart_dropbox_path.config_path()

# get username and password from config file
with open(config_file) as f:
    user = f.readline().strip()
    password = f.readline().strip()


def add_jobs_to_message(jobs, message):
    """Takes a list of jobs, in the format {region:{link:title}} and formats into
    distinct lines to print in the email message"""
    for region in jobs:
        if jobs[region]:
            message += '<br>' + region.upper() + '<br>'
            for job in jobs[region]:
                message += job + ' - <a href="' + jobs[region][job] + '">Link</a><br>'
    return message

msg = MIMEMultipart()
msg['Subject'] = 'Job Report for {} {}'.format(datetime.now().strftime('%A, %B'), datetime.now().day)
msg['From'] = user
msg['To'] = user

html = """\
  <html>
    <head></head>
    <body>
      <p>"""

craigs_jobs = scrapers.scrape_craigslist()
dice_jobs = scrapers.scrape_dice()
cybercoder_jobs = scrapers.scrape_cybercoders()
indeed_jobs = scrapers.scrape_indeed()

updated_html = add_jobs_to_message(craigs_jobs, html)
updated_html = add_jobs_to_message(dice_jobs, updated_html)
updated_html = add_jobs_to_message(cybercoder_jobs, updated_html)
updated_html = add_jobs_to_message(indeed_jobs, updated_html)


updated_html += """\
      </p>
    </body>
  </html>"""

part1 = MIMEText(updated_html, 'html')
msg.attach(part1)

server = smtplib.SMTP('smtp.gmail.com', port=587)
server.ehlo()
server.starttls()
server.login(user, password)
server.sendmail(user, user, msg.as_string())
server.quit()