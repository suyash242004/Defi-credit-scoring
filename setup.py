#!/usr/bin/env python3
"""
Setup script for DeFi Credit Scoring System
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements. Please install manually:")
        print("pip install pandas numpy matplotlib seaborn")
        return False
    return True

def validate_installation():
    """Validate that all packages are installed correctly"""
    print("Validating installation...")
    try:
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns
        print("✅ All packages imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def create_sample_json():
    """Create a small sample JSON file for testing"""
    sample_data = [
        {
            "_id": {"$oid": "681d38fed63812d4655f571a"},
            "userWallet": "0x00000000001accfa9cef68cf5371a23025b6d4b6",
            "network": "polygon",
            "protocol": "aave_v2",
            "txHash": "0x695c69acf608fbf5d38e48ca5535e118cc213a89e3d6d2e66e6b0e3b2e8d4190",
            "timestamp": 1629178166,
            "action": "deposit",
            "actionData": {
                "type": "Deposit",
                "amount": "2000000000",
                "assetSymbol": "USDC",
                "assetPriceUSD": "0.9938318274296357543568636362026045"
            }
        },
        {
            "_id": {"$oid": "681d38fed63812d4655f571b"},
            "userWallet": "0x00000000001accfa9cef68cf5371a23025b6d4b6",
            "network": "polygon",
            "protocol": "aave_v2",
            "txHash": "0x695c69acf608fbf5d38e48ca5535e118cc213a89e3d6d2e66e6b0e3b2e8d4191",
            "timestamp": 1629278166,
            "action": "borrow",
            "actionData": {
                "type": "Borrow",
                "amount": "1000000000",
                "assetSymbol": "USDC",
                "assetPriceUSD": "0.9938318274296357543568636362026045"
            }
        },
        {
            "_id": {"$oid": "681d38fed63812d4655f571c"},
            "userWallet": "0x11111111111accfa9cef68cf5371a23025b6d4b7",
            "network": "polygon",
            "protocol": "aave_v2",
            "txHash": "0x695c69acf608fbf5d38e48ca5535e118cc213a89e3d6d2e66e6b0e3b2e8d4192",
            "timestamp": 1629378166,
            "action": "liquidationcall",
            "actionData": {
                "type": "LiquidationCall",
                "amount": "500000000",
                "assetSymbol": "USDC",
                "assetPriceUSD": "0.9938318274296357543568636362026045"
            }
        }
    ]
    
    import json
    with open('sample_transactions.json', 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    print("✅ Created sample_transactions.json for testing")

def main():
    """Main setup function"""
    print("🚀 Setting up DeFi Credit Scoring System")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        return
    
    # Validate installation
    if not validate_installation():
        return
    
    # Create sample data
    create_sample_json()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("1. Replace 'sample_transactions.json' with your actual data file")
    print("2. Run: python defi_credit_scorer.py your_transactions.json")
    print("3. Run: python generate_analysis_md.py")
    print("\nFor testing with sample data:")
    print("python defi_credit_scorer.py sample_transactions.json")

if __name__ == "__main__":
    main()