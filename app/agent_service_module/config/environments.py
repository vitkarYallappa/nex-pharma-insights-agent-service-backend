from .settings import Environment, Settings

class EnvironmentConfig:
    @staticmethod
    def get_config(env: Environment) -> dict:
        configs = {
            Environment.LOCAL: {
                "USE_MOCK_APIS": False,
                "USE_MOCK_STORAGE": False,
                "USE_MOCK_DATABASE": False,
                "STORAGE_TYPE": "minio",
                "DYNAMODB_ENDPOINT": "http://localhost:8000"
            },
            Environment.DEV: {
                "USE_MOCK_APIS": False,
                "USE_MOCK_STORAGE": False,
                "USE_MOCK_DATABASE": False,
                "STORAGE_TYPE": "s3",
                "DYNAMODB_ENDPOINT": None  # Use AWS DynamoDB
            },
            Environment.STAGING: {
                "USE_MOCK_APIS": False,
                "USE_MOCK_STORAGE": False,
                "USE_MOCK_DATABASE": False,
                "STORAGE_TYPE": "s3",
                "DYNAMODB_ENDPOINT": None
            },
            Environment.PROD: {
                "USE_MOCK_APIS": False,
                "USE_MOCK_STORAGE": False,
                "USE_MOCK_DATABASE": False,
                "STORAGE_TYPE": "s3",
                "DYNAMODB_ENDPOINT": None
            },
            Environment.MOCK: {
                "USE_MOCK_APIS": True,
                "USE_MOCK_STORAGE": True,
                "USE_MOCK_DATABASE": True,
                "STORAGE_TYPE": "mock",
                "DYNAMODB_ENDPOINT": "mock"
            }
        }
        return configs.get(env, configs[Environment.LOCAL]) 