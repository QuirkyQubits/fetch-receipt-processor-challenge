import datetime

from django.test import TestCase
from django.utils import timezone

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

class QuestionModelTests(TestCase):
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