from datetime import datetime
from rest_framework.generics import (
    ListAPIView, 
    ListCreateAPIView, 
    CreateAPIView, 
    UpdateAPIView, 
    )
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from restaurant.models import Restaurant, Table, Reservation
from .serializers import (
    RestaurantListSerializer,
    RestaurantDetailSerializer,
    RestaurantCompleteRegistrationSerializer,
    RestaurantConfirmSerializer,
    TableListCreateSerializer,
    ReservationCreateSerializer,
    ReservationUpdateSerializer,
    ReservationListSerializer,
    AuthTokenSerializer, 
    UserSerializer, 
    RegisterSerializer,
    UserListSerializer,
    UserDetailSerializer,
)
from django.contrib.auth import login
from knox.views import LoginView
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from knox.models import AuthToken
from knox.settings import CONSTANTS
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail
from reservation_system.settings import EMAIL_HOST_USER


class RegisterAPIView(CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1],
        })

class LoginAPI(LoginView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)

class UserListAPIView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer

class UserDetailAPIView(APIView):

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)

class UserTokenDetailAPIView(APIView):

    def get_object(self, token):
        try:
            return User.objects.get(pk=token)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, token, format=None):
        knox_object = AuthToken.objects.filter(token_key=token[:CONSTANTS.TOKEN_KEY_LENGTH]).first()
        user = self.get_object(knox_object.user.pk)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)

class RestaurantListAPI(ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantListSerializer

class RestaurantDetailAPI(APIView):

    def get_object(self, pk):
        try:
            return Restaurant.objects.get(pk=pk)
        except Restaurant.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        restaurant = self.get_object(pk)
        serializer = RestaurantDetailSerializer(restaurant)
        return Response(serializer.data)

class RestaurantTokenDetailAPIView(APIView):

    def get_object(self, token):
        try:
            return Restaurant.objects.get(user_id__pk=token)
        except Restaurant.DoesNotExist:
            raise Http404

    def get(self, request, token, format=None):
        knox_object = AuthToken.objects.filter(token_key=token[:CONSTANTS.TOKEN_KEY_LENGTH]).first()
        user = self.get_object(knox_object.user.pk)
        serializer = RestaurantDetailSerializer(user)
        return Response(serializer.data)

class RestaurantConfirmAPI(UpdateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantConfirmSerializer
    http_method_names = ['patch']

    def patch(self, request, *args, **kwargs):
        restaurant = Restaurant.objects.get(id=kwargs['pk'])
        restaurant.is_verified = True
        restaurant.save()
        current_site = get_current_site(self.request)
        if restaurant.is_verified:
            message = render_to_string('complete-registration.html', {
                'domain': current_site.domain,
                'restaurant_id': kwargs['pk']
            })
            subject = 'Complete Your Registration.'
            from_email = EMAIL_HOST_USER
            to_email = restaurant.user_id.email
            send_mail(
                subject = subject,
                message = message,
                from_email = from_email,
                recipient_list = [to_email, ]
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

class RestaurantCompleteAPI(UpdateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantCompleteRegistrationSerializer

class TableCreateAPI(CreateAPIView):
    queryset = Table.objects.all()
    serializer_class = TableListCreateSerializer

class TableListAPI(ListAPIView):
    serializer_class = TableListCreateSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Table.objects.filter(restaurant_id=pk).all()

class ReservationCreateAPI(ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationCreateSerializer

    def create(self, request, *args, **kwargs):
        # Get the `restaurant_id` from the URL path
        restaurant_id = self.kwargs.get('pk')
        # Create a mutable copy of the request data
        mutable_data = request.data.copy()
        # Add the `restaurant_id` to the mutable data
        mutable_data['restaurant_id'] = restaurant_id
        user_id = mutable_data.get('user_id')
        restaurant = Restaurant.objects.get(pk=restaurant_id)
        current_site = get_current_site(self.request)
        if mutable_data['user_id']:
            user = User.objects.get(pk=user_id)
            first_name = user.first_name
            last_name = user.last_name
        else:       
            first_name = mutable_data['first_name']
            last_name = mutable_data['last_name']

        restaurant = restaurant.name
        date_query = mutable_data['date']
        time = datetime.strptime(date_query, '%Y-%m-%dT%H:%M').strftime('%H:%M')
        date = datetime.strptime(date_query, '%Y-%m-%dT%H:%M').strftime('%d/%m/%Y')

        message = render_to_string('make-reservation.html', {
            'domain': current_site.domain,
            'reservation': kwargs['pk'],
            'first_name': first_name,
            'last_name': last_name,
            'restaurant': restaurant,
            'time': time,
            'date': date

        })
        subject = 'Confirmation of Reservation!'
        from_email = EMAIL_HOST_USER
        if mutable_data['user_id']:
            to_email = user.email
        else:
            to_email = mutable_data['email']
        send_mail(
            subject = subject,
            message = message,
            from_email = from_email,
            recipient_list = [to_email, ]
        )
        # Deserialize the mutable data and create a new reservation
        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return the response
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ReservationListAPI(ListAPIView):
    serializer_class = ReservationListSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        # Get the reservations for the restaurant
        queryset = Reservation.objects.filter(restaurant_id=pk)
        # Get the date query parameter from the URL
        date_str = self.request.query_params.get('date')
        if date_str:
            # Convert the date string to a datetime object
            date = datetime.strptime(date_str, '%d/%m/%Y')
            # Filter the queryset by the formatted date string
            queryset = queryset.filter(date__date=date, is_active=True)
        return queryset
    
class ReservationUpdateAPI(UpdateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationUpdateSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Reservation.objects.filter(pk=pk)

    def patch(self, request, *args, **kwargs):
        reservation = Reservation.objects.get(id=kwargs['pk'])
        reservation.is_active = False
        reservation.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReservationUserListAPI(ListAPIView):
    serializer_class = ReservationListSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Reservation.objects.filter(user_id=pk).all()

