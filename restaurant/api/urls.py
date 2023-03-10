from django.urls import path
from knox import views as KnoxViews
from .views import (
    RestaurantListAPI,
    RestaurantConfirmAPI,
    RestaurantDetailAPI,
    RestaurantCompleteAPI,
    TableCreateAPI,
    TableListAPI,
    ReservationCreateAPI,
    ReservationListAPI,
    LoginAPI,
    RegisterAPIView,
    UserListAPIView,
    UserDetailAPIView,
    ReservationUpdateAPI,
    UserTokenDetailAPIView,
    RestaurantTokenDetailAPIView,
    ReservationUserListAPI
)

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('logout/', KnoxViews.LogoutView.as_view(), name='logout'),
    path('logoutall/', KnoxViews.LogoutAllView.as_view(), name='logoutall'),
    path('users/', UserListAPIView.as_view(), name='users'),
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='pk_user'),
    path('users/<str:token>/', UserTokenDetailAPIView.as_view(), name='token_user'),
    path('restaurant/', RestaurantListAPI.as_view(), name="restaurants"),
    path('restaurant/<int:pk>/', RestaurantDetailAPI.as_view(), name='restaurant'),
    path('restaurant/<str:token>/',
         RestaurantTokenDetailAPIView.as_view(), name='token_restaurant'),
    path('confirm/<int:pk>/', RestaurantConfirmAPI.as_view(),
         name='confirm-restaurant'),
    path('complete-registration/<int:pk>/', RestaurantCompleteAPI.as_view(),
         name='complete-restaurant-registration'),
    path('restaurant/<int:pk>/create-table/',
         TableCreateAPI.as_view(), name='create-table'),
    path('restaurant/<int:pk>/tables/',
         TableListAPI.as_view(), name="list-table"),
    path('restaurant/<int:pk>/reservations/',
         ReservationListAPI.as_view(), name='reserved_restaurants'),
    path('restaurant/<int:pk>/make-reservation/', ReservationCreateAPI.as_view(),
         name="make-reservation"),
    path('users/<int:pk>/my-reservations/',
         ReservationUserListAPI.as_view(), name='user_reservations'),
    path('cancel/<int:pk>/', ReservationUpdateAPI.as_view(),
         name="cancel-reservation"),

]
