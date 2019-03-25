# Les joies de ULaval - Events

A Scraper of all events from the Laval university's faculties to never miss one.
[http://evenements.lesjoiesdeulaval.be](http://evenements.lesjoiesdeulaval.be)

## Architecture

Scraper is developped with Python3.
For each faculty, the URLs are opened with Get from Requests.
Selenium is used if the page's content is loaded with ajax.
BeautifulSoup is then used to read the data needed to build a json objects for every events.
It is then sorted by date and finally printed.

Front End Website is minimalist, React is used to read and display data.

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