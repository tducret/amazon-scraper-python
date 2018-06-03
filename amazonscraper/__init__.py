# -*- coding: utf-8 -*-
""" This package allows you to search for products on Amazon and extract some
useful information (title, ratings, number of reviews).
"""
from builtins import object
from amazon.client import Client
import json

__version__ = '0.0.1'  # Should be the same in setup.py


class Products(object):
    """Class of the products"""
    def __init__(self, product_dict_list=[]):
        self.products = product_dict_list

    def _add_product(self, product_dict):
        self.products.append(product_dict)

    def __repr__(self):
        return json.dumps(self.products, indent=1)

    def __len__(self):
        return len(self.products)

    def __getitem__(self, key):
        """ Method to access the object as a list
        (ex : products[1]) """
        return self.products[key]

    def csv(self, separator=","):
        csv_string = separator.join([
                                    "Product title",
                                    "Rating",
                                    "Number of customer reviews",
                                    "Product URL"])
        for product in self:
            rating = product.get("rating", "")
            if separator == ";":  # French convention
                rating = rating.replace(".", ",")
            csv_string += ("\n"+separator.join([
                                        product.get("title", ""),
                                        rating,
                                        product.get("review_nb", ""),
                                        product.get("url", "")]))
        return csv_string


def get_products(keywords="", url=""):
    """Function to get the list of products from amazon"""
    amz = Client()
    product_dict_list = amz._get_products(keywords=keywords, search_url=url)
    products = Products(product_dict_list)

    return products
