from babel.numbers import format_currency
import requests
import time
import os
import json
from dotenv import load_dotenv
from discord_webhook import DiscordWebhook, DiscordEmbed


load_dotenv()
webhook_url = os.environ.get('DISCORD_FAHASA_WEBHOOK')


def write_log(content):
    with open("log.txt", "a") as file:
        file.write(f'{content}\n')


def getTheProducts(category):
    url = f"https://cdn0.fahasa.com/fahasa_catalog/product/loadproducts?category_id={category}&filters[book_layout]=9_1840_126&currentPage=1&limit=24&order=created_at&series_type=0"

    r = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0'
    }).json()

    return r['product_list']


def webhooks(title, url, image, price, og_price):
    price = format_currency((price), 'VND', locale='vi_VN')
    og_price = format_currency((og_price), 'VND', locale='vi_VN')

    webhook = DiscordWebhook(url=webhook_url, rate_limit_retry=True)
    embed = DiscordEmbed(
        title=title,
        url=url
    )
    embed.set_author(
        name="Cập nhật truyện mới / manga.glhf.vn",
        url="https://manga.glhf.vn/",
        icon_url="https://res.cloudinary.com/glhfvn/image/upload/v1650536017/LOGO_shomth.png"
    )
    embed.set_thumbnail(url=image)
    embed.add_embed_field(name="Giá", value=price)
    embed.add_embed_field(name="Giá bìa", value=og_price)
    embed.set_timestamp()

    webhook.add_embed(embed)
    response = webhook.execute()


# READ LATEST PRODUCT
try:
    with open("latest.json", "r") as file:
        last_products = json.loads(file.read())
except:
    last_products = []

# GET CURRENT TIME
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)

# BEGIN CRAWL - 6718 for MANGA / 5981 for LN
product_array = getTheProducts(6718) + getTheProducts(5981)

# CHECK FOR NEW PRODUCTS
output = []
for product in product_array:
    output.append(product['product_name'])

    # run until current product matches last latest product
    if (product['product_name'] not in last_products) and (product['type_id'] != "series"):
        write_log(f'[{current_time}] NEW: {product["product_name"]}')
        webhooks(product['product_name'], product["product_url"], product['image_src'],
                 int(product['product_finalprice'].replace(".", "")), int(product['product_price'].replace(".", "")))

# WRITE LATEST PRODUCT
with open("latest.json", "w") as file:
    json.dump(output, file, indent=4)
