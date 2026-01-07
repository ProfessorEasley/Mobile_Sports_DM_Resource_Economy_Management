#!/usr/bin/env python3
"""
🚀 Economy Management API - Unified Demo & Test Suite
====================================================

This consolidated script combines all demo, test, and utility functionality
into a single comprehensive tool.

Usage:
    python unified_demo.py [command] [options]

Commands:
    demo        - Run comprehensive API demonstration
    test        - Run API tests
    health      - Run health monitoring demos
    alerts      - Show all types of alerts
    generate    - Generate API output files
    server      - Server management (start/stop/status)
    help        - Show detailed help

Options:
    --player-id <id>     - Use specific player ID
    --weeks <n>          - Analysis period in weeks
    --scenarios <n>      - Number of test scenarios
    --output <file>      - Output file for generation
"""

import requests
import json
import sys
import subprocess
import time
import os
from datetime import datetime
from uuid import uuid4
from typing import Dict, List, Any, Optional

# Configuration
API_BASE_URL = "http://localhost:8000"
DEFAULT_PLAYER_ID = str(uuid4())

class UnifiedDemoSuite:
    """Unified demo and test suite for Economy Management API"""
    
    def __init__(self):
        self.api_base_url = API_BASE_URL
        self.player_id = DEFAULT_PLAYER_ID
        
    def print_header(self, title: str, char: str = "=", width: int = 60):
        """Print a formatted header"""
        print(f"\n{char * width}")
        print(f"{title:^{width}}")
        print(f"{char * width}")
    
    def print_section(self, title: str, char: str = "-", width: int = 50):
        """Print a formatted section"""
        print(f"\n{char * width}")
        print(f"{title}")
        print(f"{char * width}")
    
    def check_api_status(self) -> bool:
        """Check if the API server is running"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def ensure_api_running(self):
        """Ensure API server is running or exit"""
        if not self.check_api_status():
            print("❌ API Server is not running!")
            print("💡 Start the server first with: uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
            sys.exit(1)
        print("✅ API Server is running!")
    
    def demo_wallet_simulation(self):
        """Demonstrate wallet simulation functionality"""
        self.print_section("🎮 WALLET SIMULATION DEMO")
        
        # Test with default parameters
        print("📊 Testing with default parameters...")
        try:
            response = requests.get(f"{self.api_base_url}/api/v1/wallet/simulate/browser")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Player ID: {data['player_id']}")
                print(f"💰 Initial Wallet: {data['initial_wallet']['coins']} coins, {data['initial_wallet']['gems']} gems")
                print(f"💰 Final Wallet: {data['final_wallet']['coins']} coins, {data['final_wallet']['gems']} gems")
                print(f"📈 Net Changes: +{data['net_changes']['coins']} coins, +{data['net_changes']['gems']} gems")
                print(f"🔄 Total Transactions: {data['simulation_summary']['total_transactions']} over 7 days")
                print(f"⚠️ Risk Alerts: {len(data['alerts'])} alerts")
                
                if data['alerts']:
                    for alert in data['alerts']:
                        print(f"   ⚠️ {alert}")
            else:
                print(f"❌ Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def demo_health_monitoring(self, scenarios: int = 3):
        """Demonstrate health monitoring functionality"""
        self.print_section("🏥 ECONOMY HEALTH MONITORING DEMO")
        
        for i in range(scenarios):
            player_id = str(uuid4())
            print(f"\n🎯 Scenario {i+1}/{scenarios}:")
            print(f"   Player ID: {player_id}")
            
            try:
                health_params = {
                    'player_id': player_id,
                    'analysis_period_weeks': 4,
                    'include_predictions': True,
                    'include_suggestions': True
                }
                response = requests.get(f"{self.api_base_url}/api/v1/wallet/health", params=health_params)
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Health Status: {data['health_status'].upper()}")
                    print(f"   ⚠️ Risk Score: {data['economic_metrics']['risk_score']:.1f}/100")
                    print(f"   🔮 Predictions: {len(data['failure_predictions'])}")
                    print(f"   💡 Suggestions: {len(data['mitigation_suggestions'])}")
                    
                    if data['failure_predictions']:
                        for pred in data['failure_predictions']:
                            print(f"      - Week {pred['next_failure_week']}: {pred['failure_type']} ({pred['failure_probability']:.1%})")
                else:
                    print(f"   ❌ Error: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def demo_health_history(self):
        """Demonstrate health history functionality"""
        self.print_section("📚 HEALTH HISTORY & SUMMARY DEMO")
        
        # Run multiple analyses for history
        print("🔄 Running multiple analyses for history...")
        for i in range(3):
            self.analyze_player_health(str(uuid4()), f"History Test {i+1}", 4)
        
        # Get health summary
        print("\n📊 Getting health summary...")
        try:
            summary_params = {'player_id': self.player_id}
            response = requests.get(f"{self.api_base_url}/api/v1/wallet/health/summary", params=summary_params)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health Summary:")
                print(f"   Current Status: {data['current_status']}")
                print(f"   Risk Score: {data['risk_score']:.1f}/100")
                print(f"   Active Predictions: {data['active_predictions']}")
                print(f"   Suggestions Count: {data['suggestions_count']}")
            else:
                print(f"❌ Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def analyze_player_health(self, player_id: str, scenario_name: str, analysis_weeks: int = 4):
        """Analyze a player's health and display results"""
        try:
            response = requests.get(f"{self.api_base_url}/api/v1/wallet/health", params={
                "player_id": player_id,
                "analysis_period_weeks": analysis_weeks,
                "include_predictions": True,
                "include_suggestions": True
            })
            response.raise_for_status()
            data = response.json()
            
            print(f"   📊 {scenario_name}:")
            print(f"      Status: {data['health_status'].upper()}")
            print(f"      Risk: {data['economic_metrics']['risk_score']:.1f}/100")
            print(f"      Predictions: {len(data['failure_predictions'])}")
            print(f"      Suggestions: {len(data['mitigation_suggestions'])}")
            
            return data
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error analyzing player health: {e}")
            return None
    
    def show_alerts(self, alert_type: str = "all"):
        """Show different types of alerts"""
        if alert_type in ["all", "wallet"]:
            self.show_wallet_alerts()
        if alert_type in ["all", "health"]:
            self.show_health_alerts()
    
    def show_wallet_alerts(self):
        """Show daily wallet simulation alerts"""
        self.print_section("🎮 DAILY WALLET SIMULATION ALERTS")
        
        scenarios = [
            {"name": "Low Balance", "params": {"initial_coins": 50, "daily_expenses_coins": 100}},
            {"name": "High Spending", "params": {"initial_coins": 1000, "daily_expenses_coins": 200}},
            {"name": "Balanced", "params": {"initial_coins": 1000, "daily_expenses_coins": 50}}
        ]
        
        for scenario in scenarios:
            print(f"\n🎯 {scenario['name']}:")
            try:
                response = requests.get(f"{self.api_base_url}/api/v1/wallet/simulate/browser", params=scenario['params'])
                if response.status_code == 200:
                    data = response.json()
                    print(f"   📊 Alerts: {len(data['alerts'])}")
                    if data['alerts']:
                        for alert in data['alerts']:
                            print(f"      ⚠️ {alert}")
                    else:
                        print(f"      ✅ No alerts - Wallet is healthy")
                else:
                    print(f"   ❌ Error: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def show_health_alerts(self):
        """Show health monitoring alerts"""
        self.print_section("🏥 HEALTH MONITORING ALERTS")
        
        for i in range(3):
            player_id = str(uuid4())
            print(f"\n🎯 Player Scenario {i+1}:")
            try:
                params = {
                    "player_id": player_id,
                    "analysis_period_weeks": 6,
                    "include_predictions": True,
                    "include_suggestions": True
                }
                response = requests.get(f"{self.api_base_url}/api/v1/wallet/health", params=params)
                if response.status_code == 200:
                    data = response.json()
                    print(f"   📊 Status: {data['health_status'].upper()}")
                    print(f"   ⚠️ Risk: {data['economic_metrics']['risk_score']:.1f}/100")
                    print(f"   🔮 Predictions: {len(data['failure_predictions'])}")
                    print(f"   💡 Suggestions: {len(data['mitigation_suggestions'])}")
                else:
                    print(f"   ❌ Error: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def run_api_tests(self):
        """Run comprehensive API tests"""
        self.print_section("🧪 API TESTS")
        
        endpoints = [
            ("/health", "Health Check"),
            ("/api/v1/wallet/simulate/browser", "Wallet Simulation"),
            (f"/api/v1/wallet/health?player_id={self.player_id}", "Health Monitoring")
        ]
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.api_base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    print(f"✅ {name}: OK")
                else:
                    print(f"❌ {name}: Error {response.status_code}")
            except Exception as e:
                print(f"❌ {name}: Error - {e}")
    
    def generate_api_outputs(self, output_file: str = "api_outputs.json"):
        """Generate comprehensive API outputs"""
        self.print_section("📊 GENERATING API OUTPUTS")
        
        sample_player_id = str(uuid4())
        timestamp = datetime.now().isoformat()
        
        api_outputs = {
            "metadata": {
                "generated_at": timestamp,
                "api_base_url": self.api_base_url,
                "api_version": "1.0.0",
                "description": "Comprehensive API outputs"
            },
            "endpoints": {}
        }
        
        # Test all endpoints
        endpoints_to_test = [
            ("health_check", "GET", f"{self.api_base_url}/health", None, None),
            ("wallet_simulation", "GET", f"{self.api_base_url}/api/v1/wallet/simulate/browser", 
             {"initial_coins": 1000, "initial_gems": 50}, None),
            ("health_monitoring", "GET", f"{self.api_base_url}/api/v1/wallet/health",
             {"player_id": sample_player_id, "analysis_period_weeks": 4}, None)
        ]
        
        for name, method, url, params, payload in endpoints_to_test:
            print(f"🔄 Testing {name}...")
            try:
                if method == "GET":
                    response = requests.get(url, params=params, timeout=10)
                elif method == "POST":
                    response = requests.post(url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    api_outputs["endpoints"][name] = {
                        "method": method,
                        "url": url,
                        "status_code": response.status_code,
                        "response": response.json()
                    }
                    if params:
                        api_outputs["endpoints"][name]["parameters"] = params
                    print(f"✅ {name}: OK")
                else:
                    print(f"❌ {name}: Error {response.status_code}")
            except Exception as e:
                print(f"❌ {name}: Error - {e}")
        
        # Save outputs
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(api_outputs, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n✅ API outputs saved to: {output_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return False
    
    def manage_server(self, action: str):
        """Manage API server (start/stop/status)"""
        if action == "start":
            self.print_header("🚀 STARTING API SERVER")
            print("📋 Starting uvicorn server...")
            print("💡 Server will be available at: http://localhost:8000")
            print("📖 API docs will be available at: http://localhost:8000/docs")
            print("🛑 Press Ctrl+C to stop the server")
            try:
                subprocess.run([
                    "uvicorn", "main:app", 
                    "--host", "0.0.0.0", 
                    "--port", "8000", 
                    "--reload", 
                    "--log-level", "info"
                ])
            except KeyboardInterrupt:
                print("\n🛑 Server stopped by user")
        elif action == "stop":
            self.print_header("🛑 STOPPING API SERVER")
            try:
                result = subprocess.run(["pkill", "-f", "uvicorn main:app"], capture_output=True)
                if result.returncode == 0:
                    print("✅ Server stopped successfully!")
                else:
                    print("ℹ️ No server processes found to stop")
            except Exception as e:
                print(f"❌ Error stopping server: {e}")
        elif action == "status":
            self.print_header("🔍 CHECKING API STATUS")
            if self.check_api_status():
                print("✅ API Server is running!")
                print(f"   URL: {self.api_base_url}")
                print(f"   Docs: {self.api_base_url}/docs")
            else:
                print("❌ API Server is not running")
                print("💡 Start the server with: python unified_demo.py server start")
    
    def show_browser_urls(self):
        """Show all browser-friendly URLs"""
        self.print_section("🌐 BROWSER-FRIENDLY URLS")
        
        print("📋 Copy these URLs into your browser to test:")
        print()
        print("🎮 Wallet Simulation:")
        print(f"   Default: {self.api_base_url}/api/v1/wallet/simulate/browser")
        print(f"   Custom: {self.api_base_url}/api/v1/wallet/simulate/browser?initial_coins=2000&initial_gems=100")
        print()
        print("🏥 Health Monitoring:")
        print(f"   Health Check: {self.api_base_url}/api/v1/wallet/health?player_id={self.player_id}")
        print(f"   Health History: {self.api_base_url}/api/v1/wallet/health/history?player_id={self.player_id}")
        print(f"   Health Summary: {self.api_base_url}/api/v1/wallet/health/summary?player_id={self.player_id}")
        print()
        print("📊 JSON API Endpoints (Direct JSON Access):")
        print(f"   Wallet Simulation JSON: {self.api_base_url}/api/v1/wallet/simulate/browser")
        print(f"   Health Monitoring JSON: {self.api_base_url}/api/v1/wallet/health?player_id={self.player_id}")
        print(f"   Health History JSON: {self.api_base_url}/api/v1/wallet/health/history?player_id={self.player_id}")
        print(f"   Health Summary JSON: {self.api_base_url}/api/v1/wallet/health/summary?player_id={self.player_id}")
        print()
        print("📖 Interactive API Documentation:")
        print(f"   Swagger UI: {self.api_base_url}/docs")
        print(f"   OpenAPI JSON: {self.api_base_url}/openapi.json")
    
    def show_json_links(self):
        """Show direct JSON links for easy browser access"""
        self.print_section("📊 DIRECT JSON LINKS")
        
        print("🔗 Click these links to view JSON responses directly in your browser:")
        print()
        print("🎮 Wallet Simulation JSON:")
        print(f"   {self.api_base_url}/api/v1/wallet/simulate/browser")
        print()
        print("🏥 Health Monitoring JSON:")
        print(f"   {self.api_base_url}/api/v1/wallet/health?player_id={self.player_id}")
        print()
        print("📚 Health History JSON:")
        print(f"   {self.api_base_url}/api/v1/wallet/health/history?player_id={self.player_id}")
        print()
        print("📋 Health Summary JSON:")
        print(f"   {self.api_base_url}/api/v1/wallet/health/summary?player_id={self.player_id}")
        print()
        print("🔧 API Health Check JSON:")
        print(f"   {self.api_base_url}/health")
        print()
        print("📖 API Documentation:")
        print(f"   Swagger UI: {self.api_base_url}/docs")
        print(f"   OpenAPI Schema: {self.api_base_url}/openapi.json")
        print()
        print("💡 Tip: Right-click and 'Open in new tab' for easy access!")
        print()
        print("🌐 HTML Interface:")
        print(f"   Open 'api_links.html' in your browser for a clickable interface")

    def run_comprehensive_demo(self):
        """Run comprehensive demonstration"""
        self.print_header("🚀 ECONOMY MANAGEMENT API - COMPREHENSIVE DEMO")
        
        print(f"🎯 Demo Player ID: {self.player_id}")
        print(f"🌐 API Base URL: {self.api_base_url}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.ensure_api_running()
        
        # Run demonstrations
        self.demo_wallet_simulation()
        self.demo_health_monitoring()
        self.demo_health_history()
        self.show_browser_urls()
        
        self.print_header("🎉 DEMONSTRATION COMPLETE!")
        print("✅ All features have been successfully demonstrated!")
        print("🌐 You can now use the browser URLs to test the API interactively.")
        print("📖 Visit the API documentation at: http://localhost:8000/docs")

def show_help():
    """Show detailed help message"""
    print("""
🚀 Economy Management API - Unified Demo & Test Suite
====================================================

USAGE:
    python unified_demo.py [command] [options]

COMMANDS:
    demo        - Run comprehensive API demonstration
    test        - Run API tests
    health      - Run health monitoring demos
    alerts      - Show all types of alerts
    generate    - Generate API output files
    links       - Show direct JSON links for browser access
    server      - Server management (start/stop/status)
    help        - Show this help message

OPTIONS:
    --player-id <id>     - Use specific player ID
    --weeks <n>          - Analysis period in weeks
    --scenarios <n>      - Number of test scenarios
    --output <file>      - Output file for generation
    --type <type>        - Alert type (wallet/health/all)

EXAMPLES:
    python unified_demo.py demo
    python unified_demo.py test
    python unified_demo.py health --scenarios 5
    python unified_demo.py alerts --type wallet
    python unified_demo.py generate --output my_outputs.json
    python unified_demo.py links
    python unified_demo.py server start
    python unified_demo.py server status

FEATURES:
    ✅ Wallet Simulation (One Week)
    ✅ Economy Health Monitoring
    ✅ Health History & Summary
    ✅ Alert Visualization
    ✅ API Output Generation
    ✅ Direct JSON Links
    ✅ Server Management
    ✅ Browser-friendly URLs
""")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    demo_suite = UnifiedDemoSuite()
    
    # Parse options
    options = {}
    for i, arg in enumerate(sys.argv[2:], 2):
        if arg.startswith("--"):
            if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("--"):
                options[arg[2:]] = sys.argv[i + 1]
            else:
                options[arg[2:]] = True
    
    # Set options
    if "player-id" in options:
        demo_suite.player_id = options["player-id"]
    
    if command == "demo":
        demo_suite.run_comprehensive_demo()
    elif command == "test":
        demo_suite.ensure_api_running()
        demo_suite.run_api_tests()
    elif command == "health":
        demo_suite.ensure_api_running()
        scenarios = int(options.get("scenarios", 3))
        demo_suite.demo_health_monitoring(scenarios)
    elif command == "alerts":
        demo_suite.ensure_api_running()
        alert_type = options.get("type", "all")
        demo_suite.show_alerts(alert_type)
    elif command == "generate":
        demo_suite.ensure_api_running()
        output_file = options.get("output", "api_outputs.json")
        demo_suite.generate_api_outputs(output_file)
    elif command == "links":
        demo_suite.show_json_links()
    elif command == "server":
        if len(sys.argv) < 3:
            print("❌ Server command requires action: start, stop, or status")
            return
        action = sys.argv[2].lower()
        demo_suite.manage_server(action)
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()
