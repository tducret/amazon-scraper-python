import amazonscraper

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


def test_amazonscraper_get_100_products():

    products = amazonscraper.search(
                                keywords="Python",
                                max_product_nb=100)

    assert len(products) == 100


def test_amazonscraper_csv_header():

    products = amazonscraper.search(
                                keywords="Python",
                                max_product_nb=1)
    assert "Product title,Rating,Number of customer reviews,Product URL,\
ASIN\n" in str(products.csv())
