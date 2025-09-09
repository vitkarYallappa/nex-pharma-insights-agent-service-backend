#!/usr/bin/env python3
"""
Example usage of the Agent Service Module

This demonstrates how to use the modular agent service system with
environment-based configuration and factory pattern.
"""

import asyncio
import os
from config.settings import settings, Environment
from agents.agent1_deduplication.service import Agent1DeduplicationService
from agents.agent1_deduplication.models import Agent1DeduplicationRequest

async def example_local_environment():
    """Example using local environment with real APIs."""
    print("=== Local Environment Example ===")
    
    # Set environment
    os.environ['ENVIRONMENT'] = 'local'
    
    # Create service (automatically uses local configuration)
    dedup_service = Agent1DeduplicationService()
    
    # Create request
    request = Agent1DeduplicationRequest(
        request_id="example-001",
        content="Sample content for deduplication processing"
    )
    
    # Process request
    response = await dedup_service.process(request)
    print(f"Response: {response.json()}")

async def example_mock_environment():
    """Example using mock environment for testing."""
    print("\n=== Mock Environment Example ===")
    
    # Set environment to mock
    os.environ['ENVIRONMENT'] = 'mock'
    
    # Create service (automatically uses mock implementations)
    dedup_service = Agent1DeduplicationService()
    
    # Create request
    request = Agent1DeduplicationRequest(
        request_id="mock-001",
        content="Sample content for mock processing"
    )
    
    # Process request (will use mocks)
    response = await dedup_service.process(request)
    print(f"Mock Response: {response.json()}")

async def example_environment_switching():
    """Example showing how easy it is to switch environments."""
    print("\n=== Environment Switching Example ===")
    
    environments = ['local', 'mock', 'prod']
    
    for env in environments:
        print(f"\n--- Switching to {env.upper()} environment ---")
        os.environ['ENVIRONMENT'] = env
        
        # Reload settings to pick up new environment
        from importlib import reload
        from config import settings as settings_module
        reload(settings_module)
        
        # Create service with new environment
        service = Agent1DeduplicationService()
        
        # Show which implementations are being used
        print(f"Environment: {settings_module.settings.ENVIRONMENT}")
        print(f"Using Mock APIs: {settings_module.settings.USE_MOCK_APIS}")
        print(f"Using Mock Storage: {settings_module.settings.USE_MOCK_STORAGE}")
        print(f"Using Mock Database: {settings_module.settings.USE_MOCK_DATABASE}")

def demonstrate_configuration():
    """Demonstrate configuration management."""
    print("\n=== Configuration Management ===")
    
    print(f"Current Environment: {settings.ENVIRONMENT}")
    print(f"Storage Type: {settings.STORAGE_TYPE}")
    print(f"OpenAI Model: {settings.OPENAI_MODEL}")
    print(f"AWS Region: {settings.AWS_REGION}")
    print(f"DynamoDB Endpoint: {settings.DYNAMODB_ENDPOINT}")

async def main():
    """Main example function."""
    print("Agent Service Module - Example Usage")
    print("=" * 50)
    
    # Show current configuration
    demonstrate_configuration()
    
    # Run examples
    await example_local_environment()
    await example_mock_environment()
    await example_environment_switching()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nTo switch environments, set the ENVIRONMENT variable:")
    print("  export ENVIRONMENT=local    # Use local services")
    print("  export ENVIRONMENT=mock     # Use all mocks")
    print("  export ENVIRONMENT=prod     # Use production services")

if __name__ == "__main__":
    asyncio.run(main()) 