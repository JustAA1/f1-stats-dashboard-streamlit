import requests
from bs4 import BeautifulSoup

# Get soup to parse through
def get_soup(race, year):
    link = f"https://www.formula1.com/en/results/{year}/{race}"
    soup = BeautifulSoup(str(requests.get(link).content), "html.parser")
    return soup

# Get final race results
def get_race_data(race_link, year):
    soup = get_soup(race_link, year)

    data_rows = []
    tr_content = soup.find_all('tr')[1:]  # Ignore first element b/c it's the headers
    
    # Process data
    for tr in tr_content:
        row_data = []
        for td in tr.find_all('td'):
            text_ele = td.find('p')
            if text_ele:
                # fixes any weird non-ASCII characters
                text_content = text_ele.get_text(strip=True).replace('\\xc2\\xa0', ' ').encode('utf-8').decode('unicode_escape').encode('latin-1').decode('utf-8')
                row_data.append(text_content)
            else:
                row_data.append('')

        if row_data:
            data_rows.append(row_data)
    
    # Removes the "Note" element
    data_rows = [row for row in data_rows if len(row) != 1]
    
    # Splits the full name from tricode
    data_rows = [row[:2] + [(row[2][:-3], row[2][-3:])] + row[3:] for row in data_rows]

    # All data into a list of dicts
    race_data = []
    for row in data_rows:
        keys = ["pos", "num", "driver", "team", "laps", "time", "pts"]
        indiv_data = dict(zip(keys, row))
        race_data.append(indiv_data)
    
    return race_data
