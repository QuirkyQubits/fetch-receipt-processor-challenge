from django.http import HttpResponse, JsonResponse
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


def index(request):
    a_dict = {'id': get_random_hexadecimal_id()}
    return JsonResponse(a_dict)
