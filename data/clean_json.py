import json
import glob



def find_json_files():
    files = glob.glob('./*.json')
    files.pop()
    return [x.strip('.\\') for x in files]


class ingredient:
    def __init__(self, id, name, serving_unit, serving_weight_grams,
                 calories, total_fat, saturated_fat,
                 cholesterol, sodium, total_carbohydrate, dietary_fiber,
                 sugars, protein, potassium):
        self.id = id
        self.origin = set()
        self.name = name
        self.serving_unit = serving_unit
        self.grams = serving_weight_grams
        self.calories = calories
        self.total_fat = total_fat
        self.saturated_fat = saturated_fat
        self.cholesterol = cholesterol
        self.sodium = sodium
        self.total_carbohydrate = total_carbohydrate
        self.dietary_fiber = dietary_fiber
        self.sugars = sugars
        self.protein = protein
        self.potassium = potassium


def clean_json_files():
    result = {}
    files = find_json_files()
    id_tracker = 1
    for file in files:
        with open(file) as f:
            ingredients = json.load(f)
        for origin, item in ingredients.items():
            food = item.get('foods', 3)
            if food != 3:
                foo = food[0]
                name = foo.get('food_name')
                if name in result:
                    obj = result[name]
                    obj.origin.add(origin)
                else:
                    obj = ingredient(id_tracker, name,
                                     foo.get("serving_unit", 0),
                                     foo.get("serving_weight_grams", 0),
                                     foo.get("nf_calories", 0),
                                     foo.get("nf_total_fat", 0),
                                     foo.get("nf_saturated_fat", 0),
                                     foo.get("nf_cholesterol", 0),
                                     foo.get("nf_sodium", 0),
                                     foo.get("nf_total_carbohydrate", 0),
                                     foo.get("nf_dietary_fiber", 0),
                                     foo.get("nf_sugars", 0),
                                     foo.get("nf_protein", 0),
                                     foo.get("nf_potassium", 0))
                    result[name] = obj
                    id_tracker += 1
    return result
