# Under the help of ChatGPT4
import requests
from bs4 import BeautifulSoup
import csv

# URL of the page to crawl
url = 'https://splatoonwiki.org/wiki/List_of_weapons_in_Splatoon_3'
url2 = "https://splatoonwiki.org/wiki/"

# Send a GET request to the URL
response = requests.get(url)

# If the request was successful
if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')
    weapons = soup.find_all('tbody')[0]  # You need to update this based on the page's structure.

    with open('all.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Index', 'Name', 'Sub', 'Special', "SP",'Class', "Range", "Damage", "FireRate"])  # Header row
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
                _url = url2 + _name
                # Send a GET request to the URL
                response2 = requests.get(_url)
                print(_url)
                # If the request was successful
                if response2.status_code == 200:
                    # Parse the HTML content of the page
                    soup2 = BeautifulSoup(response.text, 'html.parser')
                    try: 
                        table = soup2.find_all('tbody')[6]

                        _range = table.find_all("tr")[7].text
                        _range = _range.split("\n")[3].split(" ")[0]

                        _damage = table.find_all("tr")[8].text
                        _damage = _damage.split("\n")[3].split(" ")[0]

                        _fire_rate = table.find_all("tr")[10].text
                        _fire_rate = _fire_rate.split("\n")[3].split(" ")[0]
                    except:
                        table = soup.find_all('tbody')[7]

                        _range = table.find_all("tr")[7].text
                        _range = _range.split("\n")[3].split(" ")[0]

                        _damage = table.find_all("tr")[8].text
                        _damage = _damage.split("\n")[3].split(" ")[0]

                        _fire_rate = table.find_all("tr")[10].text
                        _fire_rate = _fire_rate.split("\n")[3].split(" ")[0]

            if _index != -1:
                writer.writerow([_index, _name, _sub, _special, _sp, _class, _range, _damage, _fire_rate])
            _index +=1

print("CSV file has been created.")