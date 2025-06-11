import requests
from bs4 import BeautifulSoup

# Get soup to parse through
def getSoup(year=2025):
    yearUrl = f"https://www.formula1.com/en/results/{year}/races"
    soup = BeautifulSoup(str(requests.get(yearUrl).content), "html.parser")
    return soup

# Get final race results
def getAllRaces(year):
    soup = getSoup(year)

    dataRows = []
    trContent = soup.find_all('tr')[1:]  # Ignore first element b/c it's the headers

    # Process data
    for tr in trContent:
        rowData = []
        for td in tr.find_all('td'):
            textEle = td.find('p')
            someLink = td.find('a')['href'] if td.find('a') != None else None

            # fixes any weird non-ASCII characters
            textContent = str(textEle.get_text(strip=True).replace('\\xc2\\xa0', ' ')).encode('utf-8').decode('unicode_escape').encode('latin-1').decode('utf-8')
            rowData.append(textContent)
            rowData.append(someLink) if someLink != None else None
        
        if rowData:
            dataRows.append(rowData)

    # Splits the full name from tricode
    dataRows = [row[:3] + [(row[3][:-3], row[3][-3:])] + row[4:] for row in dataRows]
    return dataRows
