from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.WaitlistCreateView.as_view(), name='waitlist-register'),
    path('check/<str:email>/', views.CheckWaitlistStatusView.as_view(), name='waitlist-check'),
    path('<str:email>/', views.WaitlistDetailView.as_view(), name='waitlist-detail'),
    path('all/', views.WaitlistListView.as_view(), name='waitlist-list'),
]