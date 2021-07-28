from django.urls import path
from . import views
from .views import (
    PVSystemCreateView, PVSystemDetailView, PVSystemListView, PVSystemUpdateView, PVSystemDeleteView,
)

urlpatterns = [
    #Landing Page
    path('', views.dashboard, name='dashboard'),

    #PVSystem Pages
    path('pvsystems/add/', PVSystemCreateView.as_view(), name='pvsystem_create'),
    path('pvsystems/<uuid:pk>/', PVSystemDetailView.as_view(), name='pvsystem_detail'),
    path('pvsystems/', PVSystemListView.as_view(), name='pvsystems_list'),
    path('pvsystems/<uuid:pk>/edit/', PVSystemUpdateView.as_view(), name='pvsystem_edit'),
    path('pvsystems/<uuid:pk>/delete/', PVSystemDeleteView.as_view(), name='pvsystem_delete'),

    
]