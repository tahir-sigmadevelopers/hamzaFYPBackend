import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import joblib

# Create some sample data
np.random.seed(42)
n_samples = 1000

# Generate synthetic data
data = {
    'size': np.random.uniform(500, 5000, n_samples),
    'bedrooms': np.random.randint(1, 7, n_samples),
    'location_urban': np.random.randint(0, 2, n_samples),
    'location_suburban': np.random.randint(0, 2, n_samples),
    'location_rural': np.random.randint(0, 2, n_samples),
}

# Create price based on features (with some noise)
prices = (
    data['size'] * 100 + 
    data['bedrooms'] * 50000 + 
    data['location_urban'] * 100000 +
    data['location_suburban'] * 75000 +
    data['location_rural'] * 50000 +
    np.random.normal(0, 50000, n_samples)
)

# Create DataFrame
df = pd.DataFrame(data)
df['price'] = prices

# Prepare features and target
X = df[['size', 'bedrooms', 'location_urban', 'location_suburban', 'location_rural']]
y = df['price']

# Create and fit scaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Create and train model
model = LinearRegression()
model.fit(X_scaled, y)

# Save model and scaler
joblib.dump(model, 'model.pkl')
joblib.dump(scaler, 'scaler.pkl')

print("Model and scaler saved successfully!") 