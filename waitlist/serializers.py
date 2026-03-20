from rest_framework import serializers
import re
from .firebase_service import FirebaseWaitlistService
from .firebase_service import FirebaseWaitlistService

class WaitlistSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20)
    business_name = serializers.CharField(max_length=200)
    business_type = serializers.ChoiceField(choices=[
        ('ISP', 'ISP'),
        ('GYM', 'Gym'),
        ('SACCO', 'Sacco'),
        ('CHAMA', 'Chama'),
        ('OTHER', 'Other')
    ])
    other_business_description = serializers.CharField(
        max_length=200, 
        required=False, 
        allow_blank=True, 
        allow_null=True
    )
    business_type_label = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def get_business_type_label(self, obj):
        """Return human-readable business type"""
        choices = {
            'ISP': 'ISP',
            'GYM': 'Gym',
            'SACCO': 'Sacco',
            'CHAMA': 'Chama',
            'OTHER': 'Other'
        }
        return choices.get(obj.get('business_type'), obj.get('business_type'))

    def validate_phone_number(self, value):
        """Validate phone number format"""
        phone_clean = value.replace(' ', '')
        phone_pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
        
        if not phone_pattern.match(phone_clean):
            raise serializers.ValidationError(
                'Please enter a valid phone number with country code (e.g., +254...)'
            )
        return value

    def validate(self, data):
        """Custom validation"""
        business_type = data.get('business_type')
        other_description = data.get('other_business_description')
        
        # Validate that other_business_description is provided when business_type is 'OTHER'
        if business_type == 'OTHER' and not other_description:
            raise serializers.ValidationError({
                'other_business_description': 'Please specify your business industry when selecting "Other"'
            })
        
        # Validate that other_business_description is not provided when business_type is not 'OTHER'
        if business_type != 'OTHER' and other_description:
            raise serializers.ValidationError({
                'other_business_description': 'This field should only be filled when business type is "Other"'
            })
        
        return data

    def create(self, validated_data):
        """Create a new entry in Firebase"""
        
        service = FirebaseWaitlistService()
        return service.create_entry(validated_data)

    def update(self, instance, validated_data):
        """Update an existing entry"""        
        service = FirebaseWaitlistService()
        return service.update_entry(instance['id'], validated_data)