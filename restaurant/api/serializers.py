from rest_framework import serializers
from restaurant.models import Category, Image, Restaurant, Table, Reservation, User, Map, WorkingTime
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail
from reservation_system.settings import EMAIL_HOST_USER


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    msg = (
                        'İstifadəçi aktivləşdirilməmişdir! Zəhmət olmasa, email ünvanınıza daxil olun və aktiv edin!')
                    raise serializers.ValidationError(msg)
            else:
                msg = ('Email ünvanı və şifrə düzgün deyil. Yenidən cəhd edin!')
                raise serializers.ValidationError(msg)
        elif email:
            msg = ('Zəhmət olmasa şifrəni daxil edin!')
            raise serializers.ValidationError(msg)
        else:
            msg = ('Zəhmət olmasa email ünvanını daxil edin!')
            raise serializers.ValidationError(msg)
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "phone_number"]


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('password', 'password2', 'location', 'restaurant_name',
                  'email', 'first_name', 'last_name', 'phone_number')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.pop('password2')
        if password != password2:
            raise serializers.ValidationError(
                "Təsdiq şifrəsi şifrə ilə eyni olmalıdır. Zəhmət olmasa, yenidən cəhd edin!")
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number'],
            location=validated_data['location'],
            restaurant_name=validated_data['restaurant_name']
        )
        if validated_data['location'] != "" and validated_data['restaurant_name'] != "":
            client = Restaurant(
                name=validated_data['restaurant_name'],
                location=validated_data['location'],
                user_id=user,
            )
            email = client.user_id.email
            client.save()
            id = Restaurant.objects.get(user_id=client.user_id).pk
            current_site = get_current_site(self.context['request'])
            message = render_to_string('confirm-restaurant.html', {
                'domain': current_site.domain,
                'id': id,
            })
            subject = 'Restoranınızın Qeydiyyatı Təsdiqləndi!'
            from_email = EMAIL_HOST_USER
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[email, ]
            )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email',
                  'phone_number', 'location', 'restaurant_name', 'is_client']


class UserDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email',
                  'phone_number', 'location', 'restaurant_name', 'is_client']


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name']


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ['id', 'image', 'restaurant']


class WorkingHoursSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkingTime
        fields = ['id', 'day', 'open_at', 'close_at']


class RestaurantListSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True, source='restaurant_images')
    working_hours = WorkingHoursSerializer(
        many=True, read_only=True, source='restaurant_working_times')
    user_id = UserListSerializer()

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'location', 'images',
                  'rate', 'working_hours', 'user_id']


class RestaurantConfirmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Restaurant
        fields = ['id', 'is_verified']


class RestaurantCompleteRegistrationSerializer(serializers.ModelSerializer):
    working_hours = WorkingHoursSerializer(
        many=True, read_only=True, source='restaurant_working_times')
    working_hours_data = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Restaurant
        fields = ['id', 'table_count', 'category', 'people_count',
                  'working_hours', 'working_hours_data', 'description', 'subscription',  'phone', 'googleMapLink']

class RestaurantDetailSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True, source='restaurant_images')
    category = CategorySerializer()
    working_hours = WorkingHoursSerializer(
        many=True, read_only=True, source='restaurant_working_times')

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'location', 'rate', 'category', 'images',
                  'phone', 'description', 'working_hours', 'googleMapLink']


class TableListCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Table
        fields = ['id', 'name', 'type', 'count', 'size', 'rotate',
                  'xcod', 'ycod', 'restaurant_id']


class TableUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Table
        fields = ['id', 'name', 'size', 'rotate', 'xcod', 'ycod']


class MapListSerializer(serializers.ModelSerializer):
    table = TableListCreateSerializer(many=True)
    restaurant = RestaurantDetailSerializer()

    class Meta:
        model = Map
        fields = ['id', 'wall', 'table', 'restaurant']


class MapCreateUpdateSerializer(serializers.ModelSerializer):
    wall = serializers.FileField(write_only=True, use_url=True)

    class Meta:
        model = Map
        fields = ['id', 'wall']


class ReservationListSerializer(serializers.ModelSerializer):
    restaurant_id = RestaurantDetailSerializer()
    table_id = TableListCreateSerializer()
    user_id = UserListSerializer()
    date = serializers.DateTimeField(format="%d/%m/%Y %H:%M")

    class Meta:
        model = Reservation
        fields = ['id', 'restaurant_id', 'table_id', 'user_id', 'date',
                  'is_active',  'email', 'first_name', 'last_name', 'phone_number']


class ReservationCreateSerializer(serializers.ModelSerializer):

    table_id = serializers.PrimaryKeyRelatedField(
        queryset=Table.objects.all()
    )

    class Meta:
        model = Reservation
        fields = ['id', 'table_id', 'user_id', 'date', 'restaurant_id',
                  'email', 'first_name', 'last_name', 'phone_number']

    def __init__(self, *args, **kwargs):
        restaurant_id = kwargs['context'].get('restaurant_id')
        super().__init__(*args, **kwargs)
        if restaurant_id:
            self.fields['table_id'].queryset = Table.objects.filter(
                restaurant_id=restaurant_id)


class ReservationUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reservation
        fields = ['id', 'restaurant_id']
