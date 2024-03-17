import requests
from bs4 import BeautifulSoup
import csv
import re


name = "weapons_data"
url = "https://splatoonwiki.org/wiki/"

# Open the CSV file for reading
with open(name+'.csv', 'r') as csv_file:
    # Create a CSV reader
    csv_reader = csv.DictReader(csv_file)
    # Convert CSV to dictionary
    data = list(csv_reader)

with open('all.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Index', 'Name', 'Sub', 'Special', "SP",'Class', "Range"])
    for item in data:
        _url = url + item["Name"]
        index = item["Index"]
        name = item["Name"]
        sub = item["Sub"]
        special = item['Special']
        sp = item['SP']
        Class = item["Class"]
        print(_url)
        # Send a GET request to the URL
        response = requests.get(_url)

        # If the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            try:
                soup = BeautifulSoup(response.text, 'html.parser')

                table = soup.find_all('tbody')[6]
                td = soup.find_all('b', text='Range')[-1].parent.next_sibling.next_sibling
                range = td.text.split(" ")[0]
            except:
                range = "TODO"


        writer.writerow([index, name, sub, special, sp, Class, range])
