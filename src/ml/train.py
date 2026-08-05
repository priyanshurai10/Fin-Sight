import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, precision_score, recall_score, f1_score
from xgboost import XGBClassifier

from src.core.config import settings
from src.services.etl import ETLPipeline
from src.ml.feature_engineering import NUMERICAL_FEATURES, CATEGORICAL_FEATURES, prepare_feature_matrix

def train_fraud_models():
    # 1. Run ETL if processed data doesn't exist
    if not os.path.exists(settings.PROCESSED_DATA_PATH):
        etl = ETLPipeline()
        df = etl.run()
    else:
        df = pd.read_csv(settings.PROCESSED_DATA_PATH)
        
    X = prepare_feature_matrix(df)
    y = df['is_fraud_actual'].astype(int)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 2. Build Preprocessor Pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), NUMERICAL_FEATURES),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), CATEGORICAL_FEATURES)
        ]
    )
    
    # 3. Supervised Model (XGBoost)
    xgb_clf = XGBClassifier(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='logloss'
    )
    
    supervised_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', xgb_clf)
    ])
    
    print("Training Supervised XGBoost Fraud Classifier...")
    supervised_pipeline.fit(X_train, y_train)
    
    # Evaluation
    y_pred = supervised_pipeline.predict(X_test)
    y_proba = supervised_pipeline.predict_proba(X_test)[:, 1]
    
    roc_auc = roc_auc_score(y_test, y_proba)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)
    
    metrics = {
        "roc_auc": round(float(roc_auc), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "confusion_matrix": cm.tolist()
    }
    
    print("\n--- Supervised Model Performance ---")
    print(f"ROC-AUC: {metrics['roc_auc']}")
    print(f"Precision: {metrics['precision']}")
    print(f"Recall: {metrics['recall']}")
    print(f"F1 Score: {metrics['f1_score']}")
    print(f"Confusion Matrix:\n{cm}")
    
    # 4. Unsupervised Anomaly Detection (Isolation Forest)
    print("\nTraining Unsupervised Isolation Forest Anomaly Detector...")
    X_train_proc = preprocessor.transform(X_train)
    iso_forest = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    iso_forest.fit(X_train_proc)
    
    # 5. Save Artifacts
    os.makedirs(settings.MODEL_DIR, exist_ok=True)
    model_artifact = {
        "pipeline": supervised_pipeline,
        "iso_forest": iso_forest,
        "preprocessor": preprocessor,
        "metrics": metrics,
        "feature_names": NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    }
    
    model_path = os.path.join(settings.MODEL_DIR, "fraud_model.joblib")
    joblib.dump(model_artifact, model_path)
    print(f"\nSaved trained model artifact -> {model_path}")
    return metrics

if __name__ == "__main__":
    train_fraud_models()
