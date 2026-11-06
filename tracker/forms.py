from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Project, Developer, Technology, Status


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Имя пользователя",
        widget=forms.TextInput(attrs={"autofocus": True, "autocomplete": "username"}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "status" in self.fields:
            current = self.instance.status_id if self.instance.pk else None
            allowed = {None: [1], 1: [1, 2], 2: [1, 2, 3], 3: [3]}
            self.fields["status"].queryset = Status.objects.filter(
                pk__in=allowed[current]
            )
            self.fields["status"].help_text = (
                "Доступны только разрешенные переходы; новый проект начинается со статуса «Запланирован»."
            )

    class Meta:
        model = Project
        fields = ["name", "developer", "technologies", "deadline", "status"]
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "technologies": forms.CheckboxSelectMultiple,
        }

    def _save_m2m(self):
        # Add replacements before removing old links so the project never has no technologies.
        if "technologies" in self.cleaned_data:
            self.instance.technologies.add(*self.cleaned_data["technologies"])
        super()._save_m2m()


class DeveloperForm(forms.ModelForm):
    class Meta:
        model = Developer
        fields = ["name"]
        labels = {"name": "ФИО разработчика"}


class TechnologyForm(forms.ModelForm):
    class Meta:
        model = Technology
        fields = ["name"]
        labels = {"name": "Название технологии"}


class ProjectFilterForm(forms.Form):
    q = forms.CharField(
        label="Поиск",
        required=False,
        max_length=200,
        widget=forms.TextInput(
            attrs={"placeholder": "Проект, разработчик или технология"}
        ),
    )
    status = forms.ChoiceField(
        label="Статус",
        required=False,
        choices=[
            ("", "Все"),
            ("1", "Запланирован"),
            ("2", "В работе"),
            ("3", "Завершен"),
        ],
    )
    sort = forms.ChoiceField(
        label="Сортировка",
        required=False,
        choices=[
            ("deadline", "Ближайший срок"),
            ("-deadline", "Поздний срок"),
            ("name", "Название А–Я"),
            ("-name", "Название Я–А"),
            ("developer", "По разработчику"),
        ],
    )
    date = forms.DateField(
        label="Срок завершения",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    developer = forms.ModelChoiceField(
        label="Разработчик",
        queryset=Developer.objects.all(),
        required=False,
        empty_label="Все",
    )
    technology = forms.ModelChoiceField(
        label="Технология",
        queryset=Technology.objects.all(),
        required=False,
        empty_label="Все",
    )


class DateForm(forms.Form):
    date = forms.DateField(
        label="Контрольная дата", widget=forms.DateInput(attrs={"type": "date"})
    )
