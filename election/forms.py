from django import forms
from django.contrib.auth import get_user_model
from .models import Organization, Unit_department,UserOrganization, Election


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = '__all__'


class Unit_departmentForm(forms.ModelForm):
    """Unit_departmentForm definition."""
    class Meta:
        model = Unit_department
        fields = '__all__'
    # def __init__(self, *args,**kwargs):
    #     # user_organizations = kwargs.pop('user_organizations', None)
    #     super(Unit_departmentForm, self).__init__(*args, **kwargs)
    #     user = get_user_model()
    #     if user:
    #         user_organizations = UserOrganization.objects.filter(member=user)
    #         organizations = [user_org.organization for user_org in user_organizations]
    #         if user_organizations:
    #             self.fields['organization'].queryset = organizations



class ElectionFormStage1(forms.ModelForm):
    class Meta:
        model= Election
        fields = '__all__'
