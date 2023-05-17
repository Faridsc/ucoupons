import scrapy
from datetime import datetime, timedelta


class CouponsSpider(scrapy.Spider):
    name = "coupons"
    allowed_domains = ["www.discudemy.com"]

    def start_requests(self):
        url = "https://www.discudemy.com/all"
        yield scrapy.Request(url=url, callback=self.parse)

    def norm_date(self, date):
        d = date
        if date.upper() == "TODAY":
            d = datetime.today().date()
        if date.upper() == "YESTERDAY":
            today = datetime.today().date()
            d = today - timedelta(1)

        return str(d)

    def parse(self, response):
        data = {}
        next = response.css("ul.pagination3 li:last-child").css("a::attr(href)").get()

        cards = response.css("section.card")
        for card in cards:
            if card.css("ins.adsbygoogle"):
                continue
            data = {
                "title": card.css("div.content div.header a::text").get(),
                "lang": card.css("label.ui.label::text").get(),
                "date": self.norm_date(
                    card.css("div.content div.meta span.category div::text").get()
                ).replace(" ", "-"),
                "url": card.css("div.content div.header a::attr(href)").get(),
                "img": card.css("div.content div.image amp-img::attr(src)").get(),
                "description": card.css("div.content div.description::text")
                .get()
                .strip(),
                "price": "->".join(
                    [
                        i.css("::text").get()
                        for i in card.css("div.content div.meta span:nth-child(2)").css(
                            "span"
                        )[0::2]
                    ]
                )
                .replace("\t", "")
                .replace("\n", "")[2:],
                "topic": card.css("div.extra div.author a span::text").get(),
            }
            yield scrapy.Request(
                "https://www.discudemy.com/go/" + data["url"].split("/")[-1],
                callback=self.finalize,
                cb_kwargs=data,
            )

        if next:
            yield scrapy.Request(next, callback=self.parse)

    def finalize(self, response, **data):
        url = response.css("a#couponLink::attr(href)").get()
        data["url"] = url
        yield data
