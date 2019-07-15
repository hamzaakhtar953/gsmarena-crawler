from scrapy.spiders import Spider, Request
from w3lib.url import urlparse

from ..items import Accessory


class ProductParser(Spider):
    name = 'gsmarena-parse'
    brands = []

    @staticmethod
    def clean(lst_str):
        if isinstance(lst_str, list):
            return [x.strip() for x in lst_str if x.strip()]
        
        return lst_str.strip()

    def parse(self, response):
        phone = Accessory()

        phone['name'] = self.extract_name(response)
        phone['misc'] = self.extract_misc(response)
        phone['brand'] = self.extract_brand(response)
        phone['body'] = self.extract_body_specs(response)
        phone['sound'] = self.extract_sound_specs(response)
        phone['comms'] = self.extract_comms_specs(response)
        phone['features'] = self.extract_features(response)
        phone['launch'] = self.extract_launch_specs(response)
        phone['memory'] = self.extract_memory_specs(response)
        phone['network'] = self.extract_network_specs(response)
        phone['display'] = self.extract_display_specs(response)
        phone['battery'] = self.extract_battery_specs(response)
        phone['platform'] = self.extract_platform_specs(response)
        phone['main_camera'] = self.extract_main_camera_specs(response)
        phone['selfie_camera'] = self.extract_selfie_camera_specs(response)

        phone['userreviews'] = []
        phone['image_urls'] = []

        phone['requests'] = self.review_requests(response) + self.image_requests(response)
        return self.phone_or_review_request(phone)

    def phone_or_review_request(self, phone):
        if not phone['requests']:
            del phone['requests']
            return phone

        review_request = phone['requests'].pop()
        review_request.meta['phone'] = phone
        return review_request

    def parse_review(self, response):
        phone = response.meta['phone']
        phone['userreviews'] += self.extract_reviews(response)

        return self.phone_or_review_request(phone)

    def parse_images(self, response):
        phone = response.meta['phone']
        phone['image_urls'] += self.extract_images(response)

        return self.phone_or_review_request(phone)

    def extract_name(self, response):
        return response.css('.specs-phone-name-title::text').get()

    def extract_network_specs(self, response):
        return {'technology': response.css('[data-spec="nettech"] ::text').get(default='')}

    def extract_launch_specs(self, response):
        return {'announced': response.css('[data-spec="year"] ::text').get(default=''),
                'status': response.css('[data-spec="status"] ::text').get(default='')}

    def extract_body_specs(self, response):
        return {'dimensions': response.css('[data-spec="dimensions"] ::text').get(default=''),
                'weight': response.css('[data-spec="weight"] ::text').get(default=''),
                'build': response.css('[data-spec="build"] ::text').get(default=''),
                'sim': response.css('[data-spec="sim"] ::text').get(default=''),
                'other': self.clean(response.css('[data-spec="bodyother"] ::text').getall())}

    def extract_display_specs(self, response):
        return {'type': response.css('[data-spec="displaytype"] ::text').get(default=''),
                'size': response.css('[data-spec="displaysize"] ::text').get(default=''),
                'resolution': response.css('[data-spec="displayresolution"] ::text').get(default=''),
                'protection': response.css('[data-spec="displayprotection"] ::text').get(default=''),
                'other': self.clean(response.css('[data-spec="displayother"] ::text').getall())}

    def extract_platform_specs(self, response):
        return {'os': response.css('[data-spec="os"] ::text').get(default=''),
                'chipset': response.css('[data-spec="chipset"] ::text').getall(),
                'cpu': response.css('[data-spec="cpu"] ::text').getall(),
                'gpu': response.css('[data-spec="gpu"] ::text').getall()}

    def extract_memory_specs(self, response):
        return {'card_slot': response.css('[data-spec="memoryslot"] ::text').get(default=''),
                'internal': response.css('[data-spec="internalmemory"] ::text').get(default='')}

    def extract_main_camera_specs(self, response):
        return {'quad': self.clean(response.css('[data-spec="cam1modules"] ::text').getall()),
                'features': response.css('[data-spec="cam1features"] ::text').get(default=''),
                'video': response.css('[data-spec="cam1video"] ::text').get(default='')}

    def extract_selfie_camera_specs(self, response):
        return {'dual': self.clean(response.css('[data-spec="cam2modules"] ::text').getall()),
                'features': response.css('[data-spec="cam2features"] ::text').get(default=''),
                'video': response.css('[data-spec="cam2video"] ::text').get(default='')}

    def extract_sound_specs(self, response):
        return {'loudspeaker': response.xpath('//td[contains(., "Loudspeaker")]/following-sibling::td/text()').get(default=''),
                '3.5mm jack': response.xpath('//td[contains(., "3.5mm jack")]/following-sibling::td/text()').get(default=''),
                'other': self.clean(response.css('[data-spec="optionalother"] ::text').getall())}

    def extract_comms_specs(self, response):
        return {'wlan': response.css('[data-spec="wlan"] ::text').get(default=''),
                'bluetooth': response.css('[data-spec="bluetooth"] ::text').get(default=''),
                'gps': response.css('[data-spec="gps"] ::text').get(default=''),
                'nfc': response.css('[data-spec="nfc"] ::text').get(default=''),
                'radio': response.css('[data-spec="radio"] ::text').get(default=''),
                'usb': response.css('[data-spec="usb"] ::text').get(default='')}

    def extract_features(self, response):
        return {'sensors': response.css('[data-spec="sensors"] ::text').get(default=''),
                'other': self.clean(response.css('[data-spec="featuresother"] ::text').getall())}

    def extract_battery_specs(self, response):
        charging_x = '//td[contains(., "Charging")]/following-sibling::td/text()'
        return {'charging': self.clean(response.xpath(charging_x).getall()),
                'other': response.css('[data-spec="batdescription1"] ::text').get(default='')}

    def extract_misc(self, response):
        return {'colours': response.css('[data-spec="colors"] ::text').get(default=''),
                'price': response.css('[data-spec="price"] ::text').get(default='')}

    def extract_images(self, response):
        return response.css('#pictures-list ::attr(src)').getall()

    def extract_brand(self, response):
        phone_name = self.extract_name(response).lower()
        brand = [b for b in self.brands if b.lower() in phone_name]
        return brand[0] if brand else 'GSmarena'

    def extract_reviews(self, response):
        reviews = []

        for review_s in response.css('#all-opinions .user-thread'):
            review = {}

            reviewer_name = self.clean(review_s.css('.uname2 ::text, .uname ::text').getall())[0]
            entry_id = review_s.css('::attr(id)').get()

            review_text = ' '.join(review_s.css('.uopin ::text').getall())

            review[f'{reviewer_name}_{entry_id}'] = review_text
            reviews.append(review)
        
        return reviews

    def review_requests(self, response):
        reviews_per_page = 20

        total_opinions = int(response.css('#opinions-total ::text').re_first(r'\d+'))
        pages = total_opinions // reviews_per_page + 2

        xpath = '//*[contains(@class, "button-links")]//a[contains(text(), "Read")]/@href'
        url = response.urljoin(response.xpath(xpath).get())
        path = urlparse(url).path.replace('.php', '')

        return [response.follow(url.replace(path, f'{path}p{page}'), callback=self.parse_review)
                for page in range(1, pages)]

    def image_requests(self, response):
        xpath = '//*[contains(@class, "article-info-meta-link")]//a[contains(text(), "Pictures")]/@href'
        url = response.xpath(xpath).get()
        return [response.follow(url, callback=self.parse_images)]
