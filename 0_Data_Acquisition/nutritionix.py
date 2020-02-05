'''
LINK: https://developer.nutritionix.com/admin/access_details
PYTHON WRAPPER: https://github.com/leetrout/python-nutritionix
'''


APPLICATION_ID = '95dfa943'
APPLICATION_KEY = '59e2efc1a67da04885a07f8ea16d5114'

STRING = curl -XPOST https://api.nutritionix.com/v1_1/search -H 'Content-Type: application/json' -d'
{
 "appId":"95dfa943",
 "appKey":"59e2efc1a67da04885a07f8ea16d5114",
 "query":"Cookies `n Cream"
}
