from django import forms
from django.forms import inlineformset_factory
from .models import Sale, SaleDetail

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer','staff','discount','sale_datetime','payment_method','receipt_no']

class SaleDetailForm(forms.ModelForm):
    class Meta:
        model = SaleDetail
        fields = ['product','quantity_sold','unit_price','discount_value','batch_number']

SaleDetailFormSet = inlineformset_factory(Sale, SaleDetail, form=SaleDetailForm, extra=1, can_delete=True)
