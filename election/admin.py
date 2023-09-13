from django.contrib import admin
from .models import Organization, Unit_department,UserOrganization, Position, Voter, Vote, Aspirant
# Register your models here.
admin.site.register(Organization)
admin.site.register(Unit_department)
admin.site.register(UserOrganization)
admin.site.register(Position)
admin.site.register(Voter)
admin.site.register(Vote)
admin.site.register(Aspirant)
