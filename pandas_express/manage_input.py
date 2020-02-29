import configparser

config = configparser.ConfigParser()
config.read('../wrapper/constants.ini')
DATABASE_FILENAME = config['DEFAULT']['DATABASE_FILENAME']
UI = {'categories': list, 'level': str, 'title': str,
      'time': tuple, 'term': str, 'nutrition' : dict}

def input_verification(args_to_ui):
    '''
    From ui_input, verify ui_input is correct
    '''
    ui_input = args_to_ui.copy()
    for key, typ in UI.items():
        val = ui_input.get(key, None)
        if val is None:
            continue            
        if type(val) != typ:
            raise ValueError("input type for {} should be {}".format(key, typ))
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
        if key == 'nutrition':
            for k, v in val.items():
                if k not in ['calories', 'total_fat', 'saturated_fat',
                             'cholesterol','sodium', 'total_carbohydrate',
                             'dietary_fiber', 'sugars', 'protein',
                             'potassium']:
                    raise ValueError("nutrition value not supported")
                if v != 1 and v != -1:
                    raise ValueError("side for {} should be 1 or -1".format(k))

    return ui_input
