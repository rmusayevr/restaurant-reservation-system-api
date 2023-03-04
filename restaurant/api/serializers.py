from rest_framework import serializers
from restaurant.models import Category, Image, Restaurant, Table, Reservation, User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    msg = ('User account is disabled.')
                    raise serializers.ValidationError(msg)
            else:
                msg = ('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = ('Must include "email" and "password".')
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
            'password': {'write_only': True}}

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.pop('password2')
        if password != password2:
            raise serializers.ValidationError(
                "Password and Confirm Password Does not match")
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
            user.is_client = True
            client = Restaurant(
                name = validated_data['restaurant_name'],
                location=validated_data['location'],
                user_id=user,
            )
            client.save()
        user.set_password(validated_data['password'])
        user.save()

        return user

class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'location', 'restaurant_name', 'is_client']

class UserDetailSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'location', 'restaurant_name', 'is_client']

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name']

class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ['id', 'image']

class RestaurantListSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'location', 'images', 'rate']

class RestaurantConfirmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Restaurant
        fields = ['id', 'is_verified']

class RestaurantCompleteRegistrationSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'table_count', 'category', 'people_count', 'images', 'description', 'subscription']

class RestaurantDetailSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'location', 'rate', 'category', 'images', 'description']

class TableListCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Table
        fields = ['id', 'name', 'type', 'count',
                'xcod', 'ycod', 'restaurant_id']

class TableReservationSerializer(serializers.ModelSerializer):
    restaurant_id = RestaurantListSerializer()

    class Meta:
        model = Table
        fields = ['id', 'name', 'restaurant_id']

class ReservationListSerializer(serializers.ModelSerializer):
    restaurant_id = RestaurantDetailSerializer()
    table_id = TableListCreateSerializer()
    user_id = UserListSerializer()
    date = serializers.DateTimeField(format="%d/%m/%Y %H:%M")

    class Meta:
        model = Reservation
        fields = ['id', 'restaurant_id', 'table_id', 'user_id', 'date', 'is_active']

class ReservationCreateSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = Reservation
        fields = ['id', 'table_id', 'user_id', 'date', 'restaurant_id', 'email', 'first_name', 'last_name', 'phone_number']


class ReservationUpdateSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = Reservation
        fields = ['id', 'restaurant_id']
