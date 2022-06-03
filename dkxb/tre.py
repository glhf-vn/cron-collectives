import pandas as pd
import time
from discord_webhook import DiscordWebhook, DiscordEmbed

import os
import time
from dotenv import load_dotenv

load_dotenv()
webhook_url = os.environ.get('DISCORD_TRE_REGISTRY_WEBHOOK')


def crawl(publisher_id, check_range):
    registries = []
    for page in range(1, check_range):
        # Set the HTML
        url = f'https://ppdvn.gov.vn/web/guest/ke-hoach-xuat-ban?id_nxb={str(publisher_id)}&p={str(page)}'
        tables = pd.read_html(url)  # Returns list of all tables on page

        for row in range(9):  # Each row has 10 registrations
            # Check for applicable registration (which is a string - not blank, and contain a translator)
            if (type(tables[0].loc[row, "Người dịch hoặc người biên dịch"]) == str):
                title = tables[0].loc[row, "Tên xuất bản phẩm"]
                author = tables[0].loc[row, "Tác giả hoặc người biên soạn"]
                registries.append({
                    'title': title,
                    'author': author
                })
        time.sleep(0.2)  # Sleep for 200ms before next request

    return registries


def write_log(content):
    with open("log.txt", "a") as file:
        file.write(f'{content}\n')


def webhooks(title, author):
    webhook = DiscordWebhook(url=webhook_url, rate_limit_retry=True)
    embed = DiscordEmbed(
        title=title,
        #color = '05729C',
    )
    embed.set_author(
        name="Đăng ký xuất bản / manga.glhf.vn",
        url="https://manga.glhf.vn/",
        icon_url="https://res.cloudinary.com/glhfvn/image/upload/v1650536017/LOGO_shomth.png"
    )
    embed.add_embed_field(name="Tác giả", value=author, inline=False)
    embed.add_embed_field(name="Nhà xuất bản",
                          value="NXB Trẻ", inline=False)
    embed.set_timestamp()

    webhook.add_embed(embed)
    response = webhook.execute()


# READ LATEST REGISTRY
latest_registry = ''
try:
    with open("latest_tre.txt", "r") as file:
        latest_registry = file.read().rstrip()
except:
    latest_registry = ''

# GET CURRENT TIME
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)

registries = crawl(37, 3)  # 37 = Tre

for registry in registries:
    # run until current product matches last latest product
    if str.strip(registry['title']) == str.strip(latest_registry):
        log_content = f'[{current_time}] DUPLICATE AT: {registry["title"]}'
        write_log(str(log_content))
        break
    else:
        log_content = f'[{current_time}] NEW: {registry["title"]}'
        write_log(str(log_content))
        webhooks(registry['title'], registry['author'])


# UPDATE THE LATEST REGISTRIES
latest_registry = registries[0]['title']
with open("latest_tre.txt", "wt") as file:
    file.write(latest_registry)
