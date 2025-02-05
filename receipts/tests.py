import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Receipt

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
    

    def test_sending_empty_string_to_receipt_process_view_throws_error(self):
        '''
        Test that sending an empty string is not ok and returns 400.
        '''

        json_string = ''

        url = reverse("receipts:get_id_for_receipt")
        post_dict = {'receipt_json_str': json_string}
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 400)
    

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