from typing import Dict, Any
import logging
import pandas as pd
from pathlib import Path
from ..core.llm_integration import LLMIntegration
from ..core.nlp_processor import NLPProcessor
from ..core.information_retrieval import InformationRetrieval
from ..data_finetuned.fine_tuned_classifier import fine_tuned_classifier

logger = logging.getLogger(__name__)

class CategoryClassifierAgent:
    def __init__(self):
        self.llm = LLMIntegration()
        self.nlp = NLPProcessor()
        self.categories = ["Apparel", "Accessories", "Footwear", "Personal Care", "Free Items"]
        
        # Initialize InformationRetrieval with product data
        self.ir = self._initialize_information_retrieval()
        
        # Try to load fine-tuned model
        self.use_fine_tuned = fine_tuned_classifier.is_model_available()
        if self.use_fine_tuned:
            logger.info("Using fine-tuned model for classification")
        else:
            logger.info("Using pre-trained model for classification")
    
    def _initialize_information_retrieval(self):
        """Initialize InformationRetrieval with product data from CSV."""
        try:
            # Load product data
            data_path = Path(__file__).resolve().parents[2] / "data" / "cleaned_product_data.csv"
            if not data_path.exists():
                data_path = Path(__file__).resolve().parents[2] / "data" / "product.csv"
            
            if data_path.exists():
                # Use shared instance for better performance
                ir = InformationRetrieval.get_shared_instance(str(data_path))
                
                # If the shared instance doesn't have data, load it
                if not ir.product_database:
                    df = pd.read_csv(data_path)
                    product_data = df.to_dict('records')
                    ir.product_database = product_data
                    ir.build_index()
                
                return ir
            else:
                logger.warning("No product data found for InformationRetrieval")
                return InformationRetrieval()
        except Exception as e:
            logger.error(f"Error initializing InformationRetrieval: {e}")
            return InformationRetrieval()
    
    def classify_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Use fine-tuned model if available
            if self.use_fine_tuned:
                return self._classify_with_fine_tuned_model(product_data)
            else:
                return self._classify_with_pretrained_model(product_data)
                
        except Exception as e:
            logger.error(f"Error in category classification: {e}")
            return {"error": str(e), "category": "Unknown", "subcategory": "Unknown", "confidence": 0.0}
    
    def _classify_with_fine_tuned_model(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify using fine-tuned model"""
        try:
            result = fine_tuned_classifier.classify_product(product_data)
            
            # Ensure confidence is float
            if 'confidence' in result:
                try:
                    result['confidence'] = float(result['confidence'])
                except (ValueError, TypeError):
                    result['confidence'] = 0.5
            
            return result
            
        except Exception as e:
            logger.error(f"Error in fine-tuned classification: {e}")
            return self._classify_with_pretrained_model(product_data)
    
    def _classify_with_pretrained_model(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify using pre-trained model (original method)"""
        try:
            product_name = product_data.get('productDisplayName', '')
            product_description = product_data.get('description', '') or product_name
            
            # Preprocess text
            processed_text = self.nlp.preprocess_text(product_description)
            
            # Get similar products for context
            similar_products = self.ir.search_similar_products(product_name, top_k=3)
            similar_categories = list(set([p.get('masterCategory', '') for p in similar_products]))
            
            # Prepare prompt for LLM
            prompt = f"""
            Classify the following product into one of these categories: {', '.join(self.categories)}
            
            Product: {product_name}
            Description: {product_description}
            
            Similar products are categorized as: {', '.join(similar_categories) if similar_categories else 'No similar products found'}
            
            Respond with a JSON object containing:
            - category: the main category
            - subcategory: a specific subcategory
            - confidence: your confidence level (0.0 to 1.0)
            - reasoning: brief explanation of your classification
            """
            
            response_format = {
                "category": "string",
                "subcategory": "string", 
                "confidence": "float",
                "reasoning": "string"
            }
            
            result = self.llm.generate_structured_response(prompt, response_format)
            
            # Validate and ensure confidence is float
            if 'confidence' in result:
                try:
                    result['confidence'] = float(result['confidence'])
                except (ValueError, TypeError):
                    result['confidence'] = 0.5
            
            return result
            
        except Exception as e:
            logger.error(f"Error in pre-trained classification: {e}")
            return {"error": str(e), "category": "Unknown", "subcategory": "Unknown", "confidence": 0.0}