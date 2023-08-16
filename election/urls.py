from django.urls import include, path
from . import views

urlpatterns = [
    # path('get_user_organizations/', views.load_organizations, name='load_organizations'),
    path('load_units/', views.load_units, name='load_units'),
    path('organization/', views.organization_list, name='organization_list'),
    path('organization/create/', views.create_organization, name='create_organization'),
    path('organization/update/<int:organization_id>', views.update_organization, name='update_organization'),
    path('organization/delete/<int:organization_id>', views.delete_organization, name='delete_organization'),
    path('unit/list/', views.unit_list, name='unit'),
    path('unit/list/create', views.create_unit, name='create_unit'),
    path('unit/list-and-create/update/<int:unit_id>/', views.update_unit, name='update_unit'),
    path('unit/list-and-create/delete/<int:unit_id>/', views.delete_unit, name='delete_unit'),
    path('create_election/', views.create_election, name='create_election'),
    path('elections/', views.election_list, name='elections'),
    path('elections/update/<int:election_id>/', views.update_election, name='update_election'),
    path('elections/delete/<int:election_id>/', views.delete_election, name='delete_election'),
]

    # path('detail/<int:organization_id>/', views.organization_detail, name='organization_detail'),
