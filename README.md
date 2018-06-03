# amazon-scraper-python

# Description

This package allows you to search for products on [Amazon](https://www.amazon.com/) and extract some useful information (ratings, number of comments).

# Requirements

- Python 3
- pip3

# Installation

```bash
pip3 install -U amazonscraper
```

# Command line tool `amz`

After the package installation, you can use the `amz` command in the terminal.

```bash
amz
```

After passing a search request to the command, it will return the results as csv :

```csv
Product title,Rating,Number of customer reviews,Product URL
"Learning Python, 5th Edition",4.0,293,https://www.amazon.com/Learning-Python-5th-Mark-Lutz/dp/1449355730
"Fluent Python: Clear, Concise, and Effective Programming",4.6,87,https://www.amazon.com/Fluent-Python-Concise-Effective-Programming/dp/1491946008
```

More info about the command in the help :

```bash
amz --help
```

# Using the amazonscraper Python package

```python
# -*- coding: utf-8 -*-
import amazonscraper

results = amazonscraper.search("Python programming")

for result in results:
    print("%s (%.2f out of 5 stars, %d customer reviews) :  %s" % (result.title, result.rating, result.review_nb, result.url))

print("Number of results : %d€" % (len(results)))

```

Which will output :

```
Learning Python, 5th Edition (4.0 out of 5 stars, 293 customer reviews) : https://www.amazon.com/Learning-Python-5th-Mark-Lutz/dp/1449355730
Fluent Python: Clear, Concise, and Effective Programming (4.6 out of 5 stars, 87 customer reviews) : https://www.amazon.com/Fluent-Python-Concise-Effective-Programming/dp/1491946008
[...]
Number of results : 3000
```

### Attributes of the `Product` object

Attribute name      | Description
------------------- | ---------------------------------------
title               | Product title
rating      	    | Rating of the products (number between 0 and 5, False if missing)
review_nb	        | Number of customer reviews (False if missing)
url 				| Product URL


# TODO
- Add a max number of results