from rest_framework import serializers
from .models import User, SensorData, Action, MCU

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email','waterPump')  
        extra_kwargs = {'password': {'write_only': True}}  # Hide password field

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['email'], validated_data['password'])
        return user
    
class MCUSerializer(serializers.ModelSerializer):
    # Include user's email in a read-only field (optional)
    # user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = MCU
        fields = ('user', 'waterPumpVal', 'name', 'threshold', 'irrigationTime', 'sleepingTime')  # Adjust fields as needed

class SensorDataSerializer(serializers.ModelSerializer):
    # Include user's email in a read-only field (optional)
    # user_email = serializers.CharField(source='userId.email', read_only=True)

    class Meta:
        model = SensorData
        fields = ('mcuId', 'soilMoisture', 'temperature', 'humidity', 'dateTime')
    
class ActionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Action
        fields = ('sensorData', 'waterPumpVal',)

