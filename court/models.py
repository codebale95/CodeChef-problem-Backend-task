from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('defendant', 'Defendant'),
        ('plaintiff', 'Plaintiff'),
        ('juror', 'Juror'),
        ('judge', 'Judge'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='defendant')

class Case(models.Model):
    title = models.CharField(max_length=200)
    argument = models.TextField()
    evidence = models.TextField(blank=True)  # Plaintext
    evidence_file = models.FileField(upload_to='evidence/', blank=True, null=True)  # For document uploads
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_cases')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Vote(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='votes')
    juror = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    verdict = models.CharField(max_length=20, choices=[
        ('guilty', 'Guilty'),
        ('not_guilty', 'Not Guilty'),
    ])
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('case', 'juror')  # One vote per juror per case
