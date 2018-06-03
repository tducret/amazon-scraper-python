# -*- coding: utf-8 -*-
"""
Module to get and parse the product info on Amazon
"""

import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

_BASE_URL = "https://www.amazon.com/"
_DEFAULT_BEAUTIFULSOUP_PARSER = "html.parser"
CSS_SELECTORS_1 = {
    "product": "#resultItems > li",
    "title": "a > div > div.sx-table-detail > h5 > span",
    "rating": "a > div > div.sx-table-detail > \
               div.a-icon-row.a-size-small > i > span",
    "review_nb": "a > div > div.sx-table-detail > \
                  div.a-icon-row.a-size-small > span",
    "url": "a['href']",
    "next_page_url": "ul.a-pagination > li.a-last > a['href']",
}
# Sometimes, the result page is displayed with another layout
CSS_SELECTORS_2 = {
    "product": "#grid-atf-content > li > div.s-item-container",
    "title": "a > div > h5.sx-title > span",
    "rating": "a > div > div.a-icon-row.a-size-mini > i > span",
    "review_nb": "a > div > div.a-icon-row.a-size-mini > span",
    "url": "a['href']",
    "next_page_url": "ul.a-pagination > li.a-last > a['href']",
}


class Client(object):
    """Do the requests with the Amazon servers"""

    def __init__(self):
        """ Init of the client """

        self.session = requests.session()
        self.headers = {
                    'Host': 'www.amazon.com',
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 7.0; \
                        SM-A520F Build/NRD90M; wv) AppleWebKit/537.36 \
                        (KHTML, like Gecko) Version/4.0 \
                        Chrome/65.0.3325.109 Mobile Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,\
                        application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    }
        self.product_dict_list = []

    def _get(self, url):
        """ GET request with the proper headers """
        return self.session.get(url, headers=self.headers)

    def _post(self, url, post_data):
        """ POST request with the proper headers """
        return self.session.post(url, headers=self.headers, data=post_data)

    def _update_headers(self, search_url):
        self.base_url = "https://" + \
                search_url.split("://")[1].split("/")[0] + "/"
        # https://www.amazon.com/s/lkdjsdlkjlk => https://www.amazon.com/
        self.headers['Host'] = self.base_url.split("://")[1].split("/")[0]
        # https://www.amazon.com/ => www.amazon.com

    def _get_search_url(self, keywords):
        search_url = urljoin(_BASE_URL, ("s/field-keywords=%s" % (keywords)))
        return search_url

    def _get_products(self, keywords="", search_url="", max_product_nb=100):
        if search_url == "":
            search_url = self._get_search_url(keywords)
        self._update_headers(search_url)
        res = self._get(search_url)
        soup = BeautifulSoup(res.text, _DEFAULT_BEAUTIFULSOUP_PARSER)

        css_selector_dict = CSS_SELECTORS_1

        products = soup.select(css_selector_dict.get("product", ""))
        if len(products) < 1:
            # Test the other css selectors
            css_selector_dict = CSS_SELECTORS_2
            products = soup.select(css_selector_dict.get("product", ""))

        # For each product of the result page
        for product in products:
            if len(self.product_dict_list) >= max_product_nb:
                # Check if the maximum number to search has been reached
                break
            else:
                product_dict = {}
                title = _css_select(product,
                                    css_selector_dict.get("title", ""))
                product_dict['title'] = title
                rating = _css_select(product,
                                     css_selector_dict.get("rating", ""))
                review_nb = _css_select(product,
                                        css_selector_dict.get("review_nb", ""))
                if rating:
                    proper_rating = rating.split(" ")[0].strip()
                    # In French results, ratings with comma
                    # Replace it with a dot (3,5 => 3.5)
                    proper_rating = proper_rating.replace(",", ".")
                    product_dict['rating'] = proper_rating
                if review_nb:
                    proper_review_nb = review_nb.split("(")[1].split(")")[0]
                    product_dict['review_nb'] = proper_review_nb
                url_product_soup = product.select(
                                   css_selector_dict.get("url", ""))
                if url_product_soup:
                    url = urljoin(
                        self.base_url,
                        url_product_soup[0].get('href'))
                    proper_url = url.split("/ref=")[0]
                    product_dict['url'] = proper_url
                    if "slredirect" not in proper_url:  # slredirect = bad url
                        self.product_dict_list.append(product_dict)

        if len(self.product_dict_list) < max_product_nb:
            # Check if there is another page
            # only if we have not already reached the max number of products
            url_next_page_soup = soup.select(
                                 css_selector_dict.get("next_page_url", ""))
            if url_next_page_soup:
                url_next_page = urljoin(
                    self.base_url,
                    url_next_page_soup[0].get('href'))
                self._get_products(search_url=url_next_page,
                                   max_product_nb=max_product_nb)

        return self.product_dict_list


def _css_select(soup, css_selector):
        """ Renvoie le contenu de l'élément du sélecteur CSS, ou une
        chaine vide """
        selection = soup.select(css_selector)
        if len(selection) > 0:
            retour = selection[0].text.strip()
        else:
            retour = False
        return retour
