import scrapy
from ..items import JobsSearchItem
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class IndeedSpider(scrapy.Spider):
    name = 'indeed_spider'
    start_urls = [
        'https://au.indeed.com/jobs?q=software+engineer&l=Sydney+NSW'
    ]
    user_input = ''
    page_number = -1

    def gsheet(self):
        scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('secret.json', scopes)
        client = gspread.authorize(creds)
        sheet = client.open('Indeed Jobs Scrape').get_worksheet(0)
        return sheet

    def parse(self, response):
        # Google sheet prep
        item = JobsSearchItem()

        #Job Title
        div_root = '//*[contains(concat( " ", @class, " " ),concat( " ", "jobsearch-SerpJobCard", " " ))]'
        a_title = '//a[contains(concat( " ", @class, " " ),concat( " ", "jobtitle", " " ))]'
        job_title = response.xpath(div_root+a_title+'/@title').getall()

        #Job Link
        job_link = response.xpath(div_root + a_title + '/@href').getall()
        for i in range(len(job_link)):
           job_link[i] = 'https://au.indeed.com' + job_link[i]

        #Job Company
        div_root = '//div[contains(concat( " ", @class, " " ),concat( " ", "sjcl", " " ))]/div'
        span_text = '//span[contains(concat( " ", @class, " " ),concat( " ", "company", " " ))]'
        job_company = response.xpath(span_text).getall()

        #Some companies have <span> tag and text while some companies have <span> tag
        # and a nested <a> tag, so the solution is a form of regex
        for i in range(len(job_company)):
            temp_company = ''
            company = job_company[i]

            # if company uses nested <a> tag
            if company.find('</a>') != -1:
                keyword = '</a>'
            else:
                keyword = '</span>'

            index = company.find(keyword)
            while company[index - 1] != '>':
                temp_company = company[index - 1] + temp_company
                index -= 1

            # now change temp_company as the actual company
            # also omit the first two index position as it is
            # '\n' the newline character
            job_company[i] = temp_company[1:]

        if IndeedSpider.page_number != -1:
            item['job_title'] = job_title
            item['job_company'] = job_company
            item['job_link'] = job_link
            item['job_keyword'] = IndeedSpider.user_input
            yield item

        # increment page number
        IndeedSpider.page_number += 1

        # limit to 5 pages of search
        if IndeedSpider.page_number < 2:
            next_page = 'https://au.indeed.com/jobs?q='+self.user_input+'&l=Sydney+NSW&start=' + \
                        str(IndeedSpider.page_number) + '0'
            yield response.follow(next_page, callback=self.parse)

class SeekSpider(scrapy.Spider):
    name = 'seek_spider'
    start_urls = [
        'https://www.seek.com.au/software-engineer-jobs?page=2'
    ]
    user_input = ''
    page_number = -1

    def gsheet(self):
        scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('secret.json', scopes)
        client = gspread.authorize(creds)
        sheet = client.open('Indeed Jobs Scrape').get_worksheet(0)
        return sheet

    def parse(self, response):
        # Google sheet prep
        item = JobsSearchItem()

        #Job Title
        article_tag = '//article[contains(concat( " ", @class, " " ),concat( " ", "_37iADb_", " " ))]'
        job_title = response.xpath(article_tag+'/@aria-label').getall()

        #Job Link
        a_title = '//a[contains(concat( " ", @class, " " ),concat( " ", "_2S5REPk", " " ))]'
        job_link = response.xpath(a_title + '/@href').getall()
        for i in range(len(job_link)):
           job_link[i] = 'https://www.seek.com.au/' + job_link[i]

        #Job Company
        span_root = '//span[contains(concat( " ", @class, " " ),concat( " ", "_3mgsa7- _15GBVuT _2Ryjovs", " " ))]'
        a_company = '//a[contains(concat( " ", @class, " " ),concat( " ", "_17sHMz8", " " ))]'
        raw_company = response.xpath(span_root + a_company + '/@aria-label').getall()
        job_company = []
        for i in range(len(raw_company)):
            if('Jobs' in raw_company[i]):
                job_company.append(raw_company[i][7:])
        if SeekSpider.page_number != -1:
            item['job_title'] = job_title
            item['job_company'] = job_company
            item['job_link'] = job_link
            item['job_keyword'] = IndeedSpider.user_input
            yield item
        else:
            # Initially, add the header of each column
            SeekSpider.page_number += 1

        # increment page number
        SeekSpider.page_number += 1

        # limit to 5 pages of search
        if SeekSpider.page_number < 3:
            temp_user_input = self.user_input.replace('+','-')
            next_page = 'https://www.seek.com.au/'+temp_user_input+\
                        '-jobs/in-All-Sydney-NSW?page='+str(SeekSpider.page_number)
            yield response.follow(next_page, callback=self.parse)

class Reset(scrapy.Spider):
    # NOT A SPIDER, JUST TO RESET THE DATABASE
    name = 'reset_spider'
    start_urls = ['https://www.google.com.au']
    def gsheet(self):
        scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('secret.json', scopes)
        client = gspread.authorize(creds)
        sheet = client.open('Indeed Jobs Scrape').get_worksheet(0)
        return sheet

    def parse(self,response):
        file = open("temp.csv", "a")
        file.truncate(0)
        file.write("Title, Company, Source, Keyword, Link" + "\n")
        file.close()
        sheet = Reset.gsheet(self)
        sheet.clear()