from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Waitlist
from .serializers import WaitlistSerializer

class WaitlistCreateView(generics.CreateAPIView):
    """
    View for creating a new waitlist entry
    Public access - anyone can join waitlist
    """
    queryset = Waitlist.objects.all()
    serializer_class = WaitlistSerializer
    permission_classes = [AllowAny]  # Explicitly allow anyone

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({
            'message': 'Successfully joined the waitlist!',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

class WaitlistDetailView(generics.RetrieveAPIView):
    """
    View for retrieving a specific waitlist entry by email
    Public access - anyone can check their status
    """
    queryset = Waitlist.objects.all()
    serializer_class = WaitlistSerializer
    permission_classes = [AllowAny] 
    lookup_field = 'email'
    lookup_url_kwarg = 'email'

    def get_object(self):
        email = self.kwargs.get('email')
        try:
            return Waitlist.objects.get(email=email)
        except Waitlist.DoesNotExist:
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
    Public access - anyone can view the list
    """
    queryset = Waitlist.objects.all()
    serializer_class = WaitlistSerializer
    permission_classes = [AllowAny]  # Allow anyone to view
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })

class CheckWaitlistStatusView(generics.GenericAPIView):
    """
    Simple view to check if an email is already registered
    """
    permission_classes = [AllowAny]

    def get(self, request, email):
        exists = Waitlist.objects.filter(email=email).exists()
        return Response({
            'email': email,
            'registered': exists,
            'message': 'This email is already on the waitlist.' if exists else 'This email is not registered yet.'
        })