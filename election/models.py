from django.db import models
from django.utils import timezone
from voteme.users.models import User

class Organization(models.Model):
    """Model definition for Organization."""
    """will riqure another model for obtaining users that can see an initiated election"""
    """user that create an organization will be default be part of it"""
    name = models.CharField( max_length=50)
    industry = models.CharField(max_length=50, help_text='software, union, government,construction...')
    description = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    contact = models.CharField(max_length=50)
    membership_size = models.IntegerField(help_text='help for counter overvotting, can be updated if neccessary')
    create_by =  models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        """Meta definition for Organization."""

        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'

    def __str__(self):
        """Unicode representation of Organization."""
        return str(self.name)


class Unit_department(models.Model):
    """Model definition for Unit_department."""
    """for identifying range of voters in an organization"""
    title = models.CharField(max_length=50)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,null=True,default=None ,related_name='organization_units')

    class Meta:
        """Meta definition for Unit_department."""
        verbose_name = 'Unit_department'
        verbose_name_plural = 'Unit_departments'

    def __str__(self):
        """Unicode representation of Unit_department."""
        return str(self.title)
    # def save(self, *args, **kwargs):
    #     if not self.id:
    #         # If the instance is being created (not yet saved to the database)
    #         # Set the default title as "all"
    #         self.title = "all"
    #     super(Unit_department, self).save(*args, **kwargs)


class UserOrganization(models.Model):
    """Model definition for UserOrganization."""
    member = models.ForeignKey(to=User, on_delete=models.CASCADE)
    organization  = models.ForeignKey(to=Organization,null=True ,on_delete=models.CASCADE)
    class Meta:
        """Meta definition for UserOrganization."""

        verbose_name = 'UserOrganization'
        verbose_name_plural = 'UserOrganizations'

    def __str__(self):
        """Unicode representation of UserOrganization."""
        return str(self.member.email)


class Election(models.Model):
    """Model definition for Election."""
    title = models.CharField(max_length=50, blank=True)
    organization = models.ForeignKey(to=Organization, null=True ,on_delete=models.CASCADE, related_name='ElectionOrganization')
    department = models.ForeignKey(to=Unit_department, null=True ,on_delete=models.CASCADE, related_name='ElectionDepartment')
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)
    aspirant_start = models.BooleanField(default=False)
    approved_all_contestant = models.BooleanField(default=False)
    voting_start = models.BooleanField(default=False)
    voting_end = models.BooleanField(default=False)

    class Meta:
        """Meta definition for Election."""

        verbose_name = 'Election'
        verbose_name_plural = 'Elections'

    def __str__(self):
        """Unicode representation of Election."""
        return str('{}{}'.format(self.organization, self.title))

    

class Position(models.Model):
    title = models.CharField(max_length=50)
    department = models.ForeignKey(Unit_department, on_delete=models.CASCADE, related_name='positions')
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='positions', null=True, blank=True)
    num_of_contestant = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return self.title


class Aspirant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=True, default="default name")
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='aspirants')
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='aspirants')
    withdrawn = models.BooleanField(default=False)
    picture = models.ImageField(upload_to='aspirant_pictures/', null=True, blank=True)
    manifesto = models.TextField()
    registered_at = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.position} ({self.election})"
    
    class Meta:
        unique_together = ('user', 'election')
        


class Voter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    election = models.ForeignKey('Election', on_delete=models.CASCADE)
    organization_id = models.CharField( max_length=15)
    registered_at = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email
    class Meta:
        unique_together = ('user', 'election', 'organization_id')


class Vote(models.Model):
    voter = models.ForeignKey (Voter, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    aspirant = models.ForeignKey(Aspirant, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('voter', 'position', 'election')  # To ensure a user can only vote once per position in an election

    def __str__(self):
        return f"Vote by {self.voter.user} for {self.position} in {self.election}"

