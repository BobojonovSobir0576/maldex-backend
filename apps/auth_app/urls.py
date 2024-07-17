from django.urls import path

from apps.auth_app.api.views import auth


urlpatterns = [
    path('register/', auth.RegisterView.as_view()),
    path('login/', auth.LoginView.as_view()),
    path('profile/', auth.ProfileView.as_view()),
]
