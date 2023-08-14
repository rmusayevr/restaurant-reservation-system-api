from rest_framework import serializers, fields
from restaurant.models import (
    Map,
    Tag,
    User,
    Image,
    Table,
    Cuisine,
    Restaurant,
    Reservation,
    WorkingTime,
    MenuCategory,
    RestaurantType,
    OnlineReservTime,
    MenuCategoryProduct,
    RestaurantCondition,
    Wishlist,
    payment_choices,
    parking_choices,
)

from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.template.loader import render_to_string
from django.core.mail import send_mail
from reservation_system.settings import EMAIL_HOST_USER
from django.contrib.auth.hashers import check_password


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


class UserUpdateSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(write_only=True, required=False)
    old_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email',
                  'phone_number', 'new_password', 'old_password']

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get(
            'phone_number', instance.phone_number)

        old_password = validated_data.get('old_password')
        if old_password:
            new_password = validated_data.pop('new_password')
            if not check_password(old_password, instance.password):
                raise serializers.ValidationError(
                    "The old password provided is incorrect.")
            elif old_password == new_password:
                raise serializers.ValidationError(
                    "The new password cannot be the same as the old password.")
            else:
                instance.set_password(new_password)

        return super().update(instance, validated_data)


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
            restaurant_name=validated_data['restaurant_name'].lower()
        )
        if validated_data['location'] != "" and validated_data['restaurant_name'] != "":
            client = Restaurant(
                name=validated_data['restaurant_name'].lower(),
                location=validated_data['location'],
                user_id=user,
            )
            email = client.user_id.email
            last_name = client.user_id.last_name
            first_name = client.user_id.first_name
            client.save()
            id = Restaurant.objects.get(user_id=client.user_id).pk
            message = render_to_string('confirm-restaurant.html', {
                'id': id,
                'last_name': last_name,
                'first_name': first_name
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


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ['id', 'image', 'restaurant']


class RestaurantConditionSerializer(serializers.ModelSerializer):

    class Meta:
        model = RestaurantCondition
        fields = ['id', 'condition', 'restaurant']


class WorkingHoursSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkingTime
        fields = ['id', 'day', 'open_at', 'close_at']


class OnlineReservHoursSerializer(serializers.ModelSerializer):

    class Meta:
        model = OnlineReservTime
        fields = ['id', 'day', 'open_at', 'close_at']


class RestaurantTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = RestaurantType
        fields = ['id', 'type']


class CuisineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cuisine
        fields = ['id', 'name']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name']


class RestaurantListSerializer(serializers.ModelSerializer):
    tag = TagSerializer(many=True)
    type = RestaurantTypeSerializer(many=True)
    images = ImageSerializer(many=True, read_only=True,
                             source='restaurant_images')
    working_hours = WorkingHoursSerializer(
        many=True, read_only=True, source='restaurant_working_times')
    online_reserv_hours = OnlineReservHoursSerializer(
        many=True, read_only=True, source='restaurant_online_reserv_times')
    user_id = UserListSerializer()

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'city', 'images', 'rate', 'working_hours',
                  'online_reserv_hours', 'user_id', 'is_verified', 'slug',
                  'tag', 'type']


class RestaurantConfirmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Restaurant
        fields = ['id', 'is_verified']


class RestaurantCompleteRegistrationSerializer(serializers.ModelSerializer):
    payment = fields.MultipleChoiceField(choices=payment_choices)
    parking = fields.MultipleChoiceField(choices=parking_choices)
    working_hours = WorkingHoursSerializer(
        many=True, read_only=True, source='restaurant_working_times')
    working_hours_data = serializers.ListField(write_only=True, required=False)
    online_reserv_hours = OnlineReservHoursSerializer(
        many=True, read_only=True, source='restaurant_online_reserv_times')
    online_reserv_hours_data = serializers.ListField(
        write_only=True, required=False)

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'location', 'city', 'table_count', 'people_count', 'working_hours', 'minimum_price', 'websiteLink', 'instagramLink', 'facebookLink',
                  'maximum_price', 'service_charge', 'working_hours_data', 'online_reserv_hours', 'online_reserv_hours_data', 'description', 'minimum_age',
                  'subscription', 'phone', 'googleMapLink', 'is_allowed', 'tag', 'type', 'cuisine', 'payment', 'parking', 'notes']


class RestaurantDetailSerializer(serializers.ModelSerializer):
    tag = TagSerializer(many=True)
    type = RestaurantTypeSerializer(many=True)
    cuisine = CuisineSerializer(many=True)
    images = ImageSerializer(many=True, read_only=True,
                             source='restaurant_images')
    conditions = RestaurantConditionSerializer(
        many=True, read_only=True, source='restaurant_conditions')
    payment = fields.MultipleChoiceField(choices=payment_choices)
    parking = fields.MultipleChoiceField(choices=parking_choices)
    working_hours = WorkingHoursSerializer(
        many=True, read_only=True, source='restaurant_working_times')
    online_reserv_hours = OnlineReservHoursSerializer(
        many=True, read_only=True, source='restaurant_online_reserv_times')

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'location', 'city', 'rate', 'images', 'phone', 'minimum_price', 'maximum_price',
                  'service_charge', 'description', 'working_hours', 'online_reserv_hours', 'googleMapLink',
                  'is_allowed', 'tag', 'type', 'cuisine', 'payment', 'parking', 'conditions',
                  'instagramLink', 'facebookLink', 'websiteLink', 'minimum_age', 'notes', 'slug']


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
        fields = ['id', 'restaurant_id', 'table_id', 'user_id', 'date', 'comment',
                  'is_active',  'email', 'first_name', 'last_name', 'phone_number', 'people_count']


class ReservationCreateSerializer(serializers.ModelSerializer):

    table_id = serializers.PrimaryKeyRelatedField(
        queryset=Table.objects.all()
    )

    class Meta:
        model = Reservation
        fields = ['id', 'table_id', 'user_id', 'date', 'restaurant_id', 'comment',
                  'email', 'first_name', 'last_name', 'phone_number', 'people_count']

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


class MenuCategoryProductListSerializer(serializers.ModelSerializer):

    class Meta:
        model = MenuCategoryProduct
        fields = ['id', 'name', 'price', 'image', 'content']


class MenuCategoryListCreateSerializer(serializers.ModelSerializer):
    products = MenuCategoryProductListSerializer(
        many=True, read_only=True, source='menu_category_products')

    class Meta:
        model = MenuCategory
        fields = ['id', 'category', 'restaurant', 'products']


class WishlistSerializer(serializers.ModelSerializer):
    restaurants = RestaurantListSerializer(many=True)

    class Meta:
        model = Wishlist
        fields = [
            'user',
            'restaurants'
        ]

