from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
from datetime import datetime

#TODO select font path
font_path = './splat/fonts/DFP_GBZY9.ttf'
URL = "./splat/images/"



def render_battle(li, tz = "东部"):
    width = 400
    height = 1000
    i = 0
    re = Image.new("RGBA", (width, height), "white")
    draw  = ImageDraw.Draw(re)
    x = 100
    y = 40
    for idx, item in enumerate(li):
        start = item['start']
        end = item['end']
        name = item['name_cn']
        url = item['img']
          
        # Open the image using Pillow
        image_to_add = Image.open(url)
        
        # Resize image:
        scale = 0.3
        size = (int(scale * image_to_add.size[0]), int(scale * image_to_add.size[1]))
        image_to_add = image_to_add.resize(size)

        # Put add image
        position = (x, y)

        re.paste( image_to_add,position)
        
        # Choose a font and size
        font = ImageFont.truetype("arial.ttf", size=18)
        
        # Specify text position
        text_position = (0, y)
        end_position = (0,y+30)
    
        # Add text to the image
        draw.text(text_position, start, fill="black", font=font)
        draw.text(end_position, end, fill="black", font=font)

        # Update x y
        x = 340 - x
        if idx % 2 == 1:
            y+= 70


            
        i = 1 - i
    return re

def render_zg(li, tz = "东部"):
    width = 400
    height = 1000
    i = 0
    re = Image.new("RGBA", (width, height), "white")
    draw  = ImageDraw.Draw(re)
    x = 100
    y = 40
    for idx, item in enumerate(li):
        # print(item)
        start = item['start']
        end = item['end']
        name = item['name_cn']
        url = item['img']
        rule = item['rule']
            
        # Open the image using Pillow
        image_to_add = Image.open(url)
        
        # Resize image:
        scale = 0.3
        size = (int(scale * image_to_add.size[0]), int(scale * image_to_add.size[1]))
        image_to_add = image_to_add.resize(size)

        # Add image
        position = (x, y)


        re.paste( image_to_add,position)
        
        rule_position = (0,y+50)
        link = URL+"rule/"+rule+".png"
        rule_img = Image.open(link)
        # Resize image
        scale = 0.2
        size = (int(scale * rule_img.size[0]), int(scale * rule_img.size[1]))
        rule_img = rule_img.resize(size)
        # Add image
        re.paste( rule_img,rule_position)

        # Choose a font and size
        font = ImageFont.truetype(font_path, size=18)

        
        # Specify text position
        text_position = (0, y)
        end_position = (0, y+25)
    
        # Add text to the image
        draw.text(text_position, start, fill="black", font=font)
        draw.text(end_position, end, fill="black", font=font)

        # Update x y
        x = 340 - x
        if idx % 2 == 1:
            y+= 70

        i = 1 - i
    return re

def render_coop(li, tz = "东部"):
    width = 400
    height = 1060 - (5 - len(li)) * 160
    dim = (width,height)

    re = Image.new("RGBA", dim, "white")

    # Set background colors
    color = Image.new('RGBA', dim, (0, 0, 0, 0))
    draw = ImageDraw.Draw(color)
    draw.rectangle([0, 0, width, height], fill=(255, 98, 8, 255))
    re = Image.alpha_composite(re, color)

    # Set background overlay
    background_path = URL+"misc/coop_bg.PNG"
    background = Image.open(background_path)
    scale = 0.05
    size = (int(scale * background.size[0]), int(scale * background.size[1]))
    background = background.resize(size)
    for x in range(0, width, background.width):
        for y in range(0, height, background.height):
            re.paste(background, (x, y), background)

    draw  = ImageDraw.Draw(re)

    x = 0
    y = 420

    for idx, item in enumerate(li):
        start = item['start']
        end = item['end']
        boss = item['name_en']
        url = item['img']
        weapons_name = item['weapons_name']
        remain = item['remain']
        stage_cn = item['stage_cn']

        image_to_add = Image.open(url)
        if idx == 0:
            # Resize image:
            scale = 1
            size = (int(scale * image_to_add.size[0]), int(scale * image_to_add.size[1]))
            image_to_add = image_to_add.resize(size)
            
            position = (0, y-320)
            # image_to_add.show()
            re.paste(image_to_add,position)
            # Choose a font and size
            font = ImageFont.truetype(font_path, size=20)

            # Calculate remaining time            
            hours, remainder = divmod(remain.seconds, 3600)
            if remain.days == 1:
                hours +=24
            minutes, seconds = divmod(remainder, 60)
            
            # Add text to the image
            txt = "开放中: " + end + ", 剩余：" + str(hours)+ "时" + str(minutes) + "分" 
            text_width = draw.textlength(txt,font=font)
            _x = int((width - text_width) / 2)
            _y = y-350
            left, top, right, bottom = draw.textbbox((_x,_y),txt,font=font)
            draw.rectangle((left-10, top-5, right+10, bottom+5),fill="black")
            draw.text((_x,_y), txt, fill="white", font=font)

            # Add Boss
            position = (0,y-200)
            link = URL+"bosses/"+boss+".png"
            boss_img = Image.open(link)
            size = (80,80)
            boss_img = boss_img.resize(size)
            re.paste(boss_img,position,boss_img)
            
            # Add stage name
            stage_font = ImageFont.truetype(font_path, size=30)
            text_width = draw.textlength(stage_cn,font=stage_font)
            _x = int((width - text_width) / 2)
            _y = y-160
            left, top, right, bottom = draw.textbbox((_x,_y),stage_cn,font=stage_font)
            draw.rectangle((left-10, top-5, right+10, bottom+5),fill="black")
            draw.text((_x, _y),stage_cn,fill="white",font=stage_font)

            # Add weapons for main stage
            draw.rounded_rectangle((20,y-120,380,y-50),radius=8,fill="black")
            _y = y-120
            for idx2, wp in enumerate(weapons_name):
                link = URL+"weapons/"+wp+".webp"
                image_to_add = Image.open(link)

                size = (70,70)
                image_to_add = image_to_add.resize(size)

                _x = 24 + 94*idx2
                position = (_x, _y)
                re.paste(image_to_add,position, image_to_add)

            # draw.line((0, 60, 400, 60), fill=(0, 0, 0), width=5)


        else:
            x = 20
            # Resize image:
            scale = 0.56
            size = (int(scale * image_to_add.size[0]), int(scale * image_to_add.size[1]))
            image_to_add = image_to_add.resize(size)

            position=(x,y)
            re.paste(image_to_add,position)

            # Add time shift
            txt = start + " - " + end 

            font = ImageFont.truetype(font_path, size=20)
            text_width = draw.textlength(txt,font=font)
            _x = int((width - text_width) / 2)
            _y = y-35
            left, top, right, bottom = draw.textbbox((_x,_y),txt,font=font)
            draw.rectangle((left-10, top-5, right+10, bottom+5),fill="black")
            draw.text((_x,_y), txt, fill="white", font=font)


            # Add Boss
            position = (x,y+50)
            link = URL+"bosses/"+boss+".png"
            boss_img = Image.open(link)
            size = (60,60)
            boss_img = boss_img.resize(size)
            re.paste(boss_img,position,boss_img)

            # Add stage name
            stage_font = ImageFont.truetype(font_path, size=20)
            text_width = draw.textlength(stage_cn,font=stage_font)
            _x = int((image_to_add.width - text_width) / 2) + x
            _y = y + 4
            left, top, right, bottom = draw.textbbox((_x,_y),stage_cn,font=stage_font)
            draw.rectangle((left-10, top-4, right+10, bottom+4),fill="black")
            draw.text((_x, _y),stage_cn,fill="white",font=stage_font)

            # Add weapons
            _x = 245+x
            _y = y
            draw.rounded_rectangle((_x-5,_y,_x+112+5,_y+112),radius=8,fill="black")
            for idx2, wp in enumerate(weapons_name):
                link = URL+"weapons/"+wp+".webp"
                image_to_add = Image.open(link)

                size = (56,56)
                image_to_add = image_to_add.resize(size)

                __x = _x + 56 * (idx2 // 2)
                __y = _y + 56 * (idx2 % 2)
                position = (__x, __y)
                re.paste(image_to_add,position, image_to_add)

            y += 160
        # draw.line((0, y-40, 400, y-40), fill=(0, 0, 0), width=5)
    return re