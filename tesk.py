
import re
from copy import deepcopy
from scrapy import Request, Spider
from collections import OrderedDict


class vaughandesigns(Spider):
    name = 'hrirugs'

    # Custom settings for exporting data to an Excel file
    custom_settings = {
        'FEED_EXPORTERS': {'xlsx': 'scrapy_xlsx.XlsxItemExporter'},
        'FEED_FORMAT': 'xlsx',
        'FEED_URI': 'hrirugs_data.xlsx',
    }

    url = "https://hrirugs.com/"  # Base URL for the website

    # HTTP headers to mimic a browser request
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    def start_requests(self):
        # Start the request to the base URL
        meta = {'dont_merge_cookies': True}
        yield Request(self.url, self.parse_navigation, meta=meta, headers=self.headers)

    def parse_navigation(self, response):     
        # Extract collections from the navigation menu
        collections = response.css('ul.list-unstyled li a')

        for collection in collections:
            label = collection.css('::text').get('').strip()  # Get collection name
            url = collection.css('::attr(href)').get()  # Get collection URL

            # Construct full URL if needed
            if url and not url.startswith('http'):
                url = response.urljoin(url)

            # Prepare metadata for the next request
            meta = deepcopy(response.meta)
            meta['cat'] = label
           
            if label not in ['Show All','New Arrivals']:
            # if label in ['Aba']:
                yield response.follow(url, self.parse_collection, meta=meta, headers=self.headers)

    def parse_collection(self, response):
        # Extract rug items from the collection page
        rug_items = response.css('.thumbtable .img-portfolio')
        for rug in rug_items:
            rug_name = rug.css('div.copy a::text').get('').strip()  # Get rug name
            rug_url = rug.css('a::attr(href)').get()  # Get rug URL
            
            # Construct the full URL for the rug
            if rug_url:
                full_rug_url = response.urljoin(rug_url)
                yield Request(full_rug_url, self.parse_detail, meta=response.meta, dont_filter=True, headers=self.headers)

    def parse_detail(self, response):
        # Initialize an ordered dictionary for the rug item
        item = OrderedDict()
        item['category'] = response.meta['cat']  # Set category
        item['Url'] = response.url  # Set the rug detail page URL
        item['rug_name'] = response.css('h1.page-header::text').get().strip()  # Rug name
        item['rug_description'] = response.css('div.rugdesc::text').get().strip()  # Rug description
        item['rug_colorway'] = response.css('div.ruginfo li.copy::text').get().strip()  # Colorway
        item['hand_loomed'] = response.css('div.ruginfo li.copy:nth-of-type(2)::text').get().strip()  # Looming details
        item['country'] = response.css('div.ruginfo li.copy:nth-of-type(4)::text').get().strip()  # Country of origin

        # Check for discontinued status
        discont_text = response.css('h1.page-header .discont::text').get()
        collection_header = response.css('img[title="Made To Order Icon"]::attr(title)').get()
        item['discont'] = discont_text.strip() if discont_text else collection_header or ''

        item['rugsize'] = ', '.join(response.css('div.rugsize::text').getall()).strip()  # Rug size
        item['image_url'] = response.urljoin(response.css('a.cloud-zoom::attr(href)').get())  # Main image URL

        # Initialize a counter for additional image URLs
        url_counter = 1

        # Extract all additional image links
        image_urls = response.css('div.thumbtable .smallthumbnail a::attr(href)').getall()
        
        # Loop through the image URLs and assign them to item fields
        for url in image_urls:
            item[f'url{url_counter}'] = response.urljoin(url)
            url_counter += 1

        # Get download link for PDF tearsheet
        item['download_link'] = response.urljoin(response.css('a[href*="hri-pdf-tearsheet.php"]::attr(href)').get())

        yield item  # Yield the collected item
