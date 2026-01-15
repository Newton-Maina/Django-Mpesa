from django.db import models

# Create your models here.
class Transaction(models.Model):
    checkout_request_id = models.CharField(max_length=100, unique=True)
    merchant_request_id = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    mpesa_receipt_number = models.CharField(max_length=20, blank=True, null=True)
    result_code = models.IntegerField(blank=True, null=True)
    result_desc = models.TextField(blank=True, null=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return f"{self.phone_number} - {self.amount} - {self.status}"
