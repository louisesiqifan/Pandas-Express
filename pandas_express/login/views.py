from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def login(request):
    html = '''
    <html>
    <link href="https://fonts.googleapis.com/css?family=Quicksand:300,500" rel="stylesheet">
    <link rel="shortcut icon" href="{% static '../static/favicon.ico' %}" />
    <meta name="viewport" content="width=device-width, initial-scale=0.67">
    <head>
        <title>Pandas Express</title>
        <link rel="stylesheet" type="text/css" href="{% static "/home.css" %}" />
    </head>
    <body>
        <div id="header">
            <h1>Log in</h1>
        </div>
    </body>
</html>'''
    return HttpResponse(html)
