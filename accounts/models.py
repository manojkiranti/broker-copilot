import uuid
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils.translation import gettext_lazy as _

class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.
        """
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    class OauthType(models.IntegerChoices):
        DEFAULT = 0, _('Default')
        FACEBOOK = 1, _('Facebook')
        MICROSOFT = 2, _('Microsoft')
        GOOGLE = 3, _('Google')

    GENDER_TYPE = (
        ('male', 'male'),
        ('female', 'female'),
        ('other', 'other')
    )
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(max_length=255, null=True, unique=True)
    fullname = models.CharField(max_length=255)
    email = models.EmailField(
        max_length=255,
        verbose_name='email address',
        unique=True
    )
    password = models.CharField(_("password"), max_length=128, null=True, blank=True)
    oauth_type = models.IntegerField(
        choices=OauthType.choices,
        default=OauthType.DEFAULT,
        blank=True
    )
    oauth_id=models.CharField(max_length=255, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = [
            '-created_at'
        ]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def set_unusable_password(self):
        """
        Sets a value that will never be a valid hash
        """
        self.password = None
