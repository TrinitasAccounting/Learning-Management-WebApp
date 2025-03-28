
from api import views as api_views     # this is just the same as saying views.MyToken----------
from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    # Authentication Endpoints
    path("user/token/", api_views.MyTokenObtainPairView.as_view()),
    path("user/token/refresh/", TokenRefreshView.as_view()),    # for classed based views, we have to pass the "as_view()" method on the end
    path("user/register/", api_views.RegisterView.as_view()),
    path("user/password-reset/<email>/", api_views.PasswordResetEmailVerifyAPIView.as_view()),
    path("user/password-change/", api_views.PasswordChangeAPIView.as_view()),

    # Core Endpoints
    path('course/category/', api_views.CategoryListAPIView.as_view()),
    path('course/course-list/', api_views.CourseListAPIView.as_view()),
    path('course/course-detail/<slug>/',api_views.CourseDetailAPIView.as_view()),
    path("course/cart/", api_views.CartAPIView.as_view()),
    path("course/cart-list/<cart_id>/", api_views.CartListAPIView.as_view()),
    path("course/cart-item-delete/<cart_id>/<item_id>/", api_views.CartItemDeleteAPIView.as_view()),
    path("cart/stats/<cart_id>/", api_views.CartStatsAPIView.as_view()),
    


]





