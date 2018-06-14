#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import click
import amazonscraper


@click.command()
@click.option(
    '--keywords', '-k',
    type=str,
    help='your keywords to find some products (ex : "python+scraping")',
    default="",
)
@click.option(
    '--url', '-u',
    type=str,
    help='an Amazon result page URL (ex : \
https://www.amazon.com/s/field-keywords=python%2Bscraping',
    default="",
)
@click.option(
    '--csvseparator', '-s',
    type=str,
    help='CSV separator (ex : ;)',
    default=",",
)
@click.option(
    '--maxproductnb', '-m',
    type=int,
    help='Maximum number of products (ex : 100)',
    default="100",
)
@click.version_option(
    version=amazonscraper.__version__,
    message='%(prog)s, based on amazonscraper module version %(version)s'
)
def main(keywords, url, csvseparator, maxproductnb):
    """ Search for products on Amazon, and extract it as CSV """
    products = amazonscraper.search(
                                    keywords=keywords,
                                    search_url=url,
                                    max_product_nb=maxproductnb)

    print(products.csv(separator=csvseparator))


if __name__ == "__main__":
    main()
