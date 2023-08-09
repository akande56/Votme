from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Organization,UserOrganization,Unit_department
from .forms import OrganizationForm,Unit_departmentForm

# Organization
@login_required  # Requires the user to be logged in to access this view
def organization_list(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('organization_list')  # Redirect to the list view after successful creation

    else:
        form = OrganizationForm()

    # Filter organizations based on the current logged-in user's membership
    user_organizations = UserOrganization.objects.filter(member=request.user)
    # Get the list of organizations from the filtered UserOrganization instances
    organizations = [user_org.organization for user_org in user_organizations]

    return render(request, 'election/organization_list.html', {'organizations': organizations, 'form': form})


@login_required  # Requires the user to be logged in to access this view
def create_organization(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save()
            # Get the current logged-in user
            current_user = request.user

            # Create a UserOrganization instance for the current user and the newly created organization
            user_organization = UserOrganization.objects.create(member=current_user, organization=organization)
            user_organization.save()
            return redirect('organization_list')  # Redirect to the list view after successful creation
    else:
        form = OrganizationForm()

    return render(request, 'election/organization_list.html', {'form': form})


@login_required  # Requires the user to be logged in to access this view
def update_organization(request, organization_id):
    organization = get_object_or_404(Organization, id=organization_id)
    if request.method == 'POST':
        form = OrganizationForm(request.POST, instance=organization)
        if form.is_valid():
            form.save()
            return redirect('organization_list')  # Redirect to the list view after successful update
    else:
        form = OrganizationForm(instance=organization)

    return render(request, 'election/organization_list.html', {'form': form})


@login_required  # Requires the user to be logged in to access this view
def delete_organization(request, organization_id):
    organization = get_object_or_404(Organization, id=organization_id)
    if request.method == 'POST':
        organization.delete()
        return redirect('organization_list')  # Redirect to the list view after successful deletion

    return render(request, 'election/organization_list.html', {'organization': organization})



#Unit/Department
# class UnitListAndCreateView(LoginRequiredMixin, View):
#     template_name = 'unit.html'

#     def get(self, request):
#         user_organizations = Organization.objects.filter(userorganization__member=self.request.user)
#         units = Unit_department.objects.filter(organization__in=user_organizations)
#         form = Unit_departmentForm()
#         print(form)
#         return render(request, self.template_name, {'units': units, 'form': form})

#     def post(self, request):
#         form = Unit_departmentForm(request.POST)
#         if form.is_valid():
#             unit = form.save()
#             organization_id = request.POST.get('organization')
#             try:
#                 organization = Organization.objects.get(id=organization_id)
#             except Organization.DoesNotExist:
#                 return redirect('unit')
#             if organization in Organization.objects.filter(userorganization__member=self.request.user):
#                 unit.organization = organization
#                 unit.save()
#         return redirect('unit'  )

@login_required  # Requires the user to be logged in to access this view
def unit_list(request):
    # if request.method == 'POST':
    #     form = Unit_departmentForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('unit')  # Redirect to the list view after successful creation

    # else:
    form = Unit_departmentForm(request.POST)

    user_organizations = Organization.objects.filter(userorganization__member=request.user)
    units = Unit_department.objects.filter(organization__in=user_organizations)
    print('ss')
    print(form)
    print(request)
    return render(request, 'election/unit.html', {'units': units, 'form': form})



@login_required  # Requires the user to be logged in to access this view
def create_unit(request):
    form = Unit_departmentForm(request.POST)
    if form.is_valid():
        unit = form.save()
        organization_id = request.POST.get('organization')
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
                return redirect('unit')
        if organization in Organization.objects.filter(userorganization__member=request.user):
            unit.organization = organization
            unit.save()
    else:
        form = Unit_departmentForm()

    return render(request, 'election/unit.html', {'form': form})



def update_unit(request, unit_id):
    unit = get_object_or_404(Unit_department, id=unit_id)
    if request.method == 'POST':
        form = Unit_departmentForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            return redirect('unit')  # Redirect to the list view after successful update
    else:
        form = Unit_departmentForm(instance=unit)

    return render(request, 'election/unit.html', {'form': form})


def delete_unit(request, unit_id):
    unit = get_object_or_404(Unit_department, id=unit_id)
    if request.method == 'POST':
        unit.delete()
        return redirect('unit')  # Redirect to the list view after successful deletion

    return render(request, 'election/unit.html', {'unit': unit})