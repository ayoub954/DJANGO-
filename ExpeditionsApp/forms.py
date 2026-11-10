from django import forms

from .models import Expedition


class ExpeditionForm(forms.ModelForm):
    class Meta:
        model = Expedition
        fields = "__all__"
        exclude = ["reference", "created_at", "updated_at"]
        widgets = {
            "date_souhaitee": forms.DateInput(attrs={"type": "date"}),
        }