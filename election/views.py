from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
import json
from .models import (
    Organization,
    UserOrganization,
    Unit_department,
    Election,
)
from .forms import (
    OrganizationForm,
    Unit_departmentForm, 
    ElectionFormStage1,
    ElectionUpdateForm,
    
)

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
            # create default unit
            Unit_department.objects.create(title='all',organization=organization)
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
   
    form = Unit_departmentForm(request.POST)

    user_organizations = Organization.objects.filter(userorganization__member=request.user)
    units = Unit_department.objects.filter(organization__in=user_organizations)
    
    return render(request, 'election/unit.html', {'units': units, 'form': form,'user_organizations': user_organizations })



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
    user_organizations = Organization.objects.filter(userorganization__member=request.user)
    units = Unit_department.objects.filter(organization__in=user_organizations)
    return render(request, 'election/unit.html', {'form': form, 'units':units})



# def get_user_organizations(request):
    
#     user = request.user
#     organizations = Organization.objects.filter(userorganization__member=request.user)

 
#     return JsonResponse({'organizations': organizations})



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



# Election
def create_election(request):
    # user = request.user
    organizations = Organization.objects.filter(userorganization__member=request.user)
    organizations_json = json.dumps(list(organizations.values("id", "name")))
    
    if request.method == 'POST':
        form = ElectionFormStage1(request.POST)
        if form.is_valid():
            form.save()
            redirect('elections')
    else:
        # initial_data = {'organization': organizations}
        form = ElectionFormStage1()  # Initial form for stage 1
    form = ElectionFormStage1()
    return render(request, 'create_election.html', {'form': form,
            'organizations_json': organizations_json,
            }
    )


def load_units(request):
    organization_id = request.GET.get('organization_id')
    units = Unit_department.objects.filter(organization_id=organization_id)
    data = {
        "units": list(units.values("id", "title"))
    }
    return JsonResponse(data)


@login_required  
def election_list(request):
    organizations = Organization.objects.filter(userorganization__member=request.user)
    election = Election.objects.filter(organization__in=organizations) 
    form = ElectionFormStage1(request.POST)
    return render(request, 'election_list.html', {'elections': election, 'form':form})


@login_required
def delete_election(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    election.delete()
    messages.success(request, 'Election deleted successfully.')
    return redirect('elections')

    
@login_required
def update_election(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    
    if request.method == 'POST':
        form = ElectionUpdateForm(request.POST, instance=election)
        if form.is_valid():
            form.save()
            return redirect('elections')
        else:
            print("Form is invalid:", form.errors)
    else:
        
        form = ElectionUpdateForm(instance=election)

    return render(request, 'election_list.html', {'form': form})