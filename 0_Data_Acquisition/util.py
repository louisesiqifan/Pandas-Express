'''
Utility functions

'''
import json

def read_json(filename):
    '''
    Read json

    Inputs:
        filename: string

    Outputs:
        dictionary
    '''
    with open(filename) as file:
        result = json.load(file)
    return result