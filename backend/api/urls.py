
from api import views as api_views     # this is just the same as saying views.MyToken----------
from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("user/token/", api_views.MyTokenObtainPairView.as_view()),
    path("user/token/refresh/", TokenRefreshView.as_view()),    # for classed based views, we have to pass the "as_view()" method on the end
    path("user/register/", api_views.RegisterView.as_view()),
    path("user/password-reset/<email>/", api_views.PasswordResetEmailVerifyAPIView.as_view()),
    path("user/password-change/", api_views.PasswordChangeAPIView.as_view())
]





