import pandas as pd
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datasets import Dataset
import logging

logger = logging.getLogger(__name__)

class TrainingDataPreparation:
    def __init__(self, data_path: str = None):
        self.data_path = data_path or self._get_default_data_path()
        self.training_data = None
        self.validation_data = None
        
    def _get_default_data_path(self) -> str:
        """Get default data path"""
        return str(Path(__file__).resolve().parents[1] / "data" / "cleaned_product_data.csv")
    
    def load_product_data(self) -> pd.DataFrame:
        """Load product data from CSV"""
        try:
            if os.path.exists(self.data_path):
                df = pd.read_csv(self.data_path)
                logger.info(f"Loaded {len(df)} products from {self.data_path}")
                return df
            else:
                # Try alternative path
                alt_path = str(Path(__file__).resolve().parents[1] / "data" / "product.csv")
                if os.path.exists(alt_path):
                    df = pd.read_csv(alt_path)
                    logger.info(f"Loaded {len(df)} products from {alt_path}")
                    return df
                else:
                    raise FileNotFoundError("No product data file found")
        except Exception as e:
            logger.error(f"Error loading product data: {e}")
            raise e
    
    def prepare_classification_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Prepare data for category classification fine-tuning"""
        training_examples = []
        
        for _, row in df.iterrows():
            # Create input text
            product_name = str(row.get('productDisplayName', ''))
            description = str(row.get('description', ''))
            
            # Combine name and description
            input_text = f"{product_name}. {description}".strip()
            
            # Create labels
            category = str(row.get('masterCategory', 'Unknown'))
            subcategory = str(row.get('subCategory', 'Unknown'))
            gender = str(row.get('gender', 'Unknown'))
            article_type = str(row.get('articleType', 'Unknown'))
            color = str(row.get('baseColour', 'Unknown'))
            usage = str(row.get('usage', 'Unknown'))
            season = str(row.get('season', 'Unknown'))
            
            # Create structured output
            labels = {
                'category': category,
                'subcategory': subcategory,
                'gender': gender,
                'article_type': article_type,
                'color': color,
                'usage': usage,
                'season': season
            }
            
            training_examples.append({
                'input_text': input_text,
                'labels': labels,
                'product_id': row.get('id', ''),
                'original_data': row.to_dict()
            })
        
        return training_examples
    
    def prepare_sequence_labeling_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Prepare data for sequence labeling (NER-style) fine-tuning"""
        training_examples = []
        
        for _, row in df.iterrows():
            product_name = str(row.get('productDisplayName', ''))
            description = str(row.get('description', ''))
            
            # Combine text
            full_text = f"{product_name}. {description}".strip()
            
            # Create entity labels
            entities = []
            
            # Extract gender entities
            gender = str(row.get('gender', ''))
            if gender and gender != 'Unknown':
                entities.append({
                    'text': gender,
                    'label': 'GENDER',
                    'start': full_text.lower().find(gender.lower()),
                    'end': full_text.lower().find(gender.lower()) + len(gender)
                })
            
            # Extract color entities
            color = str(row.get('baseColour', ''))
            if color and color != 'Unknown':
                entities.append({
                    'text': color,
                    'label': 'COLOR',
                    'start': full_text.lower().find(color.lower()),
                    'end': full_text.lower().find(color.lower()) + len(color)
                })
            
            # Extract article type entities
            article_type = str(row.get('articleType', ''))
            if article_type and article_type != 'Unknown':
                entities.append({
                    'text': article_type,
                    'label': 'ARTICLE_TYPE',
                    'start': full_text.lower().find(article_type.lower()),
                    'end': full_text.lower().find(article_type.lower()) + len(article_type)
                })
            
            training_examples.append({
                'text': full_text,
                'entities': entities,
                'product_id': row.get('id', ''),
                'original_data': row.to_dict()
            })
        
        return training_examples
    
    def create_huggingface_dataset(self, training_examples: List[Dict], task_type: str = "classification") -> Dataset:
        """Create Hugging Face dataset from training examples"""
        if task_type == "classification":
            # For classification task
            dataset_dict = {
                'input_text': [ex['input_text'] for ex in training_examples],
                'labels': [ex['labels'] for ex in training_examples],
                'product_id': [ex['product_id'] for ex in training_examples]
            }
        elif task_type == "sequence_labeling":
            # For sequence labeling task
            dataset_dict = {
                'text': [ex['text'] for ex in training_examples],
                'entities': [ex['entities'] for ex in training_examples],
                'product_id': [ex['product_id'] for ex in training_examples]
            }
        else:
            raise ValueError(f"Unknown task type: {task_type}")
        
        return Dataset.from_dict(dataset_dict)
    
    def split_train_validation(self, dataset: Dataset, validation_split: float = 0.2) -> Tuple[Dataset, Dataset]:
        """Split dataset into training and validation sets"""
        split_dataset = dataset.train_test_split(test_size=validation_split, seed=42)
        return split_dataset['train'], split_dataset['test']
    
    def prepare_all_training_data(self) -> Dict[str, Any]:
        """Prepare all training data for different tasks"""
        logger.info("Preparing training data...")
        
        # Load product data
        df = self.load_product_data()
        
        # Prepare classification data
        classification_data = self.prepare_classification_data(df)
        classification_dataset = self.create_huggingface_dataset(classification_data, "classification")
        
        # Prepare sequence labeling data
        sequence_data = self.prepare_sequence_labeling_data(df)
        sequence_dataset = self.create_huggingface_dataset(sequence_data, "sequence_labeling")
        
        # Split datasets
        train_classification, val_classification = self.split_train_validation(classification_dataset)
        train_sequence, val_sequence = self.split_train_validation(sequence_dataset)
        
        # Store in instance variables
        self.training_data = {
            'classification': {
                'train': train_classification,
                'validation': val_classification
            },
            'sequence_labeling': {
                'train': train_sequence,
                'validation': val_sequence
            }
        }
        
        logger.info(f"Prepared training data:")
        logger.info(f"  Classification - Train: {len(train_classification)}, Val: {len(val_classification)}")
        logger.info(f"  Sequence Labeling - Train: {len(train_sequence)}, Val: {len(val_sequence)}")
        
        return self.training_data
    
    def save_training_data(self, output_dir: str = "training_data"):
        """Save prepared training data to files"""
        if self.training_data is None:
            raise ValueError("No training data prepared. Call prepare_all_training_data() first.")
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save classification data
        classification_train_path = output_path / "classification_train.json"
        classification_val_path = output_path / "classification_validation.json"
        
        self.training_data['classification']['train'].to_json(classification_train_path)
        self.training_data['classification']['validation'].to_json(classification_val_path)
        
        # Save sequence labeling data
        sequence_train_path = output_path / "sequence_train.json"
        sequence_val_path = output_path / "sequence_validation.json"
        
        self.training_data['sequence_labeling']['train'].to_json(sequence_train_path)
        self.training_data['sequence_labeling']['validation'].to_json(sequence_val_path)
        
        logger.info(f"Training data saved to {output_path}")
        
        return str(output_path)
    
    def get_label_mappings(self) -> Dict[str, List[str]]:
        """Get label mappings for different tasks"""
        if self.training_data is None:
            raise ValueError("No training data prepared. Call prepare_all_training_data() first.")
        
        # Extract unique labels from classification data
        all_labels = []
        for example in self.training_data['classification']['train']:
            labels = example['labels']
            all_labels.append(labels)
        
        # Create label mappings
        label_mappings = {
            'categories': list(set([labels['category'] for labels in all_labels])),
            'subcategories': list(set([labels['subcategory'] for labels in all_labels])),
            'genders': list(set([labels['gender'] for labels in all_labels])),
            'article_types': list(set([labels['article_type'] for labels in all_labels])),
            'colors': list(set([labels['color'] for labels in all_labels])),
            'usages': list(set([labels['usage'] for labels in all_labels])),
            'seasons': list(set([labels['season'] for labels in all_labels]))
        }
        
        return label_mappings
    
    def create_training_config(self) -> Dict[str, Any]:
        """Create training configuration"""
        label_mappings = self.get_label_mappings()
        
        config = {
            'model_name': 'distilbert-base-uncased',
            'max_length': 512,
            'batch_size': 16,
            'learning_rate': 2e-5,
            'num_epochs': 3,
            'warmup_steps': 500,
            'weight_decay': 0.01,
            'label_mappings': label_mappings,
            'task_types': ['classification', 'sequence_labeling'],
            'output_dir': 'fine_tuned_models'
        }
        
        return config

# Example usage
if __name__ == "__main__":
    # Initialize data preparation
    data_prep = TrainingDataPreparation()
    
    # Prepare all training data
    training_data = data_prep.prepare_all_training_data()
    
    # Save training data
    output_dir = data_prep.save_training_data()
    print(f"Training data saved to: {output_dir}")
    
    # Get label mappings
    label_mappings = data_prep.get_label_mappings()
    print("Label mappings:")
    for key, values in label_mappings.items():
        print(f"  {key}: {len(values)} unique values")
    
    # Create training config
    config = data_prep.create_training_config()
    print(f"Training config created: {config}")
