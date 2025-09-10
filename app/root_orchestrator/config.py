import os
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class Environment(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class TableStrategyConfig(BaseModel):
    """Configuration for table-based processing strategy"""
    
    # Polling configuration
    polling_interval: float = Field(default=5.0, ge=1.0, le=60.0, description="Polling interval in seconds")
    max_concurrent_requests: int = Field(default=1, ge=1, le=10, description="Maximum concurrent requests")
    
    # Database configuration
    table_name: str = Field(default="market_intelligence_requests", description="Database table name")
    status_update_interval: float = Field(default=10.0, ge=1.0, le=60.0, description="Status update interval")
    
    # Cleanup configuration
    cleanup_completed_after: int = Field(default=86400, ge=3600, description="Cleanup completed requests after seconds")
    cleanup_failed_after: int = Field(default=172800, ge=3600, description="Cleanup failed requests after seconds")
    
    # Performance tuning
    batch_query_size: int = Field(default=10, ge=1, le=100, description="Batch size for querying requests")
    connection_pool_size: int = Field(default=5, ge=1, le=20, description="Database connection pool size")
    
    # Retry configuration
    max_processing_retries: int = Field(default=3, ge=1, le=10, description="Max retries for processing")
    retry_delay_base: float = Field(default=2.0, ge=1.0, le=10.0, description="Base delay for exponential backoff")
    
    # Perplexity API configuration
    perplexity_model: str = Field(default="llama-3.1-sonar-small-128k-online", description="Perplexity model to use")
    perplexity_max_tokens: int = Field(default=1024, ge=100, le=4000, description="Max tokens per Perplexity request")
    perplexity_temperature: float = Field(default=0.2, ge=0.0, le=1.0, description="Perplexity temperature setting")
    perplexity_rate_limit_delay: float = Field(default=1.0, ge=0.1, le=5.0, description="Delay between Perplexity API calls")
    perplexity_timeout: float = Field(default=30.0, ge=5.0, le=120.0, description="Perplexity API timeout in seconds")
    
    # Content generation configuration
    enable_market_summary: bool = Field(default=True, description="Enable market summary generation")
    enable_competitive_analysis: bool = Field(default=True, description="Enable competitive analysis")
    enable_regulatory_insights: bool = Field(default=True, description="Enable regulatory insights")
    enable_market_implications: bool = Field(default=True, description="Enable market implications")
    
    # SERP API configuration
    serp_engine: str = Field(default="google", description="SERP search engine")
    serp_language: str = Field(default="en", description="SERP search language")
    serp_country: str = Field(default="us", description="SERP search country")
    serp_results_per_domain: int = Field(default=5, ge=1, le=20, description="Max results per domain")
    serp_rate_limit_delay: float = Field(default=0.2, ge=0.1, le=2.0, description="Delay between SERP API calls")
    serp_timeout: float = Field(default=30.0, ge=5.0, le=120.0, description="SERP API timeout in seconds")
    
    # URL discovery configuration
    enable_url_discovery: bool = Field(default=True, description="Enable URL discovery via SERP")
    max_urls_per_analysis: int = Field(default=20, ge=5, le=50, description="Max URLs to use for analysis")
    source_domains: List[str] = Field(
        default=[
            "reuters.com", "fda.gov", "clinicaltrials.gov", 
            "pharmaphorum.com", "ema.europa.eu", "nih.gov"
        ],
        description="Domains to search for relevant content"
    )
    search_keywords: List[str] = Field(
        default=[
            "semaglutide", "tirzepatide", "wegovy", "ozempic", "mounjaro",
            "obesity drug", "weight loss medication", "GLP-1 receptor agonist"
        ],
        description="Keywords for content discovery"
    )
    
    @validator('polling_interval')
    def validate_polling_interval(cls, v):
        """Validate polling interval is reasonable"""
        if v < 1.0:
            raise ValueError("Polling interval must be at least 1 second")
        return v
    
    @validator('perplexity_model')
    def validate_perplexity_model(cls, v):
        """Validate Perplexity model name"""
        valid_models = [
            "llama-3.1-sonar-small-128k-online",
            "llama-3.1-sonar-large-128k-online", 
            "llama-3.1-sonar-huge-128k-online"
        ]
        if v not in valid_models:
            raise ValueError(f"Perplexity model must be one of {valid_models}")
        return v


class SQSStrategyConfig(BaseModel):
    """Configuration for SQS-based processing strategy"""
    
    # Queue configuration
    main_queue_url: str = Field(..., description="Main SQS queue URL")
    dlq_url: str = Field(..., description="Dead Letter Queue URL")
    
    # Worker configuration
    max_workers: int = Field(default=5, ge=1, le=50, description="Maximum number of worker processes")
    worker_timeout: int = Field(default=300, ge=60, le=3600, description="Worker timeout in seconds")
    
    # SQS settings
    visibility_timeout: int = Field(default=300, ge=30, le=43200, description="Message visibility timeout")
    max_receive_count: int = Field(default=3, ge=1, le=10, description="Max receive count before DLQ")
    long_polling_wait_time: int = Field(default=20, ge=1, le=20, description="Long polling wait time")
    
    # Retry configuration
    max_retries: int = Field(default=3, ge=1, le=10, description="Maximum retry attempts")
    retry_delay_base: float = Field(default=2.0, ge=1.0, le=10.0, description="Base delay for exponential backoff")
    
    # Batch processing
    max_messages_per_batch: int = Field(default=1, ge=1, le=10, description="Max messages per batch")
    batch_processing_enabled: bool = Field(default=False, description="Enable batch processing")
    
    # AWS configuration
    aws_region: str = Field(default="us-east-1", description="AWS region")
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS access key ID")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS secret access key")
    
    @validator('main_queue_url', 'dlq_url')
    def validate_queue_urls(cls, v):
        """Validate SQS queue URLs"""
        if not v.startswith('https://sqs.'):
            raise ValueError("Queue URL must be a valid SQS URL")
        return v


class DatabaseConfig(BaseModel):
    """Database configuration"""
    
    # Connection settings
    connection_string: Optional[str] = Field(default=None, description="Database connection string")
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, ge=1, le=65535, description="Database port")
    database: str = Field(default="market_intelligence", description="Database name")
    username: Optional[str] = Field(default=None, description="Database username")
    password: Optional[str] = Field(default=None, description="Database password")
    
    # Pool settings
    pool_size: int = Field(default=10, ge=1, le=50, description="Connection pool size")
    max_overflow: int = Field(default=20, ge=0, le=100, description="Max pool overflow")
    pool_timeout: int = Field(default=30, ge=1, le=300, description="Pool timeout in seconds")
    
    # DynamoDB settings (for existing infrastructure)
    dynamodb_table_name: str = Field(default="market_intelligence_requests", description="DynamoDB table name")
    dynamodb_region: str = Field(default="us-east-1", description="DynamoDB region")


class LoggingConfig(BaseModel):
    """Logging configuration"""
    
    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log format")
    
    # File logging
    log_file: Optional[str] = Field(default=None, description="Log file path")
    max_file_size: int = Field(default=10485760, description="Max log file size in bytes (10MB)")
    backup_count: int = Field(default=5, description="Number of backup log files")
    
    # Structured logging
    json_logging: bool = Field(default=False, description="Enable JSON structured logging")
    include_request_id: bool = Field(default=True, description="Include request ID in logs")
    
    @validator('level')
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()


class MonitoringConfig(BaseModel):
    """Monitoring and metrics configuration"""
    
    # Metrics collection
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    metrics_interval: int = Field(default=60, ge=10, le=3600, description="Metrics collection interval")
    
    # Health checks
    health_check_interval: int = Field(default=30, ge=10, le=300, description="Health check interval")
    health_check_timeout: int = Field(default=10, ge=1, le=60, description="Health check timeout")
    
    # Alerting
    enable_alerts: bool = Field(default=False, description="Enable alerting")
    alert_thresholds: Dict[str, float] = Field(default_factory=lambda: {
        "error_rate": 0.05,  # 5% error rate
        "processing_time": 300.0,  # 5 minutes
        "queue_depth": 100  # 100 messages
    }, description="Alert thresholds")


class RootOrchestratorConfig(BaseModel):
    """Main configuration for Root Orchestrator"""
    
    # Environment
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Environment type")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Processing strategy
    default_strategy: str = Field(default="table", description="Default processing strategy")
    
    # Strategy configurations
    table_config: TableStrategyConfig = Field(default_factory=TableStrategyConfig, description="Table strategy config")
    sqs_config: Optional[SQSStrategyConfig] = Field(default=None, description="SQS strategy config")
    
    # Database configuration
    database_config: DatabaseConfig = Field(default_factory=DatabaseConfig, description="Database configuration")
    
    # Logging configuration
    logging_config: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging configuration")
    
    # Monitoring configuration
    monitoring_config: MonitoringConfig = Field(default_factory=MonitoringConfig, description="Monitoring configuration")
    
    # Market Intelligence Service integration
    market_intelligence_service_timeout: int = Field(default=1800, ge=60, le=7200, description="Service timeout in seconds")
    
    # API configuration
    api_timeout: int = Field(default=30, ge=5, le=300, description="API timeout in seconds")
    max_request_size: int = Field(default=1048576, description="Max request size in bytes (1MB)")
    
    @validator('default_strategy')
    def validate_default_strategy(cls, v):
        """Validate default strategy"""
        valid_strategies = ["table", "sqs"]
        if v not in valid_strategies:
            raise ValueError(f"Default strategy must be one of {valid_strategies}")
        return v
    
    @classmethod
    def from_environment(cls) -> "RootOrchestratorConfig":
        """Create configuration from environment variables"""
        
        # Determine environment
        env_name = os.getenv("ENVIRONMENT", "development").lower()
        try:
            environment = Environment(env_name)
        except ValueError:
            environment = Environment.DEVELOPMENT
        
        # Basic configuration
        config_data = {
            "environment": environment,
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "default_strategy": os.getenv("DEFAULT_PROCESSING_STRATEGY", "table"),
        }
        
        # Table strategy configuration
        table_config = TableStrategyConfig(
            polling_interval=float(os.getenv("TABLE_POLLING_INTERVAL", "5.0")),
            max_concurrent_requests=int(os.getenv("TABLE_MAX_CONCURRENT", "1")),
            table_name=os.getenv("TABLE_NAME", "market_intelligence_requests"),
            cleanup_completed_after=int(os.getenv("CLEANUP_COMPLETED_AFTER", "86400")),
        )
        config_data["table_config"] = table_config
        
        # SQS strategy configuration (if enabled)
        main_queue_url = os.getenv("SQS_MAIN_QUEUE_URL")
        dlq_url = os.getenv("SQS_DLQ_URL")
        
        if main_queue_url and dlq_url:
            sqs_config = SQSStrategyConfig(
                main_queue_url=main_queue_url,
                dlq_url=dlq_url,
                max_workers=int(os.getenv("SQS_MAX_WORKERS", "5")),
                visibility_timeout=int(os.getenv("SQS_VISIBILITY_TIMEOUT", "300")),
                aws_region=os.getenv("AWS_REGION", "us-east-1"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            )
            config_data["sqs_config"] = sqs_config
        
        # Database configuration
        database_config = DatabaseConfig(
            connection_string=os.getenv("DATABASE_URL"),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "market_intelligence"),
            username=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            dynamodb_table_name=os.getenv("DYNAMODB_TABLE_NAME", "market_intelligence_requests"),
            dynamodb_region=os.getenv("DYNAMODB_REGION", "us-east-1"),
        )
        config_data["database_config"] = database_config
        
        # Logging configuration
        logging_config = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE"),
            json_logging=os.getenv("JSON_LOGGING", "false").lower() == "true",
        )
        config_data["logging_config"] = logging_config
        
        # Monitoring configuration
        monitoring_config = MonitoringConfig(
            enable_metrics=os.getenv("ENABLE_METRICS", "true").lower() == "true",
            enable_alerts=os.getenv("ENABLE_ALERTS", "false").lower() == "true",
        )
        config_data["monitoring_config"] = monitoring_config
        
        return cls(**config_data)
    
    def get_strategy_config(self, strategy: str) -> Dict[str, Any]:
        """Get configuration for specific strategy"""
        if strategy == "table":
            return self.table_config.dict()
        elif strategy == "sqs":
            if self.sqs_config:
                return self.sqs_config.dict()
            else:
                raise ValueError("SQS configuration not available")
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def is_sqs_enabled(self) -> bool:
        """Check if SQS strategy is enabled"""
        return self.sqs_config is not None
    
    def validate_strategy(self, strategy: str) -> bool:
        """Validate if strategy is available"""
        if strategy == "table":
            return True
        elif strategy == "sqs":
            return self.is_sqs_enabled()
        else:
            return False


# Global configuration instance
_config: Optional[RootOrchestratorConfig] = None


def get_config() -> RootOrchestratorConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = RootOrchestratorConfig.from_environment()
    return _config


def set_config(config: RootOrchestratorConfig):
    """Set global configuration instance"""
    global _config
    _config = config


def reload_config():
    """Reload configuration from environment"""
    global _config
    _config = RootOrchestratorConfig.from_environment()


# Configuration factory functions
def create_development_config() -> RootOrchestratorConfig:
    """Create development configuration"""
    return RootOrchestratorConfig(
        environment=Environment.DEVELOPMENT,
        debug=True,
        default_strategy="table",
        table_config=TableStrategyConfig(
            polling_interval=2.0,
            max_concurrent_requests=1,
        ),
        logging_config=LoggingConfig(
            level="DEBUG",
            json_logging=False,
        ),
        monitoring_config=MonitoringConfig(
            enable_metrics=True,
            enable_alerts=False,
        )
    )


def create_production_config() -> RootOrchestratorConfig:
    """Create production configuration"""
    return RootOrchestratorConfig(
        environment=Environment.PRODUCTION,
        debug=False,
        default_strategy="sqs",  # Use SQS for production scalability
        table_config=TableStrategyConfig(
            polling_interval=10.0,
            max_concurrent_requests=3,
            cleanup_completed_after=86400,  # 24 hours
        ),
        logging_config=LoggingConfig(
            level="INFO",
            json_logging=True,
            include_request_id=True,
        ),
        monitoring_config=MonitoringConfig(
            enable_metrics=True,
            enable_alerts=True,
        )
    ) 