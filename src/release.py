"""
Run as a cron job for getting today releases
"""

from datetime import datetime, timedelta, date, time, timezone
import os

from dotenv import load_dotenv

from lib.calendar_events import get_events
from lib.discord_webhook import send_today_releases

load_dotenv()
WEBHOOK_URL = os.environ.get('DISCORD_UPDATES_WEBHOOK')


def get_the_events(calendar_id):
    events_list: str = ''

    events = get_events(calendar_id=calendar_id,
                        start_time=datetime.combine(
                            date.today(), time(), timezone(timedelta(hours=7))).isoformat(),
                        end_time=datetime.combine(
                            date.today() + timedelta(1), time(), timezone(timedelta(hours=7))).isoformat())

    if events:
        for event in events:
            events_list += f"{event['summary']}\n"

    return events_list


def main():
    lists = [
        {
            'name': 'NXB Kim Đồng',
            'icon': '<:nxbkimdong:973132429483184138>',
            'events': get_the_events('kim0qh2rt2k3pts7mhs9pdf84s@group.calendar.google.com'),
        },
        {
            'name': 'NXB Trẻ',
            'icon': '<:nxbtre:973132427935502356>',
            'events': get_the_events('55vfna92d05k21up0brcmsbq0o@group.calendar.google.com'),
        },
        {
            'name': 'AMAK',
            'icon': '<:amak:973128525647319040>',
            'events': get_the_events('fjevdjbpr2m9r5gooaigs3595s@group.calendar.google.com'),
        },
        {
            'name': 'Hikari',
            'icon': '<:hikari:973132428715626516>',
            'events': get_the_events('d4oi2g1csqm6d2a0e71j6fpjuo@group.calendar.google.com'),
        },
        {
            'name': 'Ichi Light Novels',
            'icon': '<:ichiln:973132429147652106>',
            'events': get_the_events('s4m05q1nrpuq7p40ml2ct30jh8@group.calendar.google.com'),
        },
        {
            'name': 'IPM',
            'icon': '<:ipm:973127092004880444>',
            'events': get_the_events('7ht69okrmeph6snctucjn77vt0@group.calendar.google.com'),
        },
        {
            'name': 'SkyComics',
            'icon': '<:skycomics:973132403440758814>',
            'events': get_the_events('aammvnpdffcsq4oen8er6e6v10@group.calendar.google.com'),
        },
        {
            'name': 'Tsuki LightNovels',
            'icon': '<:tsuki:973132863228743730>',
            'events': get_the_events('5kjai0tie7kubu4nqls4j8e3uk@group.calendar.google.com'),
        },
        {
            'name': 'Uranix',
            'icon': '<:uranix:973132428656934962>',
            'events': get_the_events('5756jhpd8sj8doer4j39tsopl0@group.calendar.google.com'),
        },
        {
            'name': 'WingsBooks',
            'icon': '<:wingsbooks:973128536292474880>',
            'events': get_the_events('1eajtmaus1kib4s8mgd3cp82ho@group.calendar.google.com'),
        }
    ]

    send_today_releases(WEBHOOK_URL, lists)


if __name__ == "__main__":
    main()
