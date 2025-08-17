from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tickets import views  # Import your views module

# Create a router and register your viewsets
router = DefaultRouter()
router.register(r'organizers', views.OrganizerViewSet, basename='organizer')
router.register(r'tickets', views.TicketViewSet, basename='ticket')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'dependents', views.DependentViewSet, basename='dependent')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),  # Frontend homepage
    path('api/', include(router.urls)),      # All API endpoints under /api/
]
