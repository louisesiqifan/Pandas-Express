'''
Web crawler for https://www.foodnetwork.com/
'''

import string
import bs4
import urllib3
import certifi
import util

INDICES = ["123"] + list(string.ascii_lowercase)[:-3] + ["xyz"]


def get_info(soup, recipe_dict):
    '''
    Get the level and time of a recipe.

    Inputs:
        soup: BeautifulSoup Object
        recipe_dict: dictionary

    Outputs:
        None
    '''
    level = None
    time_dict = {}
    info_tags = soup.find_all("div", class_="recipeInfo")
    if info_tags:
        info = info_tags[0]
        items = info.find_all('li')
        for item in items:
            try:
                head = item.find_all('span', class_="o-RecipeInfo__a-Headline")[0].text.strip()
                desc = item.find_all('span', class_="o-RecipeInfo__a-Description")[0].text.strip()
            except IndexError:
                continue
            if head == "Level:":
                level = desc
            elif head == "Yield:":
                continue
            else:
                time_dict[head[:-1]] = desc

    recipe_dict['level'] = level
    recipe_dict['time'] = time_dict


def get_categories(soup, recipe_dict):
    '''
    Get the categories of a recipe.

    Inputs:
        soup: BeautifulSoup Object
        recipe_dict: dictionary

    Outputs:
        None
    '''
    categories = []
    cat_tags = soup.find_all("section", class_="o-Capsule o-Tags")
    if cat_tags:
        cat_tags = cat_tags[0].find_all("a")
        for tag in cat_tags:
            categories.append(tag.text.strip())

    recipe_dict["categories"] = categories


def get_ingredients(soup, recipe_dict):
    '''
    Get the ingredients of a recipe.

    Inputs:
        soup: BeautifulSoup Object
        recipe_dict: dictionary

    Outputs:
        None
    '''
    ingredients = []
    ingr_tags = soup.find_all("section", class_="o-Ingredients")
    if ingr_tags:
        ingr_tags = ingr_tags[0].find_all("p", class_="o-Ingredients__a-Ingredient")
        for tag in ingr_tags:
            ingredients.append(tag.text.strip())

    recipe_dict['ingredients'] = ingredients


def get_directions(soup, recipe_dict):
    '''
    Get the directions of a recipe.

    Inputs:
        soup: BeautifulSoup Object
        recipe_dict: dictionary

    Outputs:
        None
    '''
    directions = []
    direct_tags = soup.find_all("section", class_="o-Method")
    if direct_tags:
        direct_tags = direct_tags[0].find_all("li", class_="o-Method__m-Step")
        for tag in direct_tags:
            directions.append(tag.text.strip())

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
            url = "https:"+link['href']
            soup = util.get_soup(url, pm)
            if soup is not None:
                recipe_dict = {'name': link.text, 'url': url}
                print(recipe_dict['name'])
                get_info(soup, recipe_dict)
                get_categories(soup, recipe_dict)
                get_ingredients(soup, recipe_dict)
                get_directions(soup, recipe_dict)
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
