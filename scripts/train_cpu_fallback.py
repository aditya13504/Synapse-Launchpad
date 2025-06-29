#!/usr/bin/env python3
"""
CPU Fallback Training Script for Partner Recommender

This script provides a CPU-based training fallback when GPU is not available.
Uses scikit-learn instead of HugeCTR for compatibility.
"""

import os
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
import pickle
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CPUTrainer:
    """CPU-based training for partner matching model"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def load_data(self):
        """Load training data from database or generate synthetic data"""
        logger.info("Loading training data...")
        
        # Generate synthetic data for demonstration
        np.random.seed(42)
        n_samples = 10000
        
        # Generate features
        data = {
            'funding_a': np.random.lognormal(15, 2, n_samples),
            'employees_a': np.random.randint(10, 1000, n_samples),
            'growth_a': np.random.normal(25, 15, n_samples),
            'sentiment_a': np.random.normal(0, 0.3, n_samples),
            'funding_b': np.random.lognormal(15, 2, n_samples),
            'employees_b': np.random.randint(10, 1000, n_samples),
            'growth_b': np.random.normal(25, 15, n_samples),
            'sentiment_b': np.random.normal(0, 0.3, n_samples),
            'overlap_score': np.random.beta(2, 5, n_samples),
        }
        
        # Add culture vector features
        for i in range(128):
            data[f'culture_a_{i}'] = np.random.normal(0, 1, n_samples)
            data[f'culture_b_{i}'] = np.random.normal(0, 1, n_samples)
        
        df = pd.DataFrame(data)
        
        # Generate labels based on similarity
        funding_sim = 1 - np.abs(np.log(df['funding_a']) - np.log(df['funding_b'])) / 10
        size_sim = 1 - np.abs(np.log(df['employees_a']) - np.log(df['employees_b'])) / 5
        growth_sim = 1 - np.abs(df['growth_a'] - df['growth_b']) / 50
        sentiment_sim = 1 - np.abs(df['sentiment_a'] - df['sentiment_b'])
        
        # Culture similarity
        culture_a = df[[f'culture_a_{i}' for i in range(128)]].values
        culture_b = df[[f'culture_b_{i}' for i in range(128)]].values
        culture_sim = np.sum(culture_a * culture_b, axis=1) / (
            np.linalg.norm(culture_a, axis=1) * np.linalg.norm(culture_b, axis=1)
        )
        culture_sim = (culture_sim + 1) / 2  # Normalize to 0-1
        
        # Combine similarities
        match_prob = (
            funding_sim * 0.2 +
            size_sim * 0.15 +
            growth_sim * 0.15 +
            sentiment_sim * 0.2 +
            culture_sim * 0.3
        )
        
        # Add noise and create binary labels
        match_prob += np.random.normal(0, 0.1, n_samples)
        match_prob = np.clip(match_prob, 0, 1)
        df['label'] = (match_prob > 0.6).astype(int)
        
        logger.info(f"Generated {len(df)} training samples")
        logger.info(f"Positive samples: {df['label'].sum()} ({df['label'].mean():.2%})")
        
        return df
    
    def preprocess_data(self, df):
        """Preprocess data for training"""
        logger.info("Preprocessing data...")
        
        # Separate features and labels
        feature_cols = [col for col in df.columns if col != 'label']
        X = df[feature_cols]
        y = df['label']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled, y, feature_cols
    
    def train_model(self, X, y):
        """Train the model"""
        logger.info("Training Random Forest model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_pred = self.model.predict_proba(X_train)[:, 1]
        test_pred = self.model.predict_proba(X_test)[:, 1]
        
        train_auc = roc_auc_score(y_train, train_pred)
        test_auc = roc_auc_score(y_test, test_pred)
        
        test_pred_binary = self.model.predict(X_test)
        test_accuracy = accuracy_score(y_test, test_pred_binary)
        
        logger.info(f"Training AUC: {train_auc:.4f}")
        logger.info(f"Test AUC: {test_auc:.4f}")
        logger.info(f"Test Accuracy: {test_accuracy:.4f}")
        
        # Detailed classification report
        logger.info("Classification Report:")
        logger.info(classification_report(y_test, test_pred_binary))
        
        return {
            'train_auc': train_auc,
            'test_auc': test_auc,
            'test_accuracy': test_accuracy
        }
    
    def save_model(self, feature_cols, metrics):
        """Save the trained model"""
        model_dir = "/app/models"
        os.makedirs(model_dir, exist_ok=True)
        
        # Save model
        model_path = f"{model_dir}/partner_recommender_cpu.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        # Save scaler
        scaler_path = f"{model_dir}/scaler_cpu.pkl"
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        # Save feature columns
        features_path = f"{model_dir}/features_cpu.json"
        with open(features_path, 'w') as f:
            json.dump(feature_cols, f)
        
        # Save metrics
        metrics_path = f"{model_dir}/metrics_cpu.json"
        metrics_data = {
            **metrics,
            'model_type': 'RandomForest',
            'training_date': datetime.utcnow().isoformat(),
            'feature_count': len(feature_cols)
        }
        
        with open(metrics_path, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        logger.info(f"Model saved to {model_path}")
        logger.info(f"Scaler saved to {scaler_path}")
        logger.info(f"Features saved to {features_path}")
        logger.info(f"Metrics saved to {metrics_path}")

def main():
    """Main training function"""
    logger.info("Starting CPU-based training pipeline...")
    
    trainer = CPUTrainer()
    
    # Load and preprocess data
    df = trainer.load_data()
    X, y, feature_cols = trainer.preprocess_data(df)
    
    # Train model
    metrics = trainer.train_model(X, y)
    
    # Save model
    trainer.save_model(feature_cols, metrics)
    
    logger.info("CPU training completed successfully!")
    logger.info("Model is ready for inference.")

if __name__ == "__main__":
    main()