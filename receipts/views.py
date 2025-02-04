from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from .forms import NameForm

import random

'''
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
'''

def get_random_hexadecimal_id() -> str:
    randint_1 = random.randint(0, 16**8-1)
    randint_2 = random.randint(0, 16**4-1)
    randint_3 = random.randint(0, 16**4-1)
    randint_4 = random.randint(0, 16**4-1)
    randint_5 = random.randint(0, 16**12-1)

    return '-'.join([hex(randint_1)[2:], hex(randint_2)[2:], hex(randint_3)[2:], hex(randint_4)[2:], hex(randint_5)[2:]])


def get_id_for_receipt(request):
    if request.method == "POST":
        # print(f"Receipt json string received: {receipt_json_str}")
        a_dict = {'id': get_random_hexadecimal_id()}
        return JsonResponse(a_dict)
    else:
        return HttpResponse("Invalid request method, this can only take POST")



def get_receipt(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:

            print("POST request and Form is valid!")

            return HttpResponseRedirect("/receipts/results") # passing in some id

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, "receipts/upload_receipt_and_get_id.html", {"form": form})


def points(request, receipt_id: str) -> JsonResponse:
    if request.method == "GET":
        print(f"Receipt json string received: {receipt_id}")
        a_dict = {'points': 32}
        return JsonResponse(a_dict)
    else:
        return HttpResponse("Invalid request method, this can only take GET")