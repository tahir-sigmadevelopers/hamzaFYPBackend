from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .serializers import SignupSerializer, LoginSerializer, PropertySerializer, BidSerializer  
from .models import CustomUser, Property, PropertyImage, Bid
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import DestroyAPIView
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse
import joblib
import pandas as pd
import os
from django.conf import settings
from django.shortcuts import get_object_or_404



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
        if 'predicted_price' in data:
            data.pop('predicted_price')  # Remove predicted_price from the data
        images = request.FILES.getlist('images')  # Get multiple images

        property_instance = Property.objects.create(
            location=data.get("location"),
            address=data.get("address"),
            size=data.get("size"),
            bedrooms=data.get("bedrooms"),
            bathrooms=data.get("bathrooms"),
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






@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_bid(request):
    try:
        property_id = request.data.get('property_id')
        bid_amount = request.data.get('bid_amount')
        
        # Get the property
        property_obj = Property.objects.get(id=property_id)
        
        # Validate minimum bid amount
        min_bid = property_obj.actual_price * 1.5
        if float(bid_amount) < min_bid:
            return Response(
                {'error': f'Bid must be at least {min_bid}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if this is the highest bid
        highest_bid = property_obj.bids.first()
        if highest_bid and float(bid_amount) <= highest_bid.bid_amount:
            return Response(
                {'error': 'Bid must be higher than the current highest bid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the bid
        bid = Bid.objects.create(
            property=property_obj,
            bidder=request.user,
            bid_amount=bid_amount
        )
        
        serializer = BidSerializer(bid)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Property.DoesNotExist:
        return Response(
            {'error': 'Property not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    serializer_class = BidSerializer

    def get_queryset(self):
        property_id = self.kwargs['property_id']
        return Bid.objects.filter(property_id=property_id).order_by('-amount')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        highest_bid = queryset.first()
        response_data = {
            'highest_bid': BidSerializer(highest_bid).data if highest_bid else None,
            'total_bids': queryset.count(),
            'all_bids': BidSerializer(queryset, many=True).data
        }
        return Response(response_data)


    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        property_id = request.data.get('property')
        amount = float(request.data.get('amount'))

        property_instance = get_object_or_404(Property, id=property_id)
        highest_bid = Bid.objects.filter(property=property_instance).order_by('-amount').first()

        # Validate bid amount
        min_increment = float(property_instance.actual_price) * 1.5
        if highest_bid and amount <= highest_bid.amount:
            return Response({"error": "Bid must be higher than the current highest bid"}, status=status.HTTP_400_BAD_REQUEST)
        if amount < min_increment:
            return Response({"error": f"Minimum bid increment is Rs. {min_increment}"}, status=status.HTTP_400_BAD_REQUEST)

        # Create bid
        bid = Bid.objects.create(property=property_instance, bidder=request.user, amount=amount)
        return Response(BidSerializer(bid).data, status=status.HTTP_201_CREATED)

    def get(self, request, property_id):
        try:
            bids = Bid.objects.filter(property_id=property_id).order_by('-amount')
            highest_bid = bids.first()
            
            response_data = {
                'highest_bid': BidSerializer(highest_bid).data if highest_bid else None,
                'total_bids': bids.count(),
                'all_bids': BidSerializer(bids, many=True).data
            }
            
            return Response(response_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST) 

class PropertyBidsView(APIView):
    def get(self, request, property_id):
        try:
            bids = Bid.objects.filter(property_id=property_id).order_by('-amount')
            highest_bid = bids.first()
            
            response_data = {
                'highest_bid': BidSerializer(highest_bid).data if highest_bid else None,
                'total_bids': bids.count(),
                'all_bids': BidSerializer(bids, many=True).data
            }
            
            return Response(response_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PlaceBidView(APIView):
    def post(self, request):
        try:
            print("Request data:", request.data)
            
            property_id = request.data.get('property')
            amount = float(request.data.get('amount'))
            
            # Get the property
            property_obj = get_object_or_404(Property, id=property_id)
            
            # Create the bid
            bid = Bid.objects.create(
                property=property_obj,
                amount=amount
            )
            
            return Response({
                'message': 'Bid placed successfully',
                'bid': BidSerializer(bid).data
            }, status=status.HTTP_201_CREATED)
            
        except Property.DoesNotExist:
            return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print("Error:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST) 

class AllBidsView(APIView):
    def get(self, request):
        try:
            # Get all bids with related property and bidder info
            bids = Bid.objects.select_related('property', 'bidder').all().order_by('-created_at')
            
            # Serialize with additional property info
            bid_data = []
            for bid in bids:
                bid_info = {
                    'id': bid.id,
                    'property': bid.property.id,
                    'property_address': bid.property.address,
                    'amount': bid.amount,
                    'bidder_username': bid.bidder.username if bid.bidder else 'Anonymous',
                    'created_at': bid.created_at,
                    'status': bid.status
                }
                bid_data.append(bid_info)
            
            return Response(bid_data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class BidActionView(APIView):
    def post(self, request, bid_id, action):
        try:
            bid = get_object_or_404(Bid, id=bid_id)

            if action == 'accept':
                bid.status = 'accepted'
                # Reject all other bids
                Bid.objects.filter(property=bid.property).exclude(id=bid.id).update(status='rejected')
            elif action == 'reject':
                bid.status = 'rejected'
            
            bid.save()
            
            return Response({'message': f'Bid {action}ed successfully'})
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST) 