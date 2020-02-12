import re
import spacy
import csv
from spacy.matcher import Matcher
from fractions import Fraction
from word2number import w2n

NLP = spacy.load('en_core_web_sm')
UNITS1 = {"cup": ["cups", "cup", "c.", "c"], "fluid_ounce": ["fl. oz.", "fl oz", "fluid ounce", "fluid ounces"],
         "gallon": ["gal", "gal.", "gallon", "gallons"], "ounce": ["oz", "oz.", "ounce", "ounces"],
         "pint": ["pt", "pt.", "pint", "pints"], "pound": ["lb", "lb.", "pound", "pounds"],
         "quart": ["qt", "qt.", "qts", "qts.", "quart", "quarts"],
         "tablespoon": ["tbsp.", "tbsp", "T", "T.", "tablespoon", "tablespoons", "tbs.", "tbs"],
         "teaspoon": ["tsp.", "tsp", "t", "t.", "teaspoon", "teaspoons"],
         "gram": ["g", "g.", "gr", "gr.", "gram", "grams"], "kilogram": ["kg", "kg.", "kilogram", "kilograms"],
         "liter": ["l", "l.", "liter", "liters"], "milligram": ["mg", "mg.", "milligram", "milligrams"],
         "milliliter": ["ml", "ml.", "milliliter", "milliliters"], "pinch": ["pinch", "pinches"],
         "dash": ["dash", "dashes"], "touch": ["touch", "touches"], "handful": ["handful", "handfuls"],
         "stick": ["stick", "sticks"], "clove": ["cloves", "clove"], "can": ["cans", "can"],
         "slice": ["slice", "slices"], "scoop": ["scoop", "scoops"], "filets": ["filet", "filets"], "sprig": ["sprigs", "sprig"]}

UNITS = {"cup": ["cups", "cup", "c"], "fluid_ounce": ["fl oz", "fluid ounce", "fluid ounces"],
         "gallon": ["gal", "gallon", "gallons"], "ounce": ["oz", "ounce", "ounces"],
         "pint": ["pt", "pint", "pints"], "pound": ["lb", "pound", "pounds"],
         "quart": ["qt", "qts", "quart", "quarts"],
         "tablespoon": ["tbsp", "T", "tablespoon", "tablespoons", "tbs"],
         "teaspoon": ["tsp", "t", "teaspoon", "teaspoons"],
         "gram": ["g", "gr", "gram", "grams"], "kilogram": ["kg", "kilogram"],
         "liter": ["l", "liter", "liters"], "milligram": ["mg", "milligram", "milligrams"],
         "milliliter": ["ml", "milliliter", "milliliters"], "pinch": ["pinch", "pinches"],
         "dash": ["dash", "dashes"], "touch": ["touch", "touches"], "handful": ["handful", "handfuls"],
         "stick": ["stick", "sticks"], "clove": ["cloves", "clove"], "can": ["cans", "can"],
         "slice": ["slice", "slices"], "scoop": ["scoop", "scoops"],
         "filets": ["filet", "filets"], "sprig": ["sprigs", "sprig"],
         "box": ["box", "boxes"]}


class String:
    def __init__(self, s):
        self.s_origin = s
        self.s_clean = None
        self.num = None
        self.quantifier = None
        self.root = None
        self.check = False

    def rough_clean(self):
        s1 = re.sub(r'\(.*\)', '', self.s_origin.split(',')[0])
        s2 = re.sub(r'\.', '', s1).lower()
        s3 = clean_unicode_fractions(s2)
        self.s_clean = s3

    def find_num(self):
        matcher = Matcher(NLP.vocab)
        pattern = [{'POS': 'X', 'OP': '?'}, {'POS': 'NUM', 'OP': '*'}]
        matcher.add('num', None, pattern)
        doc = NLP(self.s_clean)
        m = matcher(doc)
        n = sorted([doc[a:b].text for _, a, b in m], key=lambda z: len(z))
        if n != []:
            self.s_clean = re.sub(n[-1], '', self.s_clean)
            try:
                k = float(sum(Fraction(k) for k in n[-1].split()))
            except:
                try:
                    k = w2n.word_to_num(n[-1])
                except:
                    k = n[-1]
                    self.check = True
            self.num = k

    def find_quantifier(self):
        words = self.s_clean.split(' ')
        for word in words:
            for unit, lst in UNITS.items():
                if word in lst:
                    self.quantifier = unit
                    self.s_clean = re.sub(word, '', self.s_clean)
                    return

    def find_root(self):
        remaining_words = self.s_clean.split()
        if len(remaining_words) == 1:
            self.root = remaining_words[0]
        else:
            self.root = clean_verb(self.s_clean)

    def check_status(self):
        if self.root is None:
            self.check = true
            return
        elif len(self.root.split()) > 3:
            self.check = True
            return
        elif len(self.root.split()) > 1:
            if self.root.find('-') == 0:
                self.check = True
                return
        if self.num is None or self.num == 0:
            if self.quantifier is not None:
                self.check = True
                return



def clean_unicode_fractions(s):
    """
    Replace unicode fractions with ascii representation, preceded by a
    space.
    "1\x215e" => "1 7/8"
    """

    fractions = {u'\x215b': '1/8', u'\x215c': '3/8', u'\x215d': '5/8',
                 u'\x215e': '7/8', u'\x2159': '1/6', u'\x215a': '5/6',
                 u'\x2155': '1/5', u'\x2156': '2/5', u'\x2157': '3/5',
                 u'\x2158': '4/5', u'\xbc': ' 1/4', u'\xbe': '3/4',
                 u'\x2153': '1/3', u'\x2154': '2/3', u'\xbd': '1/2',}

    for f_unicode, f_ascii in fractions.items():
        s = s.replace(f_unicode, f_ascii)

    return s


def clean_verb(s):
    result = []
    words = s.split(' ')
    for word in words:
        doc = NLP(word)
        if len(doc) == 1:
            w = doc[0]
            p = w.pos_
            if p == 'VERB' or p == 'ADJ' or p == 'PUNCT' \
            or w.like_num or p == 'ADV' or w.is_stop:
                continue
        result.append(word)
    return ' '.join(result).strip(' ')

#######################
tests = ['3 slices bacon', '2 cups shredded monterey jack',
         '1 1/4 cups granulated sugar', '1 cup cornmeal',
         '3 tablespoons reduced-fat sour cream', 'Foil or parchment',
         '1 pound bison loin', '1/8 teaspoon grated whole nutmeg',
         '1 onion', '2 tbsp. brown sugar', '1 tsp cumin', '½ red bell pepper',
         '25 grams water', 'Four 1/2-inch-thick slices country bread']

if __name__ == "__main__":
    with open('ingredients.txt', 'r', encoding='utf-8') as f:
        x = f.read().splitlines()
    with open('cleaned_ingredients.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter="|")
        for s in x:
            print(s)
            obj = String(s)
            obj.rough_clean()
            obj.find_num()
            obj.find_quantifier()
            obj.find_root()
            obj.check_status()
            writer.writerow([obj.num, obj.quantifier, obj.root, obj.check])
