from rest_framework import generics
from .models import User
from .serializers import UserSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated 
from django.shortcuts import render
# عرض المستخدمين
class UserListView(generics.ListCreateAPIView):
  
    queryset = User.objects.all()
    serializer_class = UserSerializer

# عرض تفاصيل مستخدم واحد
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

from .forms import RegistrationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            # استخدام قيمة next لو موجودة
            next_url = request.POST.get('next') or 'index'  # 'index' الصفحة الافتراضية بعد login
            return redirect(next_url)
        else:
            messages.error(request, "Invalid email or password")

    # تمرير قيمة next للـ template لو موجودة في GET
    next_url = request.GET.get('next', '')
    return render(request, 'accounts/login.html', {'next': next_url})


from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import RegistrationForm

User = get_user_model()

def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
        else:
            return render(request, "accounts/register.html", {"form": form})

    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})
