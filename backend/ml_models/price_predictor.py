import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import joblib

class HomePricePredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        
    def train_model(self, data_path):
        # Load and prepare data
        df = pd.read_csv(data_path)
        
        # Assuming columns: 'size', 'bedrooms', 'location', 'price'
        X = df[['size', 'bedrooms']]
        y = df['price']
        
        # Convert location to dummy variables
        location_dummies = pd.get_dummies(df['location'], prefix='location')
        X = pd.concat([X, location_dummies], axis=1)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Train model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train_scaled, y_train)
        
        # Save model and scaler
        joblib.dump(self.model, 'model.pkl')
        joblib.dump(self.scaler, 'scaler.pkl')
        
    def predict_price(self, features):
        # Scale features
        features_scaled = self.scaler.transform(features)
        # Make prediction
        return self.model.predict(features_scaled)[0] 