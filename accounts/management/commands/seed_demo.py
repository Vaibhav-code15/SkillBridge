import os
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounts.models import (
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


class Command(BaseCommand):
    help = "Seed fictional demo data in an explicitly authorised development environment."

    @transaction.atomic
    def handle(self, *args, **options):
        if os.environ.get("SKILLBRIDGE_ALLOW_DEMO_SEED") != "1" or os.environ.get("POSTGRES_DB"):
            raise CommandError(
                "Set SKILLBRIDGE_ALLOW_DEMO_SEED=1 for local SQLite development only."
            )
        password = os.environ.get("SKILLBRIDGE_DEMO_PASSWORD")
        if not password or len(password) < 12:
            raise CommandError(
                "Set SKILLBRIDGE_DEMO_PASSWORD to a local password of at least 12 characters."
            )
        names = [
            "Python",
            "Django",
            "JavaScript",
            "HTML",
            "CSS",
            "SQL",
            "Git",
            "Data Analysis",
            "Machine Learning",
            "Java",
            "C++",
            "Research",
            "Communication",
            "Teamwork",
            "UI Design",
            "Figma",
            "Statistics",
            "Writing",
            "Project Management",
            "Testing",
            "Linux",
            "Cloud Computing",
            "Cybersecurity",
            "React",
            "Databases",
            "Data Visualization",
            "Algorithms",
            "Public Speaking",
        ]
        skills = []
        for name in names:
            skill, _ = Skill.objects.get_or_create(name=name)
            skills.append(skill)
        for i in range(1, 17):
            role = User.Role.STUDENT if i <= 12 else User.Role.FACULTY
            is_admin = i == 16
            username = f"demo_{'admin' if is_admin else 'student' if i <= 12 else 'faculty'}_{i}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "first_name": "Demo",
                    "last_name": f"Member {i}",
                    "role": "" if is_admin else role,
                    "is_staff": is_admin,
                    "is_superuser": is_admin,
                },
            )
            if not created and (
                user.email != f"{username}@example.com"
                or user.is_superuser != is_admin
                or (not is_admin and user.role != role)
            ):
                raise CommandError(
                    f"Existing account {username} does not match demo identity; refusing to alter it."
                )
            user.set_password(password)
            user.save(update_fields=["password"])
            if i <= 12:
                StudentProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "branch": "Computer Science",
                        "academic_year": (i % 4) + 1,
                        "interests": "Research, software and collaboration",
                    },
                )
                for n in range(4):
                    StudentSkill.objects.get_or_create(
                        student=user,
                        skill=skills[(i + n) % len(skills)],
                        defaults={"proficiency": (n % 4) + 1},
                    )
                Project.objects.get_or_create(
                    student=user,
                    title="Campus collaboration project",
                    defaults={
                        "description": "A fictional project exploring useful tools for students."
                    },
                )
                Certification.objects.get_or_create(
                    student=user, title="Foundations of Computing", issuer="Example Learning"
                )
            elif not is_admin:
                for n in range(3):
                    opportunity, _ = Opportunity.objects.get_or_create(
                        faculty=user,
                        title=f"{['Community Data Study', 'Campus Software Internship', 'Research Collaboration'][n]} {i}",
                        defaults={
                            "description": "A fictional opportunity to collaborate on a practical academic challenge.",
                            "type": ["research", "internship", "project"][n],
                            "deadline": timezone.localdate() + timedelta(days=45 + n * 10),
                            "status": "published",
                        },
                    )
                    for index in range(2):
                        RequiredSkill.objects.get_or_create(
                            opportunity=opportunity,
                            skill=skills[(i + n + index) % len(skills)],
                            defaults={"minimum_proficiency": 2, "weight": 3 + index},
                        )
        demo_students = list(
            User.objects.filter(username__startswith="demo_student_").order_by("username")
        )
        demo_opportunities = list(
            Opportunity.objects.filter(
                faculty__username__startswith="demo_faculty_", status=Opportunity.Status.PUBLISHED
            ).order_by("pk")
        )
        first_opportunity_id = demo_opportunities[0].pk if demo_opportunities else None
        for opportunity in demo_opportunities:
            for student in demo_students:
                student_number = int(student.username.rsplit("_", 1)[1])
                is_tied_seed_application = (
                    opportunity.pk == first_opportunity_id and student_number in (1, 2)
                )
                if not is_tied_seed_application and (student_number + opportunity.pk) % 3 == 0:
                    continue
                applied_at = datetime(2026, 10, 1, 12) + timedelta(
                    days=(student_number + opportunity.pk) % 14
                )
                if opportunity.pk == first_opportunity_id and student_number in (1, 2):
                    applied_at = datetime(2026, 10, 1, 12)
                Application.objects.get_or_create(
                    student=student,
                    opportunity=opportunity,
                    defaults={"applied_at": timezone.make_aware(applied_at)},
                )
        self.stdout.write(
            self.style.SUCCESS(
                "Demo data ready. All demo accounts use the following local password for this run:"
            )
        )
        self.stdout.write(password)
        self.stdout.write(
            "Usernames: demo_student_1 through demo_student_12, demo_faculty_13 through demo_faculty_15, demo_admin_16"
        )
