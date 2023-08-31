from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
import json
from .models import (
    Organization,
    UserOrganization,
    Unit_department,
    Election,
    Position,
    Aspirant,
)
from .forms import (
    OrganizationForm,
    Unit_departmentForm,
    ElectionFormStage1,
    ElectionUpdateForm,
    PositionForm,
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
            # Get the current logged-in user
            current_user = request.user
            organization = form.save(commit=False)
            organization.create_by = current_user
            organization.save()

            # Create a UserOrganization instance for the current user and the newly created organization
            UserOrganization.objects.create(member=current_user, organization=organization)
            # create default unit
            Unit_department.objects.create(title='all', organization=organization)
            messages.success(request, 'Organization created successfully!')
            return redirect('unit')  # Redirect to the list view after successful creation
    else:
        form = OrganizationForm()

    return render(request, 'election/organization_list.html', {'form': form})


@login_required  # Requires the user to be logged in to access this view
def update_organization(request, organization_id):
    organization = get_object_or_404(Organization, id=organization_id)

    if organization.create_by != request.user:
        messages.error(request, "You do not have permission to update this organization.")
        messages.error(request, 'You neet to be the one who added the organization..')
        return redirect('home')  # Redirect to home with an error message

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

    if organization.create_by != request.user:
        messages.error(request, "You do not have permission to update this organization.")
        messages.error(request, 'You neet to be the one who added the organization..')
        return redirect('home')  # Redirect to home with an error message

    if request.method == 'POST':
        organization.delete()
        return redirect('organization_list')  # Redirect to the list view after successful deletion

    return render(request, 'election/organization_list.html', {'organization': organization})


# Unit/Department
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

    return render(request, 'election/unit.html', {'units': units, 'form': form, 'user_organizations': user_organizations})


@login_required  # Requires the user to be logged in to access this view
def create_unit(request):
    form = Unit_departmentForm(request.POST)
    if form.is_valid():
        unit = form.save()
        organization_id = request.POST.get('organization')
        organization = get_object_or_404(Organization, id=organization_id)
        if organization.create_by != request.user:
            messages.error(request, "You do not have permission to update this organization.")
            return redirect('home')

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
    return render(request, 'election/unit.html', {'form': form, 'units': units})


# def get_user_organizations(request):

#     user = request.user
#     organizations = Organization.objects.filter(userorganization__member=request.user)


#     return JsonResponse({'organizations': organizations})


def update_unit(request, unit_id):
    unit = get_object_or_404(Unit_department, id=unit_id)
    organization = unit.organization

    if organization.create_by != request.user:
        messages.error(request, "You do not have permission to delete this unit.")
        return redirect('home')

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
    print(unit)
    print(unit.organization)
    print(unit.organization.create_by)
    if request.method == 'POST':
        organization = unit.organization
        if organization.create_by != request.user:
            messages.error(request, "You do not have permission to delete this unit.")
            return redirect('home')
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
            organization = form.cleaned_data['organization']  # Get selected organization
            if organization.create_by != request.user:
                messages.error(request, "You do not have permission to create an election for this organization.")
                return redirect('create_election')
            messages.success(request,'success; election created successfully')
            form.save()
            return redirect('elections')
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
    return render(request, 'election_list.html', {'elections': election, 'form': form})


@login_required
def delete_election(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    organization = election.organization
    if organization.create_by != request.user:
        messages.error(request, "You do not have permission to delete.")
        return redirect('elections')
    election.delete()
    messages.success(request, 'Election deleted successfully.')
    return redirect('elections')


@login_required
def update_election(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    
    organization = election.organization
    if organization.create_by != request.user:
        messages.error(request, "You do not have permission to update.")
        return redirect('elections')

    if request.method == 'POST':
        form = ElectionUpdateForm(request.POST, instance=election)
        if form.is_valid():
            form.save()
            messages.success(request, 'Election updated successfully')
            return redirect('elections')
        else:
            print("Form is invalid:", form.errors)
    else:

        form = ElectionUpdateForm(instance=election)

    return render(request, 'election_list.html', {'form': form})


# Postion

def position_list(request, election_id):
    positions = Position.objects.filter(election_id=election_id)
    form = PositionForm(request.POST)

    election = Election.objects.get(id=election_id)
    Organization = election.organization
    # get department list for form
    department = Unit_department.objects.filter(organization=Organization)
    department_json = json.dumps(list(department.values('id', 'title')))
    context = {
        'positions': positions,
        'form': form,
        'department': department_json,
        'election_id': election_id,
    }

    if request.method == 'POST':

        if form.is_valid():
            
            if Organization.create_by != request.user:
                messages.error(request, "You do not have permission to add positions to election.")
                return redirect('elections')
            position = form.save(commit=False)
            position.election = election
            position.save()
            messages.success(request, 'Success. New position added to election')
            url = reverse('position', kwargs={'election_id': election_id})
            return redirect(url)
        else:
            print(form.errors)

    return render(request, 'position.html', context)


#Aspirant
def aspirant_signup(request, election_id):
    try:
        election = Election.objects.get(id=election_id)
        positions = Position.objects.filter(election=election)
        aspirants = Aspirant.objects.filter(position__in=positions)
        sorted_aspirants = sorted(aspirants, key=lambda aspirant: aspirant.position.title)

    except Election.DoesNotExist:
        return JsonResponse({"error": "Election not found"}, status=400)

    if request.method == "POST":
        # Handle individual aspirant signup for the selected position
        position_id = request.POST.get("position")
        position = Position.objects.get(id=position_id)
        aspirant_name = request.POST.get("aspirant_name")
        manifesto = request.POST.get("manifesto")

        # Save aspirant with associated user and election
        aspirant = Aspirant.objects.create(
            user=request.user,
            election=election,
            position=position,
            name = aspirant_name,
            manifesto=manifesto
        )

        # Handle aspirant picture upload
        picture = request.FILES.get("aspirant_picture")
        if picture:
            aspirant.picture = picture
            aspirant.save()

        return JsonResponse({"message": "Signup successful"})

    context = {
        "election": election,
        "positions": positions,
        "aspirants": sorted_aspirants,
    }
    return render(request, "aspirant_signup.html", context)