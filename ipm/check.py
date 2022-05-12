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
import argparse

load_dotenv()
webhook_url = os.environ.get('DISCORD_PUBLISHER_WEBHOOK')


def write_log(content):
    with open("log.txt", "a") as file:
        file.write(f'{content}\n')


def getTheHtml(product: str, option: bool):
    chrome_options = Options()
    chrome_options.headless = True
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=chrome_options)
    driver.get(f"https://ipm.vn/products/{product}")
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product-title"))
        )
    finally:
        if option == True:
            options = driver.find_element(
                by=By.ID, value="product-select-option-0").find_elements(by=By.TAG_NAME, value="option")
            for option in options:
                if str.strip(option.get_attribute("value")) == "Bản Đặc Biệt":
                    option.click()
        page = BeautifulSoup(driver.page_source, features='html.parser')
        driver.quit()
        return page


def check(soup):
    try:
        # if disabled attr exists
        soup.find("select", id="add-to-cart")['disabled']
        return False  # out of stock
    except:
        return {
            'title': str.strip(soup.find("div", class_="product-title").find("h1").get_text()),
            'image': soup.find("img", class_="product-image-feature").get("src"),
            'price': soup.find("div", class_="product-price").find("span").get_text(),
            'og_price': soup.find("div", class_="product-price").find("del").get_text(),
            'status': True  # in stock
        }


def sendWebhook(title, url, image, price, og_price):
    webhook = DiscordWebhook(url=webhook_url, rate_limit_retry=True)
    embed = DiscordEmbed(
        title=title,
        description='Cập nhật trên website IPM',
        # color='01a14b', buggy somehow
        url=url
    )
    embed.set_author(
        name="Co hang / manga.glhf.vn",
        url="https://manga.glhf.vn/",
        icon_url="https://res.cloudinary.com/glhfvn/image/upload/v1650536017/LOGO_shomth.png"
    )
    embed.set_thumbnail(url=image)
    embed.add_embed_field(name="Giá", value=price)
    embed.add_embed_field(name="Giá bìa", value=og_price)
    embed.set_timestamp()

    webhook.add_embed(embed)
    response = webhook.execute()


parser = argparse.ArgumentParser(
    description='Check an available status of a IPM item.')
parser.add_argument(
    "--item", help="Slug of the product to check", type=str, required=True)
parser.add_argument(
    "--advanced", help="Advanced option (checking for 'Ban Dac Biet')", action='store_const', const=True, default=False)
args = parser.parse_args()

# GET CURRENT TIME
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)

# BEGIN CRAWL
soup = getTheHtml(args.item, args.advanced)
try:
    product = check(soup)
    print(f'[{current_time}] AVAILABLE: {product["title"]}')
    sendWebhook(product["title"], f"https://ipm.vn/products/{args.item}",
                f'https://{product["image"]}', product["price"], product["og_price"])
except TypeError or AttributeError:
    print(f'[{current_time}] UNAVAILABLE: {args.item}')
