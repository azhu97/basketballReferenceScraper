import scrapy
from bballRefScraper.items import BballrefscraperItem

class BasketballSpider(scrapy.Spider):
    name = "bballRef"
    allowed_domains = ["basketball-reference.com"]
    start_urls = ["https://www.basketball-reference.com/"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        team_urls = []
        all_teams = response.css("tr.full_table")
        for team in all_teams:
            team_url = team.css("th > a::attr(href)").get()
            if team_url:
                team_urls.append(response.urljoin(team_url))
        team_urls = team_urls[:30]

        for url in team_urls:  
            yield scrapy.Request(url, callback=self.parse_team)

    def parse_team(self, response):
        item = BballrefscraperItem()
        info = response.css('div[data-template="Partials/Teams/Summary"]')

        item["name"] = info.css("h1 > span:nth-child(2)::text").get(default="Unknown")
        standing_and_record = (
            info.css("p:nth-of-type(1) > strong::text").get(default="") +
            info.css("p:nth-of-type(1) > a::text").get(default="")
        )
        item["standing"] = standing_and_record
        item["record"] = standing_and_record.split(",", 1)[0] if "," in standing_and_record else "0-0"
        item["wins"], item["losses"] = item["record"].split("-", 1) if "-" in item["record"] else ("0", "0")
        item["coach"] = info.css("p:nth-of-type(4) > a::text").get(default="Unknown")
        item["pace"] = info.css("p:nth-of-type(7) strong::text").getall()[1].split(" ", 1)[0]

        ratings = info.css("p:nth-of-type(8) strong::text").getall()
        if len(ratings) >= 3:
            item["offensive_rating"] = ratings[0]
            item["defensive_rating"] = ratings[1]
            item["net_rating"] = ratings[2]

        yield item