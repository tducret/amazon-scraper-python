# -*- coding: utf-8 -*-
"""
Module to get and parse the product info on Amazon
"""

import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import time

_BASE_URL = "https://www.amazon.com/"
_DEFAULT_BEAUTIFULSOUP_PARSER = "html.parser"
_DEFAULT_USER_AGENT = 'Mozilla/5.0 (Linux; Android 7.0; \
SM-A520F Build/NRD90M; wv) AppleWebKit/537.36 \
(KHTML, like Gecko) Version/4.0 \
Chrome/65.0.3325.109 Mobile Safari/537.36'
_CHROME_DESKTOP_USER_AGENT = 'Mozilla/5.0 (Macintosh; \
Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/67.0.3396.79 Safari/537.36'

_USER_AGENT_LIST = [
                    _DEFAULT_USER_AGENT,
                    _CHROME_DESKTOP_USER_AGENT,
                   ]

_CSS_SELECTORS_MOBILE = {
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
_CSS_SELECTORS_MOBILE_GRID = {
    "product": "#grid-atf-content > li > div.s-item-container",
    "title": "a > div > h5.sx-title > span",
    "rating": "a > div > div.a-icon-row.a-size-mini > i > span",
    "review_nb": "a > div > div.a-icon-row.a-size-mini > span",
    "url": "a['href']",
    "next_page_url": "ul.a-pagination > li.a-last > a['href']",
}
_CSS_SELECTORS_DESKTOP = {
    "product": "ul > li.s-result-item > div.s-item-container",
    "title": "a.s-access-detail-page > h2",
    "rating": "i.a-icon-star > span",
    "review_nb": "div.a-column.a-span5.a-span-last > \
                div.a-row.a-spacing-mini > \
                a.a-size-small.a-link-normal.a-text-normal",
    "url": "div.a-row.a-spacing-small > div.a-row.a-spacing-none > a['href']",
    "next_page_url": "a#pagnNextLink",
}
_CSS_SELECTORS_DESKTOP_2 = {
    "product": "div.s-result-list.sg-row > div.s-result-item",
    "title": "div div.sg-row  h5 > span",
    "rating": "div div.sg-row .a-spacing-top-mini i span",
    "review_nb": "div div.sg-row .a-spacing-top-mini span.a-size-small",
    "url": "div div.sg-col-8-of-12 a.a-link-normal",
    "next_page_url": "li.a-last",
}

_CSS_SELECTOR_LIST = [
                        _CSS_SELECTORS_MOBILE,
                        _CSS_SELECTORS_MOBILE_GRID,
                        _CSS_SELECTORS_DESKTOP,
                        _CSS_SELECTORS_DESKTOP_2,
                     ]

# Maximum number of requests to do if Amazon returns a bad page (anti-scraping)
_MAX_TRIAL_REQUESTS = 5
_WAIT_TIME_BETWEEN_REQUESTS = 1


class Client(object):
    """Do the requests with the Amazon servers"""

    def __init__(self):
        """ Init of the client """

        self.session = requests.session()
        self.current_user_agent_index = 0
        self.headers = {
                    'Host': 'www.amazon.com',
                    'User-Agent': _USER_AGENT_LIST[0],
                    'Accept': 'text/html,application/xhtml+xml,\
                        application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    }
        self.product_dict_list = []

    def _change_user_agent(self):
        """ Change the User agent of the requests
        (useful if anti-scraping)
        >>> c = Client()
        >>> c.current_user_agent_index
        0
        >>> c.headers['User-Agent'] == _USER_AGENT_LIST[0]
        True
        >>> c._change_user_agent()
        >>> c.current_user_agent_index
        1
        >>> c.headers['User-Agent'] == _USER_AGENT_LIST[1]
        True
        >>> c2 = Client()
        >>> for i in range(0,9): c2._change_user_agent()
        >>> c2.current_user_agent_index == 9 % len(_USER_AGENT_LIST)
        True
        """
        index = (self.current_user_agent_index + 1) % len(_USER_AGENT_LIST)
        self.headers['User-Agent'] = _USER_AGENT_LIST[index]
        self.current_user_agent_index = index

    def _get(self, url):
        """ GET request with the proper headers """
        ret = self.session.get(url, headers=self.headers)
        if ret.status_code != 200:
            raise ConnectionError(
                'Status code {status} for url {url}\n{content}'.format(
                    status=ret.status_code, url=url, content=ret.text))
        return ret

    def _update_headers(self, search_url):
        """ Update the 'Host' field in the header with the proper Amazon domain
        >>> c = Client()
        >>> print(c.headers['Host'])
        www.amazon.com
        >>> c._update_headers("https://www.amazon.fr/s/lkdjsdlkjlk")
        >>> print(c.headers['Host'])
        www.amazon.fr
        """
        self.base_url = "https://" + \
            search_url.split("://")[1].split("/")[0] + "/"
        self.headers['Host'] = self.base_url.split("://")[1].split("/")[0]

    def _get_search_url(self, keywords):
        """ Get the Amazon search URL, based on the keywords passed
        >>> c = Client()
        >>> print(c._get_search_url(keywords="python"))
        https://www.amazon.com/s/field-keywords=python
        """
        search_url = urljoin(_BASE_URL, ("s/field-keywords=%s" % (keywords)))
        return search_url

    def _check_page(self, html_content):
        """ Check if the page is a valid result page
        (even if there is no result) """
        if "Sign in for the best experience" in html_content:
            valid_page = False
        elif "The request could not be satisfied." in html_content:
            valid_page = False
        else:
            valid_page = True
        return valid_page

    def _get_products(self, keywords="", search_url="", max_product_nb=100):
        if search_url == "":
            search_url = self._get_search_url(keywords)
        self._update_headers(search_url)

        trials = 0
        while trials < _MAX_TRIAL_REQUESTS:
            trials += 1
            try:
                res = self._get(search_url)
                valid_page = self._check_page(res.text)
            except requests.exceptions.SSLError:
                # To counter the "SSLError bad handshake" exception
                valid_page = False
                pass
            except ConnectionError:
                valid_page = False
                pass
            if valid_page:
                    break
            else:
                self._change_user_agent()
                time.sleep(_WAIT_TIME_BETWEEN_REQUESTS)

        self.last_html_page = res.text
        soup = BeautifulSoup(res.text, _DEFAULT_BEAUTIFULSOUP_PARSER)

        selector = 0
        for css_selector_dict in _CSS_SELECTOR_LIST:
            selector += 1
            css_selector = css_selector_dict.get("product", "")
            products = soup.select(css_selector)
            if len(products) >= 1:
                break

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
                if rating != "":
                    proper_rating = rating.split(" ")[0].strip()
                    # In French results, ratings with comma
                    # Replace it with a dot (3,5 => 3.5)
                    proper_rating = proper_rating.replace(",", ".")
                    product_dict['rating'] = proper_rating
                if review_nb != "":
                    if len(review_nb.split("(")) > 1:
                        proper_review_nb = review_nb.split("(")[1].\
                                           split(")")[0]
                    else:
                        proper_review_nb = review_nb
                    # Remove the comma for thousands (2,921 => 2921)
                    proper_review_nb = proper_review_nb.replace(",", "")
                    product_dict['review_nb'] = proper_review_nb

                css_selector = css_selector_dict.get("url", "")
                url_product_soup = product.select(css_selector)
                if url_product_soup:
                    url = urljoin(
                        self.base_url,
                        url_product_soup[0].get('href'))
                    proper_url = url.split("/ref=")[0]
                    product_dict['url'] = proper_url

                    url_token = proper_url.split("/")
                    asin = url_token[len(url_token)-1]
                    product_dict['asin'] = asin

                    if "slredirect" not in proper_url:  # slredirect = bad url
                        self.product_dict_list.append(product_dict)

        if len(self.product_dict_list) < max_product_nb:
            # Check if there is another page
            # only if we have not already reached the max number of products
            css_selector = css_selector_dict.get("next_page_url", "")
            url_next_page_soup = soup.select(css_selector)
            if url_next_page_soup:
                url_next_page = urljoin(
                    self.base_url,
                    url_next_page_soup[0].get('href'))
                self._get_products(search_url=url_next_page,
                                   max_product_nb=max_product_nb)

        return self.product_dict_list


def _css_select(soup, css_selector):
        """ Returns the content of the element pointed by the CSS selector,
        or an empty string if not found """
        selection = soup.select(css_selector)
        if len(selection) > 0:
            if hasattr(selection[0], 'text'):
                retour = selection[0].text.strip()
            else:
                retour = ""
        else:
            retour = ""
        return retour
