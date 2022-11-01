"""
Discord webhook functions for sending notification to the server
"""

from datetime import date
from discord_webhook import DiscordWebhook, DiscordEmbed


def send_cover_webhook(webhook_url, title, release_date, image_url, **args):
    """
    To send "new cover updated" message
    """

    price = args.pop("price", "Chưa có")

    webhook = DiscordWebhook(url=webhook_url)
    embed = DiscordEmbed(
        title=title,
        url='https://manga.glhf.vn/'
    )
    embed.set_author(
        name="Cập nhật ảnh bìa / manga.glhf.vn",
        url="https://manga.glhf.vn/",
        icon_url="https://res.cloudinary.com/glhfvn/image/upload/v1650536017/LOGO_shomth.png"
    )
    embed.set_image(url=image_url)
    embed.add_embed_field(name="Ngày phát hành", value=release_date)
    embed.add_embed_field(name="Giá dự kiến", value=price)
    embed.set_timestamp()

    webhook.add_embed(embed)
    webhook.execute()


def send_today_releases(webhook_url, lists):
    """
    To send "today releases" message
    """
    current_date = date.today().strftime("%d/%m/%Y")

    webhook = DiscordWebhook(url=webhook_url)
    embed = DiscordEmbed(
        title=f"Phát hành hôm nay - {current_date}",
        url='https://manga.glhf.vn/'
    )
    embed.set_author(
        name="Lịch phát hành / manga.glhf.vn",
        url="https://manga.glhf.vn/",
        icon_url="https://res.cloudinary.com/glhfvn/image/upload/v1650536017/LOGO_shomth.png"
    )
    embed.set_thumbnail(
        url="https://res.cloudinary.com/glhfvn/image/upload/v1652066199/releases.png")
    embed.set_timestamp()

    if all(entry['events'] is None for entry in lists):
        return

    for publisher in lists:
        if publisher['events'] != '':
            embed.add_embed_field(
                name=f'{publisher["icon"]} {publisher["name"]}',
                value=publisher['events'],
                inline=False)
    webhook.add_embed(embed)
    webhook.execute()
