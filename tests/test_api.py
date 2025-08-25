"""
Test cases for the sentiment analysis API
"""

import unittest
import json
import tempfile
import os
from app import create_app


class SentimentAPITestCase(unittest.TestCase):
    """Test cases for sentiment analysis API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests"""
        self.app_context.pop()
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('services', data)
    
    def test_analyze_text_valid(self):
        """Test text analysis with valid input"""
        test_data = {
            'text': 'This is a great product! I love it so much.',
            'options': {'generate_insights': False}
        }
        
        response = self.client.post('/api/analyze',
                                  data=json.dumps(test_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check expected response structure
        self.assertIn('results', data)
        self.assertIn('summary', data)
        self.assertIn('job_id', data)
        
        # Check results format
        self.assertEqual(len(data['results']), 1)
        result = data['results'][0]
        self.assertIn('text', result)
        self.assertIn('sentiment', result)
        self.assertIn('confidence', result)
        self.assertIn('language', result)
        
        # Check summary format
        summary = data['summary']
        self.assertIn('positive', summary)
        self.assertIn('negative', summary)
        self.assertIn('neutral', summary)
    
    def test_analyze_text_empty(self):
        """Test text analysis with empty input"""
        test_data = {'text': ''}
        
        response = self.client.post('/api/analyze',
                                  data=json.dumps(test_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_analyze_text_too_short(self):
        """Test text analysis with too short input"""
        test_data = {'text': 'Hi'}
        
        response = self.client.post('/api/analyze',
                                  data=json.dumps(test_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_analyze_text_too_long(self):
        """Test text analysis with too long input"""
        test_data = {'text': 'A' * 10001}  # Over the 10000 character limit
        
        response = self.client.post('/api/analyze',
                                  data=json.dumps(test_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_analyze_no_json(self):
        """Test analyze endpoint with no JSON data"""
        response = self.client.post('/api/analyze',
                                  data='not json',
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
    
    def test_analyze_missing_text(self):
        """Test analyze endpoint with missing text field"""
        test_data = {'not_text': 'some value'}
        
        response = self.client.post('/api/analyze',
                                  data=json.dumps(test_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_file_upload_invalid_format(self):
        """Test file upload with invalid format"""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.exe', delete=False) as f:
            f.write('This is not a valid format')
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = self.client.post('/api/upload/file/analyze',
                                          data={'file': (f, 'test.exe')})
            
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn('error', data)
        finally:
            os.unlink(temp_path)
    
    def test_file_upload_empty_file(self):
        """Test file upload with empty file"""
        response = self.client.post('/api/upload/file/analyze',
                                  data={'no_file': 'value'})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main()
