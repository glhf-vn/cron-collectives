import requests
import os
import time
from dotenv import load_dotenv
import argparse
from discord_webhook import DiscordWebhook, DiscordEmbed
from babel.numbers import format_currency

load_dotenv()
webhook_url = os.environ.get('DISCORD_TIKI_WEBHOOK')


def crawl(product_id):
    url = f"https://tiki.vn/api/v2/products/{product_id}?platform=web"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    }

    r = requests.get(url, headers=headers).json()

    return r


def webhooks(title, image, url, price):
    price = format_currency((price), 'VND', locale='vi_VN')

    webhook = DiscordWebhook(url=webhook_url, rate_limit_retry=True)
    embed = DiscordEmbed(
        title=title,
        description="Đã có hàng tren TIKI.vn",
        # color='d0011b',
        url=url
    )
    embed.set_author(
        name="Cập nhật truyện mới / manga.glhf.vn",
        url="https://manga.glhf.vn/",
        icon_url="https://res.cloudinary.com/glhfvn/image/upload/v1650536017/LOGO_shomth.png"
    )
    embed.set_thumbnail(url=image)
    embed.add_embed_field(name="Giá", value=price)
    embed.set_timestamp()

    webhook.add_embed(embed)
    response = webhook.execute()


parser = argparse.ArgumentParser(
    description='Check an available status of a Tiki item.')
parser.add_argument(
    "--item", help="Id of the product to check", type=int, required=True)
args = parser.parse_args()

t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
r = crawl(args.item)

if (r.get('inventory_status') == 'available'):
    print(f'[{current_time}] AVAILABLE: {r.get("name")}')
    webhooks(r.get('name'), r.get('thumbnail_url'), r.get('short_url'), r.get('list_price'))

if (r.get('inventory_status') == 'out_of_stock') or (r.get('inventory_status') == 'discontinued'):
    print(f'[{current_time}] UNAVAILABLE: {r.get("name")}')
