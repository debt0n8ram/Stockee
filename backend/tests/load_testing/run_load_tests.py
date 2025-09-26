#!/usr/bin/env python3
"""
Load testing runner for the Stockee application.
"""

import os
import sys
import subprocess
import argparse
import time
import json
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run load tests for Stockee backend")
    parser.add_argument("--host", default="http://localhost:8000", help="Target host URL")
    parser.add_argument("--users", type=int, default=10, help="Number of concurrent users")
    parser.add_argument("--spawn-rate", type=int, default=2, help="User spawn rate per second")
    parser.add_argument("--run-time", type=str, default="5m", help="Test run time (e.g., 5m, 1h)")
    parser.add_argument("--user-class", choices=["StockeeUser", "WebSocketOnlyUser", "CacheLoadUser"], 
                       default="StockeeUser", help="User class to test")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--html-report", help="Generate HTML report")
    parser.add_argument("--csv-report", help="Generate CSV report")
    parser.add_argument("--json-report", help="Generate JSON report")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       default="INFO", help="Log level")
    
    args = parser.parse_args()
    
    # Change to load testing directory
    load_test_dir = Path(__file__).parent
    os.chdir(load_test_dir)
    
    # Build locust command
    locust_cmd = [
        "locust",
        "-f", "locustfile.py",
        "--host", args.host,
        "--users", str(args.users),
        "--spawn-rate", str(args.spawn_rate),
        "--run-time", args.run_time,
        "--user-class", args.user_class,
        "--log-level", args.log_level
    ]
    
    # Add headless mode
    if args.headless:
        locust_cmd.append("--headless")
    
    # Add reports
    if args.html_report:
        locust_cmd.extend(["--html", args.html_report])
    
    if args.csv_report:
        locust_cmd.extend(["--csv", args.csv_report])
    
    if args.json_report:
        locust_cmd.extend(["--json", args.json_report])
    
    # Convert to string
    locust_cmd_str = " ".join(locust_cmd)
    
    # Run load test
    success = run_command(locust_cmd_str, f"Load testing with {args.users} users for {args.run_time}")
    
    if success:
        print(f"\n📊 Load test completed successfully!")
        
        if args.html_report:
            print(f"📈 HTML report generated: {args.html_report}")
        
        if args.csv_report:
            print(f"📊 CSV report generated: {args.csv_report}")
        
        if args.json_report:
            print(f"📋 JSON report generated: {args.json_report}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
