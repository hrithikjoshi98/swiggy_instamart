from scrapy.cmdline import execute
from QC.items import QcItem
import QC.db_config as db
import pymysql
import scrapy
import gzip
import json
import os


class SwiggyInstamartSpider(scrapy.Spider):
    name = "swg"
    custom_settings = {
        'COOKIES_ENABLED': False,
    }

    def __init__(self, start_id, end_id):
        super().__init__()

        # Setting start and end id for running in batch files by fetching only
        self.start_id = start_id
        self.end_id = end_id
        self.con = pymysql.connect(host=db.db_host,
                                   user=db.db_user,
                                   password=db.db_password,
                                   database=db.db_name,
                                   autocommit=True)
        self.cursor = self.con.cursor()  # Creating cursor for Database operations
        self.input_table = 'mapped_swiggy_inputs'  # Inputs table name to fetch product details
        self.store = 'swg'  # store name to scrape

        cookies_filename = 'swiggy_instamart_cookies.json'  # Cookies filename
        cookies_path = '\\'.join(os.getcwd().split('\\')[:-1]) + '\\cookies' + '\\' + cookies_filename
        self.cookies_json = json.loads(open(cookies_path, 'r').read())

    def start_requests(self):
        # SELECT query for fetching product details
        self.cursor.execute(
            f"select index_id, fkg_pid, pincode , link from {self.input_table} where index_id between {self.start_id} and {self.end_id}"
            f" and (status='pending' or status = 'error')")

        results = self.cursor.fetchall()  # Fetching results from executed query

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        }

        # Iterating on each record to send request for each product
        for result in results:
            index_id = result[0]
            fkg_pid = result[1]
            pincode = result[2]
            swg_url = result[3]
            meta = {
                'index_id': index_id,
                'input_table': self.input_table,
                'fkg_pid': fkg_pid,
                'swg_url': swg_url,
                'pincode': pincode,
            }
            cookies = self.cookies_json[pincode]  # Fetching respective cookie for the pincode fetched

            if swg_url == "na":
                update_query = f"""UPDATE {self.input_table} SET status='Link_NA' WHERE index_id={meta['index_id']}"""
                self.cursor.execute(update_query)
                print('Status Updated Link_NA...')
            else:
                yield scrapy.Request(url=swg_url, headers=headers, cookies=cookies, callback=self.parse,
                                     dont_filter=True, meta=meta)

    def parse(self, response, **kwargs):
        meta = response.meta
        pincode = meta['pincode']
        swg_url = meta['swg_url']
        fkg_pid = meta['fkg_pid']
        index_id = meta['index_id']

        if response.status == 404:
            update_query = f"""UPDATE {self.input_table} SET status='404' WHERE index_id={index_id}"""
            self.cursor.execute(update_query)
            print('Status Updated 404...')

        elif response.status == 200:
            try:
                self.con.ping(reconnect=True)
                print('SQL Conn. Reconnected!')
            except Exception as e:
                print(e)
                print('SQL Conn. Not Reconnected!')
            try:
                item = QcItem()  # Making instance of item

                json_data = response.xpath('//script[contains(text(),"window.___INITIAL_STATE___")]/text()').get()
                page_data = self.clean_json(json_data)
                product_data = page_data['instamart']['cachedProductItemData']

                file_name = meta['fkg_pid'] + meta['pincode'] + ".html.gz"
                page_save_path = db.dynamic_drive(store=self.store)  # Setting page_save_path using dynamic_drive function from db_config
                file_path = os.path.join(page_save_path, file_name)
                gzip.open(file_path, "wb").write(json.dumps(page_data).encode())
                print("Page saved.")

                item['comp'] = 'Swiggy Instamart'
                item['url'] = swg_url
                item['fk_id'] = fkg_pid
                item['pincode'] = pincode
                item['index_id'] = index_id

                if product_data:
                    print('Product Data found...')
                    product_data = product_data['lastItemState']
                    variations = product_data['variations']
                    data = variations[0]
                    item['name'] = data['display_name'] + ' ' + data['sku_quantity_with_combo']
                    item['price'] = data['price']['offer_price']

                    mrp = data['price']['mrp']
                    item['mrp'] = mrp

                    discount = data['price']['offer_applied']['product_description']
                    item['discount'] = discount if discount else '0'

                    if data['inventory']['in_stock'] == True:
                        item['availability'] = True
                    else:
                        item['availability'] = False
                    yield item  # Sending item to pipeline for inserting into product data table
                else:
                    print('Product Data not found...')

                    error_msg = response.xpath(
                        '//div[contains(text(),"Our best minds are on it.'
                        ' You may retry or check back soon")]/text()').get()

                    if error_msg:
                        print('Error msg...')
                        self.cursor.execute(f"UPDATE {self.input_table} SET STATUS = 'ERROR' WHERE index_id=%s", index_id)
                    else:
                        print('Inserting empty item')
                        item['name'] = ''
                        item['price'] = ''
                        item['mrp'] = ''
                        item['discount'] = ''
                        item['availability'] = ''
                        yield item  # Sending item to pipeline for inserting into product data table

            except Exception as e:
                print("ERROR: ", e)

    def clean_json(self, raw_data):
        json_data = raw_data.replace('window.___INITIAL_STATE___ = ', '')
        start_idx = json_data.find(f'var App = {{')
        result = json_data[:start_idx].strip()

        return json.loads(result.strip(';'))


if __name__ == '__main__':
    execute(f"scrapy crawl swg -a start_id=1000 -a end_id=1010".split())
