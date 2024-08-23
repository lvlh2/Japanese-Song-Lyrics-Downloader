#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File: download_lyrics_from_utaten.py
@Time: 2024/08/23 09:37:36
@Author: lvlh2
"""


import os
import re

import requests
from lxml import etree


class UtatenDownloader:
    """Downloads the lyrics of a song from utaten.com."""

    base_url = 'https://utaten.com'
    search_url = 'https://utaten.com/search'

    def __init__(self, title: str) -> None:
        """Initializes a new UtatenDownloader instance.

        Args:
            title (str): The title of the song.
        """
        self.title = title

    def get_page_url_and_search_result(self) -> tuple[str, str, str]:
        """Gets the url of the lyrics page and the search result.

        Returns:
            tuple: The url of the lyrics page, the search result title and the name of the singer.
        """
        response = requests.get(self.search_url, params={'title': self.title})

        tree = etree.HTML(response.text)

        xpath = '//table//p[@class="searchResult__title"]/a/@href'
        try:
            href = tree.xpath(xpath)[0]
        except IndexError:
            raise Exception('No lyrics found!')

        page_url = self.base_url + href

        xpath = '//table//p[@class="searchResult__title"]/a/text()'
        search_result_title = tree.xpath(xpath)[0].strip()

        xpath = '//table//p[@class="searchResult__name"]/a/text()'
        singer_name = tree.xpath(xpath)[0].strip()

        return page_url, search_result_title, singer_name

    def fetch_lyrics(self, page_url: str) -> str:
        """Fetches the lyrics of the song.

        Args:
            page_url (str): The url of the lyrics page.

        Returns:
            str: The lyrics of the song.
        """
        response = requests.get(page_url)

        tree = etree.HTML(response.text)

        xpath = '//div[@class="hiragana"]'
        div = tree.xpath(xpath)[0]

        div = etree.tostring(div, encoding='utf-8').decode('utf-8')

        pat = re.compile(r'<span class="rt">(?P<hiragana>.*?)</span>')
        div = pat.sub(r'<span class="rt">(\g<hiragana>)</span>', div)
        pat = re.compile(r'<br />')
        div = pat.sub(r'\n', div)

        tree = etree.HTML(div)

        xpath = '//div[@class="hiragana"]//text()'
        lyrics = ' '.join(tree.xpath(xpath))

        lyrics = '\n'.join([line.strip() for line in lyrics.splitlines()])
        return lyrics


def main():
    path = os.path.dirname(__file__)
    os.chdir(path)

    title = input('Please input the title of the song: ')
    utaten = UtatenDownloader(title=title)

    page_url, search_result_title, singer_name = utaten.get_page_url_and_search_result()
    print(f'The search result is: {search_result_title} - {singer_name}.')

    lyrics = utaten.fetch_lyrics(page_url=page_url)

    with open(f'{search_result_title}_{singer_name}.txt', 'w', encoding='utf-8') as f:
        f.write(search_result_title + ' - ' + singer_name + '\n' + lyrics)


if __name__ == '__main__':
    main()
