from babel.numbers import format_currency
import requests
import time
import os
from dotenv import load_dotenv
from discord_webhook import DiscordWebhook, DiscordEmbed

load_dotenv()
webhook_url = os.environ.get('DISCORD_TIKI_WEBHOOK')


def write_log(content):
    with open("log.txt", "a") as file:
        file.write(f'{content}\n')


def getTheProducts():
    url = "https://tiki.vn/api/personalish/v1/blocks/listings?limit=24&category=1084&page=1&sort=newest&seller=1&urlKey=truyen-tranh"

    r = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0'
    }).json()

    return r['data']


def webhooks(title, url, image, price, og_price, author, description):
    price = format_currency((price), 'VND', locale='vi_VN')
    og_price = format_currency((og_price), 'VND', locale='vi_VN')

    webhook = DiscordWebhook(url=webhook_url, rate_limit_retry=True)
    embed = DiscordEmbed(
        title=title,
        description=description,
        # color = '1a94ff',
        url=url
    )
    embed.set_author(
        name="Cập nhật truyện mới / manga.glhf.vn",
        url="https://manga.glhf.vn/",
        icon_url="https://res.cloudinary.com/glhfvn/image/upload/v1650536017/LOGO_shomth.png"
    )
    embed.set_thumbnail(url=image)
    embed.add_embed_field(name="Tác giả", value=author)
    embed.add_embed_field(name="Nhà cung cấp", value="Tiki Trading")
    embed.add_embed_field(name="Giá", value=price)
    embed.add_embed_field(name="Giá bìa", value=og_price)
    embed.set_timestamp()

    webhook.add_embed(embed)
    response = webhook.execute()


# READ LATEST PRODUCT
try:
    with open("latest.txt", "r") as file:
        last_product = file.read().rstrip()
except:
    last_product = ''

# GET CURRENT TIME
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)

# BEGIN CRAWL
product_array = getTheProducts()

# CHECK FOR NEW PRODUCTS
for product in product_array:
    # run until current product matches last latest product
    if product['name'] == last_product:
        write_log(f'[{current_time}] DUPLICATE AT: {product["name"]}')
        break
    else:
        write_log(f'[{current_time}] NEW: {product["name"]}')
        webhooks(product['name'], f'https://tiki.vn/{product["url_path"]}', product['thumbnail_url'],
                 product['price'], product['list_price'], product['author_name'], product['short_description'])

# WRITE LATEST PRODUCT
with open("latest.txt", "w") as file:
    file.write(product_array[0]['name'])
