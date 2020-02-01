'''
Web crawler for https://www.foodnetwork.com/
'''

import string
import bs4
import urllib3
import certifi
import util

INDICES = ["123"] + list(string.ascii_lowercase)[:-3] + ["xyz"]


def parse_detail(recipe_dict, pm):
    '''
    Parse the recipe detail and update recipe dictionary

    Inputs:
        recipe_dict with two keys: ['name', 'url']

    Outputs:
        None
    '''
    print(recipe_dict['name'])
    url = recipe_dict['url']
    soup = util.get_soup(url, pm)
    if soup is None:
        return

    info_tags = soup.find_all("div", class_="recipeInfo")
    if not info_tags:
        return
    info = info_tags[0]

    level_tags = info.find_all('ul', class_="o-RecipeInfo__m-Level")
    if not level_tags:
        return
    level = level_tags[0]
    level = level.find_all('span', class_="o-RecipeInfo__a-Description")[0].text

    time_tags = info.find_all('ul', class_="o-RecipeInfo__m-Time")
    if not time_tags:
        return
    time_tags = time_tags[0].find_all('span')
    if not time_tags:
        return
    time_dict = {}
    stack = []
    for tag in time_tags:
        tag = tag.text
        if tag[-1] == ":":
            time_dict[tag[:-1]] = None
            stack.append(tag[:-1])
        elif tag[-1] == ")":
            continue
        else:
            key = stack.pop()
            time_dict[key] = tag.strip()

    ingr_tags = soup.find_all("section", class_="o-Ingredients")
    if not ingr_tags:
        return
    ingr_tags = ingr_tags[0].find_all("p", class_="o-Ingredients__a-Ingredient")
    ingredients = []
    for tag in ingr_tags:
        ingredients.append(tag.text.strip())

    direct_tags = soup.find_all("section", class_="o-Method")
    if not direct_tags:
        return
    direct_tags = direct_tags[0].find_all("li", class_="o-Method__m-Step")
    directions = []
    for tag in direct_tags:
        directions.append(tag.text.strip())

    cat_tags = soup.find_all("section", class_="o-Capsule o-Tags")
    if not cat_tags:
        return
    cat_tags = cat_tags[0].find_all("a")
    categories = []
    for tag in cat_tags:
        categories.append(tag.text.strip())

    recipe_dict['level'] = level
    recipe_dict['time'] = time_dict
    recipe_dict["categories"] = categories
    recipe_dict['ingredients'] = ingredients
    recipe_dict['directions'] = directions


def get_recipes(index, pm):
    '''
    Get recipes starting with the given index.

    Inputs:
        index: string

    Outputs:
        a list of dictionary with keys: ['name', 'url']
    '''

    url = "https://www.foodnetwork.com/recipes/recipes-a-z/{}".format(index)
    soup = util.get_soup(url, pm)
    tags = soup.find_all("ul", class_="m-PromoList o-Capsule__m-PromoList")
    recipes = []
    for tag in tags:
        links = tag.find_all("a")
        for link in links:
            recipe_dict = {'name': link.text, 'url': "https:"+link['href']}
            parse_detail(recipe_dict, pm)
            recipes.append(recipe_dict)

    return recipes


def crawl(pm, filename):
    '''
    Crawl https://www.foodnetwork.com/

    Inputs:
        None

    Outputs:
        json file
    '''
    all_recipes = {}
    num = 0
    for index in INDICES:
        recipes = get_recipes(index, pm)
        all_recipes[index] = recipes
        num += len(recipes)

    print("Scrape {} recipes!".format(num))
    util.write_json(all_recipes, filename)


if __name__ == "__main__":
    usage = "python3 foodnetwork.py"
    pm = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    filename = "foodnetwork.json"
    crawl(pm, filename)
