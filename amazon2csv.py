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
@click.option(
    '--outputhtml', '-o',
    type=str,
    help='Save the html page to the current folder with the specified name',
    default="",
)
def main(keywords, url, csvseparator, maxproductnb, outputhtml):
    """ Search for products on Amazon, and extract it as CSV """
    products = amazonscraper.search(
                                    keywords=keywords,
                                    search_url=url,
                                    max_product_nb=maxproductnb)

    print(products.csv(separator=csvseparator))

    if (outputhtml != ""):
        with open(outputhtml, "w") as f:
            f.write(products.last_html_page)


if __name__ == "__main__":
    main()
