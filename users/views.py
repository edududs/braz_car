from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from .forms import UserRegistrationForm


def index(request):
    return render(request, "index.html")


@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    """View para login de usuários."""
    if request.user.is_authenticated:
        return redirect("braz_car:index")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Por favor, preencha todos os campos.")
            return render(request, "login.html")

        # Autenticar usuário
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Bem-vindo(a), {user.get_full_name() or user.username}!")

                # Redirecionar para próxima página ou home
                next_page = request.GET.get("next", "braz_car:index")
                return redirect(next_page)
            messages.error(request, "Sua conta está desativada.")
        else:
            messages.error(request, "Usuário ou senha incorretos.")

    return render(request, "login.html")


def logout_view(request):
    """View para logout de usuários"""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Você foi desconectado com sucesso.")
    return redirect("braz_car:index")


@csrf_protect
@require_http_methods(["GET", "POST"])
def register_view(request):
    """View para cadastro de novos usuários"""
    if request.user.is_authenticated:
        return redirect("braz_car:index")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            # Salvar usuário
            user = form.save()

            # Fazer login automaticamente
            login(request, user)

            messages.success(
                request,
                f"Bem-vindo(a) ao BrazCar, {user.get_full_name() or user.username}! "
                "Seu cadastro foi realizado com sucesso.",
            )

            return redirect("braz_car:index")
        messages.error(request, "Por favor, corrija os erros abaixo.")
    else:
        form = UserRegistrationForm()

    return render(request, "register.html", {"form": form})
