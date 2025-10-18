from typing import Dict, Any, List
import logging
from ..core.llm_integration import LLMIntegration
from ..core.nlp_processor import NLPProcessor

logger = logging.getLogger(__name__)

class AttributeExtractorAgent:
    def __init__(self):
        self.llm = LLMIntegration()
        self.nlp = NLPProcessor()
    
    def extract_attributes(self, product_data: Dict[str, Any], category: str = None) -> Dict[str, Any]:
        try:
            product_name = product_data.get('productDisplayName', '')
            base_color = product_data.get('baseColour', '')
            usage = product_data.get('usage', '')
            season = product_data.get('season', '')
            
            # prompt for LLM
            prompt = f"""
            Extract detailed attributes from the following product information:
            
            Product: {product_name}
            Base Color: {base_color}
            Usage: {usage}
            Season: {season}
            Category: {category if category else 'Not specified'}
            
            Extract the following attributes:
            - color: primary color(s)

            - material: fabric or material composition

            - size: size information if available

            - pattern: pattern or design

            - style: fashion or product style

            - gender: intended gender if specified

            - seasonality: appropriate seasons

            - occasion: suitable occasions
            
            Respond with a JSON object containing these attributes.
            For each attribute, provide a value and confidence score (0.0 to 1.0).
            """
            
            response_format = {
                "color": {"value": "string", "confidence": "float"},

                "material": {"value": "string", "confidence": "float"},

                "size": {"value": "string", "confidence": "float"},

                "pattern": {"value": "string", "confidence": "float"},

                "style": {"value": "string", "confidence": "float"},

                "gender": {"value": "string", "confidence": "float"},

                "seasonality": {"value": "string", "confidence": "float"},
                
                "occasion": {"value": "string", "confidence": "float"}
            }
            
            result = self.llm.generate_structured_response(prompt, response_format)
            
            # Also extract entities using NLP
            nlp_entities = self.nlp.extract_entities(product_name)
            if nlp_entities:
                result['entities'] = nlp_entities
            
            # Post-process to ensure valid values
            for attr_name, attr_data in result.items():
                if isinstance(attr_data, dict):
                    # Clean up values
                    value = attr_data.get('value', '') or ''
                    value = str(value).strip()
                    if not value or value.lower() in ['', 'not specified', 'unknown', 'n/a', 'none']:
                        attr_data['value'] = "Unknown"
                    
                    # Ensure confidence is valid float
                    try:
                        confidence = float(attr_data.get('confidence', 0.5))
                        attr_data['confidence'] = max(0.0, min(1.0, confidence))
                    except (ValueError, TypeError):
                        attr_data['confidence'] = 0.5
            
            return {"attributes": result}
            
        except Exception as e:
            logger.error(f"Error in attribute extraction: {e}")
            return {"error": str(e), "attributes": {}}
    
    def extract_specific_attributes(self, product_data: Dict[str, Any], 
                                  attributes: List[str], category: str = None) -> Dict[str, Any]:
        """
        Extract only specific attributes from product data.
        
        Args:
            product_data: Product information dictionary
            attributes: List of specific attributes to extract
            category: Product category for context
            
        Returns:
            Dictionary containing extracted attributes
        """
        try:
            product_name = product_data.get('productDisplayName', '')
            base_color = product_data.get('baseColour', '')
            usage = product_data.get('usage', '')
            season = product_data.get('season', '')
            
            # Create dynamic response format based on requested attributes
            response_format = {}
            for attr in attributes:
                response_format[attr] = {"value": "string", "confidence": "float"}
            
            prompt = f"""
            Extract only the following specific attributes from the product information:
            {', '.join(attributes)}
            
            Product: {product_name}
            Base Color: {base_color}
            Usage: {usage}
            Season: {season}
            Category: {category if category else 'Not specified'}
            
            For each requested attribute, provide a value and confidence score (0.0 to 1.0).
            If an attribute cannot be determined, use "Unknown" as the value with low confidence.
            """
            
            result = self.llm.generate_structured_response(prompt, response_format)
            
            # Post-process results
            for attr_name, attr_data in result.items():
                if isinstance(attr_data, dict):
                    value = attr_data.get('value', '') or ''
                    value = str(value).strip()
                    if not value or value.lower() in ['', 'not specified', 'unknown', 'n/a', 'none']:
                        attr_data['value'] = "Unknown"
                    
                    try:
                        confidence = float(attr_data.get('confidence', 0.5))
                        attr_data['confidence'] = max(0.0, min(1.0, confidence))
                    except (ValueError, TypeError):
                        attr_data['confidence'] = 0.5
            
            return {"attributes": result}
            
        except Exception as e:
            logger.error(f"Error in specific attribute extraction: {e}")
            return {"error": str(e), "attributes": {}}
    
    def validate_attributes(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean extracted attributes.
        
        Args:
            attributes: Dictionary of extracted attributes
            
        Returns:
            Cleaned and validated attributes
        """
        validated = {}
        
        for attr_name, attr_data in attributes.items():
            if isinstance(attr_data, dict):
                value = attr_data.get('value', '') or ''
                value = str(value).strip()
                
                # Clean up value
                if not value or value.lower() in ['', 'not specified', 'unknown', 'n/a', 'none']:
                    value = "Unknown"
                
                # Validate confidence
                try:
                    confidence = float(attr_data.get('confidence', 0.5))
                    confidence = max(0.0, min(1.0, confidence))
                except (ValueError, TypeError):
                    confidence = 0.5
                
                validated[attr_name] = {
                    "value": value,
                    "confidence": confidence
                }
                
            else:
                # Handle simple string values
                value = str(attr_data).strip() if attr_data else "Unknown"
                validated[attr_name] = {
                    "value": value,
                    "confidence": 0.5
                }
        
        return validated
        

      