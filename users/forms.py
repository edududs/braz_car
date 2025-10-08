from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from utils.validations.cpf import normalize_cpf, validate_cpf

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    """Formulário de cadastro de usuário com validações"""

    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "Digite uma senha forte"}),
        help_text="Mínimo 8 caracteres",
    )
    password_confirm = forms.CharField(
        label="Confirmar Senha",
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "Digite a senha novamente"}),
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "cpf", "phone", "birth_date"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-input", "placeholder": "Escolha um nome de usuário"}),
            "email": forms.EmailInput(attrs={"class": "form-input", "placeholder": "seu@email.com"}),
            "first_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Seu nome"}),
            "last_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Seu sobrenome"}),
            "cpf": forms.TextInput(attrs={"class": "form-input", "placeholder": "000.000.000-00", "maxlength": "14"}),
            "phone": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "(61) 99999-9999", "maxlength": "15"}
            ),
            "birth_date": forms.DateInput(attrs={"class": "form-input", "type": "date", "placeholder": "dd/mm/aaaa"}),
        }
        labels = {
            "username": "Nome de Usuário",
            "email": "Email",
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "cpf": "CPF",
            "phone": "Telefone",
            "birth_date": "Data de Nascimento",
        }
        help_texts = {
            "username": "Apenas letras, números e @/./+/-/_",
            "cpf": "Apenas números, com ou sem formatação",
            "phone": "DDD + número com 9 dígitos",
        }

    def clean_cpf(self):
        """Valida e normaliza o CPF"""
        cpf = self.cleaned_data.get("cpf")

        if not cpf:
            raise ValidationError("CPF é obrigatório.")

        # Validar CPF
        try:
            validate_cpf(cpf)
        except ValidationError as e:
            raise ValidationError(str(e))

        # Normalizar (remover formatação)
        cpf = normalize_cpf(cpf)

        # Verificar se já existe
        if User.objects.filter(cpf=cpf).exists():
            raise ValidationError("Este CPF já está cadastrado.")

        return cpf

    def clean_email(self):
        """Verifica se o email já está em uso"""
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise ValidationError("Este email já está cadastrado.")

        return email.lower()

    def clean_username(self):
        """Verifica se o username já está em uso"""
        username = self.cleaned_data.get("username")

        if User.objects.filter(username=username).exists():
            raise ValidationError("Este nome de usuário já está em uso.")

        return username.lower()

    def clean_phone(self):
        """Normaliza o telefone"""
        phone = self.cleaned_data.get("phone")

        # Remove caracteres especiais
        phone = "".join(filter(str.isdigit, phone))

        # Valida tamanho (DDD + 9 dígitos)
        if len(phone) not in [10, 11]:
            raise ValidationError("Telefone deve ter DDD + 8 ou 9 dígitos.")

        return phone

    def clean_birth_date(self):
        """Valida a data de nascimento"""
        from datetime import date

        birth_date = self.cleaned_data.get("birth_date")

        if not birth_date:
            raise ValidationError("Data de nascimento é obrigatória.")

        # Calcular idade
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        if age < 18:
            raise ValidationError("Você deve ter pelo menos 18 anos para se cadastrar.")

        if age > 120:
            raise ValidationError("Data de nascimento inválida.")

        return birth_date

    def clean(self):
        """Validações que envolvem múltiplos campos"""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        # Verificar se as senhas coincidem
        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError({"password_confirm": "As senhas não coincidem."})

            # Validar força da senha
            if len(password) < 8:
                raise ValidationError({"password": "A senha deve ter pelo menos 8 caracteres."})

        return cleaned_data

    def save(self, commit=True):
        """Salva o usuário com a senha criptografada"""
        user = super().save(commit=False)

        # Definir senha criptografada
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user
