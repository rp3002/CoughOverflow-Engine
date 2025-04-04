# test_api.py
# [1] Structure and logic for test cases were developed with ChatGPT's help to simulate full workflow and ensure endpoint coverage.
import unittest
import requests
import os
import base64
import json
import time

class TestPASAPI(unittest.TestCase):
    BASE_URL = "http://localhost:8080/api/v1"
    
    def test_health(self):
        """Test the health endpoint."""
        response = requests.get(f"{self.BASE_URL}/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
    
    def test_labs(self):
        """Test the labs endpoint."""
        response = requests.get(f"{self.BASE_URL}/labs")
        self.assertEqual(response.status_code, 200)
        # Check that we get a list of lab IDs
        self.assertIsInstance(response.json(), list)
    
    def test_analysis_workflow(self):
        """Test submitting an analysis job and retrieving results."""
        # [2] ChatGPT helped create this multi-part test to simulate a real job submission and analysis workflow.
	# Get a valid lab ID
        labs_response = requests.get(f"{self.BASE_URL}/labs")
        self.assertEqual(labs_response.status_code, 200)
        lab_ids = labs_response.json()
        self.assertTrue(len(lab_ids) > 0, "No lab IDs available")
        
        # Prepare test data
        test_lab_id = lab_ids[0]
        test_patient_id = "12345678901"  # 11-digit Medicare number
        
        # Find a sample image to test with
        sample_path = None
        for img_file in os.listdir("sample-images"):
            if img_file.endswith(".jpg"):
                sample_path = os.path.join("sample-images", img_file)
                break
        
        self.assertIsNotNone(sample_path, "No sample images found for testing")
        
        # Submit an analysis job
        with open(sample_path, "rb") as f:
            files = {"file": (os.path.basename(sample_path), f, "image/jpeg")}
            data = {
                "lab_id": test_lab_id,
                "patient_id": test_patient_id,
                "urgent": "false"
            }
            response = requests.post(f"{self.BASE_URL}/analysis", files=files, data=data)
        
        self.assertEqual(response.status_code, 201, f"Failed to submit analysis: {response.text}")
        result = response.json()
        request_id = result["request_id"]
        
        # Wait a moment for processing to complete
        time.sleep(2)
        
        # Get the analysis result
        response = requests.get(f"{self.BASE_URL}/analysis?request_id={request_id}")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["request_id"], request_id)
        self.assertEqual(result["lab_id"], test_lab_id)
        self.assertEqual(result["patient_id"], test_patient_id)
        self.assertIn(result["result"], ["pending", "covid", "h5n1", "healthy", "failed"])
        
        # Test lab results endpoint
        response = requests.get(f"{self.BASE_URL}/labs/results/{test_lab_id}")
        self.assertEqual(response.status_code, 200)
        results = response.json()
        self.assertIsInstance(results, list)
        
        # Test lab summary endpoint
        response = requests.get(f"{self.BASE_URL}/labs/results/{test_lab_id}/summary")
        self.assertEqual(response.status_code, 200)
        summary = response.json()
        self.assertEqual(summary["lab_id"], test_lab_id)
        
        # Test patient results endpoint
        response = requests.get(f"{self.BASE_URL}/patients/results?patient_id={test_patient_id}")
        self.assertEqual(response.status_code, 200)
        results = response.json()
        self.assertIsInstance(results, list)

if __name__ == "__main__":
    unittest.main()
