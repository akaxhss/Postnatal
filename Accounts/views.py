from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import *
from .models import *
from django.http import JsonResponse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework.response import Response


# Create your views here.
class UserRegistrationView(APIView):
    def post(self, request):
        data = request.data
        serializer = UserPostNatalSerializer(data=data)

        if serializer.is_valid():
            # Create the user instance
            user = UserPostNatal.objects.create_user(
                email=serializer.validated_data['email'],
                firstname=serializer.validated_data['firstname'],
                lastname=serializer.validated_data['lastname'],
                mobile=serializer.validated_data['mobile'],
                fcm_token=serializer.validated_data['fcm_token'],
                password=serializer.validated_data['password']  # Set the password
            )

            # Create CustomerDetails for the user
            customer_details_data = {
                "user": user.pk,  # Pass the user's primary key
                "address": "",  # Add any other fields as needed
                "date_of_birth_parent": None,
                "babydob": None,
                "babyGender": None
            }
            customer_details_serializer = CustomerDetailsSerializer(data=customer_details_data)

            if customer_details_serializer.is_valid():
                customer_details_serializer.save()
            else:
                # Handle errors with CustomerDetails creation
                user.delete()  # Delete the user if CustomerDetails creation fails
                return Response(
                    customer_details_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

from django.contrib.auth import login as django_login
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .models import UserPostNatal  # Import your custom token model
from .serializers import UserPostNatalSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    data = request.data
    email = data.get('email')
    password = data.get('password')

    try:
        user_postnatal = UserPostNatal.objects.get(email=email)
    except UserPostNatal.DoesNotExist:
        user_postnatal = None

    if user_postnatal is not None and user_postnatal.check_password(password):
        if not user_postnatal.is_active:
            return JsonResponse(
                {
                    "error": "Please call your salesperson to activate this account."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        else:
            # Log the user in
            django_login(request, user_postnatal)

            # Check if the user already has a token
            token, created = Token.objects.get_or_create(user=user_postnatal)

            return JsonResponse(
                {
                    "message": "User is logged in successfully.",
                    "token": token.key  # Include the token in the response
                },
                status=status.HTTP_200_OK
            )
    else:
        return JsonResponse(
            {
                "error": "Login failed"
            },
            status=status.HTTP_401_UNAUTHORIZED
        )
    

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
# @authentication_classes([TokenAuthentication])
def logout_view(request):
    customer = request.user.id
    if customer is not None:
        try:
            token = Token.objects.get(user=customer)
            token.delete()
            return JsonResponse({'message': 'User logged out successfully'})
        except Token.DoesNotExist:
            return JsonResponse({'message': 'User already logged out'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"Error": "User customer not provided"}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_customer_details(request):
    user = request.user  # Retrieve the user associated with the token

    try:
        customer_details = CustomerDetails.objects.get(user=user)
        serializer = CustomerDetailsSerializer(customer_details)
        return Response(serializer.data, status=200)
    except CustomerDetails.DoesNotExist:
        return Response({"error": "Customer details not found for this user."}, status=404)


from django.views.decorators.csrf import csrf_exempt

@api_view(['POST'])  # Change to POST
@permission_classes([IsAuthenticated])
@csrf_exempt
def update_customer_details(request):
    user = request.user  # Retrieve the user associated with the token
    print(f"User: {user}")  # Print user for debugging
    print(f"Request Data: {request.data}")

    try:
        customer_details = CustomerDetails.objects.get(user=user)
    except CustomerDetails.DoesNotExist:
        return Response({"error": "Customer details not found for this user."}, status=404)

    serializer = CustomerDetailsSerializer(customer_details, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=200)
    else:
        return Response(serializer.errors, status=400)