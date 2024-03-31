from selenium import webdriver 
from selenium.webdriver.common.by import By
import time
from PIL import Image,ImageFont,ImageDraw
from sentence_transformers import SentenceTransformer, util
import glob
import os

class WZW():
    def __init__(self, URL):
        self.URL = URL + "WordCon"
        options = webdriver.ChromeOptions()
        options.add_argument("headless") 
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://www.lddgo.net/common/chinese-letter")
        # time.sleep(2)
    
    def flatten_comprehension(self, matrix):
        return [item for row in matrix for item in row]
    
    def conversion(self, word = ""):
        input_element = self.driver.find_element(By.NAME, "word")
        input_element.clear()
        input_element.send_keys(word)
        self.driver.find_element(By.ID, "startCompute").click()
        time.sleep(1)
        tbody = self.driver.find_element(By.ID, "resultTableBody")
        td_elements = tbody.find_elements(By.TAG_NAME, 'td')
        re = [td.text for td in td_elements]
        re = [item.split(" ") for item in re]
        re = [item for item in re if item != [""]]
        return re
    
    def get(self, word = "", num = 10):
        re = self.conversion(word)
        comb = len(re)
        flat = self.flatten_comprehension(re)
        total = len(flat)
        files = glob.glob( self.URL + '/tmp/*.jpg')
        for f in files:
            os.remove(f)
        font = ImageFont.truetype(self.URL + "/DFP_GBZY7.ttf", 40)
        for i in range(total):
            im = Image.new("RGB", (50, 50), (230, 230, 230))
            dr = ImageDraw.Draw(im)
            text = flat[i]
            dr.text((0, 0), text,font=font, fill="#000000")
            im.save(self.URL+"/tmp/"+str(i)+".jpg")

        model = SentenceTransformer('clip-ViT-B-32')
        image_names = list(glob.glob(self.URL+'/tmp/*.jpg'))
        image_names.sort()
        image_names.extend(glob.glob(self.URL+"/default/*.jpg"))

        encoded_image = model.encode([Image.open(filepath) for filepath in image_names], batch_size=128, convert_to_tensor=True, show_progress_bar=True)

        processed_images = util.paraphrase_mining_embeddings(encoded_image)

        counter = 0
        image = Image.new("RGB", (50*num, total * 100 + comb * 30), (230, 230, 230))
        _font = ImageFont.truetype(self.URL + "/fonts.otf", 30)
        draw = ImageDraw.Draw(image)
        x = 0
        y = 0
        for i in range(comb):
            draw.text((x, y), "拆分 " + str(i + 1) + ": ",font=_font, fill="#000000")
            y += 30
            for j in range(len(re[i])):
                threshold = 0.99
                near_duplicates = [image for image in processed_images if image[0] < threshold and image[1] == counter and image[2] > total - 1]
                base = image_names[near_duplicates[0][1]]
                base_image = Image.open(base)

                image.paste(base_image, (x, y))
                y += 50
                
                for score, image_id1, image_id2 in near_duplicates[0:num]:
                    rep_image = Image.open(image_names[image_id2])
                    image.paste(rep_image, (x, y))
                    x += 50
                    if x == 50*num :
                        x = 0
                y += 50
                counter +=1
        return image