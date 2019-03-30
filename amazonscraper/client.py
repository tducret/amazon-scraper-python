# -*- coding: utf-8 -*-
"""
Module to get and parse the product info on Amazon
"""

import requests
import re
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
    "url": "a[href]",
    "img": "img[src]",
    "next_page_url": "ul.a-pagination > li.a-last > a[href]",
}
# Sometimes, the result page is displayed with another layout
_CSS_SELECTORS_MOBILE_GRID = {
    "product": "#grid-atf-content > li > div.s-item-container",
    "title": "a > div > h5.sx-title > span",
    "rating": "a > div > div.a-icon-row.a-size-mini > i > span",
    "review_nb": "a > div > div.a-icon-row.a-size-mini > span",
    "url": "a[href]",
    "img": "img[src]",
    "next_page_url": "ul.a-pagination > li.a-last > a[href]",
}
_CSS_SELECTORS_DESKTOP = {
    "product": "ul > li.s-result-item > div.s-item-container",
    "title": "a.s-access-detail-page > h2",
    "rating": "i.a-icon-star > span",
    "review_nb": "div.a-column.a-span5.a-span-last > \
                div.a-row.a-spacing-mini > \
                a.a-size-small.a-link-normal.a-text-normal",
    "url": "div.a-row.a-spacing-small > div.a-row.a-spacing-none > a[href]",
    "img": "div.a-column.a-span12.a-text-center > a.a-link-normal.a-text-normal > img[src]",
    "next_page_url": "a#pagnNextLink",
}
_CSS_SELECTORS_DESKTOP_2 = {
    "product": "div.s-result-list.sg-row > div.s-result-item",
    "title": "div div.sg-row  h5 > span",
    "rating": "div div.sg-row .a-spacing-top-mini i span",
    "review_nb": "div div.sg-row .a-spacing-top-mini span.a-size-small",
    "url": "div div.sg-col-8-of-12 a.a-link-normal",
    "img": "img[src]",
    "next_page_url": "li.a-last > a[href]",
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
        self.html_pages = []

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
        https://www.amazon.com/s?k=python
        """
        search_url = urljoin(_BASE_URL, ("s?k=%s" % (keywords)))
        return search_url

    def _check_page(self, html_content):
        """ Check if the page is a valid result page
        (even if there is no result) """
        if "Sign in for the best experience" in html_content:
            valid_page = False
        elif "The request could not be satisfied." in html_content:
            valid_page = False
        elif "Robot Check" in html_content:
            valid_page = False
        else:
            valid_page = True
        return valid_page


    def _get_n_ratings(self, product):
        """Given the HTML for a particular `product`, extract the number of ratings"""

        n_ratings_css_selectors = [
            "div.a-row.a-size-small span.a-size-base",
            "div div.sg-row .a-spacing-top-mini span.a-size-small",
            "div.a-column.a-span5.a-span-last > div.a-row.a-spacing-mini > a.a-size-small.a-link-normal.a-text-normal",
        ]

        for selector in n_ratings_css_selectors:

            n_ratings = _css_select(product, selector)

            try:
                n_ratings = int(n_ratings.replace(',', ''))
                break
            except ValueError:
                pass

        if not n_ratings:
            print(f'  Failed to extract number of ratings!')

        return n_ratings


    def _get_title(self, product):
        """Given the HTML for a particular `product`, extract the title"""

        title_css_selectors = [
            'h5 span',
            "a.s-access-detail-page > h2",
            "div div.sg-row  h5 > span"
        ]

        for selector in title_css_selectors:

            title = _css_select(product, selector)

            if title:
                break

        if not title:
            print('  Failed to extract title!')

        return title


    def _get_rating(self, product):
        """Given the HTML for a particular `product`, extract the average rating"""

        rating = re.search(r'(\d.\d) out of 5', str(product))

        if rating:
            rating = rating.groups()[0]
            # convert string to float and replace European decimal seperator ',' with '.'s
            rating = float(rating.replace(",", "."))
        else:
            rating = float('nan')
            print(f'  Failed to extract rating!')

        return rating


    def _get_price(self, product):
        """Given the HTML for a particular `product`, extract the price"""
        prices = re.findall(r'\$([\d,]*.\d\d)', str(product))

        # convert strings to floats and sort
        prices = list(sorted(map(float, prices)))

        # sometimes a promotional price of zero dolars is returned
        try:
            prices.remove(0.0)
        except ValueError:
            pass

        if not prices:
            print(f'  Failed to extract price!')

        return min(prices)


    def _get_products(self, keywords="", search_url="", max_product_nb=100):

        if search_url == "":
            search_url = self._get_search_url(keywords)
        self._update_headers(search_url)

        trials = 0
        res = None

        while trials < _MAX_TRIAL_REQUESTS:
            print('Trying user agent: {}'.format(self.headers['User-Agent']))
            trials += 1
            try:
                res = self._get(search_url)

                valid_page = self._check_page(res.text)

            # To counter the "SSLError bad handshake" exception
            except requests.exceptions.SSLError:
                valid_page = False

            except ConnectionError:
                valid_page = False

            if valid_page:
                break

            self._change_user_agent()
            time.sleep(_WAIT_TIME_BETWEEN_REQUESTS)

        self.html_pages.append(res.text)

        if not valid_page:
            print('No valid pages found! Perhaps the page returned is a CAPTCHA? Check products.last_html_page')
            return {}

        soup = BeautifulSoup(res.text, _DEFAULT_BEAUTIFULSOUP_PARSER)

        # shuffle through CSS selectors until we get a list of products
        selector = 0
        for css_selector_dict in _CSS_SELECTOR_LIST:
            selector += 1
            css_selector = css_selector_dict.get("product", "")
            products = soup.select(css_selector)
            if len(products) >= 1:
                break

        # For each product of the result page
        for product in products:

            # Check if the maximum number to search has been reached
            if len(self.product_dict_list) >= max_product_nb:
                break

            product_dict = {}

            # extract title
            product_dict['title'] = self._get_title(product)

            print('Extracting {}'.format(product_dict['title']))

            # extract rating
            product_dict['rating'] = self._get_rating(product)

            # extract number of ratings
            product_dict['review_nb'] = self._get_n_ratings(product)

            # Get image before url and asin
            css_selector = css_selector_dict.get("img", "")
            img_product_soup = product.select(css_selector)
            if img_product_soup:
                img_url = img_product_soup[0].get('src')
                # Check if it is not a base64 formatted image
                if "data:image/webp" in img_url:
                    img_url = img_product_soup[0].get(
                        'data-search-image-source-set',
                        '').split(' ')[0]

                if img_url != '':
                    img_url = _get_high_res_img_url(img_url=img_url)

                product_dict['img'] = img_url


            # Extract ASIN, product URL and price
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
                    # Get price using asin
                    info_url = urljoin(
                        self.base_url,
                        f"gp/cart/desktop/ajax-mini-detail.html/ref=added_item_1?ie=UTF8&asin={asin}")
                    info = self._get(info_url)
                    soup_info = BeautifulSoup(info.text, _DEFAULT_BEAUTIFULSOUP_PARSER)
                    price = soup_info.select('span.a-size-medium.a-color-price.sc-price')
                    if price: # Doesn't work for ebooks
                        product_dict['price'] = price[0].getText()

            # use alternate method to extract price
            if 'price' not in product_dict:
                product_dict['price'] = self._get_price(product)

            self.product_dict_list.append(product_dict)
        # end for loop


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
        # end if


        return self.product_dict_list


def _css_select(soup, css_selector):
    """
    Returns the content of the element pointed by the CSS selector, or an empty string if not
    found
    """
    selection = soup.select(css_selector)
    retour = ""
    if len(selection) > 0:
        if hasattr(selection[0], 'text'):
            retour = selection[0].text.strip()
    return retour

def _get_high_res_img_url(img_url):
    """ Returns a modified url pointing to the high resolution version of
    the image
    >>> print(_get_high_res_img_url("https://images-na.ssl-images-amazon.com/\
images/I/513gErH1dML._AC_SX236_SY340_FMwebp_QL65_.jpg"))
    https://images-na.ssl-images-amazon.com/\
images/I/513gErH1dML.jpg
    >>> print(_get_high_res_img_url("https://images-na.ssl-images-amazon.com/\
images/I/51F48HFHq6L._AC_SX118_SY170_QL70_.jpg"))
    https://images-na.ssl-images-amazon.com/\
images/I/51F48HFHq6L.jpg
    """
    high_res_url = img_url.split("._")[0] + ".jpg"
    return high_res_url
