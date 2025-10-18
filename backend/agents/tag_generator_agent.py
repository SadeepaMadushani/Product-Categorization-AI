

from typing import Dict, Any, List, Optional
import logging
import re
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class TagGeneratorAgent:
    """
    Agent responsible for generating relevant tags for products.
    Uses both LLM and NLP approaches to create comprehensive product tags.
    """
    
    def __init__(self, llm_client=None, nlp_processor=None):
        """
        Initialize the TagGeneratorAgent.
        
        Args:
            llm_client: Optional LLM client for generating tags
            nlp_processor: Optional NLP processor for text analysis
        """
        self.llm = llm_client
        self.nlp = nlp_processor
        self.logger = logging.getLogger(__name__)
    
    def generate_tags(self, product_data: Dict[str, Any], attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate relevant tags for a product using both LLM and NLP approaches.
        
        Args:
            product_data: Dictionary containing product information
            attributes: Optional extracted attributes from other agents
            
        Returns:
            Dictionary containing generated tags with confidence scores
        """
        try:
            self.logger.info("Starting tag generation process")
            
            # Extract basic product information
            product_name = product_data.get('productDisplayName', '')
            base_color = product_data.get('baseColour', '')
            usage = product_data.get('usage', '')
            article_type = product_data.get('articleType', '')
            season = product_data.get('season', '')
            
            # Generate tags using different methods
            all_tags = []
            
            # 1. Generate LLM-based tags if LLM client is available
            if self.llm:
                llm_tags = self._generate_llm_tags(product_name, base_color, usage, article_type, season, attributes)
                all_tags.extend(llm_tags)
            
            # 2. Generate NLP-based tags if NLP processor is available
            if self.nlp:
                nlp_tags = self._generate_nlp_tags(product_name, attributes)
                all_tags.extend(nlp_tags)
            
            # 3. Generate rule-based tags
            rule_tags = self._generate_rule_based_tags(product_data, attributes)
            all_tags.extend(rule_tags)
            
            # 4. Deduplicate and sort tags
            unique_tags = self._deduplicate_tags(all_tags)
            
            # 5. Limit to top 10 tags
            final_tags = sorted(unique_tags, key=lambda x: x.get('confidence', 0), reverse=True)[:10]
            
            result = {
                "tags": final_tags,
                "generation_timestamp": datetime.now().isoformat(),
                "total_generated": len(all_tags),
                "final_count": len(final_tags)
            }
            
            self.logger.info(f"Generated {len(final_tags)} unique tags")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in tag generation: {e}")
            return {
                "tags": [],
                "error": str(e),
                "generation_timestamp": datetime.now().isoformat()
            }
    
    def _generate_llm_tags(self, product_name: str, base_color: str, usage: str, 
                          article_type: str, season: str, attributes: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate tags using LLM if available."""
        try:
            prompt = f"""
            Generate specific, descriptive tags for this product:

            PRODUCT: {product_name}
            BASE COLOR: {base_color}
            USAGE: {usage}
            ARTICLE TYPE: {article_type}
            SEASON: {season}

            Create 5-10 specific tags that describe this product accurately.
            Examples of good tags: "cotton-tshirt", "red-dress", "winter-boots", "formal-shirt"
            Examples of bad tags: "product", "color", "style" (too generic)

            Make tags lowercase with hyphens, descriptive and specific.
            """

            response_format = {
                "tags": [
                    {"tag": "string", "confidence": "float"}
                ]
            }
            
            result = self.llm.generate_structured_response(prompt, response_format)
            
            tags = []
            if 'tags' in result and isinstance(result['tags'], list):
                for tag_obj in result['tags']:
                    if isinstance(tag_obj, dict) and 'tag' in tag_obj:
                        tag_text = self.clean_tag(tag_obj['tag'])
                        if tag_text:
                            tags.append({
                                "tag": tag_text,
                                "confidence": float(tag_obj.get('confidence', 0.7)),
                                "source": "llm"
                            })
            return tags
            
        except Exception as e:
            self.logger.warning(f"LLM tag generation failed: {e}")
            return []
    
    def _generate_nlp_tags(self, product_name: str, attributes: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate tags using NLP if available."""
        try:
            tags = []
            
            # Extract nouns and adjectives from product name
            nouns = self.nlp.extract_nouns(product_name)
            adjectives = self.nlp.extract_adjectives(product_name)
            
            for noun in nouns:
                clean_noun = self.clean_tag(noun)
                if clean_noun:
                    tags.append({"tag": clean_noun, "confidence": 0.7, "source": "nlp"})
            
            for adj in adjectives:
                clean_adj = self.clean_tag(adj)
                if clean_adj:
                    tags.append({"tag": clean_adj, "confidence": 0.6, "source": "nlp"})
            
            # Add attribute values as tags
            if attributes:
                for attr_name, attr_value in attributes.items():
                    if isinstance(attr_value, dict) and 'value' in attr_value:
                        tag_value = attr_value['value']
                        if tag_value and tag_value not in ["", "Unknown", "Not specified"]:
                            clean_tag = self.clean_tag(tag_value)
                            if clean_tag:
                                tags.append({
                                    "tag": clean_tag, 
                                    "confidence": attr_value.get('confidence', 0.5) * 0.8,
                                    "source": "attribute"
                                })
            
            return tags
            
        except Exception as e:
            self.logger.warning(f"NLP tag generation failed: {e}")
            return []
    
    def _generate_rule_based_tags(self, product_data: Dict[str, Any], attributes: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate tags using rule-based approach."""
        tags = []
        
        # Color-based tags
        base_color = product_data.get('baseColour', '').lower()
        if base_color and base_color not in ['', 'unknown', 'not specified']:
            tags.append({"tag": f"{base_color}-color", "confidence": 0.8, "source": "rule"})
        
        # Season-based tags
        season = product_data.get('season', '').lower()
        if season and season not in ['', 'unknown', 'not specified']:
            tags.append({"tag": f"{season}-season", "confidence": 0.7, "source": "rule"})
        
        # Usage-based tags
        usage = product_data.get('usage', '').lower()
        if usage and usage not in ['', 'unknown', 'not specified']:
            tags.append({"tag": f"{usage}-wear", "confidence": 0.6, "source": "rule"})
        
        # Article type tags
        article_type = product_data.get('articleType', '').lower()
        if article_type and article_type not in ['', 'unknown', 'not specified']:
            tags.append({"tag": article_type, "confidence": 0.9, "source": "rule"})
        
        return tags
    
    def _deduplicate_tags(self, tags: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate tags and keep the highest confidence version."""
        seen = set()
        unique_tags = []
        
        for tag_obj in tags:
            tag_name = (tag_obj.get('tag', '') or '').lower().strip()
            if tag_name not in seen and tag_name:
                seen.add(tag_name)
                unique_tags.append(tag_obj)
        
        return unique_tags
    
    def clean_tag(self, tag: str) -> str:
        """Clean and format tag text"""
        if not tag:
            return ""
        
        # Remove generic words
        tag = (tag or '').lower().strip()
        generic_words = ['product', 'type', 'color', 'style', 'occasion', 'material', 'season']
        
        for word in generic_words:
            tag = re.sub(rf'\b{word}\b', '', tag)
        
        # Clean up and format
        tag = re.sub(r'[^\w\s-]', '', tag)  # Remove special chars
        tag = re.sub(r'\s+', '-', (tag or '').strip())  # Replace spaces with hyphens
        tag = re.sub(r'-+', '-', tag)  # Remove multiple hyphens
        
        return tag if tag and tag != '-' else ""
    