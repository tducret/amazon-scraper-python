# -*- coding: utf-8 -*-
""" This package allows you to search for products on Amazon and extract some
useful information (title, ratings, number of reviews, price).
"""
from builtins import object
from amazonscraper.client import Client

__version__ = '0.0.9'  # Should be the same in setup.py


class Products(object):
    """Class of the products"""
    def __init__(self, product_dict_list=[]):
        self.products = []
        self.last_html_page = ""  # HTML content of the last scraped page
        for product_dict in product_dict_list:
            self._add_product(product_dict)

    def _add_product(self, product_dict):
        """ Append a product to the object product list
        >>> p = Products([{'title':'Book title', 'rating': '4.2',\
'review_nb': '15', 'price' : '$2.99', 'url':'http://www.amazon.com/book'}])
        >>> p.products[1]
        Traceback (most recent call last):
        ...
        IndexError: list index out of range
        >>> p._add_product({'title':'Book title 2', 'rating': '4.3',\
'review_nb': '12', 'price' : '$2.99', 'url':'http://www.amazon.com/book2'})
        >>> len(p.products)
        2
        >>> print(p[1].title)
        Book title 2
        """
        product = Product(product_dict)
        self.products.append(product)

    def __len__(self):
        return len(self.products)

    def __getitem__(self, key):
        """ Method to access the object as a list
        (ex : products[1]) """
        return self.products[key]

    def csv(self, separator=","):
        """ Returns a CSV string with the product info
        >>> p = Products([{'title':'Book title', 'rating': '4.2',\
'review_nb': '15', 'price' : '$2.99', 'url':'http://www.amazon.com/book'}])
        >>> p.csv()
        'Product title,Rating,Number of customer reviews,Price indication,\
Product URL\\n"Book title",4.2,15,$2.99,http://www.amazon.com/book'

        >>> print(p.csv(separator=";"))
        Product title;Rating;Number of customer reviews;Price indication;Product URL
        "Book title";4,2;15;$2.99;http://www.amazon.com/book

        >>> p2 = Products()
        >>> p2.csv()
        'Product title,Rating,Number of customer reviews, Price indication,Product URL'
        """
        type_list = []
        for product in self:
            for x in product.price.keys():
                if x in type_list: continue
                else :
                    type_list.append(x)
        try:
            type_list[0]
        except IndexError:
            print('Scrapping error: nothing was scrapped please try again')
        to_join = [
                "Product title",
                "Rating",
                "Number of customer reviews",
                "Product URL"]
        for x in type_list:
            to_join.append(x + '-to rent')
            to_join.append(x + '-to buy')
        csv_string = separator.join(to_join)
        for product in self:
            rating = product.rating
            if separator == ";":  # French convention
                rating = rating.replace(".", ",")
            final_string = [# Add the doublequotes " for titles
                    '"'+product.title+'"',
                    rating,
                    product.review_nb,
                    product.url]
            for x in type_list:
                if x in product.price:
                    final_string.append(product.price[x]['to rent'])
                    final_string.append(product.price[x]['to buy'])
                else:
                    final_string.append('N/A')
                    final_string.append('N/A')
            csv_string += ("\n"+separator.join(final_string))
        return csv_string


class Product(object):
    """Class of a product"""
    def __init__(self, product_dict={}):
        self.product = product_dict

    def __getattr__(self, attr):
        """ Method to access a dictionnary key as an attribute
        (ex : product.title) """
        return self.product.get(attr, "")


def search(keywords="", search_url="", max_product_nb=100, price=True):
    """Function to get the list of products from amazon"""
    amz = Client()
    product_dict_list = amz._get_products(
        keywords=keywords,
        search_url=search_url,
        max_product_nb=max_product_nb,
        price = price)
    products = Products(product_dict_list)
    products.last_html_page = amz.last_html_page

    return products
