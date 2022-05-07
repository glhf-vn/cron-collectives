from babel.numbers import format_currency
import requests
import time
from discord_webhook import DiscordWebhook, DiscordEmbed

def getTheProducts():
  url = "https://tiki.vn/api/personalish/v1/blocks/listings?limit=24&category=1084&page=1&sort=newest&seller=1&urlKey=truyen-tranh"

  r = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0'
        }).json()

  return r['data']

def webhooks(title, url, image, price, og_price, author, description):
  price = format_currency((price), 'VND', locale='vi_VN')
  og_price = format_currency((og_price), 'VND', locale='vi_VN')

  webhook = DiscordWebhook(url='https://discord.com/api/webhooks/969810331545264168/3_QkSaBjsRk1j6IlsnmySl4v7HyeTQm4CGUFhxw5k6NDluLL9uN6hISwdTUS9MMItCbT')
  embed = DiscordEmbed(
      title = title,
      description = description,
      color = '1a94ff',
      url = url
  )
  embed.set_author(
      name = "Cập nhật truyện mới / manga.glhf.vn",
      url = "https://manga.glhf.vn/",
      icon_url = "https://res.cloudinary.com/glhfvn/image/upload/v1650536017/LOGO_shomth.png"
  )
  embed.set_thumbnail(url=image)
  embed.add_embed_field(name="Tác giả", value=author, inline=False)
  embed.add_embed_field(name="Giá", value=price)
  embed.add_embed_field(name="Giá bìa", value=og_price)
  embed.set_timestamp()

  webhook.add_embed(embed)
  response = webhook.execute()

  time.sleep(2)

# READ LATEST PRODUCT
f = open("tiki_latest.txt", "r")
product_latest = f.read()
f.close() 

# GET CURRENT TIME
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)

# BEGIN CRAWL
product_array = getTheProducts()

# OPEN THE LOG
log = open("tiki_log.txt", "a")

# CHECK FOR NEW PRODUCTS
for product in product_array:
  print(str.strip(product['name']), str.strip(product_latest))
  if str.strip(product['name']) == str.strip(product_latest): # run until current product matches last latest product
    log_content = '[' + current_time + ']' + 'DUPLICATE AT:' + product['name']
    log.write(str(log_content))
    break
  else:
    log_content = '[' + current_time + ']' + 'NEW:' + product['name']
    log.write(str(log_content))
    webhooks(product['name'], 'https://tiki.vn/' + product['url_path'], product['thumbnail_url'], product['price'], product['list_price'], product['author_name'], product['short_description'])

# WRITE LATEST PRODUCT
f = open("tiki_latest.txt", "w")
f.write(product_array[0]['name'])
f.close()

log_content = '[' + current_time + ']' + 'LATEST:' + product_array[0]['name']
log.write(str(log_content))
log.close()
