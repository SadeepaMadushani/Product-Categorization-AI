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
from backend.data_finetuned.model_evaluation import ModelEvaluator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Train and evaluate fine-tuned models')
    parser.add_argument('--data-path', type=str, help='Path to product data CSV file')
    parser.add_argument('--output-dir', type=str, default='fine_tuned_models', 
                       help='Output directory for trained models')
    parser.add_argument('--model-name', type=str, default='distilbert-base-uncased',
                       help='Base model name for fine-tuning')
    parser.add_argument('--epochs', type=int, default=3, help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=16, help='Training batch size')
    parser.add_argument('--learning-rate', type=float, default=2e-5, help='Learning rate')
    parser.add_argument('--evaluate-only', action='store_true', help='Only evaluate existing models')
    parser.add_argument('--compare-models', action='store_true', help='Compare fine-tuned vs pre-trained')
    parser.add_argument('--test-prediction', type=str, help='Test single prediction with text')
    
    args = parser.parse_args()
    
    try:
        if args.evaluate_only:
            logger.info("Running evaluation only...")
            evaluator = ModelEvaluator(args.output_dir)
            
            # Load test data
            data_prep = TrainingDataPreparation(args.data_path)
            training_data = data_prep.prepare_all_training_data()
            test_data = training_data['classification']['validation']
            
            # Evaluate models
            if args.compare_models:
                results = evaluator.compare_models(test_data)
            else:
                results = evaluator.evaluate_classification_model(test_data, "fine_tuned")
            
            # Generate report
            report_path = os.path.join(args.output_dir, "evaluation_report.json")
            evaluator.generate_evaluation_report(results, report_path)
            
            # Plot confusion matrix
            plot_path = os.path.join(args.output_dir, "confusion_matrix.png")
            evaluator.plot_confusion_matrix(results, plot_path)
            
            logger.info("Evaluation completed!")
            
        elif args.test_prediction:
            logger.info("Testing single prediction...")
            evaluator = ModelEvaluator(args.output_dir)
            
            # Parse test prediction (format: "product_name|description")
            if '|' in args.test_prediction:
                product_name, description = args.test_prediction.split('|', 1)
            else:
                product_name = args.test_prediction
                description = args.test_prediction
            
            # Test prediction
            result = evaluator.test_single_prediction(product_name, description)
            print(f"Prediction result: {result}")
            
        else:
            logger.info("Starting full training and evaluation pipeline...")
            
            # Initialize fine-tuning manager
            manager = FineTuningManager(
                data_path=args.data_path,
                output_dir=args.output_dir
            )
            
            # Run fine-tuning
            success = manager.run_full_fine_tuning()
            
            if success:
                logger.info("Model training completed successfully!")
                
                # Evaluate models
                logger.info("Evaluating models...")
                evaluator = ModelEvaluator(args.output_dir)
                
                # Load test data
                data_prep = TrainingDataPreparation(args.data_path)
                training_data = data_prep.prepare_all_training_data()
                test_data = training_data['classification']['validation']
                
                # Compare models
                results = evaluator.compare_models(test_data)
                
                # Generate report
                report_path = os.path.join(args.output_dir, "evaluation_report.json")
                evaluator.generate_evaluation_report(results, report_path)
                
                # Plot confusion matrix
                plot_path = os.path.join(args.output_dir, "confusion_matrix.png")
                evaluator.plot_confusion_matrix(results, plot_path)
                
                logger.info("Training and evaluation completed successfully!")
                
            else:
                logger.error("Model training failed!")
                return 1
                
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
