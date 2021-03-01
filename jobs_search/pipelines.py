# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

class JobsSearchPipeline:
    def process_item(self, item, spider):

        if 'Seek' in str(spider):
            source = 'Seek'
        elif 'Indeed' in str(spider):
            source = 'Indeed'

        titles = item['job_title']
        companies = item['job_company']
        links = item['job_link']
        user_input = item['job_keyword']

        file = open("temp.csv", "a")
        for i in range(len(companies) if len(companies) <= len(titles) else len(titles)):
            file.write(str(titles[i].replace(',', ' ')) + "," + str(companies[i].replace(',', ' ')) + ","
                       + source + "," + user_input.replace('+', ' ') + "," +
                       str(links[i].replace(',', ' ')) + "," + "\n")

        file.close()
        scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('secret.json', scopes)
        client = gspread.authorize(creds)
        content = open('temp.csv', 'r').read()
        client.import_csv('1ScJ2LJ6wkg09vDs7nKT-UfeI2-UcphQ7cSBDTi4Qq8I', content)
        return item
