# Les joies de ULaval - Events

Scrap all events from the faculties's Laval university campus to never miss one.
[http://evenements.lesjoiesdeulaval.be](http://evenements.lesjoiesdeulaval.be)

## Architecture

Scrapper is developped with Python3.
For every faculties, the url of it is open with Get from Requests.
It can be with selenium if the content's page is loaded with ajax.
BeautifulSoup is use in next to read data we need to build a json objects of all events.
Then it's sorted by date and printed.

Front Website is minimalist. Using React to read and display data.

## HOW TO USE

```bash
$ python3 scrap.py > data
```
Then paste data in fullData obj in the HTML file.

## Project's directories
```
.
├── chromedriver
├── index.html
├── README.md
├── scrap.py
└── style.css
```