from django.urls import path
from knox import views as KnoxViews
from .views import (
    RestaurantListAPI,
    RestaurantConfirmAPI,
    RestaurantDetailNameAPI,
    RestaurantDetailIDAPI,
    RestaurantCompleteAPI,
    TableCreateAPI,
    MapListAPI,
    ReservationCreateAPI,
    ReservationListAPI,
    AllReservationListAPI,
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
    RestaurantDeleteImagesAPI,
    RestaurantConditionsAPI,
    RestaurantDeleteConditionsAPI,
    MenuCategoryListAPI,
    MenuCategoryCreateAPI,
    UserUpdateAPIView,
    WishlistAPI
)

urlpatterns = [
    # for creating, logging in, logging out user and getting user informations
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('users/', UserListAPIView.as_view(), name='users'),
    path('user/<int:pk>/update/', UserUpdateAPIView.as_view(), name='update_user'),
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='pk_user'),
    path('users/<str:token>/', UserTokenDetailAPIView.as_view(), name='token_user'),

    # for getting restaurant(s), confirm and complete them
    path('restaurant/', RestaurantListAPI.as_view(), name="restaurants"),
    path('restaurant/<int:pk>/', RestaurantDetailIDAPI.as_view(), name='restaurant'),
    path('restaurant/<slug:slug>/',
         RestaurantDetailNameAPI.as_view(), name='restaurant'),
    path('restaurant/token/<str:token>/',
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
    path('restaurant/<int:pk>/delete-images/',
         RestaurantDeleteImagesAPI.as_view(), name='delete-images'),
    path('restaurant/<int:pk>/add-condition/',
         RestaurantConditionsAPI.as_view(), name='add-condition'),
    path('restaurant/<int:pk>/delete-conditions/',
         RestaurantDeleteConditionsAPI.as_view(), name='delete-conditions'),
    path('restaurant/<int:pk>/create-table/',
         TableCreateAPI.as_view(), name='create-table'),
    path('restaurant/<int:pk>/update-table/<int:id>/',
         TableUpdateAPI.as_view(), name='update-table'),
    path('restaurant/<int:pk>/delete-table/<int:id>/',
         TableDeleteAPI.as_view(), name='delete-table'),

    # for reservation processes
    path('restaurant/<int:pk>/reservations/',
         ReservationListAPI.as_view(), name='reserved_restaurants'),
    path('restaurant/<int:pk>/all-reservations/',
         AllReservationListAPI.as_view(), name='all_reserved_restaurants'),
    path('restaurant/<int:pk>/make-reservation/', ReservationCreateAPI.as_view(),
         name="make-reservation"),
    path('users/<int:pk>/my-reservations/',
         ReservationUserListAPI.as_view(), name='user_reservations'),
    path('cancel/<int:pk>/', ReservationUpdateAPI.as_view(),
         name="cancel-update-reservation"),

    # for menu processes
    path('restaurant/<int:pk>/menu/',
         MenuCategoryListAPI.as_view(), name="list-menu"),
    path('restaurant/<int:pk>/create-menu/',
         MenuCategoryCreateAPI.as_view(), name='create-menu'),

    path('wishlist/', WishlistAPI.as_view(), name="wishlists"),

]
