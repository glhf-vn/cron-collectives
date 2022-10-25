"""
Discord webhook functions for sending notification to the server
"""

from discord_webhook import DiscordWebhook, DiscordEmbed


def send_cover_webhook(webhook_url, title, release_date, image_url, **args):
    """
    To send "new cover updated" message
    """

    price = args.pop("price", "Chưa có")
    publisher = args.pop("publisher", "N/A")

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
    embed.add_embed_field(name="Nhà xuất bản", value=publisher, inline=False)
    embed.add_embed_field(name="Ngày phát hành", value=release_date)
    embed.add_embed_field(name="Giá dự kiến", value=price)
    embed.set_timestamp()

    webhook.add_embed(embed)
    webhook.execute()
