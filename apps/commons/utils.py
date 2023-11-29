import re
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import PBKDF2PasswordHasher

from apps.account.models import UserAccountActivationKey

User = get_user_model()


def validate_email(email):
    # Regular expression pattern for email validation
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"  # abc@gmail.com
    return re.match(pattern, email)


def authenticate_user(password, username=None, email=None):
    if not username and not email:
        return
    if username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return
    else:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return
    hasher = PBKDF2PasswordHasher()
    return user if hasher.verify(password, user.password) else None


def get_random_key(size):
    import random
    alphabets = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789"
    random_key = ""
    for i in range(size):
        random_key += random.choice(alphabets)
    return random_key


def get_base_url(request):
    # "".join(["http://", "127.0.0.1:8000"])
    return "".join([f'{request.scheme}://', f'{request.get_host()}/'])  # http://127.0.0.1:8000/


def send_account_activation_mail(request, user):
    key = get_random_key(50)  # 50 characters
    base_url = get_base_url(request)  # http://127.0.0.1:8000/

    # http://127.0.0.1:8000/account/activate/user1/fnjdkjdfjdfjdfgbdfjbdfjfbd/
    activation_url = "".join([base_url, 'account/activate/', f'{user.username}/', f'{key}/'])
    subject = "Account Activation"
    message = f"""
    Hello, {user.get_full_name()}. Please click the provided link to activate your account.
    {activation_url}
    """
    from_email = "noreply@myproject.com"
    user.email_user(subject=subject, message=message, from_email=from_email)
    UserAccountActivationKey.objects.create(user=user, key=key)
