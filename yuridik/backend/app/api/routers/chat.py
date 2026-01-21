"""
Chat Router - RAG-based Chat Endpoint
Handles user queries about entrepreneur privileges.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends

from app.config import get_settings, Settings
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    DocumentSource,
    MatchedPrivilege,
)
from app.main import get_app_state


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    settings: Settings = Depends(get_settings)
) -> ChatResponse:
    """
    Process a chat message using RAG to find relevant privileges.
    
    This endpoint:
    1. Takes the user's question (Uzbek/Russian)
    2. Optionally uses business context for better matching
    3. Retrieves relevant legal documents from ChromaDB
    4. Generates a response using the LLM
    """
    app_state = get_app_state()
    
    # Generate conversation ID if not provided
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    try:
        # Check if ChromaDB is initialized
        if not app_state.chroma_collection:
            raise HTTPException(
                status_code=503,
                detail="Vector database not initialized. Please seed the database first."
            )
        
        # Query ChromaDB for relevant documents
        results = app_state.chroma_collection.query(
            query_texts=[request.message],
            n_results=settings.top_k_results,
            include=["documents", "metadatas", "distances"]
        )
        
        # Process retrieved documents
        sources = []
        context_texts = []
        
        if results and results.get("documents") and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                distance = results["distances"][0][i] if results.get("distances") else 1.0
                
                # Convert distance to relevance score (0-1, higher is better)
                relevance_score = max(0, 1 - distance)
                
                sources.append(DocumentSource(
                    title=metadata.get("title", "Nomsiz hujjat"),
                    document_id=metadata.get("decree_id", metadata.get("document_id", "N/A")),
                    url=metadata.get("source_url"),
                    relevance_score=round(relevance_score, 3),
                    excerpt=doc[:300] + "..." if len(doc) > 300 else doc
                ))
                
                context_texts.append(doc)
        
        # Build context for LLM
        context = "\n\n---\n\n".join(context_texts) if context_texts else "Hech qanday tegishli hujjat topilmadi."
        
        # Build business context string
        business_info = ""
        if request.business_context:
            bc = request.business_context
            parts = []
            if bc.industry:
                parts.append(f"Soha: {bc.industry}")
            if bc.employee_count is not None:
                parts.append(f"Xodimlar: {bc.employee_count}")
            if bc.region:
                parts.append(f"Hudud: {bc.region}")
            if bc.years_in_operation is not None:
                parts.append(f"Faoliyat yili: {bc.years_in_operation}")
            if parts:
                business_info = f"\n\nFoydalanuvchi biznes ma'lumotlari: {', '.join(parts)}"
        
        # Generate response using LLM
        response_text = await generate_llm_response(
            question=request.message,
            context=context,
            business_info=business_info,
            settings=settings
        )
        
        return ChatResponse(
            response=response_text,
            sources=sources,
            matched_privileges=[],  # TODO: Extract specific privileges from response
            conversation_id=conversation_id,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        if settings.debug:
            raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


async def generate_llm_response(
    question: str,
    context: str,
    business_info: str,
    settings: Settings
) -> str:
    """
    Generate response using the configured LLM provider.
    Supports both Groq and Google Gemini.
    """
    
    system_prompt = """Siz O'zbekiston qonunchiligida tadbirkorlar uchun imtiyozlar bo'yicha mutaxassissiz.

Sizning vazifangiz:
1. Foydalanuvchi savoliga topilgan hujjatlar asosida aniq va foydali javob berish
2. Har doim hujjat nomeri (PQ-xxx, PD-xxx) va tegishli moddani ko'rsatish
3. Imtiyozlar haqida tushunarli tilda tushuntirish
4. Agar aniq ma'lumot topilmasa, shunday deb aytish

Javobingiz qisqa, aniq va amaliy bo'lsin. O'zbek tilida javob bering."""

    user_prompt = f"""Savol: {question}
{business_info}

Topilgan hujjatlar:
{context}

Yuqoridagi ma'lumotlar asosida savolga javob bering:"""

    try:
        if settings.llm_provider == "groq":
            return await _call_groq(system_prompt, user_prompt, settings)
        else:
            return await _call_gemini(system_prompt, user_prompt, settings)
    except Exception as e:
        # Fallback response if LLM fails
        return f"Kechirasiz, hozirda javob generatsiya qilishda xatolik yuz berdi. Topilgan hujjatlarni ko'rib chiqing.\n\nXatolik: {str(e)}"


async def _call_groq(system_prompt: str, user_prompt: str, settings: Settings) -> str:
    """Call Groq API."""
    from groq import AsyncGroq
    
    if not settings.groq_api_key:
        raise ValueError("Groq API key not configured")
    
    client = AsyncGroq(api_key=settings.groq_api_key)
    
    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=1024,
        temperature=0.3
    )
    
    return response.choices[0].message.content


async def _call_gemini(system_prompt: str, user_prompt: str, settings: Settings) -> str:
    """Call Google Gemini API."""
    import google.generativeai as genai
    
    if not settings.google_api_key:
        raise ValueError("Google API key not configured")
    
    genai.configure(api_key=settings.google_api_key)
    model = genai.GenerativeModel(settings.llm_model)
    
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    response = await model.generate_content_async(full_prompt)
    
    return response.text
