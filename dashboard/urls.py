from django.urls import path
from .views import DashboardView, AdminPanelView
 
urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("admin_panel/", AdminPanelView.as_view(), name="admin_panel"),
]