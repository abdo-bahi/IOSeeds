from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """
        Return True if the user has a permission.
        """
        return self.is_staff

    def has_module_perms(self, app_label):
        """
        Return True if the user has any permissions for the given app label.
        """
        return self.is_staff

class MCU(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Foreign key to User model
    waterPumpVal = models.BooleanField(default=False)
    # changes
    name = models.CharField(max_length=255,default='esp',null=True)
    threshold = models.IntegerField(default=30,null=True)
    irrigationTime = models.IntegerField(default=5,null=True) 
    sleepingTime = models.IntegerField(default=10,null=True)

    def __str__(self):
        return f"Water Pump State for User {self.user.email}: {self.name}"    
    
class SensorData(models.Model):
    
    # Foreign key to User model (who took has the access)
    mcuId = models.ForeignKey(MCU, on_delete=models.SET_NULL, null=True, default=None)
    soilMoisture = models.IntegerField()
    temperature = models.IntegerField()
    humidity = models.IntegerField()
    dateTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" (soilMoisture: {self.soilMoisture}, temperature: {self.temperature}, humidity: {self.humidity} at {self.dateTime})"

class Action(models.Model):
    sensorData = models.ForeignKey(SensorData, on_delete=models.CASCADE)
    waterPumpVal = models.BooleanField()


    def __str__(self):
        return f"water pump ({self.waterPumpVal}) for sensor data (soilMoisture: {self.sensorData.soilMoisture}, temperature: {self.sensorData.temperature}, humidity: {self.sensorData.humidity} at {self.sensorData.dateTime})"
    
