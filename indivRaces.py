import requests
from bs4 import BeautifulSoup

# Get soup to parse through
def getSoup(race, year):
    link = f"https://www.formula1.com/en/results/{year}/{race}"
    soup = BeautifulSoup(str(requests.get(link).content), "html.parser")
    return soup

# Get final race results
def getRaceData(raceLink, year):
    soup = getSoup(raceLink, year)

    dataRows = []
    trContent = soup.find_all('tr')[1:]  # Ignore first element b/c it's the headers
    
    # Process data
    for tr in trContent:
        rowData = []
        for td in tr.find_all('td'):
            textEle = td.find('p')
            if textEle:
                # fixes any weird non-ASCII characters
                textContent = textEle.get_text(strip=True).replace('\\xc2\\xa0', ' ').encode('utf-8').decode('unicode_escape').encode('latin-1').decode('utf-8')
                rowData.append(textContent)
            else:
                rowData.append('')

        if rowData:
            dataRows.append(rowData)

    # Removes the "Note" element
    dataRows = [row for row in dataRows if len(row) != 1]

    # Splits the full name from tricode
    dataRows = [row[:2] + [(row[2][:-3], row[2][-3:])] + row[3:] for row in dataRows]

    # All data into a list of dicts
    raceData = []
    for row in dataRows:
        keys = ["pos", "num", "driver", "team", "laps", "time", "pts"]
        indivData = dict(zip(keys, row))
        raceData.append(indivData)
    
    return raceData
