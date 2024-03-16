# Under the help of ChatGPT4
import requests
from bs4 import BeautifulSoup
import csv

# URL of the page to crawl
url = 'https://splatoonwiki.org/wiki/List_of_weapons_in_Splatoon_3'

# Send a GET request to the URL
response = requests.get(url)

# If the request was successful
if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # This is an example and might need adjustments based on the actual structure of the webpage.
    # Find the table or container that holds the data you're interested in.
    weapons = soup.find_all('tbody')[0]  # You need to update this based on the page's structure.
    # for row in weapons.find_all('tr'):
    #     for idx, it in enumerate(row.find_all('td')):
           
    #         print(str(idx) +" " +it.text)
    
    with open('weapons_data.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Index', 'Name', 'Sub', 'Special', "SP",'Class'])  # Header row
        _index = -1
        _name, _sub, _special, _sp, _class = None, None, None, None, None
        for row in weapons.find_all('tr'):
            for idx, it in enumerate(row.find_all('td')):
                match idx:
                    case 1:
                        _name = it.text.replace('\r','').replace('\n','')
                    case 3:
                        _sub = it.text.replace('\r','').replace('\n','')
                    case 4:
                        _special = it.text.replace('\r','').replace('\n','')
                    case 5:
                        _sp = it.text.replace('\r','').replace('\n','')
                    case 8 :
                        _class = it.text.replace('\r','').replace('\n','')
            if _index != -1:
                writer.writerow([_index, _name, _sub, _special, _sp, _class])
            _index +=1

print("CSV file has been created.")