'''
Request data from FoodData Central (FDC) database
'''

import requests

DOMAIN = "https://api.nal.usda.gov/fdc/v1/"
MY_API_KEY = "A2cUlGaoOsiKAgzawPqcAYLuO2TqktQ1JXO2b6nI"

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
