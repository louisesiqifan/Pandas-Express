import sqlite3
import os
import re
import configparser


config = configparser.ConfigParser()
config.read('../wrapper/constants.ini')
DATABASE_FILENAME = config['DEFAULT']['DATABASE_FILENAME']
INDEX_IGNORE = config['DATA']['INDEX_IGNORE']


def score(ui_input, lim, weight={}):
    '''
    From ui_input, update score and show the top records

    Input:
        ui_input(dict)
        lim(int)
        weight(dictionary)
    Return:
        top(list)
    '''
    score  = {}
    ui_input = input_verification(ui_input)
    category = ui_input.get('categories', False)
    level = ui_input.get('level', False)
    time_params = ui_input.get('time', False)
    term = ui_input.get('term', False)
    title = ui_input.get('title', False)
    if category:
        print('Looking for category...')
        result = search_by_categories(category)
        for i, val in result:
            score[i] = score.get(i, 0) + val*weight.get('categories',1)
    if level:
        print('Looking for level...')
        result = search_by_level(level)
        for i, val in result:
            score[i] = score.get(i, 0) + val*weight.get('level',1)
    if time_params:
        print('Looking for time...')
        result = search_by_time(time_params)
        for i, val in result:
            if val:
                score[i] = score.get(i, 0) + val*weight.get('level',1)
    if term:
        print('Looking for term...')
        result = search_by_term(term)
        for i, val in result:
            score[i] = score.get(i, 0) + val*weight.get('level',1)
    if title:
        print('Looking for title...')
        result = search_by_title(title)
        for i, val in result:
            s = score.get(i, 0) + val*weight.get('level',10)
            score[i] = s
    final_score = sorted(score.items(), key=lambda item: item[1], reverse=True)
    return final_score[:lim]


def input_verification(ui_input):
    '''
    From ui_input, verify ui_input is correct
    '''
    ui = {'categories': list, 'level': str, 'title': str,
          'time': tuple, 'term': str}
    for key, typ in ui.items():
        val = ui_input.get(key, None)
        if val is not None:
            if type(val) != typ:
                raise ValueError(f"input type for {key} should be {typ}")
            if key == 'categories':
                args = [x.title() for x in val]
                ui_input['categories'] = args
            if key == 'level':
                val = val.capitalize()
                levels = ['Easy', 'Intermediate', 'Advanced']
                assert val in levels, 'incorrect level'
                ind = levels.index(val)
                val_list = [int(i<=ind) for i,_ in enumerate(levels)]
                ui_input['level'] = val_list
            if key == 'time':
                upper_bound, mode = val
                assert mode in ['total', 'active'], 'incorrect mode'
                assert upper_bound > 0, 'incorret time constraint'
                ui_input['time'] = (str(upper_bound), mode)
            if key == 'title':
                args = val.title().split(',')
                ui_input['title'] = args
            if key == 'term':
                r = re.findall(r'[a-zA-Z]{2,}', val)
                args = list(set([x.lower() for x in r if x.lower() not in INDEX_IGNORE]))
                ui_input['term'] = args
    return ui_input



def search_by_categories(args):
    '''
    To search by categories

    Input:
        args(list)
    Return:
        results(list)
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    sub_q = ','.join(['?']*len(args))
    query = f'''
    SELECT r.id AS id, ROUND(k.count*1.0/{len(args)},2) AS score
    FROM recipes AS r
    JOIN (SELECT id, COUNT(id) AS count
          FROM recipe_categories
          WHERE category IN ({sub_q})
          GROUP BY id) AS k
          ON k.id = r.id
    '''
    c.execute(query, args)
    results = c.fetchall()
    db.close()
    return results


def search_by_level(val):
    '''
    to match recipe with input level

    Input:
        val(list):
    Return:
        results(list): list of tuple with (id, score)
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    query = f'''
    SELECT id,
           CASE
               WHEN level = 'Easy' THEN {val[0]}
               WHEN level = 'Intermediate' THEN {val[1]}
               WHEN level = 'Advanced' THEN {val[2]}
           END AS score
    FROM recipes
    WHERE score IS NOT NULL;
    '''
    c.execute(query)
    results = c.fetchall()
    db.close()
    return results


def search_by_time(time_params):
    '''
    to match recipe with input time

    Input:
        time_params(tuple): (upper_bound, mode)
    Return:
        results(list): list of tuple with (id, score)
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    upper_bound, mode = time_params
    mode = 'time_' + mode
    c = db.cursor()
    query = f'''
    SELECT id,
        CASE
            WHEN {mode} > 0 AND {mode} <= ? THEN 1.0
            WHEN {mode} > 0 AND {mode} > ? THEN 1.0*(?-{mode})/?
        END AS score
    FROM recipes
    ORDER BY score desc;
    '''
    c.execute(query, (upper_bound,)*4)
    results = c.fetchall()
    db.close()
    return results


def search_by_title(args):
    '''
    to match recipe with input string terms

    Input:
        string(list)
    Return:
        results(list): list of tuple with (id, score)
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    args_dup = [x for x in args for _ in range(2)]
    case = '''
    CASE
        WHEN INSTR(name, ?) > 0 THEN 1
        ELSE 0
    END
    '''
    plus_string = '+'.join([case]*len(args))
    query = f'''
    SELECT id, ROUND(({plus_string})*1.0/{len(args)},2) AS score
    FROM recipes
    ORDER BY score desc;
    '''
    c.execute(query, tuple(args))
    results = c.fetchall()
    db.close()
    return results


def search_by_term(args):
    '''
    to match recipe with input string terms

    Input:
        string(list)
    Return:
        results(list): list of tuple with (id, score)
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    sub_q = ','.join(['?']*len(args))
    query = f'''
    SELECT id, ROUND(COUNT(id)*1.0/{len(args)},2) AS score
    FROM recipe_terms
    WHERE word IN ({sub_q})
    GROUP BY id
    ORDER BY score desc;
    '''
    c.execute(query, args)
    results = c.fetchall()
    db.close()
    return results


###########
EXAMPLE_0 = {'categories': ['italian', 'main dish'], 'level': 'easy',
             'time': (10, 'total'), 'title': 'fried chicken'}

EXAMPLE_1 = {'categories': ['italian', 'main dish'], 'level': 'eAsy',
             'time': (60, 'total'), 'term': 'italian soup'}
