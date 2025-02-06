import datetime
import json

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Receipt, Item


INVALID_RECEIPT_BAD_REQUEST_STR = "The receipt is invalid."
ID_NOT_FOUND_STR = "No receipt found for that ID."

def create_receipt_with_day_offset(days: int):
    """
    Create a receipt with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Receipt.objects.create(
        hexadecimal_id='test-hex-id',
        retailer='test-retailer',
        purchaseDate=datetime.date(time.year, time.month, time.day),
        purchaseTime=datetime.time(time.hour, time.minute, 0),
        total=3.14
    )


def create_item_with_price(receipt: Receipt, price: float):
    return Item.objects.create(receipt=receipt, shortDescription='test-short-description', price=price)


class ReceiptModelTests(TestCase):
    def test_creation_of_future_receipt_is_ok(self):
        """
        For a receipt whose purchaseDate/Time is in the future,
        treat it as a valid receipt and not throw any errors.

        If we were to create some kind of page showing a list of receipts to the user,
        we might want to do something to handle such receipts specially such as flitering them out,
        and also disallow the user from entering such a receipt in the first place
        on a purely user-facing webpage, although we can allow such receipts to be created
        and viewed through the admin portal or internal APIs.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_receipt = create_receipt_with_day_offset(30)
        self.assertIs(future_receipt.hexadecimal_id == 'test-hex-id', True)


class ItemModelTests(TestCase):
    def test_floating_point_precision_for_more_than_2_decimal_places_item(self):
        '''
        Test creating Receipts with Items that have a price with > 2 decimal points.
        It seems like Django's DecimalField "decimal_places" doesn't self-enforce
        when directly created with the raw Model class constructor,
        and the raw float value is stored in the table regardless of how many decimal places it has.

        Let's make an assumption to permit this for now, because there isn't much information
        about what the value gained from writing a lot of logic to validate decimal places is,
        such as what the concrete needs of our application are.

        However, if necessary, modify this unit test to reflect any logic needed to validate
        decimal places, e.g. if we want to send a 400 bad request if the input has > 2 decimal places.
        '''

        ''' Example:
            "items": [
                {"shortDescription": "Pepsi - 12-oz", "price": "1.255"},
                {"shortDescription": "Dasani", "price": "1.403"},
                {"shortDescription": "Coke", "price": "1.999"}
            ]
        '''

        receipt = create_receipt_with_day_offset(0)

        item = create_item_with_price(receipt, 1.255)
        self.assertEqual(item.price, 1.255)

        item = create_item_with_price(receipt, 1.403)
        self.assertEqual(item.price, 1.403)

        item = create_item_with_price(receipt, -99.999)
        self.assertEqual(item.price, -99.999)


class ReceiptViewTests(TestCase):
    def test_sending_completely_valid_json_to_receipt_process_view(self):
        '''
        Test that sending a completely valid json is fine and returns 200
        '''

        json_string = '''
        {
            "retailer": "Walgreens",
            "purchaseDate": "2022-01-02",
            "purchaseTime": "08:13",
            "total": "2.65",
            "items": [
                {"shortDescription": "Pepsi - 12-oz", "price": "1.25"},
                {"shortDescription": "Dasani", "price": "1.40"}
            ]
        }
        '''

        url = reverse("receipts:get_id_for_receipt")
        post_dict = {'receipt_json_str': json_string}
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "\"id\":")
        self.assertNotContains(response, INVALID_RECEIPT_BAD_REQUEST_STR, status_code=200)
    

    def test_floating_point_precision_for_more_than_2_decimal_places_receipt_total(self):
        '''
        Test that Receipts with Items that have a price with > 2 decimal points
        and a total with > 2 decimal points have those values rounded.
        '''

        json_string = '''
        {
            "retailer": "Walgreens",
            "purchaseDate": "2022-01-02",
            "purchaseTime": "08:13",
            "total": "2.6592568",
            "items": [
                {"shortDescription": "Pepsi - 12-oz", "price": "1.255"},
                {"shortDescription": "Dasani", "price": "1.403"},
                {"shortDescription": "Coke", "price": "1.999"},
                {"shortDescription": "Softdrink", "price": "-99.9999999"}
            ]
        }
        '''

        url = reverse("receipts:get_id_for_receipt")
        post_dict = {'receipt_json_str': json_string}
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "\"id\":")
        self.assertNotContains(response, INVALID_RECEIPT_BAD_REQUEST_STR, status_code=200)

        the_json = json.loads(response.content.decode("utf-8"))
        hex_id = the_json['id']
        receipt = Receipt.objects.get(hexadecimal_id=hex_id)

        self.assertEqual(str(receipt.total), "2.66")
        for item in receipt.item_set.all():
            self.assertTrue(str(item.price) in {"1.26", "1.40", "2.00", "-100.00"})


    def test_sending_receipts_with_negative_price_items_to_receipt_process_view_is_fine(self):
        '''
        Test that sending receipts with negative price items is ok and returns 200.
        This might be a discount or item return.
        '''

        json_string = '''
        {
            "retailer": "Walgreens",
            "purchaseDate": "2022-01-02",
            "purchaseTime": "08:13",
            "total": "2.65",
            "items": [
                {"shortDescription": "Pepsi - 12-oz", "price": "-1.25"},
                {"shortDescription": "Dasani", "price": "-1.40"}
            ]
        }
        '''

        url = reverse("receipts:get_id_for_receipt")
        post_dict = {'receipt_json_str': json_string}
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "\"id\":")
        self.assertNotContains(response, INVALID_RECEIPT_BAD_REQUEST_STR, status_code=200)
    

    def test_sending_malformed_string_to_receipt_process_view_throws_error(self):
        '''
        Test that sending malformed JSON is not ok and returns 400.
        '''

        json_string = '''
        {
        test
        }
        '''

        url = reverse("receipts:get_id_for_receipt")
        post_dict = {'receipt_json_str': json_string}
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 400)
        self.assertNotContains(response, text="\"id\":", status_code=400)
        self.assertContains(response, INVALID_RECEIPT_BAD_REQUEST_STR, status_code=400)
    

    def test_sending_empty_string_to_receipt_process_view_throws_error(self):
        '''
        Test that sending an empty string is not ok and returns 400.
        '''

        json_string = ''

        url = reverse("receipts:get_id_for_receipt")
        post_dict = {'receipt_json_str': json_string}
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 400)
        self.assertNotContains(response, text="\"id\":", status_code=400)
        self.assertContains(response, INVALID_RECEIPT_BAD_REQUEST_STR, status_code=400)
    

    def test_sending_receipts_with_no_items_to_receipt_process_view_is_fine(self):
        '''
        Test that sending receipts with no items is ok and returns 200.
        '''

        json_string = '''
        {
            "retailer": "Walgreens",
            "purchaseDate": "2022-01-02",
            "purchaseTime": "08:13",
            "total": "2.65",
            "items": [
            ]
        }
        '''

        url = reverse("receipts:get_id_for_receipt")
        post_dict = {'receipt_json_str': json_string}
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "\"id\":")
    

    def test_sending_json_with_unexpected_data_types_to_receipt_process_view_throws_error(self):
        '''
        Test that sending json with unexpected data types is not ok and returns 400.
        '''

        json_string = '''
        {
            "retailer": "Walgreens",
            "purchaseDate": 42,
            "purchaseTime": "08:13",
            "total": "2.65",
            "items": [
                {"shortDescription": type(bool), "price": "1.25"},
                {"shortDescription": "Dasani", "price": "1.40"}
            ]
        }
        '''

        url = reverse("receipts:get_id_for_receipt")
        post_dict = {'receipt_json_str': json_string}
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 400)
        self.assertNotContains(response, text="\"id\":", status_code=400)
        self.assertContains(response, INVALID_RECEIPT_BAD_REQUEST_STR, status_code=400)
    

    def test_sending_json_with_extra_kvps_to_receipt_process_view_is_fine(self):
        '''
        Test that sending json with extra key/value pairs is ok and returns 200.
        (I don't see a big problem with this, but it might be worth validating as a low-pri item)
        '''

        json_string = '''
        {
            "retailer": "Walgreens",
            "purchaseDate": "2022-01-02",
            "purchaseTime": "08:13",
            "total": "2.65",
            "items": [
                {"shortDescription": "Pepsi - 12-oz", "price": "1.25"},
                {"shortDescription": "Dasani", "price": "1.40"}
            ],
            "apples": 3,
            "bananas": 4,
            "oranges": 5
        }
        '''

        url = reverse("receipts:get_id_for_receipt")
        post_dict = {'receipt_json_str': json_string}
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "\"id\":")


    def test_sending_json_with_missing_kvps_to_receipt_process_view_throws_error(self):
        '''
        Test that sending JSON with missing key/values to receipt/process isn't ok and returns 400.
        '''

        json_string = '''
        {
            "purchaseDate": "2022-01-02",
            "purchaseTime": "08:13",
            "total": "2.65",
            "items": [
                {"shortDescription": "Pepsi - 12-oz", "price": "1.25"},
                {"shortDescription": "Dasani", "price": "1.40"}
            ]
        }
        '''

        url = reverse("receipts:get_id_for_receipt")
        post_dict = {'receipt_json_str': json_string}
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 400)
        self.assertNotContains(response, text="\"id\":", status_code=400)
        self.assertContains(response, INVALID_RECEIPT_BAD_REQUEST_STR, status_code=400)


    def test_sending_json_with_incorrectly_formatted_date_to_receipt_process_view_throws_error(self):
        '''
        Test that sending JSON with incorrectly formatted /corrupted date to receipt/process isn't ok and returns 400.
        '''

        json_string = '''
        {
            "retailer": "Walgreens",
            "purchaseDate": "2022-01-02",
            "purchaseTime": "38:13",
            "total": "2.65",
            "items": [
                {"shortDescription": "Pepsi - 12-oz", "price": "1.25"},
                {"shortDescription": "Dasani", "price": "1.40"}
            ]
        }
        '''

        url = reverse("receipts:get_id_for_receipt")
        post_dict = {'receipt_json_str': json_string}
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 400)
        self.assertNotContains(response, text="\"id\":", status_code=400)
        self.assertContains(response, INVALID_RECEIPT_BAD_REQUEST_STR, status_code=400)
    

    def test_sending_json_with_blank_retailer_to_receipt_process_view_is_fine(self):
        '''
        Test that sending JSON with a blank retailer to receipt/process is ok and returns 200.
        (Maybe the retailer just isn't known, maybe this is a backfill of data, etc.)
        '''

        json_string = '''
        {
            "retailer": "",
            "purchaseDate": "2022-01-02",
            "purchaseTime": "18:13",
            "total": "2.65",
            "items": [
                {"shortDescription": "Pepsi - 12-oz", "price": "1.25"},
                {"shortDescription": "Dasani", "price": "1.40"}
            ]
        }
        '''

        url = reverse("receipts:get_id_for_receipt")
        post_dict = {'receipt_json_str': json_string}
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "\"id\":")
    

    def test_calling_receipt_process_view_with_get_throws_error(self):
        '''
        Test that calling receipts/process with GET is not ok and returns 400.
        '''

        json_string = '''
        {
            "retailer": "",
            "purchaseDate": "2022-01-02",
            "purchaseTime": "18:13",
            "total": "2.65",
            "items": [
                {"shortDescription": "Pepsi - 12-oz", "price": "1.25"},
                {"shortDescription": "Dasani", "price": "1.40"}
            ]
        }
        '''

        url = reverse("receipts:get_id_for_receipt")
        response = self.client.get(url)
        self.assertContains(response, "Invalid request method, this can only take POST", status_code=400)
    

    def test_points_api_on_id_that_does_not_exist_returns_404(self):
        '''
        Test that calling receipts/points returns 404 for unknown id
        '''

        url = reverse("receipts:points", args=('id-that-does-not-exist',))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, ID_NOT_FOUND_STR, status_code=404)


    def test_points_api_with_post_throws_error(self):
        '''
        Test that hitting the points api with POST is not ok and returns 400.
        '''

        json_string = '''
        {
            "retailer": "",
            "purchaseDate": "2022-01-02",
            "purchaseTime": "18:13",
            "total": "2.65",
            "items": [
                {"shortDescription": "Pepsi - 12-oz", "price": "1.25"},
                {"shortDescription": "Dasani", "price": "1.40"}
            ]
        }
        '''

        url = reverse("receipts:points", args=('c288fc46-3b6-8b4c-830d-77c75e9644e6',))
        post_dict = {'receipt_json_str': json_string}
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Invalid request method, this can only take GET", status_code=400)


    def test_create_receipt_then_call_points_api_on_its_id(self):
        '''
        Test that calling receipts/points returns 404 for unknown id,
        then creating an Receipt and calling the Points api again returns 200
        and gives the expected points result.
        '''

        url = reverse("receipts:points", args=('id-that-does-not-exist',))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, ID_NOT_FOUND_STR, status_code=404)

        json_string = '''
        {
            "retailer": "Walgreens",
            "purchaseDate": "2022-01-02",
            "purchaseTime": "08:13",
            "total": "2.65",
            "items": [
                {"shortDescription": "Pepsi - 12-oz", "price": "1.25"},
                {"shortDescription": "Dasani", "price": "1.40"}
            ]
        }
        '''

        url = reverse("receipts:get_id_for_receipt")
        post_dict = {'receipt_json_str': json_string}
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "\"id\":")
        the_json = json.loads(response.content.decode("utf-8"))
        hex_id = the_json['id']
        
        url = reverse("receipts:points", args=(hex_id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, ID_NOT_FOUND_STR, status_code=200)
        the_json = json.loads(response.content.decode("utf-8"))
        self.assertEqual(the_json['points'], 15)
    

    def test_various_points_calls_return_expected_points(self):
        json_string = '''
        {
        "retailer": "Target",
        "purchaseDate": "2022-01-01",
        "purchaseTime": "13:01",
        "items": [
            {
            "shortDescription": "Mountain Dew 12PK",
            "price": "6.49"
            },{
            "shortDescription": "Emils Cheese Pizza",
            "price": "12.25"
            },{
            "shortDescription": "Knorr Creamy Chicken",
            "price": "1.26"
            },{
            "shortDescription": "Doritos Nacho Cheese",
            "price": "3.35"
            },{
            "shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ",
            "price": "12.00"
            }
        ],
        "total": "35.35"
        }
        '''
        url = reverse("receipts:get_id_for_receipt")
        post_dict = {'receipt_json_str': json_string}
        response = self.client.post(url, post_dict)
        self.assertNotContains(response, INVALID_RECEIPT_BAD_REQUEST_STR, status_code=200)
        the_json = json.loads(response.content.decode("utf-8"))
        hex_id = the_json['id']
        
        url = reverse("receipts:points", args=(hex_id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, ID_NOT_FOUND_STR, status_code=200)
        the_json = json.loads(response.content.decode("utf-8"))
        self.assertEqual(the_json['points'], 28)

        json_string = '''
        {
        "retailer": "M&M Corner Market",
        "purchaseDate": "2022-03-20",
        "purchaseTime": "14:33",
        "items": [
            {
            "shortDescription": "Gatorade",
            "price": "2.25"
            },{
            "shortDescription": "Gatorade",
            "price": "2.25"
            },{
            "shortDescription": "Gatorade",
            "price": "2.25"
            },{
            "shortDescription": "Gatorade",
            "price": "2.25"
            }
        ],
        "total": "9.00"
        }
        '''
        url = reverse("receipts:get_id_for_receipt")
        post_dict = {'receipt_json_str': json_string}
        response = self.client.post(url, post_dict)
        self.assertNotContains(response, INVALID_RECEIPT_BAD_REQUEST_STR, status_code=200)
        the_json = json.loads(response.content.decode("utf-8"))
        hex_id = the_json['id']
        
        url = reverse("receipts:points", args=(hex_id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, ID_NOT_FOUND_STR, status_code=200)
        the_json = json.loads(response.content.decode("utf-8"))
        self.assertEqual(the_json['points'], 109)