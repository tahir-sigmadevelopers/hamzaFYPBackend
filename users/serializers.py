from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import CustomUser, Property , PropertyImage, Bid
from decimal import Decimal
from decimal import InvalidOperation


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        print(user)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")







# Property Serializers




class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image']

class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id', 
            'location', 
            'address', 
            'size', 
            'bedrooms', 
            'bathrooms', 
            'actual_price',
            'owner_name',
            'date_listed',
            'description',
            'images'
        ]


def create(self, validated_data):
        # images_data = self.context['request'].FILES.getlist('images')
        property_instance = Property.objects.create(**validated_data)

        # for image in images_data:
        #     PropertyImage.objects.create(property=property_instance, image=image)

        return property_instance



class BidSerializer(serializers.ModelSerializer):
    bidder_email = serializers.SerializerMethodField()
    property_address = serializers.CharField(source='property.address')
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    notified = serializers.BooleanField(default=False)

    class Meta:
        model = Bid
        fields = ['id', 'property', 'amount', 'status', 'created_at', 
                 'bidder_email', 'property_address', 'notified']

    def get_bidder_email(self, obj):
        return obj.bidder.email if obj.bidder else None

    def validate_amount(self, value):
        try:
            # Convert to Decimal if it's a string
            if isinstance(value, str):
                value = Decimal(value.replace(',', ''))
            return value
        except (InvalidOperation, ValueError):
            raise serializers.ValidationError("Invalid bid amount")

    def create(self, validated_data):
        email = self.context.get('email')
        if email:
            user = CustomUser.objects.get(email=email)
            validated_data['bidder'] = user
        
        # Ensure amount is Decimal
        if 'amount' in validated_data:
            try:
                validated_data['amount'] = Decimal(str(validated_data['amount']))
            except InvalidOperation:
                raise serializers.ValidationError({"amount": "Invalid bid amount"})
                
        return super().create(validated_data)