'''
Utility functions.

'''

import json
import csv
import bs4


def get_soup(url, pm):
    '''
    Get a BeautifulSoup object from url

    Inputs:
        url: string
        pm: PoolManager object

    Outputs:
        a BeautifulSoup object
    '''
    try:
        html = pm.urlopen(url=url, method="GET").data
    except:
        return None

    return bs4.BeautifulSoup(html, features='lxml')


def read_json(filename):
    '''
    Read JSON file

    Inputs:
        filename: string

    Outputs:
        dictionary
    '''
    with open(filename) as file:
        result = json.load(file)
    return result


def write_json(dic, filename):
    '''
    Write JSON file

    Inputs:
        dic: dictionary
        filename: string

    Outputs:
        JSON file
    '''

    json_file = json.dumps(dic)
    file = open(filename, "w")
    file.write(json_file)
    file.close()


def write_csv(lst, filename):
    '''
    Generate a CSV file with an index.
    '''
    with open(filename, "w") as csvfile:
        writer = csv.writer(csvfile, delimiter="|")
        for e in lst:
            writer.writerow([e])
