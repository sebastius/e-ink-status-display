import requests

from datetime import datetime

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import feedparser

import epd7in5
from defs import (BUIENRADAR_ICONS, WIND_SCALE)
from wordclock import time_str

import time

WHITE = 0xFF
BLACK = 0x00
FONT_SIZE = 24
WEATHER_CODE = 2757345
WEATHER_STATION = 6344
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
NEWS_FEED = 'http://feeds.nos.nl/nosnieuwsalgemeen'

#configuration
back_ground_color = (255, 255, 255)
font_size = 24

font_small = ImageFont.truetype('Roboto-Bold.ttf', 16)
font = ImageFont.truetype('Roboto-Bold.ttf', 20)
font_big = ImageFont.truetype('Roboto-Bold.ttf', 36)
weather_font = ImageFont.truetype("./weathericons-regular-webfont.ttf", FONT_SIZE)
weather_font_big = ImageFont.truetype("./weathericons-regular-webfont.ttf", 36)

epd = epd7in5.EPD()
epd.init()

Himage = Image.new('1', (epd7in5.EPD_WIDTH, epd7in5.EPD_HEIGHT), 255)  # 255: clear the frame    
draw = ImageDraw.Draw(Himage)

url = 'https://forecast.buienradar.nl/2.0/forecast/{}'.format(WEATHER_CODE)
r = requests.get(url)

future_data = r.json()
days = future_data['days']


i = 0
today = days[0]
wind = WIND_SCALE.get(today['windspeed'])
sunrise = datetime.strptime(today['sunset'], DATE_FORMAT).strftime('%H:%M')

# Wind / sunset / 
draw.text((0, i), wind, font=weather_font, fill=0)
draw.text((35, i), "\uf052", font=weather_font, fill=0)
draw.text((70, i+4), sunrise, font=font, fill=0)

now = datetime.now()
timestr = time_str(now.hour, now.minute)
draw.text((280, i), timestr, font=font_big, fill=0)

i += 40

current_hour = days[0]['hours'][0]
iconcode = BUIENRADAR_ICONS.get(current_hour['iconcode'])
current_temp = str(round(current_hour['temperature']))

# Current temp
draw.text((0, i), iconcode, font=weather_font_big, fill=0)
draw.text((60, i), current_temp, font=font_big, fill=0)
draw.text((110, i), "\uf03c", font=weather_font_big, fill=0)


i += 50

draw.text((0, i), "----------------------", font=font, fill=0)

i += 20

for index, day in enumerate(days):
    # Skip today
    if index == 0:
        continue

    # Show 4 future days.
    if index == 5:
        break
    maxtemp = day['maxtemp']
    mintemp = day['mintemp']
    daytxt = datetime.strptime(day['datetime'], '%Y-%m-%dT%H:%M:%S').strftime('%a')
    iconcode = BUIENRADAR_ICONS.get(day['iconcode'])
    draw.text((0, i), daytxt, font=font)
    draw.text((50, i), iconcode, font=weather_font, fill=0)
    draw.text((90, i), "{}  {}".format(maxtemp, mintemp), font=font)
    i += 30


i += 10
draw.text((0, i), "Nieuws", font=font)
i += 10
draw.text((0, i), "--------", font=font)
i += 30
news_data = feedparser.parse(NEWS_FEED)
for index, entry in enumerate(news_data['items']):
    if index == 5:
        break

    draw.text((0, i), "- " + entry['title'], font=font_small, fill=0)
    i += 20

buf = epd.getbuffer(Himage)

print("Clear...")
print(time.ctime())
epd.Clear()
print('display the frame')
epd.display(buf)
print(time.ctime())
time.sleep(2)

epd.sleep()
