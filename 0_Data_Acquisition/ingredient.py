import util
from pycorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP('http://localhost:9000')


all_recipes = util.read_json("foodnetwork.json")
ingredients = set()
for recipes in all_recipes.values():
    for recipe in recipes:
        if 'ingredients' in recipe:
            for ing in recipe['ingredients']:
                result = nlp.annotate(ing, properties={'annotators': 'ner, pos', 
                                          'outputFormat': 'json',})
                tokens = result["sentences"][0]['tokens']
                for token in tokens:
                    if token['pos'] == 'NN':
                        ingredients.add(token['lemma'])

