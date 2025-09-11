#!/usr/bin/env python3
"""
Utility script to toggle between mock and real Bedrock modes in .env file
"""

import os
import sys
import argparse
from pathlib import Path

def find_env_file():
    """Find the .env file in the project root"""
    current_dir = Path(__file__).parent.parent
    env_file = current_dir / ".env"
    
    if not env_file.exists():
        print(f"❌ .env file not found at {env_file}")
        sys.exit(1)
    
    return env_file

def read_env_file(env_file):
    """Read the .env file content"""
    with open(env_file, 'r') as f:
        return f.readlines()

def write_env_file(env_file, lines):
    """Write content back to .env file"""
    with open(env_file, 'w') as f:
        f.writelines(lines)

def toggle_bedrock_mode(mode):
    """Toggle Bedrock mode in .env file"""
    env_file = find_env_file()
    lines = read_env_file(env_file)
    
    # Create backup
    backup_file = f"{env_file}.backup.toggle"
    with open(backup_file, 'w') as f:
        f.writelines(lines)
    print(f"📄 Backup created: {backup_file}")
    
    # Update lines
    updated_lines = []
    bedrock_mock_found = False
    agent3_provider_found = False
    
    for line in lines:
        if line.startswith("BEDROCK_MOCK_MODE="):
            if mode == "mock":
                updated_lines.append("BEDROCK_MOCK_MODE=true\n")
                print("🎭 Set BEDROCK_MOCK_MODE=true")
            else:
                updated_lines.append("BEDROCK_MOCK_MODE=false\n")
                print("🔧 Set BEDROCK_MOCK_MODE=false")
            bedrock_mock_found = True
        elif line.startswith("AGENT3_DEFAULT_API_PROVIDER="):
            if mode == "mock":
                updated_lines.append("AGENT3_DEFAULT_API_PROVIDER=aws_bedrock_mock\n")
                print("🎭 Set AGENT3_DEFAULT_API_PROVIDER=aws_bedrock_mock")
            else:
                updated_lines.append("AGENT3_DEFAULT_API_PROVIDER=aws_bedrock\n")
                print("🔧 Set AGENT3_DEFAULT_API_PROVIDER=aws_bedrock")
            agent3_provider_found = True
        else:
            updated_lines.append(line)
    
    # Add missing variables if not found
    if not bedrock_mock_found:
        # Find a good place to insert (after Agent3 section)
        insert_index = -1
        for i, line in enumerate(updated_lines):
            if "AGENT3_INSIGHTS_ENABLED" in line:
                insert_index = i + 1
                break
        
        if insert_index > 0:
            mock_value = "true" if mode == "mock" else "false"
            updated_lines.insert(insert_index, f"BEDROCK_MOCK_MODE={mock_value}\n")
            print(f"➕ Added BEDROCK_MOCK_MODE={mock_value}")
    
    if not agent3_provider_found:
        provider_value = "aws_bedrock_mock" if mode == "mock" else "aws_bedrock"
        updated_lines.append(f"AGENT3_DEFAULT_API_PROVIDER={provider_value}\n")
        print(f"➕ Added AGENT3_DEFAULT_API_PROVIDER={provider_value}")
    
    # Write updated content
    write_env_file(env_file, updated_lines)
    
    print(f"\n✅ Successfully switched to {mode.upper()} mode!")
    
    if mode == "mock":
        print("\n🎭 Mock Mode Benefits:")
        print("   • No AWS credentials required")
        print("   • Fast response times (~500ms)")
        print("   • No API costs")
        print("   • Realistic pharmaceutical insights")
        print("   • 100% reliable for testing")
    else:
        print("\n🔧 Real Mode Benefits:")
        print("   • Full AI-powered analysis")
        print("   • Dynamic content understanding")
        print("   • Latest model capabilities")
        print("   • Production-ready insights")
        print("\n⚠️  Make sure AWS Bedrock credentials are configured!")

def show_current_mode():
    """Show current Bedrock mode configuration"""
    env_file = find_env_file()
    lines = read_env_file(env_file)
    
    bedrock_mock = None
    agent3_provider = None
    
    for line in lines:
        if line.startswith("BEDROCK_MOCK_MODE="):
            bedrock_mock = line.strip().split("=")[1].lower()
        elif line.startswith("AGENT3_DEFAULT_API_PROVIDER="):
            agent3_provider = line.strip().split("=")[1]
    
    print("📊 Current Bedrock Configuration:")
    print(f"   BEDROCK_MOCK_MODE: {bedrock_mock or 'not set'}")
    print(f"   AGENT3_DEFAULT_API_PROVIDER: {agent3_provider or 'not set'}")
    
    if bedrock_mock == "true" or agent3_provider == "aws_bedrock_mock":
        print("   🎭 Currently in MOCK mode")
    else:
        print("   🔧 Currently in REAL mode")

def main():
    parser = argparse.ArgumentParser(description="Toggle Bedrock mode in .env file")
    parser.add_argument("mode", choices=["mock", "real", "status"], 
                       help="Mode to switch to or 'status' to show current mode")
    
    args = parser.parse_args()
    
    print("🔧 Bedrock Mode Toggle Utility")
    print("=" * 40)
    
    if args.mode == "status":
        show_current_mode()
    else:
        toggle_bedrock_mode(args.mode)

if __name__ == "__main__":
    main() 