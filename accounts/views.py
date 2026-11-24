from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    CertificationForm,
    OpportunityForm,
    ProfileForm,
    ProjectForm,
    RegistrationForm,
    RequiredSkillForm,
    SkillForm,
    StudentSkillForm,
)
from .models import (
    Certification,
    Opportunity,
    Project,
    RequiredSkill,
    Skill,
    StudentProfile,
    StudentSkill,
    User,
)


def role_required(role):
    def decorator(view):
        @login_required
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            allowed = (
                request.user.is_superuser
                if role == "admin"
                else request.user.role == role and not request.user.is_superuser
            )
            if not allowed:
                return HttpResponseForbidden("You do not have access to this page.")
            return view(request, *args, **kwargs)

        return wrapped

    return decorator


def home(request):
    return render(request, "home.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        if user.role == User.Role.STUDENT:
            StudentProfile.objects.create(user=user)
        login(request, user)
        return redirect("dashboard")
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    if request.user.is_superuser:
        return render(
            request,
            "dashboard.html",
            {
                "section": "admin",
                "skills": Skill.objects.all(),
                "user_count": User.objects.count(),
                "skill_count": Skill.objects.count(),
            },
        )
    if request.user.role == User.Role.STUDENT:
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        return render(
            request,
            "dashboard.html",
            {
                "section": "student",
                "profile": profile,
                "student_skills": request.user.student_skills.select_related("skill"),
                "projects": request.user.projects.all(),
                "certifications": request.user.certifications.all(),
            },
        )
    if request.user.role == User.Role.FACULTY:
        return render(
            request,
            "dashboard.html",
            {"section": "faculty", "opportunities": request.user.opportunities.all()},
        )
    return HttpResponseForbidden("Your account has no dashboard role.")


def edit_form(request, form, title, back="dashboard"):
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
            messages.success(request, "Changes saved successfully.")
            return redirect(back)
        except IntegrityError:
            form.add_error(None, "This record already exists or conflicts with an existing record.")
    return render(request, "form.html", {"form": form, "title": title, "back": back})


@role_required("student")
def profile_edit(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    return edit_form(request, ProfileForm(request.POST or None, instance=profile), "Edit profile")


@role_required("student")
def student_item(request, kind, pk=None):
    options = {
        "skills": (StudentSkill, StudentSkillForm, "Skill"),
        "projects": (Project, ProjectForm, "Project"),
        "certifications": (Certification, CertificationForm, "Certification"),
    }
    if kind not in options:
        from django.http import Http404

        raise Http404
    model, form_class, label = options[kind]
    item = (
        get_object_or_404(model, pk=pk, student=request.user) if pk else model(student=request.user)
    )
    return edit_form(
        request,
        form_class(request.POST or None, instance=item),
        f"{'Edit' if pk else 'Add'} {label.lower()}",
    )


@role_required("student")
@require_POST
def student_delete(request, kind, pk):
    models = {"skills": StudentSkill, "projects": Project, "certifications": Certification}
    if kind not in models:
        from django.http import Http404

        raise Http404
    get_object_or_404(models[kind], pk=pk, student=request.user).delete()
    messages.success(request, "Item removed.")
    return redirect("dashboard")


@role_required("faculty")
def opportunity_edit(request, pk=None):
    item = (
        get_object_or_404(Opportunity, pk=pk, faculty=request.user)
        if pk
        else Opportunity(faculty=request.user)
    )
    return edit_form(
        request,
        OpportunityForm(request.POST or None, instance=item),
        "Edit opportunity" if pk else "Create opportunity",
    )


@role_required("faculty")
def opportunity_detail(request, pk):
    item = get_object_or_404(Opportunity, pk=pk, faculty=request.user)
    return render(request, "opportunity.html", {"opportunity": item})


@role_required("faculty")
@require_POST
def opportunity_delete(request, pk):
    get_object_or_404(Opportunity, pk=pk, faculty=request.user).delete()
    messages.success(request, "Opportunity removed.")
    return redirect("dashboard")


@role_required("faculty")
def requirement_edit(request, pk, requirement_id=None):
    opportunity = get_object_or_404(Opportunity, pk=pk, faculty=request.user)
    item = (
        get_object_or_404(RequiredSkill, pk=requirement_id, opportunity=opportunity)
        if requirement_id
        else RequiredSkill(opportunity=opportunity)
    )
    form = RequiredSkillForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
            messages.success(request, "Requirement saved.")
            return redirect("opportunity_detail", pk=pk)
        except IntegrityError:
            form.add_error(None, "This skill is already required for this opportunity.")
    return render(
        request,
        "form.html",
        {"form": form, "title": "Configure required skill", "back_url": opportunity.pk},
    )


@role_required("faculty")
@require_POST
def requirement_delete(request, pk, requirement_id):
    opportunity = get_object_or_404(Opportunity, pk=pk, faculty=request.user)
    get_object_or_404(RequiredSkill, pk=requirement_id, opportunity=opportunity).delete()
    messages.success(request, "Requirement removed.")
    return redirect("opportunity_detail", pk=pk)


@role_required("admin")
def catalogue_edit(request, pk=None):
    item = get_object_or_404(Skill, pk=pk) if pk else Skill()
    return edit_form(
        request,
        SkillForm(request.POST or None, instance=item),
        "Edit catalogue skill" if pk else "Add catalogue skill",
    )
