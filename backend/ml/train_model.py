import pandas as pd
import numpy as np
import sys
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import cross_val_score
import xgboost as xgb
import joblib
import os

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from preprocessing import DataPreprocessor


class ModelTrainer:
    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.models = {}
        self.best_model = None
        self.best_model_name = None
        self.best_accuracy = 0
        
    def train_logistic_regression(self, X_train, y_train):
        """Train Logistic Regression model"""
        print("Training Logistic Regression...")
        lr_model = LogisticRegression(random_state=42, max_iter=1000)
        lr_model.fit(X_train, y_train)
        return lr_model
    
    def train_xgboost(self, X_train, y_train):
        """Train XGBoost model"""
        print("Training XGBoost...")
        xgb_model = xgb.XGBClassifier(
            random_state=42,
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        xgb_model.fit(X_train, y_train)
        return xgb_model
    
    def evaluate_model(self, model, X_test, y_test, model_name):
        """Evaluate model performance"""
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Calculate ROC AUC if possible
        try:
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            roc_auc = roc_auc_score(y_test, y_pred_proba)
        except:
            roc_auc = None
        
        print(f"\n{model_name} Results:")
        print(f"Accuracy: {accuracy:.4f}")
        if roc_auc:
            print(f"ROC AUC: {roc_auc:.4f}")
        print(f"Classification Report:\n{classification_report(y_test, y_pred)}")
        print(f"Confusion Matrix:\n{confusion_matrix(y_test, y_pred)}")
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_test, y_test, cv=5, scoring='accuracy')
        print(f"Cross-validation Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        return {
            'accuracy': accuracy,
            'roc_auc': roc_auc,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }
    
    def compare_models(self, X_train, X_test, y_train, y_test):
        """Train and compare both models"""
        results = {}
        
        # Train Logistic Regression
        lr_model = self.train_logistic_regression(X_train, y_train)
        lr_results = self.evaluate_model(lr_model, X_test, y_test, "Logistic Regression")
        results['LogisticRegression'] = {
            'model': lr_model,
            'results': lr_results
        }
        
        # Train XGBoost
        xgb_model = self.train_xgboost(X_train, y_train)
        xgb_results = self.evaluate_model(xgb_model, X_test, y_test, "XGBoost")
        results['XGBoost'] = {
            'model': xgb_model,
            'results': xgb_results
        }
        
        # Determine best model based on accuracy
        if lr_results['accuracy'] > xgb_results['accuracy']:
            self.best_model = lr_model
            self.best_model_name = 'LogisticRegression'
            self.best_accuracy = lr_results['accuracy']
        else:
            self.best_model = xgb_model
            self.best_model_name = 'XGBoost'
            self.best_accuracy = xgb_results['accuracy']
        
        print(f"\n{'='*50}")
        print(f"BEST MODEL: {self.best_model_name}")
        print(f"BEST ACCURACY: {self.best_accuracy:.4f}")
        print(f"{'='*50}")
        
        return results
    
    def save_models(self, save_dir, results):
        """Save all trained models"""
        os.makedirs(save_dir, exist_ok=True)
        
        # Save individual models
        joblib.dump(results['LogisticRegression']['model'], 
                   os.path.join(save_dir, 'logistic_regression_model.pkl'))
        joblib.dump(results['XGBoost']['model'], 
                   os.path.join(save_dir, 'xgboost_model.pkl'))
        
        # Save best model
        joblib.dump(self.best_model, 
                   os.path.join(save_dir, 'best_model.pkl'))
        
        # Save metadata
        metadata = {
            'best_model_name': self.best_model_name,
            'best_accuracy': self.best_accuracy
        }
        joblib.dump(metadata, os.path.join(save_dir, 'model_metadata.pkl'))
        
        print(f"\nModels saved to {save_dir}")
    
    def run_training_pipeline(self, data_path, save_dir):
        """Complete training pipeline"""
        print("Loading data...")
        df = self.preprocessor.load_data(data_path)
        
        print("Preprocessing data...")
        X, y = self.preprocessor.preprocess_data(df, fit=True)
        X_train, X_test, y_train, y_test = self.preprocessor.split_data(X, y)
        
        print("Saving preprocessor...")
        self.preprocessor.save_preprocessor(os.path.join(save_dir, 'preprocessor.pkl'))
        
        print("Comparing models...")
        results = self.compare_models(X_train, X_test, y_train, y_test)
        
        # Store models
        self.models['LogisticRegression'] = results['LogisticRegression']['model']
        self.models['XGBoost'] = results['XGBoost']['model']
        
        print("Saving models...")
        self.save_models(save_dir, results)
        
        return results


if __name__ == "__main__":
    # Paths
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'cleaned_telecom_churn_data.csv')
    save_dir = os.path.join(os.path.dirname(__file__), 'saved_models')
    
    # Run training
    trainer = ModelTrainer()
    results = trainer.run_training_pipeline(data_path, save_dir)
    
    print("\nTraining completed successfully!")
