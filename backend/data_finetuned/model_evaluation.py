import pandas as pd
import torch
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support, 
    classification_report, confusion_matrix
)
from datasets import Dataset
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Tuple
import json
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelEvaluator:
    def __init__(self, model_path: str = "fine_tuned_models/classification"):
        self.model_path = model_path
        self.evaluation_results = {}
        
    def evaluate_classification_model(self, test_dataset: Dataset, model_type: str = "fine_tuned") -> Dict[str, Any]:
        """Evaluate classification model performance"""
        logger.info(f"Evaluating {model_type} classification model...")
        
        try:
            # Import here to avoid circular imports
            from .fine_tuned_classifier import fine_tuned_classifier
            from ..core.llm_integration import LLMIntegration
            from ..core.nlp_processor import NLPProcessor
            
            predictions = []
            true_labels = []
            confidences = []
            
            # Initialize model based on type
            if model_type == "fine_tuned":
                if not fine_tuned_classifier.is_model_available():
                    logger.warning("Fine-tuned model not available, using pre-trained model")
                    model_type = "pretrained"
            
            if model_type == "fine_tuned":
                # Use fine-tuned model
                for example in test_dataset:
                    product_data = {
                        'productDisplayName': example['input_text'].split('.')[0],
                        'description': example['input_text']
                    }
                    
                    result = fine_tuned_classifier.classify_product(product_data)
                    predictions.append(result['category'])
                    true_labels.append(example['labels']['category'])
                    confidences.append(result.get('confidence', 0.5))
            else:
                # Use pre-trained model
                llm = LLMIntegration()
                nlp = NLPProcessor()
                
                for example in test_dataset:
                    product_name = example['input_text'].split('.')[0]
                    description = example['input_text']
                    true_label = example['labels']['category']
                    
                    # Create prompt for LLM
                    prompt = f"""
                    Classify the following product into one of these categories: Apparel, Accessories, Footwear, Personal Care, Free Items
                    
                    Product: {product_name}
                    Description: {description}
                    
                    Respond with just the category name.
                    """
                    
                    try:
                        response = llm.generate_response(prompt)
                        predicted_category = response.strip()
                        predictions.append(predicted_category)
                        true_labels.append(true_label)
                        confidences.append(0.7)  # Default confidence for pre-trained
                    except Exception as e:
                        logger.error(f"Error in pre-trained prediction: {e}")
                        predictions.append("Unknown")
                        true_labels.append(true_label)
                        confidences.append(0.0)
            
            # Calculate metrics
            accuracy = accuracy_score(true_labels, predictions)
            precision, recall, f1, _ = precision_recall_fscore_support(true_labels, predictions, average='weighted')
            
            # Get detailed metrics
            detailed_metrics = precision_recall_fscore_support(true_labels, predictions, average=None)
            
            # Create classification report
            report = classification_report(true_labels, predictions, output_dict=True)
            
            # Create confusion matrix
            cm = confusion_matrix(true_labels, predictions)
            
            # Calculate average confidence
            avg_confidence = np.mean(confidences)
            
            # Store results
            results = {
                'model_type': model_type,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'average_confidence': avg_confidence,
                'classification_report': report,
                'confusion_matrix': cm.tolist(),
                'predictions': predictions,
                'true_labels': true_labels,
                'confidences': confidences
            }
            
            self.evaluation_results[model_type] = results
            
            logger.info(f"Evaluation completed for {model_type} model:")
            logger.info(f"  Accuracy: {accuracy:.4f}")
            logger.info(f"  Precision: {precision:.4f}")
            logger.info(f"  Recall: {recall:.4f}")
            logger.info(f"  F1-Score: {f1:.4f}")
            logger.info(f"  Average Confidence: {avg_confidence:.4f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in model evaluation: {e}")
            return {"error": str(e)}
    
    def compare_models(self, test_dataset: Dataset) -> Dict[str, Any]:
        """Compare fine-tuned vs pre-trained models"""
        logger.info("Comparing fine-tuned vs pre-trained models...")
        
        # Evaluate fine-tuned model
        fine_tuned_results = self.evaluate_classification_model(test_dataset, "fine_tuned")
        
        # Evaluate pre-trained model
        pretrained_results = self.evaluate_classification_model(test_dataset, "pretrained")
        
        # Compare results
        comparison = {
            'fine_tuned': fine_tuned_results,
            'pretrained': pretrained_results,
            'improvement': {}
        }
        
        if 'error' not in fine_tuned_results and 'error' not in pretrained_results:
            # Calculate improvements
            for metric in ['accuracy', 'precision', 'recall', 'f1_score']:
                if metric in fine_tuned_results and metric in pretrained_results:
                    improvement = fine_tuned_results[metric] - pretrained_results[metric]
                    comparison['improvement'][metric] = improvement
            
            # Calculate relative improvement
            if pretrained_results['accuracy'] > 0:
                relative_improvement = (fine_tuned_results['accuracy'] - pretrained_results['accuracy']) / pretrained_results['accuracy']
                comparison['relative_improvement'] = relative_improvement
        
        return comparison
    
    def generate_evaluation_report(self, results: Dict[str, Any], output_path: str = "evaluation_report.json"):
        """Generate comprehensive evaluation report"""
        try:
            # Create report
            report = {
                'evaluation_timestamp': str(pd.Timestamp.now()),
                'model_path': self.model_path,
                'results': results,
                'summary': self._create_summary(results)
            }
            
            # Save report
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Evaluation report saved to {output_path}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating evaluation report: {e}")
            return {"error": str(e)}
    
    def _create_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of evaluation results"""
        summary = {}
        
        for model_type, result in results.items():
            if 'error' not in result:
                summary[model_type] = {
                    'accuracy': result.get('accuracy', 0),
                    'f1_score': result.get('f1_score', 0),
                    'average_confidence': result.get('average_confidence', 0)
                }
        
        return summary
    
    def plot_confusion_matrix(self, results: Dict[str, Any], output_path: str = "confusion_matrix.png"):
        """Plot confusion matrix"""
        try:
            if 'fine_tuned' in results and 'confusion_matrix' in results['fine_tuned']:
                cm = np.array(results['fine_tuned']['confusion_matrix'])
                labels = list(set(results['fine_tuned']['true_labels']))
                
                plt.figure(figsize=(10, 8))
                sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                           xticklabels=labels, yticklabels=labels)
                plt.title('Confusion Matrix - Fine-tuned Model')
                plt.xlabel('Predicted')
                plt.ylabel('Actual')
                plt.tight_layout()
                plt.savefig(output_path)
                plt.close()
                
                logger.info(f"Confusion matrix plot saved to {output_path}")
                return True
            else:
                logger.warning("No confusion matrix data available for plotting")
                return False
                
        except Exception as e:
            logger.error(f"Error plotting confusion matrix: {e}")
            return False
    
    def test_single_prediction(self, product_name: str, description: str, model_type: str = "fine_tuned") -> Dict[str, Any]:
        """Test single product prediction"""
        try:
            from .fine_tuned_classifier import fine_tuned_classifier
            
            product_data = {
                'productDisplayName': product_name,
                'description': description
            }
            
            if model_type == "fine_tuned" and fine_tuned_classifier.is_model_available():
                result = fine_tuned_classifier.classify_product(product_data)
            else:
                # Use pre-trained model
                from ..core.llm_integration import LLMIntegration
                llm = LLMIntegration()
                
                prompt = f"""
                Classify the following product into one of these categories: Apparel, Accessories, Footwear, Personal Care, Free Items
                
                Product: {product_name}
                Description: {description}
                
                Respond with just the category name.
                """
                
                response = llm.generate_response(prompt)
                result = {
                    'category': response.strip(),
                    'confidence': 0.7,
                    'reasoning': 'Pre-trained model prediction'
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in single prediction test: {e}")
            return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    # Initialize evaluator
    evaluator = ModelEvaluator()
    
    # Load test dataset (you would load your actual test data here)
    # test_dataset = load_test_dataset()
    
    # Evaluate models
    # results = evaluator.compare_models(test_dataset)
    
    # Generate report
    # report = evaluator.generate_evaluation_report(results)
    
    # Test single prediction
    test_result = evaluator.test_single_prediction(
        "Nike Men Blue T-shirt",
        "Men blue cotton t-shirt for casual wear"
    )
    print(f"Test prediction: {test_result}")
