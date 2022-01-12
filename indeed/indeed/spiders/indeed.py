import scrapy
import re
import pandas as pd
from urllib.parse import urlparse
from urllib.parse import parse_qs
from datetime import datetime

CLEANR = re.compile('<.*?>')


class IndeedSpider(scrapy.Spider):
    name = 'indeed'
    base_url = "https://www.indeed.com{}"

    NYJobs = []
    LAJobs = []
    AustinJobs = []
    start_urls = []
    for i in range(0,200,10):
        NYJobs = "/jobs?q&l=10006&radius=3&fromage=3&start="+str(i)+"/"
        LAJobs = "/jobs?q&l=90013&radius=3&fromage=3&start="+str(i)+"/"
        AustinJobs = "/jobs?q&l=78714&radius=6&fromage=3&start="+str(i)+"/"

        start_urls.append(base_url.format(LAJobs))

        # jobs = pd.DataFrame(
        #     columns=['job_link', 'jk', 'job_title', 'company_name', 'location', 'salary', 'description', 'rating',
        #              'posting_date', 'scraping_time'])

    def parse(self, response):
        job_links = response.xpath('//*[@id="mosaic-provider-jobcards"]/a/@href').extract()

        for job_link in job_links:
            print("--------------")
            print("--------------")
            print("aaaaaaaaaaaaaaaaaaaaaaa")
            print("--------------")
            print("--------------")
            link = self.base_url.format(job_link)
            yield scrapy.Request(link, callback=self.parse_job)


    def parse_job(self, response):



        job_link = response.url
        parsed_url = urlparse(job_link)
        # url is parsed to get jobkey from link
        job_key = parse_qs(parsed_url.query)['jk'][0]
        job_title = response.xpath('//*/div[@class="jobsearch-JobInfoHeader-title-container "][1]/h1/text()').get()
        company_name = response.xpath('//*/div[@class="icl-u-lg-mr--sm icl-u-xs-mr--xs"][1]/a/text()').get()
        if not company_name:
            # because some dont have link, a is empty
            company_name = response.xpath('//*/div[@class="icl-u-lg-mr--sm icl-u-xs-mr--xs"][1]/text()').get()
        location = response.xpath('//*/div[@class="icl-u-xs-mt--xs icl-u-textColor--secondary jobsearch-JobInfoHeader-subtitle jobsearch-DesktopStickyContainer-subtitle"][1]/div[2]/text()').get()
        if not location:
            location = response.xpath('//*/div[@class="jobsearch-jobLocationHeader-location"]/text()').get() #if location was precisely described

        salary = response.xpath('//*/span[@class="icl-u-xs-mr--xs"]/text()').get()
        if not salary:
            salary = response.xpath('//*/div[@id="coinfp-estimatedSalaries-panel"]/div[1]/ul/li[2]/text()').get() #doesn't work idk why

        description = self.cleanhtml(response.xpath('//*[@id="jobDescriptionText"]').get())

        rating_link = response.xpath('//*/div[@class="jobsearch-CompanyReview icl-u-lg-hide"]/a/@href').get()
        if rating_link:
            rating = yield scrapy.Request(rating_link, callback=self.parse_rating)
        else:
            rating = None

        posting_date = response.xpath('//*/div[@class="jobsearch-JobMetadataFooter"]/div[1]/text()').get()
        if posting_date == response.xpath('//*/div[@class="icl-u-textColor--success"]/text()').get():
            posting_date = response.xpath('//*/div[@class="jobsearch-JobMetadataFooter"]/div[2]/text()').get()

        now = datetime.now()
        scraping_time = now.strftime("%d/%m/%Y %H:%M:%S")

        job = {
            "job_link": job_link,
            "jk": job_key,
            "job_title": job_title,
            "company_name": company_name,
            "location": location,
            "rating_link": rating_link,
            "salary": salary,
            "description": description,
            "rating": rating,
            "posting_date": posting_date,
            "scraping_time": scraping_time
        }

        with open('jobs.txt', 'a', encoding='utf-8') as f:
            f.writelines(str(job))
            f.writelines('\n')


    def parse_rating(self, response):
        rating = response.xpath('//*/span[@class="css-htn3vt e1wnkr790"]/text()').get()
        yield rating

    def cleanhtml(self, raw_html):
        return re.sub(CLEANR, '', raw_html)
