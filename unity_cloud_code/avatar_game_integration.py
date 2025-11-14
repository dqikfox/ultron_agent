"""Unity Cloud Code Integration for Avatar Game"""
import requests
import json

class UnityCloudIntegration:
    def __init__(self, project_id="3f675a32-c96c-4d4e-b5a2-c81e23697d10"):
        self.project_id = project_id
        self.base_url = "https://services.api.unity.com/cloud-code/v1"
        self.token = None
    
    def call_module(self, module_name, function_name, params):
        """Call Unity Cloud Code module function"""
        if not self.token:
            return {"error": "Not authenticated"}
        
        url = f"{self.base_url}/projects/{self.project_id}/modules/{module_name}/functions/{function_name}"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.post(url, json=params, headers=headers, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def execute_command(self, command):
        """Execute command via Unity Cloud Code"""
        return self.call_module("UltronModule", "ExecuteCommand", {"command": command})
    
    def get_status(self):
        """Get module status"""
        return self.call_module("UltronModule", "GetStatus", {})

# Global instance
unity_cloud = UnityCloudIntegration()
