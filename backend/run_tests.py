#!/usr/bin/env python3
"""
Test runner script for the Stockee backend application.
"""

import os
import sys
import subprocess
import argparse
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
    parser = argparse.ArgumentParser(description="Run tests for Stockee backend")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--websocket", action="store_true", help="Run WebSocket tests only")
    parser.add_argument("--cache", action="store_true", help="Run cache tests only")
    parser.add_argument("--ml", action="store_true", help="Run ML tests only")
    parser.add_argument("--social", action="store_true", help="Run social features tests only")
    parser.add_argument("--portfolio", action="store_true", help="Run portfolio tests only")
    parser.add_argument("--trading", action="store_true", help="Run trading tests only")
    parser.add_argument("--market-data", action="store_true", help="Run market data tests only")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    
    args = parser.parse_args()
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Build pytest command
    pytest_cmd = ["python", "-m", "pytest"]
    
    # Add test selection
    if args.unit:
        pytest_cmd.extend(["-m", "unit"])
    elif args.integration:
        pytest_cmd.extend(["-m", "integration"])
    elif args.websocket:
        pytest_cmd.extend(["-m", "websocket"])
    elif args.cache:
        pytest_cmd.extend(["-m", "cache"])
    elif args.ml:
        pytest_cmd.extend(["-m", "ml"])
    elif args.social:
        pytest_cmd.extend(["-m", "social"])
    elif args.portfolio:
        pytest_cmd.extend(["-m", "portfolio"])
    elif args.trading:
        pytest_cmd.extend(["-m", "trading"])
    elif args.market_data:
        pytest_cmd.extend(["-m", "market_data"])
    else:
        # Run all tests
        pytest_cmd.append("tests/")
    
    # Add options
    if args.coverage:
        pytest_cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    if args.parallel:
        pytest_cmd.extend(["-n", "auto"])
    
    if args.verbose:
        pytest_cmd.append("-v")
    
    if args.fast:
        pytest_cmd.extend(["-m", "not slow"])
    
    # Convert to string
    pytest_cmd_str = " ".join(pytest_cmd)
    
    # Run tests
    success = run_command(pytest_cmd_str, "Running tests")
    
    if success and args.coverage:
        print(f"\n📊 Coverage report generated in htmlcov/index.html")
    
    # Run additional checks if tests pass
    if success:
        print(f"\n🧹 Running additional checks...")
        
        # Code formatting check
        run_command("python -m black --check app/", "Code formatting check")
        
        # Import sorting check
        run_command("python -m isort --check-only app/", "Import sorting check")
        
        # Linting
        run_command("python -m flake8 app/", "Code linting")
        
        # Type checking
        run_command("python -m mypy app/", "Type checking")
        
        # Security check
        run_command("python -m bandit -r app/", "Security check")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
