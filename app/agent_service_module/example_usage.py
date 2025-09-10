#!/usr/bin/env python3
"""
Example usage of the Agent Service Module

This demonstrates how to use the modular agent service system.
"""

import asyncio
from config.settings import settings
from agents.agent1_deduplication.service import Agent1DeduplicationService
from agents.agent1_deduplication.models import Agent1DeduplicationRequest

async def example_usage():
    """Example using the agent service."""
    print("=== Agent Service Example ===")
    
    # Create service
    dedup_service = Agent1DeduplicationService()
    
    # Create request
    request = Agent1DeduplicationRequest(
        request_id="example-001",
        content="Sample content for deduplication processing"
    )
    
    # Process request
    response = await dedup_service.process(request)
    print(f"Response: {response.json()}")

def demonstrate_configuration():
    """Demonstrate configuration management."""
    print("\n=== Configuration Management ===")
    
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
    
    # Run example
    await example_usage()
    
    print("\n" + "=" * 50)
    print("Example completed!")

if __name__ == "__main__":
    asyncio.run(main()) 