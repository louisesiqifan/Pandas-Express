'''
Python Wrapper fo Nutritionix
Link: https://developer.nutritionix.com/admin/access_details
Doc: https://trackapi.nutritionix.com/docs/
Reference: https://github.com/leetrout/python-nutritionix
'''

import requests

URL = "https://trackapi.nutritionix.com/v2/natural/nutrients"
APP_ID = '95dfa943'
APP_KEY = '59e2efc1a67da04885a07f8ea16d5114'
USER_ID = '0'
HEADERS = {
    "Content-Type": "application/json",
    "x-app-id": APP_ID,
    "x-app-key": APP_KEY,
    "x-remote-user-id": USER_ID
}

def get_nutrient(ingredient):
    '''
    Get nutrient informatino of an ingredient

    Inputs:
        ingredient (string)

    Outputs:
        dictionary
    '''
    data = '{"query": "' + ingredient + '", "locale": "en_US"}'
    response = requests.post(URL, headers=HEADERS, data=data)
    return response.json()
