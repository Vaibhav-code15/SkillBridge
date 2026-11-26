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
from accounts.forms import SkillBridgeAuthenticationForm

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(authentication_form=SkillBridgeAuthenticationForm),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("applications/", views.my_applications, name="my_applications"),
    path("recommendations/", views.recommendations, name="recommendations"),
    path("improvements/", views.improvements, name="improvements"),
    path(
        "applications/<int:pk>/withdraw/", views.application_withdraw, name="application_withdraw"
    ),
    path(
        "applications/<int:pk>/decision/", views.application_decision, name="application_decision"
    ),
    path("notifications/", views.notification_inbox, name="notification_inbox"),
    path("notifications/read-all/", views.notification_read_all, name="notification_read_all"),
    path("notifications/<int:pk>/read/", views.notification_read, name="notification_read"),
    path("profile/", views.profile_edit, name="profile_edit"),
    path("profile/overview/", views.profile_overview, name="profile_overview"),
    path("profile/resume/upload/", views.profile_resume_upload, name="profile_resume_upload"),
    path("profile/resume/remove/", views.profile_resume_remove, name="profile_resume_remove"),
    path("profile/resume/download/", views.profile_resume_download, name="profile_resume_download"),
    path(
        "applications/<int:pk>/resume/",
        views.application_resume_download,
        name="application_resume_download",
    ),
    path("portfolio/<str:kind>/add/", views.student_item, name="student_add"),
    path("portfolio/<str:kind>/<int:pk>/edit/", views.student_item, name="student_edit"),
    path("portfolio/<str:kind>/<int:pk>/delete/", views.student_delete, name="student_delete"),
    path("opportunities/add/", views.opportunity_edit, name="opportunity_add"),
    path("opportunities/", views.opportunity_list, name="opportunity_list"),
    path("opportunities/<int:pk>/", views.opportunity_detail, name="opportunity_detail"),
    path("opportunities/<int:pk>/apply/", views.opportunity_apply, name="opportunity_apply"),
    path(
        "opportunities/<int:pk>/applicants/",
        views.opportunity_applicants,
        name="opportunity_applicants",
    ),
    path("opportunities/<int:pk>/edit/", views.opportunity_edit, name="opportunity_edit"),
    path("opportunities/<int:pk>/team-gap/", views.team_gap, name="team_gap"),
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
    path("reports/", views.admin_reports, name="admin_reports"),
    path("moderation/", views.moderation, name="moderation"),
    path("moderation/users/<int:pk>/", views.moderate_user, name="moderate_user"),
    path(
        "moderation/opportunities/<int:pk>/",
        views.moderate_opportunity,
        name="moderate_opportunity",
    ),
    path("catalogue/<int:pk>/edit/", views.catalogue_edit, name="catalogue_edit"),
]
