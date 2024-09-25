# test_config.py
import unittest
import os
from app.config import ConfigReader

class TestConfigReader(unittest.TestCase):

    def setUp(self):
        """Setup method to create a ConfigReader instance before each test."""
        self.config_reader = ConfigReader()

    def test_get_domains(self):
        """Test if get_domains returns a dictionary and contains expected keys."""
        domains = self.config_reader.get_domains()
        self.assertIsInstance(domains, dict)
        self.assertIn('hackathon', domains)
        self.assertIn('cfp', domains)

    def test_get_domain(self):
        """Test if get_domain returns the correct domain configuration."""
        hackathon_domain = self.config_reader.get_domain('hackathon')
        self.assertEqual(hackathon_domain['name'], 'hackathon')

        cfp_domain = self.config_reader.get_domain('cfp')
        self.assertEqual(cfp_domain['name'], 'cfp')

    def test_get_models(self):
        """Test if get_models returns a dictionary and contains expected keys."""
        models = self.config_reader.get_models()
        self.assertIsInstance(models, dict)
        self.assertIn('gemini-pro', models)
        self.assertIn('gemini-15-pro-plain', models)

    def test_get_model(self):
        """Test if get_model returns the correct model configuration."""
        gemini_pro_model = self.config_reader.get_model('gemini-pro')
        self.assertEqual(gemini_pro_model['id'], 'gemini-pro')

        gemini_plain_model = self.config_reader.get_model('gemini-15-pro-plain')
        self.assertEqual(gemini_plain_model['id'], 'gemini-15-pro-plain')

    def test_read_config(self):
        """Test if _read_config reads configuration files correctly."""
        config_data = self.config_reader._read_config()
        self.assertIsInstance(config_data, dict)
        self.assertIn('domains', config_data)
        self.assertIn('models', config_data)

        # Add assertions to check the content of config_data 
        # based on your domains.json and models.json files

if __name__ == '__main__':
    unittest.main()
