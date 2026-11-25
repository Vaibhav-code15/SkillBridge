from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Prefetch, Q
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from matching import rank_candidates

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
from .matching import match_student, requirements_for, skill_levels_for
from .models import (
    Application,
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


@login_required
def opportunity_detail(request, pk):
    item = get_object_or_404(Opportunity.objects.prefetch_related("requirements__skill"), pk=pk)
    is_student = request.user.role == User.Role.STUDENT and not request.user.is_superuser
    is_owner = request.user.role == User.Role.FACULTY and item.faculty_id == request.user.pk
    if is_student:
        if item.status == Opportunity.Status.DRAFT:
            raise Http404
    elif request.user.is_superuser:
        pass
    elif request.user.role == User.Role.FACULTY:
        if not is_owner:
            raise Http404
    else:
        return HttpResponseForbidden("You do not have access to this page.")

    fit = None
    application = None
    fit_groups = []
    has_skills = False
    if is_student:
        levels = skill_levels_for(request.user)
        has_skills = bool(levels)
        fit = match_student(requirements_for(item), request.user, skill_levels=levels)
        fit_groups = [
            {
                "label": label,
                "skills": [skill for skill in fit.skills if skill.status == status],
            }
            for status, label in (
                ("matched", "Matched"),
                ("improvable", "Improvable"),
                ("missing", "Missing"),
            )
        ]
        application = Application.objects.filter(student=request.user, opportunity=item).first()
    return render(
        request,
        "opportunity.html",
        {
            "opportunity": item,
            "is_student": is_student,
            "is_owner": is_owner,
            "fit": fit,
            "fit_groups": fit_groups,
            "has_skills": has_skills,
            "application": application,
        },
    )


@login_required
def opportunity_list(request):
    if not request.user.is_superuser and request.user.role not in (
        User.Role.STUDENT,
        User.Role.FACULTY,
    ):
        return HttpResponseForbidden("You do not have access to this page.")

    opportunities = (
        Opportunity.objects.is_open()
        .select_related("faculty")
        .prefetch_related("requirements__skill")
    )
    if request.user.role == User.Role.FACULTY and not request.user.is_superuser:
        opportunities = opportunities.filter(faculty=request.user)
    search = request.GET.get("q", "").strip()
    if search:
        opportunities = opportunities.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(requirements__skill__name__icontains=search)
        ).distinct()

    selected_type = request.GET.get("type", "")
    allowed_types = {choice for choice, _ in Opportunity.Type.choices}
    if selected_type in allowed_types:
        opportunities = opportunities.filter(type=selected_type)
    else:
        selected_type = ""

    selected_skill = request.GET.get("skill", "")
    active_skills = Skill.objects.filter(active=True)
    if selected_skill.isdecimal() and active_skills.filter(pk=selected_skill).exists():
        opportunities = opportunities.filter(requirements__skill_id=selected_skill).distinct()
    else:
        selected_skill = ""

    page_obj = Paginator(opportunities, 9).get_page(request.GET.get("page"))
    match_scores = {}
    if request.user.role == User.Role.STUDENT and not request.user.is_superuser:
        student_levels = skill_levels_for(request.user)
        for item in page_obj.object_list:
            item.match_result = match_student(
                requirements_for(item), request.user, skill_levels=student_levels
            )
            match_scores[item.pk] = item.match_result

    return render(
        request,
        "opportunity_list.html",
        {
            "page_obj": page_obj,
            "search": search,
            "selected_type": selected_type,
            "selected_skill": selected_skill,
            "opportunity_types": Opportunity.Type.choices,
            "active_skills": active_skills,
            "match_scores": match_scores,
        },
    )


@role_required("student")
@require_POST
def opportunity_apply(request, pk):
    item = get_object_or_404(Opportunity, pk=pk)
    if item.status == Opportunity.Status.DRAFT:
        raise Http404
    if not item.is_open:
        messages.error(request, "Applications are closed for this opportunity.")
        return redirect("opportunity_detail", pk=item.pk)
    if Application.objects.filter(student=request.user, opportunity=item).exists():
        messages.info(request, "You have already applied to this opportunity.")
        return redirect("opportunity_detail", pk=item.pk)
    try:
        with transaction.atomic():
            Application.objects.create(student=request.user, opportunity=item)
    except IntegrityError:
        messages.info(request, "You have already applied to this opportunity.")
    else:
        messages.success(request, "Your application was submitted.")
    return redirect("opportunity_detail", pk=item.pk)


@role_required("faculty")
def opportunity_applicants(request, pk):
    item = get_object_or_404(
        Opportunity.objects.prefetch_related("requirements__skill"),
        pk=pk,
        faculty=request.user,
    )
    applications = list(
        Application.objects.filter(opportunity=item)
        .select_related("student", "student__profile")
        .prefetch_related(
            Prefetch(
                "student__student_skills", queryset=StudentSkill.objects.select_related("skill")
            ),
            "student__projects",
            "student__certifications",
        )
    )
    requirements = requirements_for(item)
    results = {}
    for application in applications:
        results[application.pk] = match_student(requirements, application.student)
    ranked = rank_candidates(
        applications,
        score_of=lambda application: results[application.pk].score,
        applied_at_of=lambda application: application.applied_at,
        applicant_name_of=lambda application: (
            application.student.get_full_name().strip() or application.student.username
        ),
        stable_id_of=lambda application: application.pk,
    )
    applicants = []
    for rank, application in enumerate(ranked, start=1):
        application.rank = rank
        application.match_result = results[application.pk]
        application.student_profile = getattr(application.student, "profile", None)
        applicants.append(application)
    return render(
        request,
        "opportunity_applicants.html",
        {"opportunity": item, "applicants": applicants},
    )


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
