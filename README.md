 .___                     _                    .____                                         
 /   \   ___  , __     ___/   ___    ____      /      _  .- \,___, .___    ___    ____   ____
 |,_-'  /   ` |'  `.  /   |  /   `  (          |__.    \,'  |    \ /   \ .'   `  (      (    
 |     |    | |    | ,'   | |    |  `--.       |       /\   |    | |   ' |----'  `--.   `--. 
 /     `.__/| /    | `___,' `.__/| \___.'      /----/ /  \  |`---' /     `.___, \___.' \___.'


Presented by Team AttributeError


## Pandas Express

Pandas Express is an interactive recipe platform that allows users to obtain personalized food recipes recommendations with nutritional information. Our searching function is designed so that users can include nutritional preference. Additionally, we incorporate a data visualization for the single dish’s nutritional data to all recipes stored in our database.


## User Direction

###Log-in Page###
New Users should register themselves through inputting a user name.

Returning users should identify themselves with the user them they register before

###Home###
A search page where the user can input terms of recipe they want to see, cooking time (active time means the time that needs for them to pay close attention to cook the cuisine; total time means the time that needs for the entire duration of cooking) and the level of cooking difficulty (set by those who upload the original recipe)

###Advance Search###
A more complicated search function that allows user to not only input their search term, cooking time and cooking difficulty, but also allows the user to input their preference for the quantile of one or more nutritional factors.

###Recipe Detail###
Allows the user to see the detailed cooking time, recipe ingredient as well as the step-by-step direction for the cooking.  We also include a data visualization piece in which user can see how the dish's one/two nutritional factors compared to all recipes included.

###Favorite###
Allows the user to save recipe they are in favor of and access this list of favorite recipes at any given time.


## Usage

Install required package::
~~~
pip install -r requirements.txt
~~~

Use the app:
~~~
./run.sh
~~~

Note: we recommend using FireFox to experience the fullest of our platform.


## Warning

Any returning user should choose returning user before they input their user name in our Login page. If a returning user inputs their user name in the login page as a new user, the platform will generate an error.


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

