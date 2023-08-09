from django.urls import include, path
from . import views

urlpatterns = [
    path('organization/', views.organization_list, name='organization_list'),
    path('organization/create/', views.create_organization, name='create_organization'),
    path('organization/update/<int:organization_id>/', views.update_organization, name='update_organization'),
    path('organization/delete/<int:organization_id>/', views.delete_organization, name='delete_organization'),
    path('unit/list/', views.unit_list, name='unit'),
    path('unit/list/create', views.create_unit, name='create_unit'),
    path('unit/list-and-create/update/<int:unit_id>/', views.update_unit, name='update_unit'),
    path('unit/list-and-create/delete/<int:unit_id>/', views.delete_unit, name='delete_unit'),
    # path('detail/<int:organization_id>/', views.organization_detail, name='organization_detail'),
]