from django.shortcuts import render

# Create your views here.
def detail(request):
    """A view of all bands."""
    return render(request, 'detail.html')