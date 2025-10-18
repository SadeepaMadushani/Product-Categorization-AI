import unittest
from backend.agents.category_classifier_agent import CategoryClassifierAgent
from backend.agents.attribute_extractor_agent import AttributeExtractorAgent
from backend.agents.tag_generator_agent import TagGeneratorAgent

class TestAgents(unittest.TestCase):
    def setUp(self):
        self.classifier = CategoryClassifierAgent()
        self.extractor = AttributeExtractorAgent()
        self.tagger = TagGeneratorAgent()
        
        self.sample_product = {
            "productDisplayName": "Nike Men Running Shoes with Air Cushion",
            "gender": "Men",
            "baseColour": "Black",
            "season": "All Season",
            "usage": "Sports",
            "year": 2023
        }
    
    def test_classifier(self):
        result = self.classifier.classify_product(self.sample_product)
        self.assertIn('category', result)
        self.assertIn('confidence', result)
        self.assertGreaterEqual(result['confidence'], 0)
        self.assertLessEqual(result['confidence'], 1)
    
    def test_extractor(self):
        result = self.extractor.extract_attributes(self.sample_product, "Footwear")
        self.assertIn('attributes', result)
        self.assertIn('color', result['attributes'])
    
    def test_tagger(self):
        attributes = {
            "color": {"value": "Black", "confidence": 0.9},
            "material": {"value": "Mesh", "confidence": 0.8}
        }
        result = self.tagger.generate_tags(self.sample_product, attributes)
        self.assertIn('tags', result)
        self.assertGreater(len(result['tags']), 0)

if __name__ == '__main__':
    unittest.main()