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
from restaurant.models import (
    Restaurant,
    Table,
    Reservation,
    Map,
    WorkingTime,
    Image,
    User,
    OnlineReservTime,
    RestaurantCondition,
    MenuCategory,
    MenuCategoryProduct,
    Wishlist
)
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
    ImageSerializer,
    RestaurantConditionSerializer,
    MenuCategoryListCreateSerializer,
    UserUpdateSerializer,
    WishlistSerializer
)
from django.contrib.auth import login
from knox.views import LoginView
from rest_framework.permissions import AllowAny
from django.template.loader import render_to_string
from django.core.mail import send_mail
from reservation_system.settings import EMAIL_HOST_USER
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


# authentication
class RestaurantUserTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        user_auth_tuple = super().authenticate(request)
        if user_auth_tuple is None:
            return None

        user, auth = user_auth_tuple
        if 'restaurant' in request.get_full_path():
            try:
                Restaurant.objects.get(user_id=user)
            except Restaurant.DoesNotExist:
                raise AuthenticationFailed('User does not own a restaurant')

            pk = request.resolver_match.kwargs.get('pk')
            owner = Restaurant.objects.get(pk=pk).user_id
            owner_auth = Token.objects.get(user=owner)

            if owner_auth.key != auth.key:
                raise AuthenticationFailed('Token does not belong to owner')
        elif 'users' in request.get_full_path():
            try:
                User.objects.get(first_name=user)
            except User.DoesNotExist:
                raise AuthenticationFailed('User does not exist')

            pk = request.resolver_match.kwargs.get('pk')
            customer = User.objects.get(pk=pk)
            customer_auth = Token.objects.get(user=customer)

            if customer_auth.key != auth.key:
                raise AuthenticationFailed('Token does not belong to customer')

        return user, auth


# CRUD operations for user
class RegisterAPIView(CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        auth_token = Token.objects.create(user=user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": str(auth_token)
        })


class LoginAPI(LoginView):
    serializer_class = AuthTokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        auth_token = Token.objects.get(user=user)
        restaurant = Restaurant.objects.filter(user_id=user).first()
        if restaurant:
            return Response({
                "user": str(user),
                "token": str(auth_token),
                "restaurant": restaurant.name
            })
        return Response({
            "user": str(user),
            "token": str(auth_token)
        })


class UserUpdateAPIView(UpdateAPIView):
    serializer_class = UserUpdateSerializer
    authentication_classes = [RestaurantUserTokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['put']

    def get_queryset(self):
        pk = self.kwargs['pk']
        return User.objects.filter(pk=pk)


class UserListAPIView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer


class UserDetailAPIView(APIView):
    authentication_classes = [RestaurantUserTokenAuthentication]
    permission_classes = [IsAuthenticated]

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
        auth_token = Token.objects.get(key=token)
        user = self.get_object(auth_token.user.pk)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)


# CRUD operations for restaurant
class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'


class RestaurantListAPI(ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantListSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Restaurant.objects.filter(user_id__is_client=True, is_verified=True)


class RestaurantDetailNameAPI(APIView):

    def get_object(self, slug):
        try:
            return Restaurant.objects.get(slug=slug)
        except Restaurant.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        restaurant = self.get_object(slug)
        serializer = RestaurantDetailSerializer(restaurant)
        return Response(serializer.data)


class RestaurantDetailIDAPI(APIView):

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
    def get(self, request, token, format=None):
        try:
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            restaurant = Restaurant.objects.get(user_id=user)
            serializer = RestaurantDetailSerializer(restaurant)
            return Response(serializer.data)
        except Token.DoesNotExist:
            raise NotFound("Invalid token")
        except Restaurant.DoesNotExist:
            raise NotFound("Restaurant not found")


class RestaurantConfirmAPI(UpdateAPIView):
    queryset = Restaurant.objects.all()
    authentication_classes = [RestaurantUserTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = RestaurantConfirmSerializer
    http_method_names = ['patch']

    def patch(self, request, *args, **kwargs):
        restaurant = Restaurant.objects.get(id=kwargs['pk'])
        restaurant.is_verified = True
        restaurant.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RestaurantCompleteAPI(UpdateAPIView):
    authentication_classes = [RestaurantUserTokenAuthentication]
    permission_classes = [IsAuthenticated]
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
            instance.restaurant_online_reserv_times.all().delete()
            for working_hour in data['working_hours_data']:
                working_hour_obj = WorkingTime.objects.create(
                    restaurant=instance, day=working_hour['day'], open_at=working_hour['open_at'], close_at=working_hour['close_at'])
                instance.restaurant_working_times.add(working_hour_obj)
            for online_reserv_hours in data['online_reserv_hours_data']:
                online_reserv_hours_obj = OnlineReservTime.objects.create(
                    restaurant=instance, day=online_reserv_hours['day'], open_at=online_reserv_hours['open_at'], close_at=online_reserv_hours['close_at'])
                instance.restaurant_online_reserv_times.add(
                    online_reserv_hours_obj)
            user = instance.user_id
            user.is_client = True
            user.save()
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RestaurantImagesAPI(CreateAPIView):
    authentication_classes = [RestaurantUserTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ImageSerializer

    def perform_create(self, serializer):
        restaurant_id = self.kwargs.get('pk')
        restaurant = Restaurant.objects.get(pk=restaurant_id)
        serializer.save(restaurant=restaurant)
        return Response(serializer.data)


class RestaurantConditionsAPI(CreateAPIView):
    authentication_classes = [RestaurantUserTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = RestaurantConditionSerializer

    def perform_create(self, serializer):
        restaurant_id = self.kwargs.get('pk')
        restaurant = Restaurant.objects.get(pk=restaurant_id)
        serializer.save(restaurant=restaurant)
        return Response(serializer.data)


class RestaurantDeleteConditionsAPI(DestroyAPIView):
    queryset = RestaurantCondition.objects.all()
    authentication_classes = [RestaurantUserTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = RestaurantConditionSerializer
    http_method_names = ['delete']

    def get_object(self):
        pk = self.kwargs['pk']
        return RestaurantCondition.objects.filter(restaurant=pk).all()

    def perform_destroy(self, instance):
        instance = self.get_object()
        return super().perform_destroy(instance)


class RestaurantDeleteImagesAPI(DestroyAPIView):
    queryset = Image.objects.all()
    authentication_classes = [RestaurantUserTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ImageSerializer
    http_method_names = ['delete']

    def get_object(self):
        pk = self.kwargs['pk']
        return Image.objects.filter(restaurant=pk).all()

    def perform_destroy(self, instance):
        instance = self.get_object()
        return super().perform_destroy(instance)


# CRUD operations for table and map
class TableCreateAPI(CreateAPIView):
    queryset = Table.objects.all()
    authentication_classes = [RestaurantUserTokenAuthentication]
    permission_classes = [IsAuthenticated]
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
    authentication_classes = [RestaurantUserTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TableUpdateSerializer
    lookup_field = 'id'
    http_method_names = ['patch']

    def get_queryset(self):
        pk = self.kwargs['id']
        return Table.objects.filter(pk=pk)


class TableDeleteAPI(DestroyAPIView):
    queryset = Table.objects.all()
    authentication_classes = [RestaurantUserTokenAuthentication]
    permission_classes = [IsAuthenticated]
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
    authentication_classes = [RestaurantUserTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MapCreateUpdateSerializer

    def perform_create(self, serializer):
        restaurant_id = self.kwargs.get('pk')
        restaurant = Restaurant.objects.get(pk=restaurant_id)
        tables = Table.objects.filter(restaurant_id=restaurant_id).all()
        arr = []
        for table in tables:
            arr.append(table)
        serializer.save(table=arr, restaurant=restaurant)


class MapUpdateAPI(UpdateAPIView):
    authentication_classes = [RestaurantUserTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MapCreateUpdateSerializer
    http_method_names = ['put']

    def put(self, request, *args, **kwargs):
        pk = kwargs['pk']
        try:
            instance = Map.objects.get(restaurant=pk)
        except Map.DoesNotExist:
            raise Http404("Map does not exist")
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


# CRUD operations for reservation
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
        if mutable_data['user_id']:
            user = User.objects.get(pk=user_id)
            first_name = user.first_name
            last_name = user.last_name
        else:
            first_name = mutable_data['first_name']
            last_name = mutable_data['last_name']

        restaurant = restaurant.name
        date_query = mutable_data['date']
        time = datetime.strptime(
            date_query, '%Y-%m-%dT%H:%M').strftime('%H:%M')
        date = datetime.strptime(
            date_query, '%Y-%m-%dT%H:%M').strftime('%d/%m/%Y')
        table_id = mutable_data['table_id']
        table = Table.objects.get(id=table_id)

        message = render_to_string('make-reservation.html', {
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
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[to_email, ]
        )
        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'admin_panel_%s' % restaurant_id,
            {
                'type': 'send_reservation_notification',
                'reservation_id': kwargs['pk'],
                'message': message,
            }
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReservationListAPI(ListAPIView):
    serializer_class = ReservationListSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        queryset = Reservation.objects.filter(restaurant_id=pk, is_active=True)
        date_str = self.request.query_params.get('date')
        if date_str:
            date = datetime.strptime(date_str, '%d/%m/%Y')
            queryset = queryset.filter(date__date=date)
        return queryset.order_by('-date')

class AllReservationListAPI(ListAPIView):
    serializer_class = ReservationListSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        queryset = Reservation.objects.filter(restaurant_id=pk)
        date_str = self.request.query_params.get('date')
        if date_str:
            date = datetime.strptime(date_str, '%d/%m/%Y')
            queryset = queryset.filter(date__date=date)
        return queryset.order_by('-date')

class ReservationUpdateAPI(UpdateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationUpdateSerializer
    http_method_names = ['patch']

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Reservation.objects.filter(pk=pk)

    def patch(self, request, *args, **kwargs):
        reservation = Reservation.objects.get(id=kwargs['pk'])
        reservation.is_active = False
        reservation.save()
        first_name = reservation.user_id.first_name
        last_name = reservation.user_id.last_name
        to_email = reservation.user_id.email
        restaurant_name = reservation.restaurant_id.name
        date_query = reservation.date
        date = datetime.strptime(
            str(date_query), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
        message = render_to_string('cancel-reservation.html', {
            'first_name': first_name,
            'last_name': last_name,
            'restaurant': restaurant_name,
            'date': date
        })
        subject = 'Rezervasiyanız ləğv olundu!'
        from_email = EMAIL_HOST_USER
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[to_email, ]
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReservationUserListAPI(ListAPIView):
    authentication_classes = [RestaurantUserTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ReservationListSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Reservation.objects.filter(user_id=pk).all()


# CRUD operations for menu
class MenuCategoryListAPI(ListAPIView):
    serializer_class = MenuCategoryListCreateSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return MenuCategory.objects.filter(restaurant=pk).all()


class MenuCategoryCreateAPI(CreateAPIView):
    serializer_class = MenuCategoryListCreateSerializer
    queryset = MenuCategory.objects.all()
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        data = request.data
        restaurant_id = self.kwargs.get('pk')
        data['restaurant'] = restaurant_id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            menu_category = serializer.save()
            for product in data['products']:
                MenuCategoryProduct.objects.create(
                    category=menu_category, name=product['name'], price=product['price'], image=product['image'], content=product['content'])
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WishlistAPI(APIView):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    authentication_classes = [RestaurantUserTokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get(self, request, *args, **kwargs):
        obj, created = Wishlist.objects.get_or_create(user = request.user)
        serializer = self.serializer_class(obj)
        return Response(serializer.data, status = status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        restaurant_id = request.data.get('restaurant')
        restaurant = Restaurant.objects.filter(pk=restaurant_id).first()
        if restaurant and self.request.user.is_authenticated:
            wishlist1, created = Wishlist.objects.get_or_create(user = request.user)
            wishlist2 = Wishlist.objects.filter(user = request.user).first()
            wishlist2.restaurants.add(restaurant)
            message = {'success': True, 'message' : 'Restaurant added to your favourites!'}
            return Response(message, status = status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        restaurant_id = request.data.get('restaurant')
        if restaurant_id:
            user_wishlist = Wishlist.objects.get(user = self.request.user)
            restaurant = user_wishlist.restaurants.get(id = restaurant_id)
            user_wishlist.restaurants.remove(restaurant.id)
        message = {'success': True, 'message' : 'Product deleted from your wishlist.'}
        return Response(message, status = status.HTTP_200_OK)
    
    