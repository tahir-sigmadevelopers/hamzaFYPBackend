from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, viewsets
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
import numpy as np
from decimal import Decimal, InvalidOperation

try:
    import pandas as pd
    import joblib
    import numpy as np
except ImportError:
    pd = None
    joblib = None
    np = None

def hello_world(request):
    return HttpResponse("Hello, World!")

class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            
            # Include user details in the response
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, created = Token.objects.get_or_create(user=user)
            user_name = user.username 
           # Include user details in the response
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_201_CREATED)    
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
            if pd is None or joblib is None or np is None:
                return Response({
                    'error': 'Required libraries not available'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
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
                'error': str(e)
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
        min_bid = property_obj.actual_price*0.97
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
            property_obj = get_object_or_404(Property, id=property_id)
            bids = Bid.objects.filter(property_id=property_id).order_by('-amount')
            highest_bid = bids.first()
            
            # Check if bidding is closed due to time or acceptance
            bidding_closed = (
                property_obj.is_bidding_closed or 
                bids.filter(status='accepted').exists()
            )
            
            response_data = {
                'highest_bid': BidSerializer(highest_bid).data if highest_bid else None,
                'total_bids': bids.count(),
                'all_bids': BidSerializer(bids, many=True).data,
                'bidding_closed': bidding_closed,
                'closed_reason': 'time_expired' if property_obj.is_bidding_closed else 'bid_accepted' if bidding_closed else None
            }
            
            return Response(response_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PlaceBidView(APIView):
    def post(self, request):
        try:
            property_id = request.data.get('property')
            property_obj = get_object_or_404(Property, id=property_id)

            # Check if bidding is closed due to time
            if property_obj.is_bidding_closed:
                return Response(
                    {'error': 'Bidding time has expired for this property'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            amount = request.data.get('amount')
            email = request.data.get('email')

            # Convert amount to Decimal
            try:
                if isinstance(amount, str):
                    amount = Decimal(amount.replace(',', ''))
                else:
                    amount = Decimal(str(amount))
            except (InvalidOperation, ValueError):
                return Response(
                    {'error': 'Invalid bid amount'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get the property and user
            property_obj = get_object_or_404(Property, id=property_id)
            user = get_object_or_404(CustomUser, email=email)

            # Create the bid with the user
            bid = Bid.objects.create(
                property=property_obj,
                amount=amount,
                bidder=user
            )

            return Response({
                'message': 'Bid placed successfully',
                'bid': BidSerializer(bid).data
            }, status=status.HTTP_201_CREATED)

        except Property.DoesNotExist:
            return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
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
                    'bidder_email': bid.bidder.email if bid.bidder else None,
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
            
            # Validate the action
            if action not in ['accept', 'reject', 'pending']:
                return Response(
                    {'error': 'Invalid action'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # If accepting a bid, reject all other bids for the same property
            if action == 'accept':
                bid.status = 'accepted'
                # Reject all other bids for this property
                Bid.objects.filter(property=bid.property).exclude(id=bid.id).update(
                    status='rejected',
                    notified=False  # Reset notification status for rejected bids
                )
            elif action == 'reject':
                bid.status = 'rejected'
            else:  # pending
                bid.status = 'pending'
            
            # Reset notification status when status changes
            bid.notified = False
            bid.save()
            
            return Response({
                'message': f'Bid {action}ed successfully',
                'status': bid.status
            })
            
        except Bid.DoesNotExist:
            return Response(
                {'error': 'Bid not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        
        # Get the user from the email
        user_email = data.get('email')
        try:
            user = CustomUser.objects.get(email=user_email)
            data['bidder'] = user.id
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return Bid.objects.all().select_related('property', 'bidder') 

class UserBidsView(APIView):
    def get(self, request, email):
        try:
            bids = Bid.objects.filter(bidder__email=email).select_related('property', 'bidder')
            serializer = BidSerializer(bids, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MarkBidNotifiedView(APIView):
    def post(self, request, bid_id):
        try:
            bid = get_object_or_404(Bid, id=bid_id)
            bid.notified = True
            bid.save()
            return Response({'message': 'Bid marked as notified'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST) 