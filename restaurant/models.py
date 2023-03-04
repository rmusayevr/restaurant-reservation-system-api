from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from .managers import UserManager
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from reservation_system.settings import EMAIL_HOST_USER

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    phone_number = models.CharField(_('phone number'), max_length=30, blank=True)
    restaurant_name = models.CharField(_('restaurant name'), max_length=100, blank=True)
    location = models.TextField(_('location'), blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=True) 
    is_client = models.BooleanField(_('client'), default=False) 

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs) 
    
    def __str__(self):
        return self.first_name 

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'), reset_password_token.key)

    send_mail(
        # title:
        "Password Reset for {title}".format(title="ResooTime"),
        # message:
        email_plaintext_message,
        # from:
        EMAIL_HOST_USER,
        # to:
        [reset_password_token.user.email]
    )

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

class Image(models.Model):
    image = models.ImageField(upload_to="restaurant_images")

    def __str__(self):
        return f'{self.pk}'

    class Meta:
        verbose_name = "Restaurant Image"
        verbose_name_plural = "Restaurant Images"

class Restaurant(models.Model):
    rates = {
        (1, "20"),
        (2, "40"),
        (3, "60"),
        (4, "80"),
        (5, "100")
    }

    name = models.CharField(max_length=150)
    location = models.TextField()
    table_count = models.PositiveIntegerField(null=True, blank=True)
    rate = models.IntegerField(choices=rates, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="restaurant_category", null=True, blank=True)
    people_count = models.PositiveIntegerField(null=True, blank=True)
    images = models.ManyToManyField(Image, related_name='restaurant_images')
    description = models.TextField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    subscription = models.CharField(max_length=30, null=True, blank=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_restaurant", blank=True, null=True)
    wall = models.ImageField(upload_to='Wall Images', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Restaurant"
        verbose_name_plural = "Restaurants"

class Table(models.Model):
    types = {
        ('small', 'small'),
        ('medium', 'medium'),
        ('large', 'large')
    }

    name = models.CharField(max_length=50)
    type = models.CharField(max_length=6, choices=types)
    count = models.PositiveIntegerField()
    xcod = models.IntegerField()
    ycod = models.IntegerField()
    restaurant_id = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='restaurant_table')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Table"
        verbose_name_plural = "Tables"

class Reservation(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_reservation", null=True, blank=True)
    email = models.EmailField(_('email address'), blank=True, null=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True, null=True)
    phone_number = models.CharField(_('phone number'), max_length=30, blank=True, null=True)
    restaurant_id = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True, related_name="reserved_restaurant")
    date = models.DateTimeField()
    table_id = models.ForeignKey(Table, on_delete=models.CASCADE, related_name="reserved_table")
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user_id}'s {self.date} reservation"

    class Meta:
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"
        