from django import forms
from .models import Holding

class HoldingForm(forms.ModelForm):
    purchase_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M']
    )

    class Meta:
        model = Holding
        fields = ['cryptocurrency', 'quantity', 'purchase_price', 'purchase_date']