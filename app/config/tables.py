from typing import Dict, Any


class TableNames:
    """Table name management for different environments"""
    
    @staticmethod
    def get_users_table(environment: str) -> str:
        """Get users table name for environment"""
        return f"users-{environment}"
    
    @staticmethod
    def get_projects_table(environment: str) -> str:
        """Get projects table name for environment"""
        return f"projects_details-{environment}"
    
    @staticmethod
    def get_requests_table(environment: str) -> str:
        """Get requests table name for environment"""
        return f"requests-{environment}"
    
    @staticmethod
    def get_content_repository_table(environment: str) -> str:
        """Get content repository table name for environment"""
        return f"content_repository-{environment}"


class TableConfig:
    """Table configuration for different environments"""
    
    def __init__(self, environment: str = "local"):
        self.environment = environment
    
    @property
    def users_table(self) -> str:
        return TableNames.get_users_table(self.environment)
    
    @property
    def projects_table(self) -> str:
        return TableNames.get_projects_table(self.environment)
    
    @property
    def requests_table(self) -> str:
        return TableNames.get_requests_table(self.environment)
    
    @property
    def content_repository_table(self) -> str:
        return TableNames.get_content_repository_table(self.environment)
    
    def get_all_tables(self) -> Dict[str, str]:
        """Get all table names as a dictionary"""
        return {
            "users": self.users_table,
            "projects": self.projects_table,
            "requests": self.requests_table,
            "content_repository": self.content_repository_table
        }
    
    def get_table_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get table configurations for creation"""
        return {
            self.users_table: {
                "KeySchema": [
                    {"AttributeName": "id", "KeyType": "HASH"}
                ],
                "AttributeDefinitions": [
                    {"AttributeName": "id", "AttributeType": "S"}
                ],
                "BillingMode": "PAY_PER_REQUEST"
            },
            self.projects_table: {
                "KeySchema": [
                    {"AttributeName": "id", "KeyType": "HASH"}
                ],
                "AttributeDefinitions": [
                    {"AttributeName": "id", "AttributeType": "S"}
                ],
                "BillingMode": "PAY_PER_REQUEST"
            },
            self.requests_table: {
                "KeySchema": [
                    {"AttributeName": "id", "KeyType": "HASH"}
                ],
                "AttributeDefinitions": [
                    {"AttributeName": "id", "AttributeType": "S"}
                ],
                "BillingMode": "PAY_PER_REQUEST"
            },
            self.content_repository_table: {
                "KeySchema": [
                    {"AttributeName": "id", "KeyType": "HASH"}
                ],
                "AttributeDefinitions": [
                    {"AttributeName": "id", "AttributeType": "S"}
                ],
                "BillingMode": "PAY_PER_REQUEST"
            }
        } 