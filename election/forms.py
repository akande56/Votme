from django import forms
from .models import Organization, Unit_department

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = '__all__'


class Unit_departmentForm(forms.ModelForm):
    """Unit_departmentForm definition."""
    class Meta:
        model = Unit_department
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        user_organizations = kwargs.pop('user_organizations', None)
        super(Unit_departmentForm, self).__init__(*args, **kwargs)
        if user_organizations:
            self.fields['organization'].queryset = user_organizations