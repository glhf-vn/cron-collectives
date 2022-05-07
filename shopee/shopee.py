import requests
import pickle
import os
import time
from dotenv import load_dotenv
import argparse
from discord_webhook import DiscordWebhook, DiscordEmbed
from babel.numbers import format_currency

load_dotenv()
webhook_url = os.environ.get('DISCORD_PUBLISHER_WEBHOOK')


def crawl(product_id, shop_id):
    url = f"https://shopee.vn/api/v4/item/get?itemid={str(product_id)}&shopid={str(shop_id)}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    }
    print(url)

    session = requests.session()
    try:
        with open('cookies', 'rb') as file:
            session.cookies.update(pickle.load(file))
    except:
        session.get("https://shopee.vn/", headers=headers)
        with open('cookies', 'wb') as file:
            pickle.dump(session.cookies, file)

    r = session.get(url, headers=headers).json()

    return r['data']


def webhooks(title, image, url, price, description):
    price = format_currency((price), 'VND', locale='vi_VN')

    webhook = DiscordWebhook(url=webhook_url, rate_limit_retry=True)
    embed = DiscordEmbed(
        title=title,
        description=description,
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
    description='Check the stock of a Shopee item.')
parser.add_argument(
    "--item", help="Id of the product to check", type=int, required=True)
parser.add_argument("--shop", help="Id of the product's shop",
                    type=int, required=True)
parser.add_argument(
    "--slug", help="The slug of the shop to generate URL", type=str, required=True)
args = parser.parse_args()

t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
r = crawl(args.item, args.shop)

if (r.get('item_status') == 'normal'):
    print(current_time, 'AVAILABLE:', r.get('name'))
    webhooks(r.get('name'), f'https://cf.shopee.vn/file/{r.get("image")}', f'https://shopee.vn/{args.slug}/{r.get("itemid")}', int(
        r.get('price'))/100000, f"Đã có hàng: {r.get('models')[0].get('stock')} sản phẩm")

if (r.get('item_status') == 'sold_out'):
    print(current_time, 'UNAVAILABLE:', r.get('name'))
