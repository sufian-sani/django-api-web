from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from .models import UserProfile, Blog
from .serializers import RegisterSerializer, ProfileSerializer,BlogSerializer

from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes, parser_classes


# Create your views here.

# login register profile start

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({'message': 'Logged in successfully'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def password_reset_request(request):
    email = request.data.get('email')
    if not email:
        return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"detail": "No user found with this email."}, status=404)

    token = default_token_generator.make_token(user)
    uid = user.pk

    # You can replace this with your frontend reset URL
    reset_url = f"http://localhost:5173/reset-password?uid={uid}&token={token}"

    # Send email (or print for testing)
    send_mail(
        subject="Reset Your Password",
        message=f"Click here to reset your password: {reset_url}",
        from_email="noreply@example.com",
        recipient_list=[user.email],
        fail_silently=False,
    )

    return Response({"detail": "Password reset link sent."}, status=status.HTTP_200_OK)

@api_view(['POST'])
def password_reset_confirm(request):
    uid = request.data.get('uid')
    token = request.data.get('token')
    new_password = request.data.get('password')

    if not all([uid, token, new_password]):
        return Response({"detail": "uid, token, and password are required."},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(pk=uid)
    except User.DoesNotExist:
        return Response({"detail": "Invalid user ID."}, status=404)

    if not default_token_generator.check_token(user, token):
        return Response({"detail": "Invalid or expired token."}, status=400)

    user.set_password(new_password)
    user.save()

    return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def profile_view(request):
#     return Response({"username": request.user.username})

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])  # if you're uploading files (like avatar)
def profile_view(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return Response({"detail": "Profile not found."}, status=404)

    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    

# login register profile end

# blog operation start

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def blog_list_create(request):
    if request.method == 'GET':
        # blogs = Blog.objects.all().order_by('-created_at')
        if request.user.is_authenticated:
            # Show all blogs for authenticated user
            blogs = Blog.objects.all().order_by('-created_at')
        else:
            # Only published blogs for anonymous users
            blogs = Blog.objects.filter(status='published').order_by('-created_at')
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=401)
        serializer = BlogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def blog_detail(request, pk):
    try:
        blog = Blog.objects.get(pk=pk)
    except Blog.DoesNotExist:
        return Response({"detail": "Blog not found."}, status=404)

    if request.method == 'GET':
        if blog.status == 'draft' and blog.author != request.user:
            return Response({"detail": "You do not have permission to view this blog."}, status=403)
        serializer = BlogSerializer(blog)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=401)
        if blog.author != request.user:
            return Response({"detail": "You do not have permission to update this blog."}, status=403)
        serializer = BlogSerializer(blog, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=401)
        if blog.author != request.user:
            return Response({"detail": "You do not have permission to delete this blog."}, status=403)
        blog.delete()
        return Response(status=204)

# blog operation end