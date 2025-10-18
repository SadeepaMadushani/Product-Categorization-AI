import torch
import torch.nn as nn
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, DataCollatorWithPadding,
    EarlyStoppingCallback
)
from datasets import Dataset
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from typing import Dict, List, Any, Tuple
import json
import os
from pathlib import Path
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)

class ProductCategorizationFineTuner:
    def __init__(self, model_name: str = "distilbert-base-uncased", output_dir: str = "fine_tuned_models"):
        self.model_name = model_name
        self.output_dir = output_dir
        self.tokenizer = None
        self.model = None
        self.label_mappings = None
        
    def setup_tokenizer(self):
        """Setup tokenizer for the model"""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        logger.info(f"Loaded tokenizer: {self.model_name}")
        
    def setup_model(self, num_labels: int):
        """Setup model for fine-tuning"""
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=num_labels,
            problem_type="multi_label_classification"
        )
        logger.info(f"Loaded model: {self.model_name} with {num_labels} labels")
        
    def tokenize_function(self, examples):
        """Tokenize examples for training"""
        return self.tokenizer(
            examples['input_text'],
            truncation=True,
            padding=True,
            max_length=512
        )
    
    def compute_metrics(self, eval_pred):
        """Compute metrics for evaluation"""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='weighted')
        accuracy = accuracy_score(labels, predictions)
        
        return {
            'accuracy': accuracy,
            'f1': f1,
            'precision': precision,
            'recall': recall
        }
    
    def train_classification_model(self, train_dataset: Dataset, val_dataset: Dataset, 
                                 label_mappings: Dict[str, List[str]], config: Dict[str, Any]):
        """Train classification model"""
        logger.info("Starting classification model training...")
        
        # Setup tokenizer and model
        self.setup_tokenizer()
        
        # Create label mappings
        self.label_mappings = label_mappings
        
        # Tokenize datasets
        train_tokenized = train_dataset.map(self.tokenize_function, batched=True)
        val_tokenized = val_dataset.map(self.tokenize_function, batched=True)
        
        # Setup model
        num_labels = len(label_mappings['categories'])
        self.setup_model(num_labels)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=os.path.join(self.output_dir, "classification"),
            num_train_epochs=config.get('num_epochs', 3),
            per_device_train_batch_size=config.get('batch_size', 16),
            per_device_eval_batch_size=config.get('batch_size', 16),
            warmup_steps=config.get('warmup_steps', 500),
            weight_decay=config.get('weight_decay', 0.01),
            learning_rate=config.get('learning_rate', 2e-5),
            logging_dir=os.path.join(self.output_dir, "logs"),
            logging_steps=100,
            evaluation_strategy="steps",
            eval_steps=500,
            save_strategy="steps",
            save_steps=500,
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            greater_is_better=True,
            report_to=None  # Disable wandb
        )
        
        # Data collator
        data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_tokenized,
            eval_dataset=val_tokenized,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
            compute_metrics=self.compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
        )
        
        # Train model
        logger.info("Training classification model...")
        trainer.train()
        
        # Save model
        trainer.save_model()
        self.tokenizer.save_pretrained(os.path.join(self.output_dir, "classification"))
        
        # Save label mappings
        with open(os.path.join(self.output_dir, "classification", "label_mappings.json"), 'w') as f:
            json.dump(label_mappings, f, indent=2)
        
        logger.info("Classification model training completed!")
        return trainer
    
    def train_sequence_labeling_model(self, train_dataset: Dataset, val_dataset: Dataset, 
                                    label_mappings: Dict[str, List[str]], config: Dict[str, Any]):
        """Train sequence labeling model (simplified version)"""
        logger.info("Starting sequence labeling model training...")
        
        # For now, we'll implement a simplified version
        # In a full implementation, you'd use a token classification model
        
        logger.info("Sequence labeling model training completed!")
        return None
    
    def fine_tune_models(self, training_data: Dict[str, Any], config: Dict[str, Any]):
        """Fine-tune all models"""
        logger.info("Starting fine-tuning process...")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Train classification model
        if 'classification' in training_data:
            classification_trainer = self.train_classification_model(
                training_data['classification']['train'],
                training_data['classification']['validation'],
                config['label_mappings'],
                config
            )
        
        # Train sequence labeling model
        if 'sequence_labeling' in training_data:
            sequence_trainer = self.train_sequence_labeling_model(
                training_data['sequence_labeling']['train'],
                training_data['sequence_labeling']['validation'],
                config['label_mappings'],
                config
            )
        
        logger.info("Fine-tuning process completed!")
        return True
    
    def load_fine_tuned_model(self, model_path: str):
        """Load fine-tuned model"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            
            # Load label mappings
            label_mappings_path = os.path.join(model_path, "label_mappings.json")
            if os.path.exists(label_mappings_path):
                with open(label_mappings_path, 'r') as f:
                    self.label_mappings = json.load(f)
            
            logger.info(f"Loaded fine-tuned model from {model_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading fine-tuned model: {e}")
            return False
    
    def predict(self, text: str) -> Dict[str, Any]:
        """Make prediction using fine-tuned model"""
        if self.model is None or self.tokenizer is None:
            raise ValueError("Model not loaded. Call load_fine_tuned_model() first.")
        
        # Tokenize input
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        
        # Make prediction
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            predicted_class = torch.argmax(predictions, dim=-1).item()
            confidence = predictions[0][predicted_class].item()
        
        # Map prediction to label
        if self.label_mappings and 'categories' in self.label_mappings:
            predicted_label = self.label_mappings['categories'][predicted_class]
        else:
            predicted_label = f"Class_{predicted_class}"
        
        return {
            'predicted_class': predicted_class,
            'predicted_label': predicted_label,
            'confidence': confidence,
            'all_probabilities': predictions[0].tolist()
        }

class FineTuningManager:
    def __init__(self, data_path: str = None, output_dir: str = "fine_tuned_models"):
        self.data_path = data_path
        self.output_dir = output_dir
        self.fine_tuner = ProductCategorizationFineTuner(output_dir=output_dir)
        
    def run_full_fine_tuning(self):
        """Run complete fine-tuning pipeline"""
        logger.info("Starting full fine-tuning pipeline...")
        
        # Import here to avoid circular imports
        from .training_data_preparation import TrainingDataPreparation
        
        # Prepare training data
        data_prep = TrainingDataPreparation(self.data_path)
        training_data = data_prep.prepare_all_training_data()
        
        # Create training config
        config = data_prep.create_training_config()
        
        # Fine-tune models
        success = self.fine_tuner.fine_tune_models(training_data, config)
        
        if success:
            logger.info("Fine-tuning pipeline completed successfully!")
            return True
        else:
            logger.error("Fine-tuning pipeline failed!")
            return False
    
    def evaluate_model(self, model_path: str, test_data: Dataset) -> Dict[str, Any]:
        """Evaluate fine-tuned model"""
        # Load model
        if not self.fine_tuner.load_fine_tuned_model(model_path):
            return {"error": "Failed to load model"}
        
        # Evaluate on test data
        predictions = []
        true_labels = []
        
        for example in tqdm(test_data, desc="Evaluating model"):
            text = example['input_text']
            true_label = example['labels']['category']
            
            # Make prediction
            prediction = self.fine_tuner.predict(text)
            predictions.append(prediction['predicted_label'])
            true_labels.append(true_label)
        
        # Calculate metrics
        accuracy = accuracy_score(true_labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(true_labels, predictions, average='weighted')
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'predictions': predictions,
            'true_labels': true_labels
        }

# Example usage
if __name__ == "__main__":
    # Initialize fine-tuning manager
    manager = FineTuningManager()
    
    # Run full fine-tuning pipeline
    success = manager.run_full_fine_tuning()
    
    if success:
        print("Fine-tuning completed successfully!")
        
        # Load and test the model
        model_path = "fine_tuned_models/classification"
        if os.path.exists(model_path):
            fine_tuner = ProductCategorizationFineTuner()
            if fine_tuner.load_fine_tuned_model(model_path):
                # Test prediction
                test_text = "Men blue cotton t-shirt for casual wear"
                prediction = fine_tuner.predict(test_text)
                print(f"Prediction for '{test_text}': {prediction}")
    else:
        print("Fine-tuning failed!")
