# sydney-jobs-scraping

## About
Scrapes jobs from two biggest sites namely Indeed and Seek for jobs in Sydney NSW and presents it at https://jobs-scrape-dashboard.herokuapp.com/ (may take up to a minute to load). 
This project uses web scraping to quickly obtain information without integrating multiple APIs. The data can also be seen in google sheet form: bit.ly/jobs-scrape.
The code that links the google sheet form to the website can be found in https://github.com/giorgioGunawan/reactAndGoogleSheets.

## Installation
Web scraping project using Python Scrapy: https://docs.scrapy.org/en/latest/intro/install.html
Installation:
```
pip install Scrapy
```

The dependencies include:

- Python: python.org

- Random User-Agent middleware package: https://pypi.org/project/scrapy-user-agents/
Installation:
```
pip install scrapy-user-agents
```

- Python API for Google Sheets: https://gspread.readthedocs.io/en/latest/
Installation:
```
pip install gspread
```

- OAuth2Client makes it easy to interact with OAuth2-protected resources, especially those related to Google APIs. 
Installation:
```
pip install --upgrade oauth2client
```

## Usage
There are 3 spiders. 2 of them are actual spiders called "indeed-spider" and "seek-spider" which expects a CLI argument "user_input".
The other spider is a dummy spider "reset-spider" which resets the database and clears all data. The CLI argument "user_input" expects the job title in a specific format.
It is important that the string in user_input uses '+' instead of spaces. 

- Using the indeed spider to find graduate software engineer jobs
```
> scrapy crawl 'indeed-spider' -a user_input="graduate+software+engineer"
```

- Using the seek spider to find school teacher jobs
```
> scrapy crawl 'seek-spider' -a user_input="school+teacher"
```

- Using the reset dummy spider to reset database
```
> scrapy crawl 'reset-spider'
```




