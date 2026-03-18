from django.urls import path
from . import views

urlpatterns = [
    path('api/waitlist/register/', views.WaitlistCreateView.as_view(), name='waitlist-register'),
    path('api/waitlist/check/<str:email>/', views.CheckWaitlistStatusView.as_view(), name='waitlist-check'),
    path('api/waitlist/<str:email>/', views.WaitlistDetailView.as_view(), name='waitlist-detail'),
    path('api/waitlist/all/', views.WaitlistListView.as_view(), name='waitlist-list'),
]