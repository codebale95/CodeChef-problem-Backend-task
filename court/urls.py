from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('auth/signup/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('case/submit/', views.submit_case, name='submit_case'),
    path('case/all/', views.get_all_cases, name='get_all_cases'),
    path('case/edit/<int:pk>/', views.edit_case, name='edit_case'),
    path('case/delete/<int:pk>/', views.delete_case, name='delete_case'),
    path('case/vote/<int:pk>/', views.vote_case, name='vote_case'),
    # Frontend views
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('switch-role/', views.switch_role_view, name='switch_role'),
    path('edit-case/<int:pk>/', views.edit_case_view, name='edit_case_view'),
]
