#!/usr/bin/env python3
"""
Script to create DynamoDB tables for local development.
Run this script before starting the FastAPI application.
"""

import boto3
import sys
import os
from botocore.exceptions import ClientError

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config.settings import settings
from app.config.tables import TableConfig


def create_dynamodb_client():
    """Create DynamoDB client for local development."""
    return boto3.client(
        'dynamodb',
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.DYNAMODB_ENDPOINT
    )


def table_exists(client, table_name):
    """Check if a table exists."""
    try:
        client.describe_table(TableName=table_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return False
        raise


def create_table(client, table_name, table_config):
    """Create a DynamoDB table."""
    try:
        print(f"Creating table: {table_name}")
        
        response = client.create_table(
            TableName=table_name,
            KeySchema=table_config['KeySchema'],
            AttributeDefinitions=table_config['AttributeDefinitions'],
            BillingMode=table_config['BillingMode']
        )
        
        print(f"✅ Table {table_name} created successfully!")
        return response
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠️  Table {table_name} already exists")
        else:
            print(f"❌ Error creating table {table_name}: {e}")
            raise


def create_all_tables():
    """Create all required tables for the application."""
    print("🚀 Setting up DynamoDB tables for local development...")
    print(f"📍 DynamoDB endpoint: {settings.DYNAMODB_ENDPOINT}")
    print(f"🏷️  Environment: {settings.TABLE_ENVIRONMENT}")
    print()
    
    # Create DynamoDB client
    try:
        client = create_dynamodb_client()
        print("✅ Connected to DynamoDB")
    except Exception as e:
        print(f"❌ Failed to connect to DynamoDB: {e}")
        print("💡 Make sure DynamoDB Local is running on http://localhost:8000")
        print("   You can start it with: docker run -p 8000:8000 amazon/dynamodb-local")
        return False
    
    # Get table configurations
    table_config = TableConfig(settings.TABLE_ENVIRONMENT)
    table_configs = table_config.get_table_configs()
    
    # Create each table
    created_count = 0
    for table_name, config in table_configs.items():
        if not table_exists(client, table_name):
            create_table(client, table_name, config)
            created_count += 1
        else:
            print(f"✅ Table {table_name} already exists")
    
    print()
    print(f"🎉 Setup complete! {created_count} new tables created.")
    print()
    print("📋 Available tables:")
    for table_name in table_configs.keys():
        print(f"   - {table_name}")
    
    print()
    print("🚀 You can now start the FastAPI application!")
    return True


def list_tables():
    """List all existing tables."""
    try:
        client = create_dynamodb_client()
        response = client.list_tables()
        
        print("📋 Existing DynamoDB tables:")
        if response['TableNames']:
            for table_name in response['TableNames']:
                print(f"   - {table_name}")
        else:
            print("   No tables found")
        
        return response['TableNames']
        
    except Exception as e:
        print(f"❌ Error listing tables: {e}")
        return []


def delete_all_tables():
    """Delete all application tables (for cleanup)."""
    print("🗑️  Deleting all application tables...")
    
    try:
        client = create_dynamodb_client()
        table_config = TableConfig(settings.TABLE_ENVIRONMENT)
        table_names = list(table_config.get_table_configs().keys())
        
        for table_name in table_names:
            if table_exists(client, table_name):
                print(f"Deleting table: {table_name}")
                client.delete_table(TableName=table_name)
                print(f"✅ Table {table_name} deleted")
            else:
                print(f"⚠️  Table {table_name} doesn't exist")
        
        print("🎉 Cleanup complete!")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage DynamoDB tables for local development")
    parser.add_argument("action", choices=["create", "list", "delete"], 
                       help="Action to perform")
    
    args = parser.parse_args()
    
    if args.action == "create":
        create_all_tables()
    elif args.action == "list":
        list_tables()
    elif args.action == "delete":
        delete_all_tables() 