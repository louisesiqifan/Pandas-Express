'''
Web crawler for https://www.foodnetwork.com/
'''

import bs4
import urllib3
import certifi
import string

INDICES = ["123"] + list(string.ascii_lowercase)[:-3] + ["xyz"]


def parse_detail(recipe_dict):
    '''
    Parse the recipe detail and update recipe dictionary

    Inputs:
        recipe_dict with two keys: ['name', 'url']

    Outputs:
        None
    '''
    print(recipe_dict['name'])
    url = recipe_dict['url']
    pm = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())    
    try:
        html = pm.urlopen(url=url, method="GET").data
    except:
        return

    soup = bs4.BeautifulSoup(html, features='lxml')
    try:
        info = soup.find_all("div", class_="recipeInfo")[0]
    except IndexError:
        return
    
    try:
        level = info.find_all('ul', class_="o-RecipeInfo__m-Level")[0]
    except IndexError:
        return

    try:
        time_tags = soup.find_all('ul', class_="o-RecipeInfo__m-Time")[0]
    except IndexError:
        return

    try:
        ingr_tags = soup.find_all("section", class_="o-Ingredients")[0]
    except IndexError:
        return 

    try:
        direct_tags = soup.find_all("section", class_="o-Method")[0]
    except IndexError:
        return

    try:
        cat_tags = soup.find_all("section", class_="o-Capsule o-Tags")[0]
    except IndexError:
        return

    level = level.find_all('span', class_="o-RecipeInfo__a-Description")[0].text
    
    time_tags = time_tags.find_all('span')
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

    ingredients = []
    ingr_tags = ingr_tags.find_all("p", class_="o-Ingredients__a-Ingredient")
    for tag in ingr_tags:
        ingredients.append(tag.text.strip())

    directions = []
    direct_tags = direct_tags.find_all("li", class_="o-Method__m-Step")
    for tag in direct_tags:
        directions.append(tag.text.strip())

    categories = []
    cat_tags = cat_tags.find_all("a")
    for tag in cat_tags:
        categories.append(tag.text.strip())

    recipe_dict['level'] = level
    recipe_dict['time'] = time_dict
    recipe_dict["categories"] = categories
    recipe_dict['ingredients'] = ingredients
    recipe_dict['directions'] = directions


def get_recipes(index):
    '''
    Get recipes starting with the given index.

    Inputs:
        index: string

    Outputs:
        a list of dictionary with keys: ['name', 'url']
    '''
    pm = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    url = "https://www.foodnetwork.com/recipes/recipes-a-z/{}".format(index)
    html = pm.urlopen(url=url, method="GET").data
    soup = bs4.BeautifulSoup(html, features='lxml')
    tags = soup.find_all("ul" , class_="m-PromoList o-Capsule__m-PromoList")
    recipes = []
    for tag in tags:
        links = tag.find_all("a")
        for link in links:
            recipe_dict = {'name': link.text, 'url': "https:"+link['href']}
            parse_detail(recipe_dict)
            recipes.append(recipe_dict)

    return recipes



def crawl():
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
        print(index)
        recipes = get_recipes(index)
        all_recipes[index] = recipes
        num += len(recipes)

    print("Scrape {} recipes!".format(num))
    json = json.dumps(all_recipes)
    f = open("foodnetwork.json","w")
    f.write(json)
    f.close()
