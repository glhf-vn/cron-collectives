import pandas as pd
import time
from discord_webhook import DiscordWebhook, DiscordEmbed

import os
import time
from dotenv import load_dotenv

load_dotenv()
webhook_url = os.environ.get('DISCORD_IPM_REGISTRY_WEBHOOK')


def crawl(publisher_id, check_range, partner):
    registries = []
    for page in range(1, check_range):
        # Set the HTML
        url = f'https://ppdvn.gov.vn/web/guest/ke-hoach-xuat-ban?id_nxb={str(publisher_id)}&p={str(page)}'
        tables = pd.read_html(url)  # Returns list of all tables on page

        for row in range(9):  # Each row has 10 registrations
            # Check for applicable registration (which is a string - not blank, and contain "IPM")
            if (type(tables[0].loc[row, "Đối tác liên kết"]) == str) and (partner in tables[0].loc[row, "Đối tác liên kết"]):
                title = tables[0].loc[row, "Tên xuất bản phẩm"]
                author = tables[0].loc[row, "Tác giả hoặc người biên soạn"]
                registries.append({
                    'title': title,
                    'author': author
                })
        time.sleep(0.2)  # Sleep for 200ms before next request

    return registries


def write_log(content):
    with open("log_ipm.txt", "a") as file:
        file.write(f'{content}\n')


def webhooks(title, author, publisher):
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
    embed.add_embed_field(name="Đối tác xuất bản",
                          value=publisher, inline=False)
    embed.set_timestamp()

    webhook.add_embed(embed)
    response = webhook.execute()


def check_new_registries(registries, publisher, latest, current_time):
    for registry in registries:
        # run until current product matches last latest product
        if str.strip(registry['title']) == str.strip(latest):
            log_content = f'[{current_time}] DUPLICATE AT: {registry["title"]}'
            write_log(str(log_content))
            break
        else:
            log_content = f'[{current_time}] NEW: {registry["title"]}'
            write_log(str(log_content))
            webhooks(registry['title'], registry['author'], publisher)


# READ LATEST REGISTRY
latest_registry = {'hong_duc': '', 'ha_noi': ''}
try:
    with open("latest_ipm.txt", "r") as file:
        lines = file.readlines()
    latest_registry['hong_duc'] = lines[0]
    latest_registry['ha_noi'] = lines[1]
except:
    latest_registry['hong_duc'] = ''
    latest_registry['ha_noi'] = ''

# GET CURRENT TIME
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)

hong_duc = check_new_registries(crawl(
    56, 20, "IPM"), "Hồng Đức", latest_registry['hong_duc'], current_time)  # 56 = Hong Duc
ha_noi = check_new_registries(crawl(
    28, 20, "IPM"), "NXB Hà Nội", latest_registry['ha_noi'], current_time)  # 28 = Ha Noi

# UPDATE THE LATEST REGISTRIES
latest_registry['hong_duc'] = crawl(56, 20, "IPM")[0]['title']
latest_registry['ha_noi'] = crawl(28, 20, "IPM")[0]['title']
with open("latest_ipm.txt", "wt") as file:
    file.write(latest_registry['hong_duc'] + '\n')
    file.write(latest_registry['ha_noi'] + '\n')
