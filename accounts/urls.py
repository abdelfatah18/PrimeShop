from django.urls import path
from .views import UserListView, UserDetailView, login_view, register_view
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
urlpatterns = [
    # تسجيل الدخول والخروج
    path('login/', login_view, name='login'),
    path("logout/", auth_views.LogoutView.as_view(next_page='login'), name="logout"),

    # تسجيل مستخدم جديد
    path('register/', register_view, name='register'),

    # عرض قائمة المستخدمين وتفاصيل المستخدم
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),

    # تغيير كلمة المرور

path('password-reset/', auth_views.PasswordResetView.as_view(
    template_name='accounts/password_reset.html',
    email_template_name='accounts/password_reset_email.html',
    success_url=reverse_lazy('password_reset_done')
), name='password_reset'),

path('password-reset-done/', auth_views.PasswordResetDoneView.as_view(
    template_name='accounts/password_reset_done.html'
), name='password_reset_done'),
    # إعادة تعيين كلمة المرور
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        success_url='/password-reset-done/'
    ), name='password_reset'),
    
    path('accounts/password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    
    
path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
    template_name='accounts/password_reset_confirm.html',
    success_url=reverse_lazy('password_reset_complete')
), name='password_reset_confirm'),

path('reset-done/', auth_views.PasswordResetCompleteView.as_view(
    template_name='accounts/password_reset_complete.html'
), name='password_reset_complete'),
]
