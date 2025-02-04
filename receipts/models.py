from django.db import models

class Receipt(models.Model):
    hexadecimal_id = models.CharField(max_length=36, unique=True) # example: "c288fc46-3b6-8b4c-830d-77c75e9644e6"

    def get_points(self):
        return 1
