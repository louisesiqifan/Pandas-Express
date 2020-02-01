'''
Web crawler for https://www.allrecipes.com/recipes/
'''

import bs4
import urllib3
import certifi
import string
import util


def crawl(pm, filename):
    '''
    Crawl https://www.foodnetwork.com/

    Inputs:
        None

    Outputs:
        json file
    '''    
    return None


if __name__ == "__main__":
    usage = "python3 allrecipes.py"
    pm = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    filename = "allrecipes.json"
    crawl(pm, filename)
