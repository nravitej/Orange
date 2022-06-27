from lxml import etree
import requests
from bs4 import BeautifulSoup as bs
from Orange.data import *



def getContent(link: str) -> str:
    webPage = requests.get(link)
    return str(bs(webPage.content, "html.parser"))


content: str = getContent("https://en.wikipedia.org/wiki/List_of_international_airports_by_country")
html: etree.ElementBase = etree.HTML(content)

print(html)

#resultList: list[str]

RELATIVE_ROOT = "//div[(@id='mw-content-text')]/div"
allNodes = html.xpath(RELATIVE_ROOT+"/*")
h2Count: int = 0
data = [[]]
i: int = 0
length: int = len(allNodes)

currentRegion= ""
currentSubRegion = ""
currentCountry = ""

while i < length:
    node: etree.ElementBase = allNodes[i]
    if node.tag == 'h2' and h2Count != 0:
        currentRegion = node.xpath("./span[@class='mw-headline'][1]")[0].text

    elif node.tag == 'h2':
        h2Count += 1
        i += 1
        continue
    if node.tag == 'h3':
        if i+1 < length:
            nextNode = allNodes[i + 1]
            if nextNode.tag == 'table':
                currentCountry = node.xpath("normalize-space(.//text())")
                currentSubRegion = ''
            elif nextNode.tag == 'h4':
                currentSubRegion = node.xpath("normalize-space(.//text())")
    if node.tag == 'h4':
        currentCountry = node.xpath("normalize-space(.//text())")
    if node.tag == 'table' and node.attrib['class'] == "wikitable":
        lines = node.xpath("./tbody/tr")
        for line in lines:

            cells = line.xpath("./td//text()")
            if len(cells) == 0:
                continue
            dataLine= [currentRegion, currentSubRegion, currentCountry]
            for cell in cells:
                if cell.strip() != '':

                    dataLine.append(cell.strip())
            data.append(dataLine)
    i += 1

#print(data[1])
data.pop(0)
lp6=[]
lp7=[]
for i in range(len(data)):
    try:
        if len(data[i])>6:
            lp6.append(data[i])
        elif len(data[i])<6:
            lp7.append(data[i])
    except IndexError:
        break
for i in range(len(lp6)):
    data.pop(data.index(lp6[i]))
for i in range(len(lp7)):
    data.pop(data.index(lp7[i]))
def push_refined(lp):
    f=[]
    for l in lp:
        if(len(l)==6):
            f.append(l)
    for k in f:
        lp.pop(lp.index(k))
        data.append(k)
    return lp
for l in lp6:
    if(l[4]==',' or l[4]=='/'):
        a=l[3]
        b=l[5]
        l[3]=a+"-"+b
        l.pop(4)
        l.pop(l.index(b))
lp6=push_refined(lp6)
while(len(lp6)!=0):
    P=[]
    for l in lp6:
        P.append(l[:-1])
    lp6=[]
    lp6=P.copy()
    lp6=push_refined(lp6)
lp8=lp7.copy()
for l in lp8:
    l.insert(3,'NA')
lp7=push_refined(lp8)
print(data[1])
continent = DiscreteVariable('continent', values=set([row[0] for row in data]))
Region = DiscreteVariable('Region', values=set([row[1] for row in data]))
country = DiscreteVariable('country', values=set([row[2] for row in data]))
city = DiscreteVariable('city', values=set([row[3] for row in data]))
AirportName = DiscreteVariable('AirportName', values=set([row[4] for row in data]))
CODE = DiscreteVariable('CODE', values=set([row[5] for row in data]))

domain = Domain([continent, Region, country,city,AirportName,CODE])
table = Table.from_list(domain, data)
out_data=table
