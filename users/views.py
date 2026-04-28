from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_http_methods
from .forms import UserRegistrationForm


def _safe_next_page(request, *, default: str = "/") -> str:
    next_page = request.GET.get("next", default)
    if not url_has_allowed_host_and_scheme(
        url=next_page,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return default
    return next_page


def index(request):
    return redirect(_safe_next_page(request))


@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    """View para login de usuários."""
    if request.method == "GET":
        return render(request, "login.html")

    if request.user.is_authenticated:
        return redirect(_safe_next_page(request))

    username = request.POST.get("username")
    password = request.POST.get("password")

    if not username or not password:
        messages.error(request, "Por favor, preencha todos os campos.")
        return render(request, "login.html")

    user = authenticate(request, username=username, password=password)

    if user is not None:
        if user.is_active:
            login(request, user)
            messages.success(request, f"Bem-vindo(a), {user.get_full_name() or user.username}!")
            return redirect(_safe_next_page(request))
        messages.error(request, "Sua conta está desativada.")
    else:
        messages.error(request, "Usuário ou senha incorretos.")

    return render(request, "login.html")


@csrf_protect
@require_POST
def logout_view(request):
    """View para logout de usuários"""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Você foi desconectado com sucesso.")
    return redirect("/")


@csrf_protect
@require_http_methods(["GET", "POST"])
def register_view(request):
    """View para cadastro de novos usuários"""
    if request.method == "GET":
        return render(request, "register.html", {"form": UserRegistrationForm()})

    if request.user.is_authenticated:
        return redirect(_safe_next_page(request))

    form = UserRegistrationForm(request.POST)

    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(
            request,
            f"Bem-vindo(a) ao BrazCar, {user.get_full_name() or user.username}! "
            "Seu cadastro foi realizado com sucesso.",
        )
        return redirect(_safe_next_page(request))

    messages.error(request, "Por favor, corrija os erros abaixo.")
    return render(request, "register.html", {"form": form})
