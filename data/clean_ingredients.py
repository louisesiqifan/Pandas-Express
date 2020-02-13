import re
import spacy
import csv
import string
from spacy.matcher import Matcher
from fractions import Fraction
from word2number import w2n

NLP = spacy.load('en_core_web_sm')

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
         "filets": ["filet", "filets"], "sprig": ["sprigs", "sprig"], "stalk": ["stalks", "stalk"]}

IGNORE = ['packages', 'package', 'boxes', 'box','packets', 'packet',
          'pieces', 'piece', 'chunk', 'jars', 'jar', 'bags', 'bag',
          'containers', 'container', 'bricks', 'brick', 'bottles', 'bottle',
          'heads', 'leaf', 'leaves', 'head', 'medium', 'large', 'small']


class String:
    def __init__(self, s):
        self.s_origin = s
        self.s_clean = None
        self.num = None
        self.quantifier = None
        self.root = None
        self.check = False

    def rough_clean(self):
        s1 = re.sub(r'\(.*\)', '', self.s_origin.split(',')[0]).lower()
        s2 = clean_unicode_fractions(s1)
        self.s_clean = s2

    def find_num(self):
        if self.s_clean.split(' ')[0] == 'one-and-a-half':
            self.s_clean = re.sub('one-and-a-half', '1 1/2', self.s_clean)
        matcher = Matcher(NLP.vocab)
        pattern = [{'POS': 'X', 'OP': '?'}, {'POS': 'NUM', 'OP': '*'}]
        matcher.add('num', None, pattern)
        doc = NLP(self.s_clean)
        m = matcher(doc)
        n = sorted([doc[a:b].text for _, a, b in m], key=lambda z: len(z))
        if n != []:
            self.s_clean = re.sub(n[-1], '', self.s_clean)
            clean_num(n[-1], self)

    def find_quantifier(self):
        if self.quantifier is not None:
            return
        words = self.s_clean.split(' ')
        for word in words:
            q = clean_quantifier(word)
            if q is not None and q != '':
                self.quantifier = q
                self.s_clean = re.sub(word, '', self.s_clean)
                return

    def find_root(self):
        remaining_words = self.s_clean.split()
        if len(remaining_words) == 1:
            self.root = remaining_words[0]
        else:
            self.root = unique_words(clean_pack(clean_verb(self.s_clean)))

    def check_status(self):
        if self.root is None:
            self.check = true
            return
        elif len(self.root.split()) > 4:
            self.check = True
            return
        elif len(self.root.split()) > 1:
            if self.root.find('-') == 0:
                self.check = True
                return
            elif self.root.find(r'\d') >= 0:
                self.check = True
                return
        if self.num is None or self.num == 0:
            if self.quantifier is not None:
                self.check = True
                return


def convert_units():
    result = {}
    for key, val in UNITS.items():
        for word in val:
            result[word] = key
    return result


def clean_pack(s):
    for word in IGNORE:
        s = s.replace(word, '')
    return s


def unique_words(s):
    ulist = []
    [ulist.append(x) for x in s.split(' ') if x not in ulist]
    return ' '.join(ulist)


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
    remove = string.punctuation
    remove = remove.replace("-", "")
    remove = remove.replace("/", "")
    return s.translate(str.maketrans('', '', remove))


def clean_quantifier(w):
    return UNIT_DICT.get(w, None)
    '''
    for unit, lst in UNITS.items():
        if w in lst:
            return unit
    return None
    '''


def clean_num(s, obj=None):
    try:
        k = round(float(sum(Fraction(k) for k in s.split())),2)
        obj.num = k
    except:
        pass

    try:
        k = w2n.word_to_num(s)
        obj.num = k
    except:
        pass

    if s.find('-') >= 0:
        words = s.split(' ')
        if words[0] == 'half':
            words.pop(0)
        if len(words) == 1:
            lst = s.split('-')
            q = clean_quantifier(lst[-1])
            obj.num = round(float(Fraction(lst[0])),2)
            obj.quantifier = q
            obj.s_clean = re.sub(lst[-1], '', obj.s_clean)
        else:
            temp = words.pop(0)
            try:
                n = int(temp)
            except:
                n = w2n.word_to_num(temp)
            s_new = ' '.join(words)
            lst = s_new.split('-')
            n_new = round(float(sum(Fraction(t) for t in lst[0].split())),2)
            q = clean_quantifier(lst[-1])
            obj.quantifier = q
            obj.s_clean = re.sub(lst[-1], '', obj.s_clean)
            if n_new != 0:
                obj.num = n*n_new
            else:
                obj.num = n


def clean_verb(s):
    result = []
    words = s.split(' ')
    for word in words:
        doc = NLP(word)
        if len(doc) == 1:
            w = doc[0]
            p = w.pos_
            if p == 'VERB' or p == 'ADJ' or p == 'PUNCT' \
            or w.like_num or p == 'ADV' or w.is_stop or len(w.text) == 1:
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
    UNIT_DICT = convert_units()
    with open('ingredients.txt', 'r', encoding='utf-8') as f:
        x = f.read().splitlines()
    with open('cleaned_ingredients.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter="|")
        n = 0
        for s in x:
            print(s)
            obj = String(s)
            obj.rough_clean()
            obj.find_num()
            obj.find_quantifier()
            obj.find_root()
            obj.check_status()
            writer.writerow([n, obj.s_origin, obj.num, obj.quantifier,
                             obj.root, obj.check])
            n += 1
