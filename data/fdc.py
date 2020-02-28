'''
Request data from FoodData Central (FDC) database
'''

import requests

DOMAIN = "https://api.nal.usda.gov/fdc/v1/"
MY_API_KEY = "A2cUlGaoOsiKAgzawPqcAYLuO2TqktQ1JXO2b6nI"

FDC_TO_OUTPUT = {"Energy": "calories",
                 "Protein": "protein",
                 "Carbohydrates": "total_carbohydrate",
                 "Carbohydrate, by difference": "total_carbohydrate",
                 "Cholesterol": "cholesterol",
                 "Fiber, total dietary": "dietary_fiber",
                 "Sugars, total including NLEA": "sugars",
                 "Potassium, K": "potassium",
                 "Sodium, Na": "sodium",
                 "Total lipid (fat)": "total_fat",
                 "Fatty acids, total saturated": "saturated_fat"}

NUTRIENT_OUTPUT = ['calories', 'total_fat', 'saturated_fat', 'cholesterol',
                  'sodium', 'total_carbohydrate', 'dietary_fiber', 'sugars',
                  'protein', 'potassium']


def search_food(food):
    '''
    Lists foods that match desired search criteria.

    Inputs:
        food: string

    Outputs:
        a list of dictionaries with keys:
        ['fdcId', 'description', 'dataType', 'gtinUpc', 'publishedDate',
         'brandOwner', 'ingredients', 'allHighlightFields', 'score']
    '''
    headers = {"Content-Type": "application/json"}
    data = '{"generalSearchInput":"' + food + '"}'
    url = '{}search?api_key={}'.format(DOMAIN, MY_API_KEY)
    response = requests.post(url, headers=headers, data=data)
    return response.json()['foods']


def get_food_detail(fdcID):
    '''
    Provides details on a particular food.

    Inputs:
        fdcID: int

    Outputs:
        a dictionary with keys:
        ['foodClass', 'description', 'foodNutrients', 'foodComponents',
         'foodAttributes', 'tableAliasName', 'foodCode', 'startDate',
         'endDate', 'wweiaFoodCategory', 'fdcId', 'dataType',
         'publicationDate', 'foodPortions', 'inputFoods', 'changes']
    '''
    url = "{}{}?api_key={}".format(DOMAIN, str(fdcID), MY_API_KEY)
    response = requests.get(url)
    return response.json()


def get_nutrition(food):
    '''
    Get the nutrition values of food.

    Inputs:
        food: string

    Outputs:
        a dictionary with keys corresponding to the nutritions in NUTRITION_CUT
        of score_assignment.py
    '''

    food_detail = get_food_detail(search_food(food)[0]["fdcId"])
    food_nutrients = food_detail["foodNutrients"]
    nutrient_dict = {key: 0 for key in NUTRIENT_OUTPUT}

    for item in food_nutrients:
        amount = item.get("amount", 0)
        nname = item["nutrient"]["name"]
        nname = FDC_TO_OUTPUT.get(nname, nname)
        unit = item["nutrient"]["unitName"]
        if nname in NUTRIENT_OUTPUT:
            if unit == "kJ":
                break
            nutrient_dict[nname] = amount

    return nutrient_dict
