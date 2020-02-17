'''
Python Wrapper fo Nutritionix
Link: https://developer.nutritionix.com/admin/access_details
Doc: https://trackapi.nutritionix.com/docs/
Reference: https://github.com/leetrout/python-nutritionix
'''

import requests

URL = "https://trackapi.nutritionix.com/v2/natural/nutrients"

APP_DICT = {'95dfa943': '59e2efc1a67da04885a07f8ea16d5114',
            'd4366d31': '77c1490af84be97e73a248a2b7bb61ac',
            '8b754284': '6cfc07a8ecd4bc61a04729e80d4170f3',
            'c96b185b': '1ef46d0ffd3eb437b3938139995538db',
            'ceb942f3': 'f8611c9451cda2053e7319b3ae5fe198'}

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
