from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone

from .private_files import private_resume_storage, resume_path, validate_pdf


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        FACULTY = "faculty", "Faculty"

    role = models.CharField(max_length=20, choices=Role.choices, blank=True)


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    branch = models.CharField(max_length=100, blank=True)
    academic_year = models.PositiveSmallIntegerField(null=True, blank=True)
    interests = models.TextField(blank=True)
    resume = models.FileField(
        storage=private_resume_storage, upload_to=resume_path, validators=[validate_pdf], blank=True
    )
    resume_name = models.CharField(max_length=200, blank=True)
    resume_size = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(academic_year__gte=1, academic_year__lte=8)
                | models.Q(academic_year__isnull=True),
                name="profile_year_range",
            )
        ]


class Skill(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(Lower("name"), name="skill_name_case_unique")]

    def __str__(self):
        return self.name


class StudentSkill(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_skills")
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT)
    proficiency = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "skill"], name="unique_student_skill"),
            models.CheckConstraint(
                condition=models.Q(proficiency__gte=1, proficiency__lte=4),
                name="student_skill_level_range",
            ),
        ]


class Project(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=150)
    description = models.TextField()
    link = models.URLField(blank=True)


class Certification(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="certifications")
    title = models.CharField(max_length=150)
    issuer = models.CharField(max_length=150)
    date_earned = models.DateField(null=True, blank=True)
    link = models.URLField(blank=True)


class OpportunityQuerySet(models.QuerySet):
    def visible(self):
        return self.filter(is_removed=False)

    def is_open(self):
        return self.visible().filter(
            status=Opportunity.Status.PUBLISHED, deadline__gte=timezone.localdate()
        )


class Opportunity(models.Model):
    class Type(models.TextChoices):
        INTERNSHIP = "internship", "Internship"
        PROJECT = "project", "Academic project"
        RESEARCH = "research", "Research"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        CLOSED = "closed", "Closed"

    faculty = models.ForeignKey(User, on_delete=models.CASCADE, related_name="opportunities")
    title = models.CharField(max_length=150)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=Type.choices)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    is_removed = models.BooleanField(default=False)
    removed_at = models.DateTimeField(null=True, blank=True)
    objects = OpportunityQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(type__in=["internship", "project", "research"]),
                name="opportunity_valid_type",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=["draft", "published", "closed"]),
                name="opportunity_valid_status",
            ),
        ]

    @property
    def is_open(self):
        return (
            not self.is_removed
            and self.status == self.Status.PUBLISHED
            and self.deadline >= timezone.localdate()
        )


class RequiredSkill(models.Model):
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name="requirements"
    )
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT)
    minimum_proficiency = models.PositiveSmallIntegerField()
    weight = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["opportunity", "skill"], name="unique_opportunity_skill"
            ),
            models.CheckConstraint(
                condition=models.Q(minimum_proficiency__gte=1, minimum_proficiency__lte=4),
                name="required_skill_level_range",
            ),
            models.CheckConstraint(
                condition=models.Q(weight__gte=1, weight__lte=100),
                name="required_skill_weight_range",
            ),
        ]


class Application(models.Model):
    class Status(models.TextChoices):
        APPLIED = "applied", "Applied"
        SHORTLISTED = "shortlisted", "Shortlisted"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name="applications"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPLIED)
    applied_at = models.DateTimeField(default=timezone.now, editable=False)
    status_changed_at = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True, max_length=1500)
    resume = models.FileField(
        storage=private_resume_storage, upload_to=resume_path, validators=[validate_pdf], blank=True
    )
    resume_name = models.CharField(max_length=200, blank=True)
    resume_size = models.PositiveIntegerField(null=True, blank=True)

    def clean(self):
        super().clean()
        self.note = (self.note or "").strip()

    class Meta:
        ordering = ["applied_at", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "opportunity"], name="unique_student_opportunity_application"
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=["applied", "shortlisted", "rejected", "withdrawn"]),
                name="application_status",
            ),
        ]
        indexes = [
            models.Index(fields=["opportunity", "applied_at"], name="application_opp_time"),
            models.Index(fields=["student", "applied_at"], name="application_student_time"),
        ]


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications"
    )
    created_at = models.DateTimeField(default=timezone.now)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
