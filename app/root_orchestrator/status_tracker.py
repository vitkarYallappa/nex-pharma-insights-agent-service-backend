from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import asyncio
import logging
from enum import Enum

from .models import (
    MarketIntelligenceRequest,
    RequestStatus,
    RequestProgress,
    RequestResults
)


class StatusTransition:
    """Represents a valid status transition"""
    
    def __init__(self, from_status: RequestStatus, to_status: RequestStatus, 
                 condition: Optional[Callable] = None, auto_timestamp: bool = True):
        self.from_status = from_status
        self.to_status = to_status
        self.condition = condition
        self.auto_timestamp = auto_timestamp
    
    def is_valid(self, request: MarketIntelligenceRequest) -> bool:
        """Check if transition is valid for the given request"""
        if request.status != self.from_status:
            return False
        
        if self.condition:
            return self.condition(request)
        
        return True


class StatusTracker:
    """
    Unified status tracking and management for market intelligence requests.
    
    This class provides centralized status management, validation, and tracking
    capabilities that can be used by both table and SQS processing strategies.
    """
    
    # Define valid status transitions
    VALID_TRANSITIONS = [
        # From PENDING
        StatusTransition(RequestStatus.PENDING, RequestStatus.PROCESSING),
        StatusTransition(RequestStatus.PENDING, RequestStatus.CANCELLED),
        
        # From PROCESSING
        StatusTransition(RequestStatus.PROCESSING, RequestStatus.EXECUTING),
        StatusTransition(RequestStatus.PROCESSING, RequestStatus.FAILED),
        StatusTransition(RequestStatus.PROCESSING, RequestStatus.CANCELLED),
        
        # From EXECUTING
        StatusTransition(RequestStatus.EXECUTING, RequestStatus.COMPLETED),
        StatusTransition(RequestStatus.EXECUTING, RequestStatus.FAILED),
        StatusTransition(RequestStatus.EXECUTING, RequestStatus.CANCELLED),
        
        # Terminal states (no transitions out)
        # COMPLETED, FAILED, CANCELLED are terminal
    ]
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._status_listeners: List[Callable] = []
        self._progress_listeners: List[Callable] = []
    
    def add_status_listener(self, callback: Callable[[str, RequestStatus, RequestStatus], None]):
        """
        Add a callback to be notified of status changes.
        
        Args:
            callback: Function that takes (request_id, old_status, new_status)
        """
        self._status_listeners.append(callback)
    
    def add_progress_listener(self, callback: Callable[[str, str, float], None]):
        """
        Add a callback to be notified of progress updates.
        
        Args:
            callback: Function that takes (request_id, stage, percentage)
        """
        self._progress_listeners.append(callback)
    
    def validate_status_transition(self, request: MarketIntelligenceRequest, 
                                 new_status: RequestStatus) -> bool:
        """
        Validate if a status transition is allowed.
        
        Args:
            request: The request to check
            new_status: The desired new status
            
        Returns:
            bool: True if transition is valid, False otherwise
        """
        current_status = request.status
        
        # Same status is always valid (idempotent)
        if current_status == new_status:
            return True
        
        # Check if transition is in valid transitions list
        for transition in self.VALID_TRANSITIONS:
            if (transition.from_status == current_status and 
                transition.to_status == new_status and 
                transition.is_valid(request)):
                return True
        
        return False
    
    def update_request_status(self, request: MarketIntelligenceRequest, 
                            new_status: RequestStatus, 
                            message: Optional[str] = None) -> bool:
        """
        Update the status of a request with validation.
        
        Args:
            request: The request to update
            new_status: The new status to set
            message: Optional message describing the change
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        old_status = request.status
        
        # Validate transition
        if not self.validate_status_transition(request, new_status):
            self.logger.warning(
                f"Invalid status transition for request {request.request_id}: "
                f"{old_status} -> {new_status}"
            )
            return False
        
        # Update the request
        try:
            request.update_status(new_status, message)
            
            # Notify listeners
            for listener in self._status_listeners:
                try:
                    listener(request.request_id, old_status, new_status)
                except Exception as e:
                    self.logger.error(f"Status listener error: {e}")
            
            self.logger.info(
                f"Status updated for request {request.request_id}: "
                f"{old_status} -> {new_status}"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update status for request {request.request_id}: {e}")
            return False
    
    def update_request_progress(self, request: MarketIntelligenceRequest,
                              stage: str, percentage: float, **kwargs) -> bool:
        """
        Update the progress of a request.
        
        Args:
            request: The request to update
            stage: Current processing stage
            percentage: Progress percentage (0-100)
            **kwargs: Additional progress data
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            # Validate percentage
            percentage = max(0.0, min(100.0, percentage))
            
            # Update progress
            request.progress.update_progress(stage, percentage, **kwargs)
            
            # Notify listeners
            for listener in self._progress_listeners:
                try:
                    listener(request.request_id, stage, percentage)
                except Exception as e:
                    self.logger.error(f"Progress listener error: {e}")
            
            self.logger.debug(
                f"Progress updated for request {request.request_id}: "
                f"{stage} - {percentage:.1f}%"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update progress for request {request.request_id}: {e}")
            return False
    
    def calculate_progress_percentage(self, stage: str, stage_progress: float = 0.0) -> float:
        """
        Calculate overall progress percentage based on current stage.
        
        Args:
            stage: Current processing stage
            stage_progress: Progress within the current stage (0-100)
            
        Returns:
            float: Overall progress percentage
        """
        # Define stage weights and order
        stage_weights = {
            "initialization": (0, 5),      # 0-5%
            "serp_discovery": (5, 25),     # 5-25%
            "content_extraction": (25, 80), # 25-80%
            "aggregation": (80, 95),       # 80-95%
            "completed": (95, 100)         # 95-100%
        }
        
        if stage not in stage_weights:
            # Unknown stage, estimate based on name
            if "search" in stage.lower() or "serp" in stage.lower():
                stage = "serp_discovery"
            elif "extract" in stage.lower() or "content" in stage.lower():
                stage = "content_extraction"
            elif "aggregat" in stage.lower() or "combin" in stage.lower():
                stage = "aggregation"
            else:
                return 0.0
        
        start_pct, end_pct = stage_weights[stage]
        stage_range = end_pct - start_pct
        
        # Calculate progress within stage
        stage_progress = max(0.0, min(100.0, stage_progress))
        stage_contribution = (stage_progress / 100.0) * stage_range
        
        return start_pct + stage_contribution
    
    def estimate_completion_time(self, request: MarketIntelligenceRequest) -> Optional[datetime]:
        """
        Estimate completion time based on current progress.
        
        Args:
            request: The request to estimate for
            
        Returns:
            Optional[datetime]: Estimated completion time, or None if cannot estimate
        """
        if not request.started_at or request.progress.percentage <= 0:
            return None
        
        try:
            # Calculate elapsed time
            elapsed = datetime.utcnow() - request.started_at
            elapsed_seconds = elapsed.total_seconds()
            
            # Calculate estimated total time based on progress
            if request.progress.percentage >= 100:
                return datetime.utcnow()  # Already complete
            
            estimated_total_seconds = elapsed_seconds / (request.progress.percentage / 100.0)
            remaining_seconds = estimated_total_seconds - elapsed_seconds
            
            # Add some buffer (20%) for safety
            remaining_seconds *= 1.2
            
            return datetime.utcnow() + timedelta(seconds=remaining_seconds)
            
        except (ZeroDivisionError, ValueError):
            return None
    
    def get_status_history(self, request: MarketIntelligenceRequest) -> List[Dict[str, Any]]:
        """
        Get the status change history for a request.
        
        Args:
            request: The request to get history for
            
        Returns:
            List[Dict[str, Any]]: List of status change events
        """
        return request.processing_metadata.get("status_history", [])
    
    def get_processing_duration(self, request: MarketIntelligenceRequest) -> Optional[float]:
        """
        Get the processing duration for a request.
        
        Args:
            request: The request to calculate duration for
            
        Returns:
            Optional[float]: Duration in seconds, or None if not applicable
        """
        return request.get_processing_duration()
    
    def is_request_stale(self, request: MarketIntelligenceRequest, 
                        max_age_hours: int = 24) -> bool:
        """
        Check if a request is stale (stuck in processing too long).
        
        Args:
            request: The request to check
            max_age_hours: Maximum age in hours before considering stale
            
        Returns:
            bool: True if request is stale, False otherwise
        """
        if not request.is_active():
            return False
        
        age = datetime.utcnow() - request.created_at
        return age.total_seconds() > (max_age_hours * 3600)
    
    def get_request_summary(self, request: MarketIntelligenceRequest) -> Dict[str, Any]:
        """
        Get a summary of request status and progress.
        
        Args:
            request: The request to summarize
            
        Returns:
            Dict[str, Any]: Summary information
        """
        duration = self.get_processing_duration(request)
        estimated_completion = self.estimate_completion_time(request)
        
        return {
            "request_id": request.request_id,
            "status": request.status,
            "progress": {
                "stage": request.progress.current_stage,
                "percentage": request.progress.percentage,
                "urls_found": request.progress.urls_found,
                "content_extracted": request.progress.content_extracted,
                "last_updated": request.progress.last_updated.isoformat()
            },
            "timing": {
                "created_at": request.created_at.isoformat(),
                "started_at": request.started_at.isoformat() if request.started_at else None,
                "completed_at": request.completed_at.isoformat() if request.completed_at else None,
                "duration_seconds": duration,
                "estimated_completion": estimated_completion.isoformat() if estimated_completion else None
            },
            "metadata": {
                "priority": request.priority,
                "request_type": request.request_type,
                "processing_strategy": request.processing_strategy,
                "error_count": len(request.errors),
                "warning_count": len(request.warnings),
                "is_stale": self.is_request_stale(request)
            }
        }
    
    def get_status_statistics(self, requests: List[MarketIntelligenceRequest]) -> Dict[str, Any]:
        """
        Get statistics about request statuses.
        
        Args:
            requests: List of requests to analyze
            
        Returns:
            Dict[str, Any]: Status statistics
        """
        if not requests:
            return {
                "total_requests": 0,
                "status_counts": {},
                "average_processing_time": 0.0,
                "success_rate": 0.0
            }
        
        # Count by status
        status_counts = {}
        processing_times = []
        completed_count = 0
        
        for request in requests:
            status = request.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Collect processing times for completed requests
            duration = self.get_processing_duration(request)
            if duration and request.is_completed():
                processing_times.append(duration)
                
            if request.status == RequestStatus.COMPLETED:
                completed_count += 1
        
        # Calculate averages
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0.0
        success_rate = (completed_count / len(requests)) * 100 if requests else 0.0
        
        return {
            "total_requests": len(requests),
            "status_counts": status_counts,
            "average_processing_time": avg_processing_time,
            "success_rate": success_rate,
            "completed_requests": completed_count,
            "active_requests": len([r for r in requests if r.is_active()])
        }


# Global status tracker instance
_status_tracker: Optional[StatusTracker] = None


def get_status_tracker() -> StatusTracker:
    """Get the global status tracker instance."""
    global _status_tracker
    if _status_tracker is None:
        _status_tracker = StatusTracker()
    return _status_tracker


def set_status_tracker(tracker: StatusTracker):
    """Set the global status tracker instance."""
    global _status_tracker
    _status_tracker = tracker 