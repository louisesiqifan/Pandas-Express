'''
Web crawler for https://www.allrecipes.com/recipes/
'''

import bs4
import urllib3
import certifi
import string
import util


def get_categories(pm, url="https://www.allrecipes.com/recipes/"):
    '''
    Get all categories in allrecipes.
    '''
    soup = util.get_soup(url, pm)
    categories = soup.find_all("div", class_="all-categories-col")
    dic = dict()
    for cat in categories:
        keys = cat.find_all("h3", class_="heading__h3")
        links_lst = cat.find_all("ul")
        for i, key in enumerate(keys):
            key = key.text
            print(key)
            dic[key] = dict()
            links = links_lst[i].find_all("a")
            for link in links:
                dic[key][link.text] = link['href']

    return dic


def get_recipe_links(pm, url):
    soup = util.get_soup(url, pm)
    links = soup.find_all("a")
    recipe_links = set()
    for link in links:
        try:
            link = link["href"]
        except KeyError:
            continue
        if link[:33] == "https://www.allrecipes.com/recipe" and link[33] != "s":
            recipe_links.add(link)
    return recipe_links


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
