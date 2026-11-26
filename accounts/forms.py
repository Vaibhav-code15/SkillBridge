from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from skills.services import skill_name_exists

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
from .private_files import validate_pdf


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.Role.choices)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "role", "password1", "password2"]


class SkillBridgeAuthenticationForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        user = User.objects.filter(username=username, is_active=False).first() if username else None
        if user and password and user.check_password(password):
            raise forms.ValidationError(
                "This account is inactive. Contact an administrator.", code="inactive"
            )
        return super().clean()


class ApplicationForm(forms.Form):
    note = forms.CharField(required=False, max_length=1500, strip=True, widget=forms.Textarea)
    resume_choice = forms.ChoiceField(
        required=False,
        choices=[("none", "No resume"), ("profile", "Profile resume"), ("upload", "Upload a PDF")],
    )
    resume = forms.FileField(required=False, validators=[validate_pdf])

    def clean(self):
        data = super().clean()
        choice = data.get("resume_choice") or "none"
        upload = data.get("resume")
        if choice == "upload" and not upload and "resume" not in self.errors:
            self.add_error("resume", "Choose a PDF resume to upload.")
        if choice != "upload" and upload:
            self.add_error("resume", "Choose the upload option to attach a file.")
        data["resume_choice"] = choice
        return data


class ProfileForm(forms.ModelForm):
    academic_year = forms.IntegerField(required=False, min_value=1, max_value=8)

    class Meta:
        model = StudentProfile
        fields = ["branch", "academic_year", "interests"]


class StudentSkillForm(forms.ModelForm):
    proficiency = forms.IntegerField(
        min_value=1, max_value=4, help_text="1 = beginner, 4 = advanced"
    )

    class Meta:
        model = StudentSkill
        fields = ["skill", "proficiency"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["skill"].queryset = Skill.objects.filter(active=True) | Skill.objects.filter(
            pk=self.instance.skill_id
        )


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description", "link"]


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ["title", "issuer", "date_earned", "link"]
        widgets = {"date_earned": forms.DateInput(attrs={"type": "date"})}


class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = ["title", "description", "type", "deadline", "status"]
        widgets = {"deadline": forms.DateInput(attrs={"type": "date"})}


class RequiredSkillForm(forms.ModelForm):
    minimum_proficiency = forms.IntegerField(min_value=1, max_value=4)
    weight = forms.IntegerField(min_value=1, max_value=100, help_text="Importance from 1 to 100")

    class Meta:
        model = RequiredSkill
        fields = ["skill", "minimum_proficiency", "weight"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["skill"].queryset = Skill.objects.filter(active=True) | Skill.objects.filter(
            pk=self.instance.skill_id
        )


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ["name", "active"]

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Enter a skill name.")
        names = Skill.objects.exclude(pk=self.instance.pk).values_list("name", flat=True)
        if skill_name_exists(name, names):
            raise forms.ValidationError("A skill with this name already exists.")
        return name
