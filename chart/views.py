from django.shortcuts import render

def covid19(request):
    return render(request, 'covid.html')