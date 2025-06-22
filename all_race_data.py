import requests
from bs4 import BeautifulSoup

# Get soup to parse through
def get_soup(year=2025):
    year_url = f"https://www.formula1.com/en/results/{year}/races"
    soup = BeautifulSoup(str(requests.get(year_url).content), "html.parser")
    return soup

# Getting data in useable format
def process_race_data(data):
    for i in range(len(data)):
        # gets race location from race link (only manual change for Imola)
        data[i][0] = data[i][1].split("/")[-2].title().replace("-", " ") 
        if data[i][0] == "Emilia Romagna":
            data[i][0] = "Imola"

        # adjusts race link by skipping the "/../../en/results/yyyy/"
        data[i][1] = data[i][1][23:]  

        # adjust the names into a tuple ( ex: "Lando NorrisNOR" -> ("Lando Norris", "NOR") )
        data[i][3] = (data[i][3][:-3], data[i][3][-3:])
    return data


# Get final race results
def get_all_races(year):
    soup = get_soup(year)

    data_rows = []
    tr_content = soup.find_all('tr')[1:]  # Ignore first element b/c it's the headers

    # Process data
    for tr in tr_content:
        row_data = []
        for td in tr.find_all('td'):
            text_ele = td.find('p')
            some_link = td.find('a')['href'] if td.find('a') != None else None

            # fixes any weird non-ASCII characters
            text_content = str(text_ele.get_text(strip=True).replace('\\xc2\\xa0', ' ')).encode('utf-8').decode('unicode_escape').encode('latin-1').decode('utf-8')
            row_data.append(text_content)
            row_data.append(some_link) if some_link != None else None
        
        if row_data:
            data_rows.append(row_data)

    return process_race_data(data_rows)
