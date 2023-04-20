from datetime import datetime
from rest_framework.generics import (
    ListAPIView, 
    ListCreateAPIView, 
    CreateAPIView, 
    UpdateAPIView, 
    DestroyAPIView,
    )
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from restaurant.models import Restaurant, Table, Reservation, Map, WorkingTime
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
    MapListSerializer,
    TableUpdateSerializer,
    MapCreateUpdateSerializer,
    ImageSerializer
)
from django.contrib.auth import login
from knox.views import LoginView
from rest_framework.permissions import AllowAny
from knox.models import AuthToken
from knox.settings import CONSTANTS
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail
from reservation_system.settings import EMAIL_HOST_USER
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

# register, login, list of users, detail of user
class RegisterAPIView(CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        context={'request': request}
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1],
        })
    

class LoginAPI(LoginView):
    serializer_class = AuthTokenSerializer
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

# list or detail of restaurant, confirm and complete restaurant
class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'

class RestaurantListAPI(ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantListSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Restaurant.objects.filter(user_id__is_client=True)

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
        return Response(status=status.HTTP_204_NO_CONTENT)

class RestaurantCompleteAPI(UpdateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantCompleteRegistrationSerializer
    http_method_names = ['put']

    def get_object(self):
        pk = self.kwargs['pk']
        return Restaurant.objects.get(pk=pk)

    @csrf_exempt
    def put(self, request, *args, **kwargs):
        data = request.data
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data)
        if serializer.is_valid():
            instance.restaurant_working_times.all().delete()
            for working_hour in data['working_hours_data']:
                working_hour_obj = WorkingTime.objects.create(restaurant=instance, day=working_hour['day'], open_at=working_hour['open_at'], close_at=working_hour['close_at'])
                instance.restaurant_working_times.add(working_hour_obj)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RestaurantImagesAPI(CreateAPIView):
    serializer_class = ImageSerializer

    def perform_create(self, serializer):
        restaurant_id = self.kwargs.get('pk')
        restaurant = Restaurant.objects.get(pk=restaurant_id)
        serializer.save(restaurant=restaurant)
        
# create, update and get tables and maps
class TableCreateAPI(CreateAPIView):
    queryset = Table.objects.all()
    serializer_class = TableListCreateSerializer

    def post(self, request, *args, **kwargs):
        restaurant_id = self.kwargs.get('pk')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        table = serializer.save()

        map_id = Map.objects.get(restaurant=restaurant_id).id
        map_instance = get_object_or_404(Map, id=map_id)
        map_instance.table.add(table)
        map_instance.save()

        return Response(serializer.data)

class TableUpdateAPI(UpdateAPIView):
    queryset = Table.objects.all()
    serializer_class = TableUpdateSerializer
    lookup_field = 'id'
    http_method_names = ['patch']
   
    def get_queryset(self):
        pk = self.kwargs['id']
        return Table.objects.filter(pk=pk)

class TableDeleteAPI(DestroyAPIView):
    queryset = Table.objects.all()
    serializer_class = TableListCreateSerializer
    lookup_field = 'id'
    http_method_names = ['delete']

    def get_queryset(self):
        pk = self.kwargs['id']
        return Table.objects.filter(pk=pk)

class MapListAPI(ListAPIView):
    serializer_class = MapListSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Map.objects.filter(restaurant=pk).all()

class MapCreateAPI(CreateAPIView):
    serializer_class = MapCreateUpdateSerializer

    def perform_create(self, serializer):
        restaurant_id = self.kwargs.get('pk')
        restaurant = Restaurant.objects.get(pk=restaurant_id)
        tables = Table.objects.filter(restaurant_id=restaurant_id).all()
        arr = []
        for table in tables:
            arr.append(table)
        serializer.save(table=arr,restaurant=restaurant)
    
class MapUpdateAPI(UpdateAPIView):
    serializer_class = MapCreateUpdateSerializer
    http_method_names = ['put']

    def put(self, request, *args, **kwargs):
        pk = kwargs['pk']
        try:
            instance = Map.objects.get(restaurant=pk)
        except Map.DoesNotExist:
            raise Http404("Map does not exist")
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

# create, get, update reservation and get for users
class ReservationCreateAPI(ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['restaurant_id'] = self.kwargs['pk']
        return context
    
    def create(self, request, *args, **kwargs):
        restaurant_id = self.kwargs.get('pk')
        mutable_data = request.data.copy()
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
        table_id = mutable_data['table_id']
        table = Table.objects.get(id=table_id)

        message = render_to_string('make-reservation.html', {
            'domain': current_site.domain,
            'reservation': kwargs['pk'],
            'first_name': first_name,
            'last_name': last_name,
            'restaurant': restaurant,
            'time': time,
            'date': date,
            'table': table
        })
        subject = 'Rezervasiyanız təsdiqləndi!'
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
        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ReservationListAPI(ListAPIView):
    serializer_class = ReservationListSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        queryset = Reservation.objects.filter(restaurant_id=pk)
        date_str = self.request.query_params.get('date')
        if date_str:
            date = datetime.strptime(date_str, '%d/%m/%Y')
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

