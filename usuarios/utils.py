from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

def generate_email_verification_link(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verification_link = f"{request.scheme}://{request.get_host()}/api/verifi-email/{uid}/{token}/"
    return verification_link