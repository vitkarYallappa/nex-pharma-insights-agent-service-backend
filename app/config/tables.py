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
    
    @staticmethod
    def get_agent3_insights_table(environment: str) -> str:
        """Get Agent 3 insights table name for environment"""
        return f"agent3_insights_results-{environment}"
    
    @staticmethod
    def get_content_insights_table(environment: str) -> str:
        """Get content insights table name for environment"""
        return f"content_insights-{environment}"


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
    
    @property
    def agent3_insights_table(self) -> str:
        return TableNames.get_agent3_insights_table(self.environment)
    
    @property
    def content_insights_table(self) -> str:
        return TableNames.get_content_insights_table(self.environment)
    
    def get_all_tables(self) -> Dict[str, str]:
        """Get all table names as a dictionary"""
        return {
            "users": self.users_table,
            "projects": self.projects_table,
            "requests": self.requests_table,
            "content_repository": self.content_repository_table,
            "agent3_insights": self.agent3_insights_table,
            "content_insights": self.content_insights_table
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
            },
            self.agent3_insights_table: {
                "KeySchema": [
                    {"AttributeName": "request_id", "KeyType": "HASH"},
                    {"AttributeName": "insight_id", "KeyType": "RANGE"}
                ],
                "AttributeDefinitions": [
                    {"AttributeName": "request_id", "AttributeType": "S"},
                    {"AttributeName": "insight_id", "AttributeType": "S"},
                    {"AttributeName": "status", "AttributeType": "S"},
                    {"AttributeName": "timestamp", "AttributeType": "S"}
                ],
                "GlobalSecondaryIndexes": [
                    {
                        "IndexName": "status-timestamp-index",
                        "KeySchema": [
                            {"AttributeName": "status", "KeyType": "HASH"},
                            {"AttributeName": "timestamp", "KeyType": "RANGE"}
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "BillingMode": "PAY_PER_REQUEST"
                    }
                ],
                "BillingMode": "PAY_PER_REQUEST"
            },
            self.content_insights_table: {
                "KeySchema": [
                    {"AttributeName": "pk", "KeyType": "HASH"}
                ],
                "AttributeDefinitions": [
                    {"AttributeName": "pk", "AttributeType": "S"}
                ],
                "BillingMode": "PAY_PER_REQUEST"
            }
        } 