from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import CustomerProfile, SellerProfile

def login_view(request):
    """Страница входа"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
            return redirect('login')
    
    return render(request, 'login.html')

def register_view(request):
    """Страница регистрации"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role', 'customer')
        
        # Проверка на пустые поля
        if not username or not email or not password1 or not password2:
            messages.error(request, 'Все поля обязательны для заполнения')
            return redirect('register')
        
        # Проверка пароля
        if password1 != password2:
            messages.error(request, 'Пароли не совпадают')
            return redirect('register')
        
        # Проверка длины пароля
        if len(password1) < 6:
            messages.error(request, 'Пароль должен содержать не менее 6 символов')
            return redirect('register')
        
        # Проверка существования пользователя
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
            return redirect('register')
        
        # Создание пользователя
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        
        # Создание профиля в зависимости от роли
        if role == 'seller':
            SellerProfile.objects.create(user=user)
            messages.success(request, 'Регистрация прошла успешно! Вы зарегистрированы как продавец.')
        else:
            CustomerProfile.objects.create(user=user)
            messages.success(request, 'Регистрация прошла успешно! Вы зарегистрированы как покупатель.')
        
        # Автоматический вход после регистрации
        login(request, user)
        return redirect('home')
    
    return render(request, 'register.html')

def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('home')

@login_required
def profile_view(request):
    """Личный кабинет пользователя"""
    user = request.user
    
    # Определяем роль пользователя
    is_seller = hasattr(user, 'seller_profile')
    is_customer = hasattr(user, 'customer_profile')
    
    context = {
        'user': user,
        'is_seller': is_seller,
        'is_customer': is_customer,
    }
    return render(request, 'profile.html', context)