# Data Logic

Note: We deleted most of the files on git, and you can find the csv and json files on the vm.


## Data Acquisition

Crawled data from foodnetwork.com by `foodnetwork.py`

Saved file as `foodnetwork.json`

## Clean Ingredients

Acquired a list of all ingredients from `foodnetwork.json`, saved it to `ingredients.txt`

Used NLP (file: `clean_ingredients.py`) to clean ingredients into a dataframe of quantity, quantifier and noun.

Saved file as `cleaned_ingredients.csv`

## Get Nutrition Value

We manually cleaned some data in  `cleaned_ingredients.csv` and split them to several files of 200 rows, because each day nutritionix api only allows 200 calls.

The saved files are numbered as `ingredient_i.csv` for `i` in `1-31`.

Then, using `nutritionix.py` to get nutrition values from the cleaned ingredients from `ingredient_i.csv` and saved them to `i.json`.

## Map ingredients back to dishes

Next, we map ingredients back to their dishes by `rid_to_cleaned_words.py`. 

Specifically, `Ingredient` class in `clean_json.py` has a `origin` attribute that saves the original ingredient string.

## Create database

Finally, we created `food_map.db` by `create_db.`

