"""
ValorVista Configuration Module
Production-grade configuration management for the application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models_saved"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure directories exist
for dir_path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, REPORTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


class Config:
    """Base configuration class."""

    # Flask Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "valorvista-secret-key-change-in-production")
    DEBUG = False
    TESTING = False

    # Application Settings
    APP_NAME = "ValorVista"
    APP_VERSION = "1.0.0"

    # Model Settings
    MODEL_PATH = MODELS_DIR / "gradient_boosting_model.joblib"
    PREPROCESSOR_PATH = MODELS_DIR / "preprocessor.joblib"
    FEATURE_NAMES_PATH = MODELS_DIR / "feature_names.joblib"

    # Data Settings
    TRAIN_DATA_PATH = RAW_DATA_DIR / "train.csv"
    TEST_DATA_PATH = RAW_DATA_DIR / "test.csv"

    # Model Hyperparameters
    MODEL_PARAMS = {
        "n_estimators": 500,
        "learning_rate": 0.05,
        "max_depth": 5,
        "min_samples_split": 10,
        "min_samples_leaf": 4,
        "subsample": 0.8,
        "max_features": "sqrt",
        "random_state": 42,
        "validation_fraction": 0.1,
        "n_iter_no_change": 20,
        "tol": 1e-4
    }

    # API Settings
    MAX_BATCH_SIZE = 100
    REQUEST_TIMEOUT = 30

    # Report Settings
    REPORTS_DIR = REPORTS_DIR
    MAX_REPORT_AGE_HOURS = 24


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY")


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True


def get_config():
    """Get configuration based on environment."""
    env = os.getenv("FLASK_ENV", "development")
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }
    return config_map.get(env, DevelopmentConfig)()
