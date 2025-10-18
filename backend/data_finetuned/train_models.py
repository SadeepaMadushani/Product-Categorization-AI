#!/usr/bin/env python3

import sys
import os
import argparse
import logging
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.data_finetuned.training_data_preparation import TrainingDataPreparation
from backend.data_finetuned.fine_tuning import FineTuningManager
from core.mongodb_service import mongodb_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Train fine-tuned models for product categorization')
    parser.add_argument('--data-path', type=str, help='Path to product data CSV file')
    parser.add_argument('--output-dir', type=str, default='fine_tuned_models', 
                       help='Output directory for trained models')
    parser.add_argument('--model-name', type=str, default='distilbert-base-uncased',
                       help='Base model name for fine-tuning')
    parser.add_argument('--epochs', type=int, default=3, help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=16, help='Training batch size')
    parser.add_argument('--learning-rate', type=float, default=2e-5, help='Learning rate')
    parser.add_argument('--use-mongodb', action='store_true', help='Use MongoDB as data source')
    parser.add_argument('--evaluate', action='store_true', help='Evaluate model after training')
    
    args = parser.parse_args()
    
    try:
        logger.info("Starting model training...")
        
        # Initialize fine-tuning manager
        manager = FineTuningManager(
            data_path=args.data_path,
            output_dir=args.output_dir
        )
        
        # Run fine-tuning
        success = manager.run_full_fine_tuning()
        
        if success:
            logger.info("Model training completed successfully!")
            
            # Evaluate if requested
            if args.evaluate:
                logger.info("Evaluating model...")
                model_path = os.path.join(args.output_dir, "classification")
                if os.path.exists(model_path):
                    # Load test data for evaluation
                    data_prep = TrainingDataPreparation(args.data_path)
                    training_data = data_prep.prepare_all_training_data()
                    test_data = training_data['classification']['validation']
                    
                    # Evaluate model
                    evaluation_results = manager.evaluate_model(model_path, test_data)
                    logger.info(f"Evaluation results: {evaluation_results}")
                else:
                    logger.warning("Model path not found for evaluation")
        else:
            logger.error("Model training failed!")
            return 1
            
    except Exception as e:
        logger.error(f"Training failed with error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
