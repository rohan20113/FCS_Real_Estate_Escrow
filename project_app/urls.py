from django.urls import path
from . import views

# ip/''
urlpatterns = [
    path("", views.login_user, name = "login_page"),
    path("signup/", views.register_user, name = "signup_page"),
    # path("logout_user", views.logout_user, name="logout_user")
    path("dashboard/", views.dashboard_user, name="dashboard_page"),
    path("admin_dashboard/", views.dashboard_admin, name="admin_dashboard_page"),
    path("users_list/", views.dashboard_user_list, name="user_list_page"),
    path("property_home/", views.add_property, name="property_home_page"),
    path("add_property/", views.add_property, name="add_property_page"),
    path("my_properties/", views.my_properties, name="my_properties_page"),
    path("search_properties/", views.search_properties, name="search_properties_page"),
]
