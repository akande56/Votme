from django.urls import include, path
from . import views

urlpatterns = [
    # path('get_user_organizations/', views.load_organizations, name='load_organizations'),
    path('load_units/', views.load_units, name='load_units'),
    path('organization/', views.organization_list, name='organization_list'),
    path('organization/create/', views.create_organization, name='create_organization'),
    path('organization/join/<int:organization_id>', views.join_organization, name='join_organization'),
    path('organization/update/<int:organization_id>', views.update_organization, name='update_organization'),
    path('organization/delete/<int:organization_id>', views.delete_organization, name='delete_organization'),
    path('unit/list/', views.unit_list, name='unit'),
    path('unit/list/create', views.create_unit, name='create_unit'),
    path('unit/list-and-create/update/<int:unit_id>/', views.update_unit, name='update_unit'),
    path('unit/list-and-create/delete/<int:unit_id>/', views.delete_unit, name='delete_unit'),
    path('create_election/', views.create_election, name='create_election'),
    path('elections/', views.election_list, name='elections'),
    path('elections/aspirant_signup/<int:election_id>/', views.aspirant_signup, name='aspirant_signup'),
    path('elections/voter_signup/<int:election_id>/', views.voter_signup, name='voter_signup'),
    path('elections/update/<int:election_id>/', views.update_election, name='update_election'),
    path('elections/delete/<int:election_id>/', views.delete_election, name='delete_election'),
    path('elections/position/<int:election_id>/', views.position_list, name='position'),
    path('elections/election/<int:election_id>/vote/', views.vote_view, name='vote_view'),
    path('elections/election/accreditions/aspirant/<int:election_id>', views.admin_aspirant, name='admin_aspirant'),
    path('elections/election/accreditions/voters/<int:election_id>', views.admin_voter, name='admin_voter'),
    path('approve_aspirants/<int:election_id>', views.approve_aspirants, name='approve_aspirants'),
    path('approve_voters/<int:election_id>', views.approve_voters, name='approve_voters'),
    path('get_aspirant_details/', views.get_aspirant_details, name='get_aspirant_details'),
    path('elections/election/vote/<int:election_id>/results/', views.election_results, name='election_results'),
]

    # path('detail/<int:organization_id>/', views.organization_detail, name='organization_detail'),
