from models.health_models import HealthMonitoringRequest, HealthMonitoringResponse
from processors.health_monitoring_processor import analyze_player_economy_health
from typing import List, Dict
import json
import os

class HealthMonitoringService:
    """Service layer for economy health monitoring"""
    
    def __init__(self):
        self.health_logs_file = "economy_health_logs.json"
        self._ensure_log_file_exists()
    
    def _ensure_log_file_exists(self):
        """Ensure the health logs file exists"""
        if not os.path.exists(self.health_logs_file):
            with open(self.health_logs_file, 'w') as f:
                json.dump([], f)
    
    def analyze_player_health(self, request: HealthMonitoringRequest) -> HealthMonitoringResponse:
        """
        Main service function for economy health analysis
        Orchestrates the health monitoring process and returns formatted response
        """
        # Run the health analysis
        response = analyze_player_economy_health(request)
        
        # Save the analysis to logs
        self._save_health_log(response)
        
        return response
    
    def _save_health_log(self, response: HealthMonitoringResponse):
        """Save health analysis to logs"""
        try:
            with open(self.health_logs_file, 'r+') as f:
                logs = json.load(f)
                # Convert UUID and datetime objects to string for JSON serialization
                log_entry = response.model_dump()
                log_entry["player_id"] = str(response.player_id)
                log_entry["analysis_timestamp"] = response.analysis_timestamp.isoformat()
                log_entry["next_analysis_due"] = response.next_analysis_due.isoformat()
                
                logs.append(log_entry)
                f.seek(0)
                json.dump(logs, f, indent=2, default=str)
                f.truncate()
        except Exception as e:
            print(f"Error saving health log: {e}")
    
    def get_player_health_history(self, player_id: str, limit: int = 10) -> List[Dict]:
        """
        Get health analysis history for a player
        """
        try:
            with open(self.health_logs_file, 'r') as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        
        # Filter logs for the player and sort by timestamp
        player_logs = [
            log for log in logs 
            if log.get("player_id") == player_id
        ]
        player_logs.sort(key=lambda x: x.get("analysis_timestamp", ""), reverse=True)
        
        return player_logs[:limit]
    
    def get_health_summary(self, player_id: str) -> Dict:
        """
        Get a summary of the player's current health status
        """
        # Get recent health analysis
        history = self.get_player_health_history(player_id, limit=1)
        
        if not history:
            return {
                "player_id": player_id,
                "status": "no_data",
                "message": "No health analysis data available",
                "recommendation": "Run initial health analysis"
            }
        
        latest_analysis = history[0]
        
        return {
            "player_id": player_id,
            "current_status": latest_analysis.get("health_status", "unknown"),
            "risk_score": latest_analysis.get("economic_metrics", {}).get("risk_score", 0),
            "last_analysis": latest_analysis.get("analysis_timestamp", "unknown"),
            "confidence": latest_analysis.get("confidence_score", 0),
            "active_predictions": len(latest_analysis.get("failure_predictions", [])),
            "suggestions_count": len(latest_analysis.get("mitigation_suggestions", [])),
            "next_analysis_due": latest_analysis.get("next_analysis_due", "unknown")
        }

