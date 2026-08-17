import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import joblib
import os


class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='mean')
        self.feature_columns = None
        
    def load_data(self, data_path):
        """Load the dataset from CSV file"""
        return pd.read_csv(data_path)
    
    def separate_features_target(self, df, target_column='Churn'):
        """Separate features and target variable"""
        X = df.drop(columns=[target_column])
        y = df[target_column]
        return X, y
    
    def handle_missing_values(self, X, fit=True):
        """Handle missing values in the dataset"""
        if fit:
            X_imputed = self.imputer.fit_transform(X)
        else:
            X_imputed = self.imputer.transform(X)
        return pd.DataFrame(X_imputed, columns=X.columns)
    
    def scale_features(self, X, fit=True):
        """Scale features using StandardScaler"""
        if fit:
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)
        return pd.DataFrame(X_scaled, columns=X.columns)
    
    def preprocess_data(self, df, target_column='Churn', fit=True):
        """Complete preprocessing pipeline"""
        # Check if target column exists (for training data)
        if target_column in df.columns:
            X, y = self.separate_features_target(df, target_column)
        else:
            # For prediction data, no target column
            X = df
            y = None
        
        if fit:
            self.feature_columns = X.columns.tolist()
        
        X_imputed = self.handle_missing_values(X, fit=fit)
        X_scaled = self.scale_features(X_imputed, fit=fit)
        
        return X_scaled, y
    
    def split_data(self, X, y, test_size=0.2, random_state=42):
        """Split data into train and test sets"""
        return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)
    
    def save_preprocessor(self, save_path):
        """Save the preprocessor objects"""
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        joblib.dump({
            'scaler': self.scaler,
            'imputer': self.imputer,
            'feature_columns': self.feature_columns
        }, save_path)
    
    def load_preprocessor(self, load_path):
        """Load the preprocessor objects"""
        preprocessor_data = joblib.load(load_path)
        self.scaler = preprocessor_data['scaler']
        self.imputer = preprocessor_data['imputer']
        self.feature_columns = preprocessor_data['feature_columns']
