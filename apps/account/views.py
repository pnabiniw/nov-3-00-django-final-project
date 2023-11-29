from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

from apps.commons.utils import authenticate_user, validate_email, send_account_activation_mail
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import UserProfile, UserAccountActivationKey

User = get_user_model()


class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'account/registration.html'
    success_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = "Sign Up"
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            messages.success(request, "An Account Activation Email Has Been Sent To You !!")
            response = self.form_valid(form)
            user = self.object
            # send_account_activation_mail(request, user)
            return response
        else:
            return self.form_invalid(form)


class UserLoginView(CreateView):
    template_name = "account/login.html"
    success_url = reverse_lazy("home")
    form = UserLoginForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context={"title": "Login", "form": self.form()})

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        username_or_email = request.POST['username_or_email']
        password = request.POST['password']
        if validate_email(username_or_email):
            user = authenticate_user(password, email=username_or_email)
        else:
            user = authenticate_user(password, username=username_or_email)
        if user is not None:
            login(request, user)
            messages.success(request, "User Logged In Successfully !!")
            return redirect('home')
        messages.error(request, "Invalid Username or Password !!")
        return redirect('user_login')


def user_logout(request):
    logout(request)
    messages.success(request, "User Logged Out !!")
    return redirect("home")


class UserProfileView(TemplateView):
    template_name = 'account/user_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "User Profile"
        # context['is_profile_complete'] = is_profile_complete(self.request.user)
        return context


class UserProfileUpdateView(CreateView):
    template_name = "account/user_profile_update.html"
    form_class = UserProfileForm
    success_url = reverse_lazy('user_profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Profile Update"
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            resume = form.cleaned_data.pop('resume', None)
            pp = form.cleaned_data.pop('profile_picture', None)
            up, _ = UserProfile.objects.update_or_create(user=self.request.user, defaults=form.cleaned_data)
            if resume or pp:
                if resume:
                    up.resume = resume
                if pp:
                    up.profile_picture = pp
                up.save()
            messages.success(request, "Your Profile Has Been Updated !!")
            return redirect('user_profile')
        else:
            error_dict = form.errors.get_json_data()
            print(form.errors)
            error_dict_values = list(error_dict.values())
            error_messg = error_dict_values[0][0].get("message")
            messages.error(request, form.errors)
            return self.form_invalid(form)


def user_account_activation(request, username, key):
    if UserAccountActivationKey.objects.filter(user__username=username, key=key):
        User.objects.filter(username=username).update(account_activated=True)
        UserAccountActivationKey.objects.filter(user__username=username).delete()
        messages.success(request, "Your Account Has Been Activated !!")
    else:
        messages.error(request, "Invalid Link OR The Link Has Been Expired !!")
    return redirect('user_login')
