import unittest
from amazonscraper.client import Client

_MAX_PRODUCT_NB = 10


class AmazonscraperClientTest(unittest.TestCase):
    def test_client_get_products_with_keywords(self):
        amz = Client()
        results = amz._get_products(
                        keywords="Python",
                        max_product_nb=_MAX_PRODUCT_NB)
        self.assertEqual(len(results), _MAX_PRODUCT_NB)

    def test_client_get_products_with_url(self):
        amz = Client()
        results = amz._get_products(
                        search_url="https://www.amazon.com/s/ref=nb_sb_noss?\
                        url=search-alias%3Daps&field-keywords=python",
                        max_product_nb=_MAX_PRODUCT_NB)
        self.assertEqual(len(results), _MAX_PRODUCT_NB)
