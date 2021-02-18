import scrapy
import re
from ..items import JobsSearchItem
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# indeed:
# first = '//*[contains(concat( " ", @class, " " ),concat( " ", "jobsearch-SerpJobCard", " " ))]'
# second = '//a[contains(concat( " ", @class, " " ),concat( " ", "jobtitle", " " ))]'
# response.xpath(first+second+'/@title').getall()

class JobsSpiderSpider(scrapy.Spider):
    name = 'indeed_jobs'
    complete_job_titles = []
    complete_job_companies = []
    complete_job_links = []
    start_urls = [
        'https://au.indeed.com/jobs?q=software+engineer&l=Sydney+NSW'
    ]
    user_input = 'intern'
    page_number = -1

    def clearDB(self):
        file = open("temp.csv", "a")
        file.truncate(0)
        file.close()

    def gsheet(self):
        scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('secret.json', scopes)
        client = gspread.authorize(creds)

        sheet = client.open('Indeed Jobs Scrape').get_worksheet(0)
        return sheet

    def parse(self, response):
        # Google sheet prep
        sheet_instance = JobsSpiderSpider.gsheet(self)
        #if JobsSpiderSpider.page_number == 0:
        #    JobsSpiderSpider.clearDB(self)
        item = JobsSearchItem()

        #Job Title
        div_root = '//*[contains(concat( " ", @class, " " ),concat( " ", "jobsearch-SerpJobCard", " " ))]'
        a_title = '//a[contains(concat( " ", @class, " " ),concat( " ", "jobtitle", " " ))]'
        job_title = response.xpath(div_root+a_title+'/@title').getall()

        # Job Link
        job_link = response.xpath(div_root + a_title + '/@href').getall()
        for i in range(len(job_link)):
           job_link[i] = 'https://au.indeed.com' + job_link[i]

        #Job Company Lister
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
            while (company[index - 1] != '>'):
                temp_company = company[index - 1] + temp_company
                index -= 1

            # now change temp_company as the actual company
            # also omit the first two index position as it is
            # '\n' the newline character
            job_company[i] = temp_company[1:]

        if JobsSpiderSpider.page_number != -1:
            item['job_title'] = job_title
            item['job_company'] = job_company
            item['job_link'] = job_link
            JobsSpiderSpider.complete_job_titles.extend(job_title)
            JobsSpiderSpider.complete_job_companies.extend(job_company)
            JobsSpiderSpider.complete_job_links.extend(job_link)
            yield item

        # increment page number
        JobsSpiderSpider.page_number += 1

        # limit to 5 pages of search
        if JobsSpiderSpider.page_number < 2:
            next_page = 'https://au.indeed.com/jobs?q='+self.user_input+'&l=Sydney+NSW&start=' + \
                        str(JobsSpiderSpider.page_number) + '0'
            yield response.follow(next_page, callback=self.parse)

        else:
            titles = JobsSpiderSpider.complete_job_titles
            companies = JobsSpiderSpider.complete_job_companies
            links = JobsSpiderSpider.complete_job_links

            sheet = JobsSpiderSpider.gsheet(self)
            sheet.clear()

            file = open("temp.csv", "a")
            file.write("Title, Company, Source, Keyword, Link" + "\n")

            for i in range(len(companies) if len(companies) <= len(titles) else len(titles)):
                file.write(str(titles[i].replace(',', ' ')) + "," + str(companies[i].replace(',', ' ')) + ","
                           + "Indeed" + "," + self.user_input.replace('+', ' ') + "," +
                           str(links[i].replace(',', ' ')) + "," + "\n")

            file.close()
            scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name('secret.json', scopes)
            client = gspread.authorize(creds)
            content = open('temp.csv', 'r').read()
            client.import_csv('1ScJ2LJ6wkg09vDs7nKT-UfeI2-UcphQ7cSBDTi4Qq8I',content)

            file = open("temp.csv", "a")
            file.truncate(0)
            file.close()


