from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import Receipt, Item

import random
import json

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
        receipt_json_str = request.POST['receipt_json_str']
        print(f"Receipt json string received: {receipt_json_str}")

        random_hex_id = get_random_hexadecimal_id()
        # in the (very!) unlikely case of a collision, regenerate the ID until it's unique
        while random_hex_id in Receipt.objects.values_list('hexadecimal_id', flat=True):
            random_hex_id = get_random_hexadecimal_id()

        # TODO: we might also want to add some data validation here

        try:
            data = json.loads(receipt_json_str)

            retailer = data['retailer']
            purchaseDate = data['purchaseDate']
            purchaseTime = data['purchaseTime']
            total = data['total']
            items = data['items']

            receipt = Receipt.objects.create(hexadecimal_id=random_hex_id, retailer=retailer, purchaseDate=purchaseDate, purchaseTime=purchaseTime, total=total)

            for item in items:
                shortDescription = item['shortDescription']
                price = item['price']
                receipt.item_set.create(shortDescription=shortDescription, price=price)

            return JsonResponse({'id': random_hex_id})
        except Exception as e:
            return HttpResponseBadRequest("Invalid or malformed JSON.")
    else:
        return HttpResponseBadRequest("Invalid request method, this can only take POST")


def accept_receipt_as_user_input(request):
    return render(request, "receipts/upload_receipt_and_get_id.html")


def points(request, receipt_id: str) -> JsonResponse:
    if request.method == "GET":
        print(f"Receipt json string received: {receipt_id}")
        receipt = get_object_or_404(Receipt, pk=receipt_id)
        return JsonResponse({'points': receipt.get_points()})
    else: # POST
        return HttpResponseBadRequest("Invalid request method, this can only take GET")