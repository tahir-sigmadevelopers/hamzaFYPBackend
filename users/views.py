from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .serializers import SignupSerializer, LoginSerializer, PropertySerializer  
from .models import CustomUser, Property, PropertyImage
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import DestroyAPIView
from rest_framework.decorators import api_view
from django.http import HttpResponse
import joblib
import pandas as pd
import os
from django.conf import settings



def hello_world(request):
    return HttpResponse("Hello, World!")

class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, created = Token.objects.get_or_create(user=user)
            user_name = user.username 
            return Response({'token': token.key, 'user_name': user_name}, status=status.HTTP_200_OK)
    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(APIView):
    
    def get(self, request):
        users = CustomUser.objects.all()  # Fetch all users
        user_data = [{"id": user.id, "username": user.username, "email": user.email} for user in users]
        return Response(user_data, status=status.HTTP_200_OK)



class PropertyCreateView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        data = request.data
        images = request.FILES.getlist('images')  # Get multiple images

        property_instance = Property.objects.create(
            location=data.get("location"),
            address=data.get("address"),
            size=data.get("size"),
            bedrooms=data.get("bedrooms"),
            bathrooms=data.get("bathrooms"),
            predicted_price=data.get("predicted_price"),
            actual_price=data.get("actual_price"),
            owner_name=data.get("owner_name"),
            date_listed=data.get("date_listed"),
            description=data.get("description"),
        )

        for image in images:
            PropertyImage.objects.create(property=property_instance, image=image)

        return Response({"message": "Property created successfully"}, status=201)

    


@api_view(['GET'])
def get_properties(request):
        properties = Property.objects.all()
        serializer = PropertySerializer(properties, many=True)
        return Response(serializer.data)

# class PropertyAPIView(APIView):

#     def get(self, request, *args, **kwargs):
#         properties = Property.objects.all()
#         serializer = PropertySerializer(properties, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def post(self, request, *args, **kwargs):
#         print("Request Data:", request.data)  # Debug

#         data = request.data.copy()

#         serializer = PropertySerializer(data=data)
#         if serializer.is_valid():
#             property_instance = serializer.save()  # Save Property first

#             return Response(serializer.data, status=status.HTTP_201_CREATED)
        
#         print("Serializer Errors:", serializer.errors)  # Debug
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PropertyDetailView(generics.RetrieveAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    lookup_field = 'id' 
       

class PropertyUpdateView(generics.UpdateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    lookup_field = 'id'  # Use the 'id' field to update a specific property




class PropertyDeleteView(DestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    lookup_field = 'id'  # Use the 'id' field to delete a specific property





class PricePredictionView(APIView):
    def __init__(self):
        # Define paths relative to Django project
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'model.pkl')
        scaler_path = os.path.join(settings.BASE_DIR, 'ml_models', 'scaler.pkl')
        
        # Load the models
        try:
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
        except FileNotFoundError as e:
            print(f"Error loading models: {e}")
            raise Exception("ML models not found. Please ensure model.pkl and scaler.pkl are in the ml_models directory.")

    def post(self, request):
        try:
            # Extract features from request
            size = float(request.data.get('size'))
            bedrooms = int(request.data.get('bedrooms'))
            location = request.data.get('location', '').lower()

            # Create location encoding
            locations = ['urban', 'suburban', 'rural']
            location_features = {f'location_{loc}': 1 if loc == location else 0 
                               for loc in locations}
            
            # Create feature dataframe
            features = pd.DataFrame({
                'size': [size],
                'bedrooms': [bedrooms],
                **location_features
            })
            
            # Make prediction
            scaled_features = self.scaler.transform(features)
            prediction = self.model.predict(scaled_features)[0]
            
            return Response({
                'predicted_price': round(prediction, 2),
                'status': 'success'
            })
            
        except Exception as e:
            return Response({
                'error': str(e),
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST) 