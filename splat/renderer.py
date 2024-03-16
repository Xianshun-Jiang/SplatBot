from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
import requests
from datetime import datetime

#TODO select font path
font_path = './splat/fonts/DFP_GBZY9.ttf'

def render_battle(li, tz = "东部", rule = "占地模式", URL= None):
    width = 400
    height = 400+ len(li) * 80
    re = Image.new("RGBA", (width, height), "white")
    draw  = ImageDraw.Draw(re)

    # Set background colors
    color = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(color)
    draw.rectangle([0, 0, width, height], fill=(23, 199, 26, 255))
    re = Image.alpha_composite(re, color)

    # Set background overlay
    background_path = URL+"misc/fight_mask.png"
    background = Image.open(background_path)
    scale = 0.05
    size = (int(scale * background.size[0]), int(scale * background.size[1]))
    background = background.resize(size)
    for x in range(0, width, background.width):
        for y in range(0, height, background.height):
            re.paste(background, (x, y), background)

    # Update draw
    draw  = ImageDraw.Draw(re)

    # Display timezone 
    txt = rule + tz + "时间"
    font = ImageFont.truetype(font_path, size=40)
    text_width = draw.textlength(txt,font=font)
    _x = int((width - text_width) / 2)
    _y = 30
    left, top, right, bottom = draw.textbbox((_x,_y), txt, font=font)
    draw.rectangle((left-10, top-5, right+10, bottom+5), fill="black")
    draw.text((_x,_y), txt, fill="white", font=font)

    x = 100
    y = 500
    for idx, item in enumerate(li):
        start = item['start']
        end = item['end']
        name = item['name_cn']
        url = item['img']
        remain = item['remain']
        if idx < 2:
            if idx % 2 == 0:
                # Setup frame background
                draw.rounded_rectangle((20,100,380,480),radius=8,fill="#202020")

                # Calculate remaining time            
                hours, remainder = divmod(remain.seconds, 3600)
                minutes, seconds = divmod(remainder, 90)
                # Add remaining time 
                txt = "开放中, 现在 -" + end.split()[1]
                _font = ImageFont.truetype(font_path, size=26) 
                text_width = draw.textlength(txt,font=_font)
                _x = int((width - text_width) / 2)
                _y = 460
                left, top, right, bottom = draw.textbbox((_x,_y),txt,font=_font)
                draw.rectangle((left-10, top-5, right+10, bottom+5),fill="black")
                draw.text((_x,_y), txt, fill="white", font=_font)

            # Add stage image
            stage = Image.open(url).convert("RGBA")
            # Resize image:
            scale = 0.8
            size = (int(scale * stage.size[0]), int(scale * stage.size[1]))
            stage = stage.resize(size)
            stage = circle_corner(stage, 20)

            _x = int((width- stage.width) / 2)
            _y = 120
            if idx % 2 == 1:
                _y = 180 + _y
            position = (_x,_y)
            re.paste(stage,position, stage)

            # Add stage name
            _font = ImageFont.truetype(font_path, size=24)
            text_width = draw.textlength(name, font=_font)
            _x = int((width - text_width) / 2)
            __y = _y + (stage.height - _font.size)/2
            position = (_x, __y)
            left, top, right, bottom = draw.textbbox((_x,__y), name, font=_font)
            draw.rectangle((left-10, top-5, right+10, bottom+5), fill="black")
            draw.text((_x,__y), name, fill="white", font=_font)

        else: 
            if idx % 2 == 0:
                # Setup frame background
                draw.rounded_rectangle((20,y,380,y+140),radius=8,fill="#202020")
                # Add time period
                time = start + " - " + end.split()[1]
                _font = ImageFont.truetype(font_path, size=20)
                text_width = draw.textlength(time, font=_font)
                _x = int((width - text_width) / 2)
                _y = y+3
                # left, top, right, bottom = draw.textbbox((_x,_y), txt, font=_font)
                # draw.rectangle((left-10, top-5, right+10, bottom+5), fill="black")
                draw.text((_x,_y), time, fill="white", font=_font)
                    
            # Add stage image
            stage = Image.open(url).convert("RGBA")
            # Resize image:
            scale = 0.4
            size = (int(scale * stage.size[0]), int(scale * stage.size[1]))
            stage = stage.resize(size)
            stage = circle_corner(stage, 20)

            _x = int((360- 2 * stage.width) / 4)+ 20
            if idx % 2 == 1:
                _x = 180 + _x
            position = (_x, y + 35)
            re.paste(stage,position, stage)

            # Add stage name
            _font = ImageFont.truetype(font_path, size=16)
            text_width = draw.textlength(name, font=_font)
            _x = _x + int((stage.width - text_width) / 2)
            _y = y + 110
            position = (_x, _y)
            left, top, right, bottom = draw.textbbox((_x,_y), name, font=_font)
            draw.rectangle((left-10, top-5, right+10, bottom+5), fill="black")
            draw.text((_x,_y), name, fill="white", font=_font)

            
            # Update y
            if idx % 2 == 1:
                y+= 160

    return re

def render_zg(li, tz = "东部",rule = "真格挑战", URL= None):
    width = 400
    height = 400+ len(li) * 80
    re = Image.new("RGBA", (width, height), "white")
    draw  = ImageDraw.Draw(re)

    # Set background colors
    color = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(color)
    if rule == "X比赛":
        draw.rectangle([0, 0, width, height], fill=(15, 201, 145, 255))
    else:
        draw.rectangle([0, 0, width, height], fill=(255, 98, 8, 255))
    re = Image.alpha_composite(re, color)

    # Set background overlay
    background_path = URL+"misc/fight_mask.png"
    background = Image.open(background_path)
    scale = 0.05
    size = (int(scale * background.size[0]), int(scale * background.size[1]))
    background = background.resize(size)
    for x in range(0, width, background.width):
        for y in range(0, height, background.height):
            re.paste(background, (x, y), background)

    # Update draw
    draw  = ImageDraw.Draw(re)

    # Display timezone 
    txt = rule + tz + "时间"
    font = ImageFont.truetype(font_path, size=40)
    text_width = draw.textlength(txt,font=font)
    _x = int((width - text_width) / 2)
    _y = 30
    left, top, right, bottom = draw.textbbox((_x,_y), txt, font=font)
    draw.rectangle((left-10, top-5, right+10, bottom+5), fill="black")
    draw.text((_x,_y), txt, fill="white", font=font)


    x = 100
    y = 500
    for idx, item in enumerate(li):
        start = item['start']
        end = item['end']
        name = item['name_cn']
        url = item['img']
        rule = item['rule']
        remain = item['remain']
        if idx < 2:
            if idx % 2 == 0:
                # Setup frame background
                draw.rounded_rectangle((20,100,380,480),radius=8,fill="#202020")

                # Calculate remaining time            
                hours, remainder = divmod(remain.seconds, 3600)
                minutes, seconds = divmod(remainder, 90)
                # Add remaining time 
                txt = "开放中, 现在 -" + end.split()[1]
                _font = ImageFont.truetype(font_path, size=26) 
                text_width = draw.textlength(txt,font=_font)
                _x = int((width - text_width) / 2)
                _y = 460
                left, top, right, bottom = draw.textbbox((_x,_y),txt,font=_font)
                draw.rectangle((left-10, top-5, right+10, bottom+5),fill="black")
                draw.text((_x,_y), txt, fill="white", font=_font)

            # Add stage image
            stage = Image.open(url).convert("RGBA")
            # Resize image:
            scale = 0.8
            size = (int(scale * stage.size[0]), int(scale * stage.size[1]))
            stage = stage.resize(size)
            stage = circle_corner(stage, 20)

            _x = int((width- stage.width) / 2)
            _y = 120
            if idx % 2 == 1:
                _y = 180 + _y
            position = (_x,_y)
            re.paste(stage,position, stage)

            # Add stage name
            _font = ImageFont.truetype(font_path, size=24)
            text_width = draw.textlength(name, font=_font)
            _x = int((width - text_width) / 2)
            __y = _y + (stage.height - _font.size)/2
            position = (_x, __y)
            left, top, right, bottom = draw.textbbox((_x,__y), name, font=_font)
            draw.rectangle((left-10, top-5, right+10, bottom+5), fill="black")
            draw.text((_x,__y), name, fill="white", font=_font)

            # Add Rule
            if idx % 2 == 1:
                link = URL+"rule/"+rule+".png"
                rule_img = Image.open(link)
                size= (100,100)
                rule_img = rule_img.resize(size)
                rule_position = (int((width -rule_img.width)/2), int(_y - size[1]/2))
                re.paste( rule_img,rule_position,rule_img)

        else: 
            if idx % 2 == 0:
                # Setup frame background
                draw.rounded_rectangle((20,y,380,y+140),radius=8,fill="#202020")
                # Add time period
                time = start + " - " + end.split()[1]
                _font = ImageFont.truetype(font_path, size=20)
                text_width = draw.textlength(time, font=_font)
                _x = int((width - text_width) / 2)
                _y = y+3
                # left, top, right, bottom = draw.textbbox((_x,_y), txt, font=_font)
                # draw.rectangle((left-10, top-5, right+10, bottom+5), fill="black")
                draw.text((_x,_y), time, fill="white", font=_font)
                    
            # Add stage image
            stage = Image.open(url).convert("RGBA")
            # Resize image:
            scale = 0.4
            size = (int(scale * stage.size[0]), int(scale * stage.size[1]))
            stage = stage.resize(size)
            stage = circle_corner(stage, 20)

            _x = int((360- 2 * stage.width) / 4)+ 20
            if idx % 2 == 1:
                _x = 180 + _x
            position = (_x, y + 35)
            re.paste(stage,position, stage)

            # Add stage name
            _font = ImageFont.truetype(font_path, size=16)
            text_width = draw.textlength(name, font=_font)
            _x = _x + int((stage.width - text_width) / 2)
            _y = y + 110
            position = (_x, _y)
            left, top, right, bottom = draw.textbbox((_x,_y), name, font=_font)
            draw.rectangle((left-10, top-5, right+10, bottom+5), fill="black")
            draw.text((_x,_y), name, fill="white", font=_font)

            # Add rule
            if idx % 2 == 1:
                link = URL+"rule/"+rule+".png"
                rule_img = Image.open(link)
                size= (70,70)
                rule_img = rule_img.resize(size)
                rule_position = (int((width -rule_img.width)/2), y+40)
                re.paste( rule_img,rule_position,rule_img)
            

            # Update y
            if idx % 2 == 1:
                y+= 160


    return re

def render_coop(li, tz = "东部", URL= None):
    width = 400
    height = 260 + len(li) * 160

    re = Image.new("RGBA", (width,height), "white")

    # Set background colors
    color = Image.new('RGBA', (width,height), (0, 0, 0, 0))
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

    # Update draw
    draw  = ImageDraw.Draw(re)

    # Display timezone 
    txt = "鲑鱼跑"+ tz + "时间"
    font = ImageFont.truetype(font_path, size=40)
    text_width = draw.textlength(txt,font=font)
    _x = int((width - text_width) / 2)
    _y = 15
    left, top, right, bottom = draw.textbbox((_x,_y),txt,font=font)
    draw.rectangle((left-10, top-5, right+10, bottom+5),fill="black")
    draw.text((_x,_y), txt, fill="white", font=font)

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
                if wp == "Random":
                    link = URL+"weapons/"+wp+".png"
                else:
                    link = URL+"weapons/"+wp+".webp"
                image_to_add = Image.open(link).convert("RGBA")

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
                if wp == "Random":
                    link = URL+"weapons/"+wp+".png"
                else:
                    link = URL+"weapons/"+wp+".webp"
                image_to_add = Image.open(link).convert("RGBA")

                size = (56,56)
                image_to_add = image_to_add.resize(size)

                __x = _x + 56 * (idx2 // 2)
                __y = _y + 56 * (idx2 % 2)
                position = (__x, __y)
                re.paste(image_to_add,position, image_to_add)

            y += 160
        # draw.line((0, y-40, 400, y-40), fill=(0, 0, 0), width=5)
    return re

def render_random(li, URL = None):
    weapons = li["weapons"]
    stage_url = URL + "stages/"+ li["stage"] + ".png"
    rule_url = URL +  "rule/" + li['rule'] +".png"
    
    width = 400
    height = 600

    re = Image.new("RGBA", (width,height), "white")

    # Set background colors
    color = Image.new('RGBA', (width,height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(color)
    draw.rectangle([0, 0, width, height], fill=(255, 98, 8, 255))
    re = Image.alpha_composite(re, color)

     # Set background overlay
    background_path = URL+"misc/fight_mask.png"
    background = Image.open(background_path)
    scale = 0.05
    size = (int(scale * background.size[0]), int(scale * background.size[1]))
    background = background.resize(size)
    for x in range(0, width, background.width):
        for y in range(0, height, background.height):
            re.paste(background, (x, y), background)

    # Update draw
    draw  = ImageDraw.Draw(re)

    # Add stage image
    stage = Image.open(stage_url).convert("RGBA")
    # Resize image:
    scale = 0.8
    size = (int(scale * stage.size[0]), int(scale * stage.size[1]))
    stage = stage.resize(size)
    stage = circle_corner(stage, 20)

    _x = int((width- stage.width) / 2)
    _y = 30
    position = (_x,_y)
    re.paste(stage,position,stage)

    rule = Image.open(rule_url).convert("RGBA")
    # Resize image:
    scale = 0.8
    size = (int(scale * rule.size[0]), int(scale * rule.size[1]))
    rule = rule.resize(size)

    _x = int((width- rule.width) / 2)
    _y = 200
    position = (_x,_y)
    re.paste(rule,position,rule)

    draw.rounded_rectangle((60,200,140,580),radius=8,fill="black")
    draw.rounded_rectangle((260,200,340,580),radius=8,fill="black")

    _x = 60
    _y = 200
    for i in range(8):
        wp = weapons[i]
        wp_url = URL+ "weapons/" + wp['Name'] +".webp"
        
        weapon = Image.open(wp_url).convert("RGBA")
        weapon = weapon.resize((80,80))
        position = (_x,_y)

        re.paste(weapon,position,weapon)
        _x = 400 - _x  - 80
        if i % 2 == 1:
            _y += 100

    return re






def circle_corner(img, radius):
    mask = Image.new('L', img.size, 0)
    _draw = ImageDraw.Draw(mask)
    left, upper, right, lower = 0, 0, mask.width, mask.height
    _draw.rounded_rectangle((left, upper, right, lower), radius=radius, fill=255)
    img.putalpha(mask)
    return img
