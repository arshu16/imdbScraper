# -*- coding: utf-8 -*-
# Script that gets the top 10 most popular titles from imdb in an year range
# USAGE
# Command: python /scriptName/ *startYear* *endYear* *genres*
# Defaults: genre is None, for multiple genres put 'horror,action,etc.'
# Defaults: startYear = 2015; endYear = currentYear
from bs4 import BeautifulSoup
import json
import urllib
from time import sleep
import sys
import datetime


def parse(url):
    page = urllib.urlopen(url)
    bs = BeautifulSoup(page, 'lxml')
    movies = bs.find_all('div', attrs={'class': 'lister-item'}, limit=10)
    parsed = {}
    for movie in movies:
        movieInfo = movie.find('div', attrs={'class': 'lister-item-content'})
        imageInfo = movie.find('div', attrs={'class': 'lister-item-image'})
        title = movieInfo.find('a').get_text()
        synopsis = movieInfo.find_all('p')[1]
        link = synopsis.find('a')
        imgLink = imageInfo.find('a')['href']
        print('http://www.imdb.com' + imgLink)
        movieLink = 'http://www.imdb.com' + imgLink
        movieHomePage = urllib.urlopen(movieLink)
        soup = BeautifulSoup(movieHomePage, 'lxml')
        cover_div = soup.find('div', attrs={"class": "poster"})
        cover_url = (cover_div.find('img'))['src']
        ratingContainer = movieInfo.find(
            'div', attrs={'class': 'ratings-imdb-rating'})
        rating = ''
        if ratingContainer:
            rating = float(ratingContainer.find('strong').get_text())
        genre = movieInfo.find('span', attrs={'class': 'genre'})
        if genre:
            genre = genre.get_text().strip()
        else:
            genre = ''

        # Only take movies without a "for full summary" link in them
        # including some synopsis.
        # We want only movies with some short synopsis for them and not a
        # long summary.
        if not link and synopsis:
            data = {}
            data['synopsis'] = synopsis.get_text().strip()
            data['genre'] = genre.split(', ')
            data['imgLink'] = cover_url
            data['rating'] = rating
            data['link'] = movieLink
            parsed[title] = data
    return parsed


f = open('dump.json', 'w')
to_write = {}
arguments = sys.argv[1:]
startYear = int((arguments and arguments[0]) or 2015)  # Start year
endYear = int((arguments and len(arguments) > 1 and arguments[1]
               ) or datetime.datetime.now().year)  # endyear
genre = (arguments and len(arguments) > 2 and arguments[2])
try:
    for i in range(startYear, endYear + 1):

        print("Year is: " + str(i))
        year_data = {}
        scrapeLink = 'http://www.imdb.com/search/title?release_date=' + \
            str(i) + '&ref_=adv_nxt&sort=moviemeter,asc&genres=' + genre
        print(scrapeLink)
        year_data.update(parse(scrapeLink))
        to_write[i] = year_data
except Exception, e:
    print("Error!", str(e))

json.dump(to_write, f, indent=4)
f.close()
