import requests
import json
import unittest

class TestFastAPI(unittest.TestCase):
    BASE_URL = "http://localhost:8080"
    
    def test_health_endpoint(self):
        """Test the health endpoint returns healthy status"""
        response = requests.get(f"{self.BASE_URL}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("agents", data)
        
    def test_root_endpoint(self):
        """Test the root endpoint returns API info"""
        response = requests.get(f"{self.BASE_URL}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("app", data)
        self.assertIn("version", data)
        self.assertIn("endpoints", data)
    
    def test_safety_agent(self):
        """Test the safety agent endpoint with a basic query"""
        payload = {
            "query": "What are basic safety protocols?",
            "model_id": "o3-mini"
        }
        response = requests.post(f"{self.BASE_URL}/safety/ask", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        self.assertTrue(len(data["response"]) > 0)
    
    def test_quality_agent(self):
        """Test the quality agent endpoint with a basic query"""
        payload = {
            "query": "What is quality assurance?",
            "model_id": "o3-mini"
        }
        response = requests.post(f"{self.BASE_URL}/quality/ask", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        self.assertTrue(len(data["response"]) > 0)
    
    def test_team_agent(self):
        """Test the team agent endpoint with a basic query"""
        payload = {
            "query": "Tell me about safety and quality standards.",
            "model_id": "o3-mini",
            "team_mode": "collaborate"
        }
        response = requests.post(f"{self.BASE_URL}/team/ask", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        self.assertTrue(len(data["response"]) > 0)

if __name__ == "__main__":
    unittest.main()