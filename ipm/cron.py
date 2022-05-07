from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Drivers
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup
from babel.numbers import format_currency
from discord_webhook import DiscordWebhook, DiscordEmbed

import os
import time
from dotenv import load_dotenv

load_dotenv()
webhook_url = os.environ.get('DISCORD_PUBLISHER_WEBHOOK')


def write_log(content):
    with open("log.txt", "a") as file:
        file.write(f'{content}\n')


def getTheHtml():
    chrome_options = Options()
    chrome_options.headless = True
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://ipm.vn/")
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "home_sach-moi"))
        )
    finally:
        page = BeautifulSoup(driver.page_source, features='html.parser')
        driver.quit()
        return page


def getTheProducts(soup):
    product_array = []
    product_list = soup.find_all(
        "div", class_="hnt-wrap")[0].find_all("div", class_="product-block")
    for product in product_list:
        title = str.strip(product.find(
            "h3", class_="pro-name").find("a").get("title"))
        url = product.find("h3", class_="pro-name").find("a").get("href")
        image = product.find("div", class_="img").find("img").get("src")
        price = product.find("p", class_="pro-price").get_text()
        og_price = product.find("p", class_="pro-price-del").get_text()

        product_array.append({
            'title': title,
            'url': f'https://ipm.vn{url}',
            'image': f'https:{image}',
            'price': format_currency(int(''.join(filter(str.isdigit, price))), 'VND', locale='vi_VN'),
            'og_price': format_currency(int(''.join(filter(str.isdigit, og_price))), 'VND', locale='vi_VN')
        })
    return product_array


def sendWebhook(title, url, image, price, og_price):
    webhook = DiscordWebhook(url=webhook_url, rate_limit_retry=True)
    embed = DiscordEmbed(
        title=title,
        description='Cập nhật trên website IPM',
        # color='01a14b', buggy somehow
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
    with open("latest.txt", "r") as file:
        last_product = file.read().rstrip()
except:
    last_product = ''

# GET CURRENT TIME
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)

# BEGIN CRAWL
soup = getTheHtml()
product_array = getTheProducts(soup)

# CHECK FOR NEW PRODUCTS
for product in product_array:
    if product['title'] == last_product:  # run until current product matches last latest product
        write_log(f'[{current_time}] DUPLICATE AT: {product["title"]}')
        break
    else:
        write_log(f'[{current_time}] NEW: {product["title"]}')
        sendWebhook(product['title'], product['url'],
                    product['image'], product['price'], product['og_price'])

# WRITE LATEST PRODUCT
with open("latest.txt", "w") as file:
    file.write(product_array[0]['title'])
