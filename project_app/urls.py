from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

# ip/''
urlpatterns = [
    path("", views.ekyc, name = "ekyc_page"),
    path("login/", views.login_user, name = "login_page"),
    path("signup/", views.register_user, name = "signup_page"),
    path("user_document_verification/<int:id>", views.user_document_verification, name = "user_document_verification_page"),
    path("logout/", views.logout_user, name = "logout_page"),
    path("dashboard/", views.dashboard_user, name="dashboard_page"),
    path("admin_dashboard/", views.dashboard_admin, name="admin_dashboard_page"),
    path("users_list/", views.dashboard_user_list, name="user_list_page"),
    # path("property_home/", views.add_property, name="property_home_page"),
    path("add_property/", views.add_property, name="add_property_page"),
    path("my_properties/", views.my_properties, name="my_properties_page"),
    path("search_properties/", views.search_properties, name="search_properties_page"),
    path("update_property/<int:id>", views.update_property),
    path("edit_property/<int:id>", views.edit_property, name = "edit_property_page"),
    path("delete_property/<int:id>", views.delete_property),
    path("apply_property_deal/<int:id>", views.apply_property_deal),
    path("display_property_applications/<int:id>", views.display_property_applications, name = 'display_property_applications_page'),
    path("accept_property_application/<int:id>", views.accept_property_application ),
    path("seller_contract/<int:id>", views.seller_contract, name = 'seller_contract_page' ),
    path("lessor_contract/<int:id>", views.lessor_contract, name = 'lessor_contract_page' ),
    path("reject_property_application/<int:id>", views.reject_property_application),
    path("payment_gateway/<int:id>", views.payment_gateway, name = 'payment_gateway_page'),
    path("rentals_payment_gateway/<int:id>", views.rentals_payment_gateway, name = 'rentals_payment_gateway_page'),
    path("process_payment/<int:id>", views.process_payment),
    path("past_buy_history", views.past_buy_history, name = "past_buy_history_page"),
    path("past_sell_history", views.past_sell_history, name = "past_sell_history_page"),
    path("view_contract/<int:id>", views.view_contract, name = "view_contract_page"),
    path("verify_contract", views.verify_contract, name = "verify_contract_page"),
    path("edit_profile", views.edit_profile, name = "edit_profile_page"),
]
