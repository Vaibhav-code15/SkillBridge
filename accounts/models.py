from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower


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
