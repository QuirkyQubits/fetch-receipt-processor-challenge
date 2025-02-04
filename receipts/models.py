from django.db import models


class Receipt(models.Model):
    hexadecimal_id = models.CharField(max_length=36, primary_key=True) # e.g. c288fc46-3b6-8b4c-830d-77c75e9644e6
    retailer = models.CharField(max_length=100)
    purchaseDate = models.DateField()
    purchaseTime = models.TimeField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
            return f"{self.retailer} - {self.purchaseDate} - {self.purchaseTime} - {self.total}"

    def get_points(self):
        return 1

class Item(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    shortDescription = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.shortDescription} - {self.price} - {self.receipt.hexadecimal_id}"


