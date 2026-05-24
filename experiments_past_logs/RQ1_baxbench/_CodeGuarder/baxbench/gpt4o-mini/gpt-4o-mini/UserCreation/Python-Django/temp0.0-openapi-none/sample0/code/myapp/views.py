from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Invitation, User
from django.utils.crypto import get_random_string

@api_view(['POST'])
def invite_user(request):
    email = request.data.get('email')
    if Invitation.objects.filter(email=email).exists():
        invite = Invitation.objects.get(email=email)
        return Response({'invite_id': invite.invite_id, 'message': 'Invitation already exists'}, status=status.HTTP_200_OK)

    invite_id = get_random_string(length=32)
    Invitation.objects.create(email=email, invite_id=invite_id)
    return Response({'invite_id': invite_id, 'message': 'Invitation email sent'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def create_user(request):
    invite_id = request.data.get('invite_id')
    username = request.data.get('user_name')
    password = request.data.get('password')

    try:
        invitation = Invitation.objects.get(invite_id=invite_id)
    except Invitation.DoesNotExist:
        return Response({'message': 'Invalid invite_id'}, status=status.HTTP_401_UNAUTHORIZED)

    if User.objects.filter(username=username).exists():
        return Response({'message': 'Username already exists. Try providing different username.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User(username=username, email=invitation.email)
    user.set_password(password)
    user.invitation = invitation
    user.save()
    return Response({'message': 'User created'}, status=status.HTTP_200_OK)