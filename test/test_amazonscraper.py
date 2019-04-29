import amazonscraper
import pytest

_MAX_PRODUCT_NB = 10


def test_amazonscraper_get_products_with_keywords():
    products = amazonscraper.search(
                                keywords="Python",
                                max_product_nb=_MAX_PRODUCT_NB)

    assert len(products) == _MAX_PRODUCT_NB


def test_amazonscraper_get_products_with_url():
    url = "https://www.amazon.com/s/\
ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=python"
    products = amazonscraper.search(
                                search_url=url,
                                max_product_nb=_MAX_PRODUCT_NB)

    assert isinstance(products, amazonscraper.Products)
    assert len(products) == _MAX_PRODUCT_NB
    product = products[0]
    assert isinstance(product, amazonscraper.Product)
    assert product.title != ""
    assert product.review_nb != ""
    assert product.rating != ""
    assert product.url != ""
    assert product.asin != ""


def test_amazonscraper_invalid_url():
    url = "https://0.0.0.0"
    with pytest.raises(Exception):
        amazonscraper.search(
                            search_url=url,
                            max_product_nb=_MAX_PRODUCT_NB)


def test_amazonscraper_sign_in_suggestion_url():
    # or https://www.amazon.com/ref=assoc_res_sw_logo
    url = "https://www.amazon.com/gp/aw/ref=mw_access"
    products = amazonscraper.search(
                                search_url=url,
                                max_product_nb=_MAX_PRODUCT_NB)
    assert len(products) == 0


def test_amazonscraper_not_satisfied_url():
    url = "https://raw.githack.com/tducret/\
amazon-scraper-python/master/test/not_satisfied.html"
    products = amazonscraper.search(
                                search_url=url,
                                max_product_nb=_MAX_PRODUCT_NB)
    assert len(products) == 0


def test_amazonscraper_404_url():
    url = "https://raw.githack.com/tducret/\
amazon-scraper-python/master/test/404.html"
    products = amazonscraper.search(
                                search_url=url,
                                max_product_nb=_MAX_PRODUCT_NB)
    assert len(products) == 0


def test_amazonscraper_get_100_products():
    products = amazonscraper.search(
                                keywords="Python",
                                max_product_nb=100)

    assert len(products) == 100


def test_amazonscraper_csv_header():
    products = amazonscraper.search(
                                keywords="Python",
                                max_product_nb=1)
    products.csv('test.csv')
    with open('test.csv') as f:
        csv_str = f.read()
    assert "title,rating,review_nb,img,url,asin,prices_per_unit,units,prices_main"  in csv_str
