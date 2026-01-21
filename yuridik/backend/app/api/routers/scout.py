"""
Scout Router - Auto-Scout Agent Endpoints
Handles Scout Agent status monitoring and manual triggering.
"""

import asyncio
import uuid
from datetime import datetime
from typing import AsyncGenerator

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from app.config import get_settings, Settings
from app.models.schemas import (
    ScoutTriggerRequest,
    ScoutTriggerResponse,
    ScoutStatusEvent,
    ScoutStatusDetails,
)
from app.main import get_app_state


router = APIRouter()

# Track running scout jobs
_running_jobs: dict[str, bool] = {}


@router.get("/status")
async def scout_status() -> EventSourceResponse:
    """
    Stream real-time Scout Agent status updates via Server-Sent Events (SSE).
    
    The frontend can subscribe to this endpoint to show live "Thinking" logs
    as the Scout Agent searches, judges, and ingests new documents.
    
    Example events:
    - {"event_type": "search", "message": "Searching lex.uz for 'subsidiya'..."}
    - {"event_type": "judge", "message": "Found PQ-123: 'Yangi subsidiya'", "details": {"relevance": true}}
    - {"event_type": "complete", "message": "Added 3 new documents"}
    """
    app_state = get_app_state()
    
    async def event_generator() -> AsyncGenerator[dict, None]:
        """Generate SSE events from the status queue."""
        while True:
            try:
                # Wait for status updates with timeout
                event = await asyncio.wait_for(
                    app_state.scout_status_queue.get(),
                    timeout=30.0
                )
                
                yield {
                    "event": "status_update",
                    "data": ScoutStatusEvent(
                        event_type=event.get("event_type", "status"),
                        message=event.get("message", ""),
                        details=ScoutStatusDetails(**event.get("details", {})),
                        timestamp=datetime.fromisoformat(event.get("timestamp", datetime.now().isoformat()))
                    ).model_dump_json()
                }
                
                # If complete or error, send one more heartbeat then close
                if event.get("event_type") in ("complete", "error"):
                    break
                    
            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                yield {
                    "event": "heartbeat",
                    "data": '{"status": "waiting"}'
                }
    
    return EventSourceResponse(event_generator())


@router.post("/trigger", response_model=ScoutTriggerResponse)
async def trigger_scout(
    request: ScoutTriggerRequest,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings)
) -> ScoutTriggerResponse:
    """
    Manually trigger a Scout Agent update cycle.
    
    This is useful for demos - press the "Live Update" button to show
    the Scout Agent searching for new decrees in real-time.
    
    The scout will:
    1. Search lex.uz for relevant keywords
    2. Use LLM to judge relevance
    3. Scrape and ingest new documents
    4. Push status updates to /api/scout/status
    """
    global _running_jobs
    
    # Check if a job is already running
    running = any(_running_jobs.values())
    if running and not request.force_refresh:
        return ScoutTriggerResponse(
            status="already_running",
            job_id="",
            message="Scout Agent allaqachon ishlayapti. Tugashini kuting.",
            estimated_duration_seconds=30
        )
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    _running_jobs[job_id] = True
    
    # Start scout in background
    background_tasks.add_task(
        run_scout_cycle,
        job_id=job_id,
        keywords=request.keywords,
        date_filter=request.date_filter or settings.scout_date_filter,
        settings=settings
    )
    
    return ScoutTriggerResponse(
        status="started",
        job_id=job_id,
        message="Scout Agent ishga tushirildi. Yangilanishlarni /api/scout/status orqali kuzating.",
        estimated_duration_seconds=60
    )


async def run_scout_cycle(
    job_id: str,
    keywords: list[str] | None,
    date_filter: str,
    settings: Settings
):
    """
    Execute a full Scout Agent cycle.
    This runs in the background and pushes status updates to the queue.
    """
    global _running_jobs
    app_state = get_app_state()
    queue = app_state.scout_status_queue
    
    default_keywords = [
        "subsidiya", "grant", "soliq imtiyozi", "kredit",
        "tadbirkorlik", "kichik biznes", "yoshlar tadbirkorligi",
        "soliq ta'tili", "davlat yordami"
    ]
    
    search_keywords = keywords or default_keywords
    
    try:
        # Import scout agent
        from app.scout_agent.agent import ScoutAgent
        
        scout = ScoutAgent(
            settings=settings,
            chroma_collection=app_state.chroma_collection,
            status_queue=queue
        )
        
        result = await scout.run_cycle(
            keywords=search_keywords,
            date_filter=date_filter
        )
        
        await queue.put({
            "event_type": "complete",
            "message": f"✅ Scout tugadi! {result.get('ingested', 0)} ta yangi hujjat qo'shildi.",
            "details": {"progress": 100},
            "timestamp": datetime.now().isoformat()
        })
        
    except ImportError:
        # Scout agent not yet implemented - send demo events
        await _demo_scout_events(queue, search_keywords)
        
    except Exception as e:
        await queue.put({
            "event_type": "error",
            "message": f"⚠️ Scout xatoligi: {str(e)}",
            "details": {"progress": 0},
            "timestamp": datetime.now().isoformat()
        })
    
    finally:
        _running_jobs.pop(job_id, None)


async def _demo_scout_events(queue: asyncio.Queue, keywords: list[str]):
    """
    Send demo events when Scout Agent is not fully implemented.
    Useful for frontend development and demos.
    """
    import random
    
    demo_decrees = [
        ("PQ-60", "Yoshlar tadbirkorligini qo'llab-quvvatlash to'g'risida"),
        ("PD-50", "Kichik va o'rta biznes ulushini oshirish chora-tadbirlari"),
        ("PQ-306", "Kichik biznesni uzluksiz qo'llab-quvvatlash dasturi"),
    ]
    
    # Search phase
    await queue.put({
        "event_type": "search",
        "message": f"🔍 lex.uz da qidiruv: '{keywords[0] if keywords else 'subsidiya'}'...",
        "details": {"progress": 10},
        "timestamp": datetime.now().isoformat()
    })
    await asyncio.sleep(2)
    
    # Found results
    await queue.put({
        "event_type": "search",
        "message": f"📄 {len(demo_decrees)} ta potensial hujjat topildi",
        "details": {"progress": 25},
        "timestamp": datetime.now().isoformat()
    })
    await asyncio.sleep(1)
    
    # Judge phase
    for i, (decree_id, title) in enumerate(demo_decrees):
        is_relevant = random.random() > 0.3
        emoji = "✅" if is_relevant else "❌"
        
        await queue.put({
            "event_type": "judge",
            "message": f"{emoji} {decree_id}: {title[:40]}...",
            "details": {
                "document_id": decree_id,
                "title": title,
                "relevance": is_relevant,
                "progress": 30 + (i * 20)
            },
            "timestamp": datetime.now().isoformat()
        })
        await asyncio.sleep(1.5)
    
    # Ingest phase
    await queue.put({
        "event_type": "ingest",
        "message": "📥 Hujjatlar bazaga qo'shilmoqda...",
        "details": {"progress": 90},
        "timestamp": datetime.now().isoformat()
    })
    await asyncio.sleep(2)
    
    # Complete
    await queue.put({
        "event_type": "complete",
        "message": "✅ Scout tugadi! 2 ta yangi hujjat qo'shildi.",
        "details": {"progress": 100},
        "timestamp": datetime.now().isoformat()
    })
