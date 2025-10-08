from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class MultiFieldBackend(ModelBackend):
    """Backend que permite login com username, email, CPF ou telefone."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            # Busca usuário por qualquer um dos campos
            user = User.objects.get(Q(username=username) | Q(email=username) | Q(cpf=username) | Q(phone=username))

            # Verifica senha
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

        return None
