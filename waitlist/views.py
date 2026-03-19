# waitlist/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from .serializers import WaitlistSerializer
from .firebase_service import FirebaseWaitlistService

class WaitlistCreateView(generics.CreateAPIView):
    """
    View for creating a new waitlist entry
    """
    serializer_class = WaitlistSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        if not settings.FIREBASE_INITIALIZED:
            return Response({
                'error': 'Firebase is not initialized. Please check your configuration.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Check if email already exists
            service = FirebaseWaitlistService()
            if service.check_email_exists(serializer.validated_data['email']):
                return Response({
                    'error': 'This email is already registered on the waitlist.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            entry = serializer.save()
            return Response({
                'message': 'Successfully joined the waitlist!',
                'data': entry
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WaitlistDetailView(generics.RetrieveAPIView):
    """
    View for retrieving a specific waitlist entry by email
    """
    permission_classes = [AllowAny]
    serializer_class = WaitlistSerializer

    def get_object(self):
        email = self.kwargs.get('email')
        
        if not settings.FIREBASE_INITIALIZED:
            return None
        
        try:
            service = FirebaseWaitlistService()
            return service.get_entry_by_email(email)
        except Exception:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance is None:
            return Response({
                'error': 'No waitlist entry found with this email address.',
                'registered': False
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        return Response({
            'registered': True,
            'data': serializer.data
        })

class WaitlistListView(generics.ListAPIView):
    """
    View for listing all waitlist entries
    """
    permission_classes = [AllowAny]
    serializer_class = WaitlistSerializer

    def get_queryset(self):
        if not settings.FIREBASE_INITIALIZED:
            return []
        
        try:
            service = FirebaseWaitlistService()
            limit = int(self.request.query_params.get('limit', 100))
            return service.get_all_entries(limit=limit)
        except Exception as e:
            print(f"Error getting entries: {e}")
            return []

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        if not settings.FIREBASE_INITIALIZED:
            return Response({
                'error': 'Firebase is not initialized',
                'count': 0,
                'results': []
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': len(queryset),
            'results': serializer.data
        })

class CheckWaitlistStatusView(generics.GenericAPIView):
    """
    Simple view to check if an email is already registered
    """
    permission_classes = [AllowAny]

    def get(self, request, email):
        if not settings.FIREBASE_INITIALIZED:
            return Response({
                'error': 'Firebase is not initialized'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        try:
            service = FirebaseWaitlistService()
            exists = service.check_email_exists(email)
            entry = service.get_entry_by_email(email) if exists else None
            
            return Response({
                'email': email,
                'registered': exists,
                'data': entry if exists else None,
                'message': 'This email is already on the waitlist.' if exists else 'This email is not registered yet.'
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)