"""
ValorVista Model Training Script
Train the Gradient Boosting model on housing data.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config, RAW_DATA_DIR, MODELS_DIR
from src.models.trainer import ModelTrainer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description='Train ValorVista model')
    parser.add_argument(
        '--data-path',
        type=str,
        default=str(RAW_DATA_DIR / 'train.csv'),
        help='Path to training data CSV'
    )
    parser.add_argument(
        '--tune',
        action='store_true',
        help='Perform hyperparameter tuning (slower but may improve accuracy)'
    )
    parser.add_argument(
        '--model-path',
        type=str,
        default=str(Config.MODEL_PATH),
        help='Path to save trained model'
    )
    parser.add_argument(
        '--processor-path',
        type=str,
        default=str(Config.PREPROCESSOR_PATH),
        help='Path to save fitted preprocessor'
    )

    args = parser.parse_args()

    # Verify data file exists
    data_path = Path(args.data_path)
    if not data_path.exists():
        logger.error(f"Training data not found at {data_path}")
        logger.info("Please download the dataset from Kaggle:")
        logger.info("https://www.kaggle.com/c/house-prices-advanced-regression-techniques/data")
        logger.info(f"Place train.csv in: {RAW_DATA_DIR}")
        sys.exit(1)

    # Ensure output directories exist
    model_path = Path(args.model_path)
    processor_path = Path(args.processor_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    processor_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("ValorVista Model Training")
    logger.info("=" * 60)
    logger.info(f"Data path: {data_path}")
    logger.info(f"Model path: {model_path}")
    logger.info(f"Processor path: {processor_path}")
    logger.info(f"Hyperparameter tuning: {'Yes' if args.tune else 'No'}")
    logger.info("=" * 60)

    # Initialize trainer
    trainer = ModelTrainer()

    # Train model
    metrics = trainer.train(
        data_path=data_path,
        model_save_path=model_path,
        processor_save_path=processor_path,
        tune_hyperparameters=args.tune
    )

    # Print results
    logger.info("=" * 60)
    logger.info("Training Complete!")
    logger.info("=" * 60)
    logger.info("Model Performance Metrics:")
    logger.info(f"  RMSE: ${metrics['rmse']:,.2f}")
    logger.info(f"  MAE: ${metrics['mae']:,.2f}")
    logger.info(f"  R² Score: {metrics['r2']:.4f}")
    logger.info(f"  MAPE: {metrics['mape']:.2f}%")
    logger.info(f"  CV RMSE: ${metrics['cv_rmse_mean']:,.2f} (±{metrics['cv_rmse_std']:,.2f})")
    logger.info("=" * 60)

    # Print feature importance
    importance = trainer.get_feature_importance(10)
    if not importance.empty:
        logger.info("\nTop 10 Important Features:")
        for _, row in importance.iterrows():
            logger.info(f"  {row['feature']}: {row['importance']:.4f}")

    logger.info("\nModel and preprocessor saved successfully!")
    logger.info(f"Model: {model_path}")
    logger.info(f"Preprocessor: {processor_path}")

    return metrics


if __name__ == "__main__":
    main()
