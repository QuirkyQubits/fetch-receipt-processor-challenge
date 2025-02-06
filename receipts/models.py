from django.db import models
import math
from .settings import DEBUG

class Receipt(models.Model):
    hexadecimal_id = models.CharField(max_length=36, primary_key=True) # e.g. c288fc46-3b6-8b4c-830d-77c75e9644e6
    retailer = models.CharField(max_length=100)
    purchaseDate = models.DateField()
    purchaseTime = models.TimeField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
            return f"{self.retailer} - {self.purchaseDate} - {self.purchaseTime} - {self.total}"

    def get_points(self):
        total_points = 0
        
        # One point for every alphanumeric character in the retailer name
        for c in self.retailer:
            if c.isalnum():
                total_points += 1
        if DEBUG:
            print(f"Total points after retailer name: {total_points}")

        # 50 points if the total is a round dollar amount with no cents.
        if self.total == int(self.total):
            total_points += 50
        if DEBUG:
            print(f"Total points after if total a round dollar amount: {total_points}")

        # 25 points if the total is a multiple of 0.25.
        self_total_as_int_times_100 = self.total * 100
        # total / 0.25 being an int is equivalent to total*100 / 25 being an int
        if self_total_as_int_times_100 / 25 == int(self_total_as_int_times_100 / 25):
            total_points += 25
        
        if DEBUG:
            print(f"Total points after if total is a multiple of 0.25: {total_points}")

        # 5 points for every two items on the receipt.
        total_points += 5 * (self.item_set.count() // 2)

        if DEBUG:
            print(f"Total points after every two items: {total_points}")

        # If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer. The result is the number of points earned.
        # multiplying the price by 0.2 is the same as dividing by 5
        for item in self.item_set.all():
            if len(item.shortDescription.strip()) % 3 == 0:
                total_points += math.ceil(item.price / 5)
        if DEBUG:
            print(f"Total points after if trimmed len is multiple of 3: {total_points}")
        
        # 6 points if the day in the purchase date is odd.
        if self.purchaseDate.day % 2 == 1: # odd
            total_points += 6
        if DEBUG:
            print(f"Total points after if purchaseDate is odd: {total_points}")

        # 10 points if the time of purchase is after 2:00pm and before 4:00pm.
        if self.purchaseTime.hour >= 14 and self.purchaseTime.hour < 16:
            total_points += 10
        if DEBUG:
            print(f"Total points after if time of purchase is between 2 and 4 PM: {total_points}")

        return total_points

class Item(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    shortDescription = models.CharField(max_length=1000)
    price = models.DecimalField(max_digits=1000, decimal_places=2)

    def __str__(self):
        return f"{self.shortDescription} - {self.price} - {self.receipt.hexadecimal_id}"


