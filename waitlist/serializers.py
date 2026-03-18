from rest_framework import serializers
from .models import Waitlist

class WaitlistSerializer(serializers.ModelSerializer):
    business_type_label = serializers.CharField(source='get_business_type_display', read_only=True)
    
    class Meta:
        model = Waitlist
        fields = [
            'id',
            'email',
            'phone_number',
            'business_name',
            'business_type',
            'other_business_description',
            'business_type_label',  
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Custom validation for the entire data payload
        """
        business_type = data.get('business_type')
        other_description = data.get('other_business_description')
        
        # Check if email already exists (for POST requests)
        if self.context.get('request') and self.context['request'].method == 'POST':
            email = data.get('email')
            if email and Waitlist.objects.filter(email=email).exists():
                raise serializers.ValidationError({
                    'email': 'This email is already registered on the waitlist.'
                })
        
        # Validate that other_business_description is provided when business_type is 'OTHER'
        if business_type == Waitlist.BusinessType.OTHER and not other_description:
            raise serializers.ValidationError({
                'other_business_description': 'Please specify your business industry when selecting "Other"'
            })
        
        # Validate that other_business_description is not provided when business_type is not 'OTHER'
        if business_type != Waitlist.BusinessType.OTHER and other_description:
            raise serializers.ValidationError({
                'other_business_description': 'This field should only be filled when business type is "Other"'
            })
        
        return data

    def validate_phone_number(self, value):
        """Validate phone number format"""
        import re
        # Remove spaces and check format
        phone_clean = value.replace(' ', '')
        phone_pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
        
        if not phone_pattern.match(phone_clean):
            raise serializers.ValidationError(
                'Please enter a valid phone number with country code (e.g., +254...)'
            )
        return value