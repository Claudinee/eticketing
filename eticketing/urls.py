from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tickets import views  # Import your views module

# Create a router and register your viewsets
router = DefaultRouter()
router.register(r'organizers', views.OrganizerViewSet)
router.register(r'tickets', views.TicketViewSet)
router.register(r'transactions', views.TransactionViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),  # Frontend homepage
    path('api/', include(router.urls)),  # All API endpoints under /api/
    
    # Additional API endpoints if needed
    path('api/organizers/', views.OrganizerViewSet.as_view({'get': 'list'}), name='organizers-list'),
    path('api/tickets/', views.TicketViewSet.as_view({'get': 'list'}), name='tickets-list'),
    path('api/transactions/', views.TransactionViewSet.as_view({'post': 'create'}), name='transactions-create'),
]