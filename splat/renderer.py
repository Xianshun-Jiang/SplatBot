from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests


def render_battle(li):
    width = 400
    height = 1000
    i = 0
    re = Image.new("RGB", (width, height), "white")
    tmp  = ImageDraw.Draw(re)
    x = 100
    y = 40
    for idx, item in enumerate(li):
        # print(item)
        start = item['start']
        end = item['end']
        name = item['name_cn']
        url = item['img']
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Read the content of the response as bytes
            image_bytes = BytesIO(response.content)
            
            # Open the image using Pillow
            image_to_add = Image.open(image_bytes)
            
            # Resize image:
            scale = 0.3
            size = (int(scale * image_to_add.size[0]), int(scale * image_to_add.size[1]))
            image_to_add = image_to_add.resize(size)

            # Put add image
            position = (x, y)
            x = 340 - x
            #x=100 is the default 
            if x == 100:
                y+= 70

            re.paste( image_to_add,position)
            
            # Choose a font and size
            font = ImageFont.truetype("arial.ttf", size=18)
            
            # Specify text position
            text_position = (0, y)
            end_position = (0,y+30)
        
            # Add text to the image
            tmp.text(text_position, start, fill="black", font=font)
            tmp.text(end_position, end, fill="black", font=font)


            
        else:
            # If the request failed, print an error message
            print(f"Failed to retrieve image from URL: {url}")
            return None
        i = 1 - i
    return re

def render_coop(li):
    width = 400
    height = 1000
    i = 0
    re = Image.new("RGB", (width, height), "white")
    tmp  = ImageDraw.Draw(re)
    x = 0
    y = 340
    for idx, item in enumerate(li):
        start = item['start']
        end = item['end']
        boss = item['name_cn']
        url = item['img']
        weapons = item['weapons']
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Read the content of the response as bytes
            image_bytes = BytesIO(response.content)

            # Open the image using Pillow
            image_to_add = Image.open(image_bytes)
            # print(idx)
            if idx == 0:
                # Resize image:
                scale = 1
                size = (int(scale * image_to_add.size[0]), int(scale * image_to_add.size[1]))
                image_to_add = image_to_add.resize(size)
                
                position = (0, 50)
                # image_to_add.show()
                re.paste(image_to_add,position)
                # Choose a font and size
                font = ImageFont.truetype("arial.ttf", size=20)
                
                # Specify text position
                text_position = (0, 10)
                txt = start + " - " + end + "Boss: "+ boss

                # Add text to the image
                tmp.text(text_position, start + " - " + end + " Boss: "+ boss, fill="black", font=font)
                for wp in weapons:
                    response = requests.get(url)

            else:
                # Resize image:
                scale = 0.5
                size = (int(scale * image_to_add.size[0]), int(scale * image_to_add.size[1]))
                image_to_add = image_to_add.resize(size)

                position=(x,y)
                re.paste(image_to_add,position)
                y += 160


            # re.show()
            # print(item)
    return re