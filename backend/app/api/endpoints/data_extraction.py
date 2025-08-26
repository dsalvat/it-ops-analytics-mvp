from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import httpx
import json
from datetime import datetime, timedelta

from app.api.dependencies import get_database, get_redis_client
from app.schemas.schemas import SLAOverview, TicketAnalysis, SatisfactionMetrics
from app.core.config import settings
from app.services.eazybi_client import EazyBIClient

router = APIRouter()

@router.get("/health")
async def data_health():
    """Check data extraction health"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@router.get("/sla-overview", response_model=SLAOverview)
async def get_sla_overview(
    db: Session = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Get SLA compliance overview"""
    cache_key = "sla_overview"
    
    # Try cache first
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    
    try:
        client = EazyBIClient()
        # Use your existing EazyBI API
        sla_data = await client.get_sla_overview()
        
        # Transform to our schema
        result = SLAOverview(
            total_tickets=sla_data.get("total_tickets", 0),
            p1_within_sla=sla_data.get("p1_within_sla", 0),
            p1_outside_sla=sla_data.get("p1_outside_sla", 0),
            p2_within_sla=sla_data.get("p2_within_sla", 0),
            p2_outside_sla=sla_data.get("p2_outside_sla", 0),
            overall_compliance=sla_data.get("overall_compliance", 0.0)
        )
        
        # Cache for 5 minutes
        redis_client.setex(cache_key, 300, result.model_dump_json())
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching SLA data: {str(e)}")

@router.get("/ticket-analysis", response_model=TicketAnalysis)
async def get_ticket_analysis(
    db: Session = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Get ticket creation and resolution analysis"""
    cache_key = "ticket_analysis"
    
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    
    try:
        client = EazyBIClient()
        ticket_data = await client.get_ticket_analysis()
        
        result = TicketAnalysis(
            created_this_week=ticket_data.get("created_this_week", 0),
            resolved_this_week=ticket_data.get("resolved_this_week", 0),
            pending_tickets=ticket_data.get("pending_tickets", 0),
            avg_resolution_time=ticket_data.get("avg_resolution_time", 0.0),
            by_priority=ticket_data.get("by_priority", {})
        )
        
        redis_client.setex(cache_key, 300, result.model_dump_json())
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching ticket data: {str(e)}")

@router.get("/satisfaction", response_model=SatisfactionMetrics)
async def get_satisfaction_metrics(
    db: Session = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Get user satisfaction metrics"""
    cache_key = "satisfaction_metrics"
    
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    
    try:
        client = EazyBIClient()
        satisfaction_data = await client.get_satisfaction_metrics()
        
        result = SatisfactionMetrics(
            avg_satisfaction=satisfaction_data.get("avg_satisfaction", 0.0),
            total_surveys=satisfaction_data.get("total_surveys", 0),
            completion_rate=satisfaction_data.get("completion_rate", 0.0),
            by_team=satisfaction_data.get("by_team", {})
        )
        
        redis_client.setex(cache_key, 300, result.model_dump_json())
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching satisfaction data: {str(e)}")

@router.post("/refresh-cache")
async def refresh_data_cache(
    redis_client = Depends(get_redis_client)
):
    """Force refresh all cached data"""
    try:
        # Clear cache
        keys = redis_client.keys("*")
        if keys:
            redis_client.delete(*keys)
        
        return {"message": "Cache refreshed successfully", "cleared_keys": len(keys)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing cache: {str(e)}")
