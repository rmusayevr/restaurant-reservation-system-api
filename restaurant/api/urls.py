from django.urls import path
from knox import views as KnoxViews
from .views import (
    RestaurantListAPI,
    RestaurantConfirmAPI,
    RestaurantDetailAPI,
    RestaurantCompleteAPI,
    TableCreateAPI,
    MapListAPI,
    ReservationCreateAPI,
    ReservationListAPI,
    LoginAPI,
    RegisterAPIView,
    UserListAPIView,
    UserDetailAPIView,
    ReservationUpdateAPI,
    UserTokenDetailAPIView,
    RestaurantTokenDetailAPIView,
    ReservationUserListAPI,
    TableUpdateAPI,
    MapCreateAPI,
    MapUpdateAPI,
    TableDeleteAPI,
    RestaurantImagesAPI,
)

urlpatterns = [
    # for creating, logging in, logging out user and getting user informations
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('logout/', KnoxViews.LogoutView.as_view(), name='logout'),
    path('logoutall/', KnoxViews.LogoutAllView.as_view(), name='logoutall'),
    path('users/', UserListAPIView.as_view(), name='users'),
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='pk_user'),
    path('users/<str:token>/', UserTokenDetailAPIView.as_view(), name='token_user'),

    # for getting restaurant(s), confirm and complete them
    path('restaurant/', RestaurantListAPI.as_view(), name="restaurants"),
    path('restaurant/<int:pk>/', RestaurantDetailAPI.as_view(), name='restaurant'),
    path('restaurant/<str:token>/',
         RestaurantTokenDetailAPIView.as_view(), name='token_restaurant'),
    path('confirm/<int:pk>/', RestaurantConfirmAPI.as_view(),
         name='confirm-restaurant'),
    path('complete-registration/<int:pk>/', RestaurantCompleteAPI.as_view(),
         name='complete-restaurant-registration'),

    # get and create maps and delete tables
    path('restaurant/<int:pk>/map/',
         MapListAPI.as_view(), name="list-map"),
    path('restaurant/<int:pk>/create-map/',
         MapCreateAPI.as_view(), name='create-map'),
    path('restaurant/<int:pk>/update-map/',
         MapUpdateAPI.as_view(), name='update-map'),
    path('restaurant/<int:pk>/create-image/',
         RestaurantImagesAPI.as_view(), name='create-image'),
    path('restaurant/<int:pk>/create-table/',
         TableCreateAPI.as_view(), name='create-table'),
    path('restaurant/<int:pk>/update-table/<int:id>/',
         TableUpdateAPI.as_view(), name='update-table'),
    path('restaurant/<int:pk>/delete-table/<int:id>/',
         TableDeleteAPI.as_view(), name='delete-table'),

    # for reservation processes
    path('restaurant/<int:pk>/reservations/',
         ReservationListAPI.as_view(), name='reserved_restaurants'),
    path('restaurant/<int:pk>/make-reservation/', ReservationCreateAPI.as_view(),
         name="make-reservation"),
    path('users/<int:pk>/my-reservations/',
         ReservationUserListAPI.as_view(), name='user_reservations'),
    path('cancel/<int:pk>/', ReservationUpdateAPI.as_view(),
         name="cancel-update-reservation"),
]
