from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse, HttpResponseServerError
from django.db.models import Count
from django.db import IntegrityError
from django.template.loader import get_template
import json
from xhtml2pdf import pisa
# from weasyprint import HTML

from .models import (
    Organization,
    UserOrganization,
    Unit_department,
    Election,
    Position,
    Aspirant,
    Vote,
    Voter,
)
from .forms import (
    OrganizationForm,
    Unit_departmentForm,
    ElectionFormStage1,
    ElectionUpdateForm,
    PositionForm,
    VoterRegistrationForm
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

    # Get organizations where the user has a UserOrganization instance
    user_organizations = UserOrganization.objects.filter(member=request.user)
    organizations_with_membership = [user_org.organization for user_org in user_organizations]

    # Get organizations where the user does not have a UserOrganization instance
    all_organizations = Organization.objects.all()
    organizations_without_membership = [org for org in all_organizations if org not in organizations_with_membership]
        
    return render(request, 'election/organization_list.html', {'organizations_with_membership': organizations_with_membership, 'organizations_without_membership': organizations_without_membership, 'form': form})


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
            return redirect('create_election')  # Redirect to the list view after successful creation
    else:
        form = OrganizationForm()

    return render(request, 'election/organization_list.html', {'form': form})



@login_required
def join_organization(request, organization_id):
    user = request.user
    organization = get_object_or_404(Organization, id = organization_id)
    UserOrganization.objects.create(member=user, organization = organization)
    messages.success(request, f'You have successful join {organization.name}')
    
    return redirect('organization_list')



@login_required  # Requires the user to be logged in to access this view
def update_organization(request, organization_id):
    organization = get_object_or_404(Organization, id=organization_id)

    if organization.create_by != request.user:
        messages.error(request, f"You do not have permission to update this {organization.name}.")
        messages.error(request, 'Adminstrator Identification required')
        return redirect('organization_list')  # Redirect to home with an error message

    if request.method == 'POST':
        form = OrganizationForm(request.POST, instance=organization)
        if form.is_valid():
            form.save()
            messages.success(request, f'{organization.name} updated successfully!')
            return redirect('organization_list')  # Redirect to the list view after successful update
    else:
        form = OrganizationForm(instance=organization)

    return render(request, 'election/organization_list.html', {'form': form})


@login_required  # Requires the user to be logged in to access this view
def delete_organization(request, organization_id):
    organization = get_object_or_404(Organization, id=organization_id)

    if organization.create_by != request.user:
        messages.error(request, f"You do not have permission to delete {organization.name}")
        messages.error(request, 'Administrator Identification required..')
        return redirect('organization_list')  # Redirect to home with an error message

    if request.method == 'POST':
        messages.success(request, f'{organization.name} Deleted, all related date deleted as well')
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

    # user_organizations = Organization.objects.filter(userorganization__member=request.user)
    # changed to if user create organization instead
    user_organizations = Organization.objects.filter(create_by=request.user)
    units = Unit_department.objects.filter(organization__in=user_organizations)

    return render(request, 'election/unit.html', {'units': units, 'form': form, 'user_organizations': user_organizations})


@login_required  # Requires the user to be logged in to access this view
def create_unit(request):
    form = Unit_departmentForm(request.POST)
    if form.is_valid():
        organization_id = request.POST.get('organization')
        organization = get_object_or_404(Organization, id=organization_id)
        if organization.create_by != request.user:
            messages.error(request, "You do not have permission to update this organization.")
            return redirect('unit')

        else:
            try:
                organization = Organization.objects.get(id=organization_id)
            except Organization.DoesNotExist:
                return redirect('unit')
            if organization in Organization.objects.filter(userorganization__member=request.user):
                unit = form.save()
                unit.organization = organization
                unit.save()
                messages.success(request, f"New unit/department added for {organization.name} successfully....")

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
        messages.info(request, 'Administrator Identification required')
        return redirect('unit')

    if request.method == 'POST':
        form = Unit_departmentForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request, f"{unit.title} updated successfully")
            return redirect('unit')  # Redirect to the list view after successful update
    else:
        form = Unit_departmentForm(instance=unit)

    return render(request, 'election/unit.html', {'form': form})


def delete_unit(request, unit_id):
    unit = get_object_or_404(Unit_department, id=unit_id)
    if request.method == 'POST':
        organization = unit.organization
        if organization.create_by != request.user:
            messages.error(request, "You do not have permission to delete this unit.")
            return redirect('unit')
        messages.success(request, f"{unit.title} Deleted successfully")
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
                messages.error(request, f"You do not have permission to create an election for {organization.name}")
                messages.info(request, "Administrator Identification required")
                return redirect('create_election')
            messages.success(request, f'success!, new Election added for {organization.name}')
            messages.info(request, 'if you did not include in the election to allow voters/aspirants to signup; you can do so by updating the election')
            messages.info(request, 'Voters/Asprant need to signup and join your organization to be able to participate in the election process')
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
        messages.info(request, 'Administrative Identification required')
        return redirect('elections')
    election.delete()
    messages.success(request, f"{election.title} Deleted successfully")
    messages.success(request, 'Election deleted successfully.')
    return redirect('elections')


@login_required
def update_election(request, election_id):
    election = get_object_or_404(Election, id=election_id)

    organization = election.organization
    if organization.create_by != request.user:
        messages.error(request, "You do not have permission to update.")
        messages.info(request, 'Administrative Identification required')
        return redirect('elections')

    if request.method == 'POST':
        form = ElectionUpdateForm(request.POST, instance=election)
        if form.is_valid():
            vote_s = form.cleaned_data['voting_start']
            vote_e  = form.cleaned_data['voting_end']
            appr_cont = form.cleaned_data['approved_all_contestant']
            if (appr_cont==False) & (vote_s==True):
                messages.error(request, "You cannot set voting_start without setting approval of all contestant/voters")
                return redirect('elections')
            if (vote_s==False) & (vote_e==True):
                messages.error(request, "You cannot set voting_end without setting vote_start")
                return redirect('elections')
            form.save()
            messages.success(request, f'{election.title} updated successfully')
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
            messages.success(request, f'Success. New position added to {Organization.name}')
            url = reverse('position', kwargs={'election_id': election_id})
            return redirect(url)
        else:
            print(form.errors)

    return render(request, 'position.html', context)


# Aspirant
def aspirant_signup(request, election_id):
    try:
        election = Election.objects.get(id=election_id)
        positions = Position.objects.filter(election=election)
        aspirants = Aspirant.objects.filter(position__in=positions)
        sorted_aspirants = sorted(aspirants, key=lambda aspirant: aspirant.position.title)

    except Election.DoesNotExist:
        return JsonResponse({"error": "Election not found"}, status=400)

    if election.aspirant_start:
        if request.method == "POST":
            try:
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
                    name=aspirant_name,
                    manifesto=manifesto
                )

                # Handle aspirant picture upload
                picture = request.FILES.get("aspirant_picture")
                if picture:
                    aspirant.picture = picture
                    aspirant.save()
                else:
                    aspirant.save()
                messages.success(request, "New aspirant registered successfully..")
            except IntegrityError:
                    # Handle the constraint violation by displaying an error message
                    messages.error(request, "Constraint violation: You are already registered Aspirant for this Election.")
    else:
        messages.error(request, 'Sorry, Aspirant/Contestant Registration has yet to begin for this election. Contact organization administrator to update Election')
        return redirect('elections')
    context = {
        "election": election,
        "positions": positions,
        "aspirants": sorted_aspirants,
    }
    return render(request, "aspirant_signup.html", context)


def get_aspirant_details(request):
    aspirant_id = request.GET.get('aspirant_id')  # Assuming the aspirant ID is passed as a query parameter

    try:
        aspirant = Aspirant.objects.get(id=aspirant_id)

        # Create a dictionary with aspirant details, including the photo URL
        aspirant_details = {
            'id': aspirant.id,
            'name': aspirant.name,
            'position': aspirant.position.title,  # Assuming 'position' has a 'title' field
            'manifesto': aspirant.manifesto,
            'photo_url': aspirant.picture.url if aspirant.picture else '',  # Assuming 'picture' is the ImageField
        }
        

        return JsonResponse(aspirant_details)
    except Aspirant.DoesNotExist:
        return JsonResponse({'error': 'Aspirant not found'}, status=404)



def admin_aspirant(request, election_id):
    try:
        election = Election.objects.get(id=election_id)
        positions = Position.objects.filter(election=election)
        aspirants = Aspirant.objects.filter(position__in=positions)
        sorted_aspirants = sorted(aspirants, key=lambda aspirant: aspirant.position.title)

    except Election.DoesNotExist:
        return JsonResponse({"error": "Election not found"}, status=400)
    
    context = {
        "election": election,
        "aspirants": sorted_aspirants,  
    }
    return render(request, "admin_aspirant.html", context)


def approve_aspirants(request, election_id):
    if request.method == 'POST':
        election = get_object_or_404(Election, id=election_id)
        organization = election.organization
        print('shllll')
        print(organization)
        aspirant_ids = request.POST.getlist('aspirants_to_approve')

        # Check if the request is coming from an authenticated admin user
        if organization.create_by == request.user:
            # Update the approval status for selected aspirants
            Aspirant.objects.filter(id__in=aspirant_ids).update(approved=True)

            # messages.success(request, f"{len(aspirant_ids)} aspirants have been approved.")
            messages.success(request, "All selected aspirants have been approved.")
        else:
            messages.error(request, "You do not have permission to approve aspirants for this election.")
    else:
        messages.error(request, "Invalid request method.")

    return redirect('admin_aspirant', election_id)  # Replace 'aspirants_list' with your aspirant list view URL name

## voter
def voter_signup(request, election_id):
    election = get_object_or_404(Election, id=election_id)

    if election.aspirant_start:
        if request.method == 'POST':
            form = VoterRegistrationForm(request.POST)
            if form.is_valid():
                try:
                    voter = form.save(commit=False)
                    voter.election = election
                    voter.user = request.user
                    voter.save()
                    messages.success(request, "Congrats, you have successfully signed up as a voter for this Election")
                    return redirect('elections')
                except IntegrityError:
                    # Handle the constraint violation by displaying an error message
                    messages.error(request, "Constraint violation: You are already registered as Voter for this Election.")
        else:
            form = VoterRegistrationForm()
    else:
        messages.error(request, 'Sorry, Voter Registration has yet to begin for this election. Contact organization administrator to update Election')
        return redirect('elections')

    return render(request, 'voter_signup.html', {'form': form, 'election': election})


def admin_voter(request, election_id):
    try:
        voters = Voter.objects.filter(election_id=election_id)
        election = get_object_or_404(Election, id=election_id)

    except Voter.DoesNotExist:
        messages.warning(request, 'There are no existing voters for this Election at the moment')
        return redirect('admin_voter', election_id)
    
    context = {
        "election": election,
        "voters": voters,  
    }
    return render(request, "admin_voter.html", context)


def approve_voters(request, election_id):
    if request.method == 'POST':
        election = get_object_or_404(Election, id=election_id)
        organization = election.organization
        
        voter_ids = request.POST.getlist('voters_to_approve')

        # Check if the request is coming from an authenticated admin user
        if organization.create_by == request.user:
            # Update the approval status for selected aspirants
            Voter.objects.filter(id__in=voter_ids).update(approved=True)

            # messages.success(request, f"{len(aspirant_ids)} aspirants have been approved.")
            messages.success(request, "All selected voters have been approved.")
        else:
            messages.error(request, "You do not have permission to approve voters for this election.")
    else:
        messages.error(request, "Invalid request method.")

    return redirect('admin_voter', election_id)  
## voting
@login_required
def vote_view(request, election_id):
    try:
        election = Election.objects.get(id=election_id)
    except Election.DoesNotExist:
        return redirect('elections')  # Redirect to a suitable page if the election does not exist

    if request.method == 'POST':
        if (election.voting_start==True) & (election.voting_end==False):
            
            # Handle the POST request for voting
            user = request.user
            position_id = request.POST.get('position_id')
            aspirant_id = request.POST.get('aspirant_id')
            # check if user is registered as a voter 
            try:
                voter = Voter.objects.get(election = election, user = user)
            except Voter.DoesNotExist:
                messages.error(request, "You are currently not registerd as a voter for this election, please do so.")
            else:
                # check if user has voted before
                try:
                    Vote.objects.get(voter=voter, election=election, position_id=position_id)
                except Vote.DoesNotExist:
                        if voter.approved:
                            vote = Vote(voter = voter, election=election, position_id=position_id, aspirant_id=aspirant_id)
                            vote.save()
                            messages.success(request, 'Vote recorded successfully.')
                        else:
                            messages.error(request, "Sorry, you are yet to be approved as a voter for this election, contact election administrator")
                else:
                    messages.error(request, "You have already casted vote for this 'position' in this election")
                    
        if election.voting_start & election.voting_end:
            messages.error(request, 'Election has already concluded.')
            # return JsonResponse({'message': 'Election has already concluded.'}, status=400)
        
    # Handle the GET request to display the aspirants for the election
    aspirants = Aspirant.objects.filter(election=election, approved=True)
    sorted_aspirants = sorted(aspirants, key=lambda aspirant: aspirant.position.title)

    return render(request, 'vote_view.html', {'election': election, 'aspirants': sorted_aspirants})


def election_results(request, election_id):
    # Get the election object
    election = get_object_or_404(Election, id=election_id)

    # Get positions for the specific election
    positions = Position.objects.filter(election=election)

    # Now, you can fetch results for each position and each aspirant
    results = []
    for position in positions:
        # Fetch all aspirants for this position in the specific election
        aspirants = Aspirant.objects.filter(position=position, election=election)

        aspirant_votes = []
        for aspirant in aspirants:
        # Calculate the number of votes for each aspirant in this position
            vote_count = Vote.objects.filter(position=position, aspirant=aspirant).count()
            aspirant_votes.append({
                'aspirant': aspirant,
                'vote_count': vote_count,
            })

        results.append({
            'position': position,
            'aspirant_votes': aspirant_votes,
        })
        
    return render(request, 'election/election_results.html', {'election': election, 'results': results})

def generate_pdf(request, election_id):
    try:
        # Get the election object
        election = get_object_or_404(Election, id=election_id)

        # Get positions for the specific election
        positions = Position.objects.filter(election=election)

        # Now, you can fetch results for each position and each aspirant
        results = []
        for position in positions:
            # Fetch all aspirants for this position in the specific election
            aspirants = Aspirant.objects.filter(position=position, election=election)

            # Calculate the number of votes for each aspirant in this position
            aspirant_votes = []
            for aspirant in aspirants:
                vote_count = Vote.objects.filter(position=position, aspirant=aspirant).count()
                aspirant_votes.append({
                    'aspirant': aspirant,
                    'vote_count': vote_count,
                })

            results.append({
                'position': position,
                'aspirant_votes': aspirant_votes,
            })

        # Render the result data in your template
        template = get_template('election/election_results_pdf.html')
        context = {'results': results, 'ok': True}
        html_content = template.render(context)

        # Create a PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="election_results.pdf"'

        # Generate the PDF using pisa
        pisa_status = pisa.CreatePDF(
            html_content,  # HTML content
            dest=response,  # File-like object to receive PDF data
        )

        if not pisa_status.err:
            return response
        else:
            # Handle the PDF generation error
            return HttpResponse("Error generating PDF", status=500)

    except Exception as e:
        # Log the exception or handle it gracefully
        print(f"Error generating PDF: {str(e)}")
        return HttpResponseServerError("Error generating PDF")