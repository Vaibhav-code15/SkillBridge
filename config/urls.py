"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from accounts import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile_edit, name="profile_edit"),
    path("portfolio/<str:kind>/add/", views.student_item, name="student_add"),
    path("portfolio/<str:kind>/<int:pk>/edit/", views.student_item, name="student_edit"),
    path("portfolio/<str:kind>/<int:pk>/delete/", views.student_delete, name="student_delete"),
    path("opportunities/add/", views.opportunity_edit, name="opportunity_add"),
    path("opportunities/<int:pk>/", views.opportunity_detail, name="opportunity_detail"),
    path("opportunities/<int:pk>/edit/", views.opportunity_edit, name="opportunity_edit"),
    path("opportunities/<int:pk>/delete/", views.opportunity_delete, name="opportunity_delete"),
    path(
        "opportunities/<int:pk>/requirements/add/", views.requirement_edit, name="requirement_add"
    ),
    path(
        "opportunities/<int:pk>/requirements/<int:requirement_id>/edit/",
        views.requirement_edit,
        name="requirement_edit",
    ),
    path(
        "opportunities/<int:pk>/requirements/<int:requirement_id>/delete/",
        views.requirement_delete,
        name="requirement_delete",
    ),
    path("catalogue/add/", views.catalogue_edit, name="catalogue_add"),
    path("catalogue/<int:pk>/edit/", views.catalogue_edit, name="catalogue_edit"),
]
