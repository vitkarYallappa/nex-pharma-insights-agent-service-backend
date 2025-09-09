# DynamoDB Tables Specification for Stage 0 Agents

This document provides the complete table specifications for creating DynamoDB tables required by the Stage 0 agents (`stage0_serp`, `stage0_perplexity`, and `stage0_orchestrator`).

## Overview

The Stage 0 agents require **5 DynamoDB tables** with **5 Global Secondary Indexes (GSI)** to function properly. All tables use PAY_PER_REQUEST billing mode for cost optimization.

## Table Specifications

### 1. `serp_requests`
**Purpose**: SERP search request tracking and metadata

#### Primary Key
- **Partition Key**: `request_id` (String)

#### Attributes
| Attribute | Type | Description |
|-----------|------|-------------|
| `request_id` | String (S) | Primary partition key - unique request identifier |
| `query` | String (S) | Search query text |
| `num_results` | Number (N) | Number of results requested |
| `total_results` | Number (N) | Total results found |
| `successful_results` | Number (N) | Successfully retrieved results |
| `failed_results` | Number (N) | Failed results |
| `search_engine` | String (S) | Search engine used (google, bing, etc.) |
| `language` | String (S) | Search language |
| `country` | String (S) | Search country |
| `storage_key` | String (S) | S3/MinIO storage location |
| `created_at` | String (S) | ISO timestamp |
| `updated_at` | String (S) | ISO timestamp |
| `status` | String (S) | Request status |

#### Global Secondary Indexes
- **GSI Name**: `created_at-index`
  - **Partition Key**: `created_at` (String)
  - **Purpose**: Query requests by creation time

---

### 2. `perplexity_extractions`
**Purpose**: Perplexity content extraction tracking

#### Primary Key
- **Partition Key**: `request_id` (String)

#### Attributes
| Attribute | Type | Description |
|-----------|------|-------------|
| `request_id` | String (S) | Primary partition key - unique request identifier |
| `total_urls` | Number (N) | Total URLs processed |
| `successful_extractions` | Number (N) | Successful extractions |
| `failed_extractions` | Number (N) | Failed extractions |
| `storage_key` | String (S) | S3/MinIO storage location |
| `created_at` | String (S) | ISO timestamp |
| `updated_at` | String (S) | ISO timestamp |
| `status` | String (S) | Extraction status |

#### Global Secondary Indexes
None required.

---

### 3. `perplexity_content`
**Purpose**: Individual content extraction results

#### Primary Key
- **Partition Key**: `content_id` (String) - Format: `{request_id}_{url_hash}`

#### Attributes
| Attribute | Type | Description |
|-----------|------|-------------|
| `content_id` | String (S) | Primary partition key - unique content identifier |
| `request_id` | String (S) | Request identifier |
| `url` | String (S) | Source URL |
| `title` | String (S) | Content title |
| `word_count` | Number (N) | Content word count |
| `extraction_confidence` | Number (N) | Confidence score (0.0-1.0) |
| `content_type` | String (S) | Content type (article, blog, etc.) |
| `language` | String (S) | Content language |
| `created_at` | String (S) | ISO timestamp |

#### Global Secondary Indexes
- **GSI Name**: `request_id-index`
  - **Partition Key**: `request_id` (String)
  - **Purpose**: Query all content items for a specific request

---

### 4. `pipeline_states`
**Purpose**: Pipeline orchestration state tracking

#### Primary Key
- **Partition Key**: `request_id` (String)

#### Attributes
| Attribute | Type | Description |
|-----------|------|-------------|
| `request_id` | String (S) | Primary partition key - unique request identifier |
| `status` | String (S) | Pipeline status (pending, searching, extracting, aggregating, completed, failed, partial_success) |
| `current_stage` | String (S) | Current processing stage |
| `progress_percentage` | Number (N) | Progress percentage (0-100) |
| `search_completed` | Boolean (BOOL) | Search stage completed |
| `extraction_completed` | Boolean (BOOL) | Extraction stage completed |
| `aggregation_completed` | Boolean (BOOL) | Aggregation stage completed |
| `urls_found` | Number (N) | URLs found in search |
| `content_extracted` | Number (N) | Successfully extracted content |
| `content_failed` | Number (N) | Failed content extractions |
| `started_at` | String (S) | ISO timestamp |
| `search_started_at` | String (S) | ISO timestamp |
| `extraction_started_at` | String (S) | ISO timestamp |
| `completed_at` | String (S) | ISO timestamp |
| `errors` | List (L) | Error messages |
| `warnings` | List (L) | Warning messages |

#### Global Secondary Indexes
- **GSI 1 Name**: `status-index`
  - **Partition Key**: `status` (String)
  - **Purpose**: Query pipelines by status
- **GSI 2 Name**: `started_at-index`
  - **Partition Key**: `started_at` (String)
  - **Purpose**: Query pipelines by start time

---

### 5. `pipeline_executions`
**Purpose**: Pipeline execution history and analytics

#### Primary Key
- **Partition Key**: `request_id` (String)

#### Attributes
| Attribute | Type | Description |
|-----------|------|-------------|
| `request_id` | String (S) | Primary partition key - unique request identifier |
| `original_query` | String (S) | Original search query |
| `total_urls` | Number (N) | Total URLs processed |
| `content_extracted` | Number (N) | Content successfully extracted |
| `processing_time` | Number (N) | Total processing time in seconds |
| `final_status` | String (S) | Final pipeline status |
| `storage_paths` | Map (M) | Storage location paths |
| `created_at` | String (S) | ISO timestamp |

#### Global Secondary Indexes
- **GSI Name**: `created_at-index`
  - **Partition Key**: `created_at` (String)
  - **Sort Key**: `request_id` (String)
  - **Purpose**: Query executions by creation time

---

## Summary

### Resource Count
| Resource Type | Count |
|---------------|-------|
| Tables | 5 |
| Global Secondary Indexes | 5 |
| Total Capacity Units | PAY_PER_REQUEST |

### Table Overview
| Table Name | Primary Key | GSI Count | Purpose |
|------------|-------------|-----------|---------|
| `serp_requests` | `request_id` | 1 | SERP search tracking |
| `perplexity_extractions` | `request_id` | 0 | Content extraction metadata |
| `perplexity_content` | `content_id` | 1 | Individual content items |
| `pipeline_states` | `request_id` | 2 | Pipeline state tracking |
| `pipeline_executions` | `request_id` | 1 | Execution history |

## Implementation Notes

1. **Billing Mode**: All tables should use `PAY_PER_REQUEST` for cost optimization
2. **Timestamps**: All timestamp fields use ISO 8601 format (YYYY-MM-DDTHH:MM:SS.sssZ)
3. **Request IDs**: Use UUID format for all request identifiers
4. **Content IDs**: Format as `{request_id}_{url_hash}` for uniqueness
5. **Storage Keys**: Reference S3/MinIO object keys for file storage locations

## Data Types Reference

| DynamoDB Type | Description | Example |
|---------------|-------------|---------|
| String (S) | Text data | "example-request-123" |
| Number (N) | Numeric data | 42, 3.14 |
| Boolean (BOOL) | True/false | true, false |
| List (L) | Array of items | ["error1", "error2"] |
| Map (M) | Key-value pairs | {"key": "value"} |

---

**Created**: $(date)  
**Version**: 1.0  
**Agent Service**: Stage 0 Components 