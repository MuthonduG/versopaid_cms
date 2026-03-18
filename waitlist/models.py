from django.db import models
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
import re

class Waitlist(models.Model):
    class BusinessType(models.TextChoices):
        ISP = 'ISP', 'ISP'
        GYM = 'GYM', 'Gym'
        SACCO = 'SACCO', 'Sacco'
        CHAMA = 'CHAMA', 'Chama'
        OTHER = 'OTHER', 'Other'

    email = models.EmailField( unique=True, validators=[EmailValidator()], help_text="Enter a valid email address" )
    phone_number = models.CharField( max_length=20, help_text="Enter your phone number with country code (e.g., +254...)" )
    business_name = models.CharField( max_length=200, help_text="Enter your business name" )
    business_type = models.CharField(
        max_length=20,
        choices=BusinessType.choices,
        default=BusinessType.OTHER,
        help_text="Select your business type"
    )
    other_business_description = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="If you selected 'Other', please specify your business industry"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Waitlist Entry'
        verbose_name_plural = 'Waitlist Entries'

    def __str__(self):
        return f"{self.business_name} - {self.email}"

    def clean(self):
        """Validate that other_business_description is provided when business_type is 'OTHER'"""
        if self.business_type == self.BusinessType.OTHER and not self.other_business_description:
            raise ValidationError({
                'other_business_description': 'Please specify your business industry when selecting "Other"'
            })
        
        if self.phone_number:
            phone_pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
            if not phone_pattern.match(self.phone_number.replace(' ', '')):
                raise ValidationError({
                    'phone_number': 'Please enter a valid phone number with country code (e.g., +254...)'
                })

    def save(self, *args, **kwargs):
        """Run full validation before saving"""
        self.full_clean()
        super().save(*args, **kwargs)