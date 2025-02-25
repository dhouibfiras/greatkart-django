from django.shortcuts import render, redirect, HttpResponse
from .forms import RegistrationForm
from .models import Account, MyAccountManager
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# vérification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            # username est nécessaire pou create_user, mais pas de field username dans le formulaire, on doit donc définir username automatiquement depuis le mail par exemple
            username = email.split("@")[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )
            # create_user ne recoit pas d'argument phone_number, donc on ne peut pas passer cet argument depuis le fields directement à l'instantiation de user.. on doit le faire après la création
            user.phone_number = phone_number
            user.save()

            # User activation
            current_site = get_current_site(request)
            # En développement, on utilise localhost, mais en production le site va etre différent, d'où current_site
            mail_subject = "Please activate your account."
            # message c'est le contenu du mail, on le met dans un template
            message = render_to_string(
                "accounts/account_verification_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    # encoder le primarykey (pk) pour que personne ne puisse le voir
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    # créer un token pour le user
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # fin User activation

            # après registration et envoi du mail de verificatio, rediriger l'utilisateur vers login.html avec les request command et email pour exécuter la condition if dans login.html qui affiche le message "we have sent you a vérification link..."
            # le + email c'est pour concaténer les 2 chaines: l'url statique et le email dynamique
            return redirect("/accounts/login/?command=verification&email=" + email)
    else:
        form = RegistrationForm()
    context = {
        "form": form,
    }
    return render(request, "accounts/register.html", context)


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        # préférer utilisation de cleaned_data (Voir cours Django Zeste de savoir)

        user = auth.authenticate(email=email, password=password)
        # utilisation possible sans auth: user = authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            # utilisation possible sans auth: login (request, user)
            messages.success(request, "You are Logged in")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid Login")
            return redirect("login")
    return render(request, "accounts/login.html")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request, "You are Logged Out")
    return redirect("login")


def activate(request, uidb64, token):
    try:
        # décoder le primary key (encoder dans register par urlsafe_base64_encode)
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! your account is activated")
        return redirect("login")
    else:
        messages.error(request, "Invalid activation link")
        return redirect("register")


@login_required(login_url="login")
def dashboard(request):
    return render(request, "accounts/dashboard.html")


def forgotpassword(request):
    if request.method == "POST":
        email = request.POST["email"]
        # vérifier si l'email existe déjà
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(
                email__exact=email
            )  # on peut écrire email = email, ou email__exact = email (plus précis), ou email__iexact = email (case insensitif)
            current_site = get_current_site(request)
            # En développement, on utilise localhost, mais en production le site va etre différent, d'où current_site
            mail_subject = "Reset password"
            # message c'est le contenu du mail, on le met dans un template
            message = render_to_string(
                "accounts/reset_password_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    # encoder le primarykey (pk) pour que personne ne puisse le voir
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    # créer un token pour le user
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(
                request, "Password reset email has been sent to your email address"
            )
            return redirect("login")
        # si l'email n'existe pas, ebvoyer erreur
        else:
            messages.error(request, "Account does not exist!")
            return redirect("forgotpassword")

    return render(request, "accounts/forgotpassword.html")


def reset_password_validate(request, uidb64, token):
    try:
        # décoder le primary key (encoder dans forgotpassword par urlsafe_base64_encode)
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "Please reset your password")
        return redirect("resetpassword")
    else:
        messages.error(request, "The link is expired")
        return redirect("login")


def reset_password(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirmpassword = request.POST["confirm_password"]
        if password == confirmpassword:
            uid = request.session.get("uid")
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successful")
            return redirect("login")
        else:
            messages.error(request, "Password do not match!")
            return redirect("resetpassword")
    else:
        return render(request, "accounts/resetpassword.html")
