"""
Scout Agent - Autonomous Document Discovery
Searches lex.uz for new legal documents, judges relevance with LLM,
and ingests them into ChromaDB.
"""

import asyncio
from datetime import datetime
from typing import Optional
import re

import httpx
from bs4 import BeautifulSoup

from app.config import Settings


class ScoutAgent:
    """
    Autonomous agent that discovers and ingests new legal documents.
    
    Workflow:
    1. HUNT: Search lex.uz for keywords using DuckDuckGo
    2. JUDGE: Use LLM to filter by relevance
    3. INGEST: Scrape, chunk, embed, store in ChromaDB
    4. REPORT: Push status updates to the UI queue
    """
    
    DEFAULT_KEYWORDS = [
        "subsidiya", "grant", "soliq imtiyozi", "kredit",
        "tadbirkorlik", "kichik biznes", "yoshlar tadbirkorligi",
        "soliq ta'tili", "davlat yordami", "imtiyozli kredit"
    ]
    
    def __init__(
        self,
        settings: Settings,
        chroma_collection,
        status_queue: asyncio.Queue
    ):
        self.settings = settings
        self.collection = chroma_collection
        self.status_queue = status_queue
        self.search_delay = settings.scout_search_delay_seconds
        self.max_results = settings.scout_max_results_per_keyword
    
    async def run_cycle(
        self,
        keywords: Optional[list[str]] = None,
        date_filter: str = "after:2025-01-01"
    ) -> dict:
        """
        Execute a full scout cycle.
        Returns dict with {ingested: int, checked: int}
        """
        search_keywords = keywords or self.DEFAULT_KEYWORDS
        
        # Step A: HUNT - Search for documents
        await self._push_status("search", "🔍 Qidiruv boshlandi...", progress=5)
        
        candidates = []
        for i, keyword in enumerate(search_keywords):
            try:
                results = await self._search_lex_uz(keyword, date_filter)
                candidates.extend(results)
                
                progress = 5 + int(15 * (i / len(search_keywords)))
                await self._push_status(
                    "search",
                    f"🔍 Qidiruv: '{keyword}' - {len(results)} ta topildi",
                    progress=progress
                )
                
                await asyncio.sleep(self.search_delay)
                
            except Exception as e:
                await self._push_status(
                    "error",
                    f"⚠️ '{keyword}' qidirishda xatolik: {str(e)[:50]}",
                    progress=progress
                )
        
        # Deduplicate by URL
        candidates = self._deduplicate(candidates)
        await self._push_status(
            "search",
            f"📄 Jami {len(candidates)} ta unikal hujjat topildi",
            progress=20
        )
        
        # Step B: JUDGE - LLM relevance filter
        relevant_docs = []
        for i, doc in enumerate(candidates):
            # Skip if already indexed
            if self._is_already_indexed(doc.get("url", "")):
                continue
            
            try:
                is_relevant = await self._judge_relevance(doc.get("title", ""))
                
                progress = 20 + int(50 * (i / max(len(candidates), 1)))
                
                if is_relevant:
                    relevant_docs.append(doc)
                    await self._push_status(
                        "judge",
                        f"✅ Mos: {doc.get('title', '')[:45]}...",
                        document_id=doc.get("decree_id"),
                        progress=progress
                    )
                else:
                    await self._push_status(
                        "judge",
                        f"❌ Mos emas: {doc.get('title', '')[:45]}...",
                        progress=progress
                    )
                
                await asyncio.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                await self._push_status(
                    "error",
                    f"⚠️ Baholashda xatolik: {str(e)[:50]}",
                    progress=progress
                )
        
        # Step C: INGEST - Scrape and store
        ingested_count = 0
        for i, doc in enumerate(relevant_docs):
            try:
                # Scrape full content
                content = await self._scrape_document(doc.get("url", ""))
                
                if not content:
                    continue
                
                # Chunk and embed
                from app.rag_engine.chunker import chunk_legal_document
                
                chunks = chunk_legal_document(
                    text=content,
                    document_id=doc.get("decree_id", "unknown"),
                    title=doc.get("title", ""),
                    metadata={
                        "source_url": doc.get("url"),
                        "date_scraped": datetime.now().isoformat()
                    }
                )
                
                # Add to ChromaDB
                if chunks and self.collection:
                    documents = [c.text for c in chunks]
                    metadatas = [c.metadata for c in chunks]
                    ids = [f"{doc.get('decree_id', 'doc')}_{c.index}" for c in chunks]
                    
                    self.collection.add(
                        documents=documents,
                        metadatas=metadatas,
                        ids=ids
                    )
                
                ingested_count += 1
                progress = 70 + int(25 * (i / max(len(relevant_docs), 1)))
                
                await self._push_status(
                    "ingest",
                    f"📥 Saqlandi: {doc.get('title', '')[:40]}... ({len(chunks)} chunk)",
                    document_id=doc.get("decree_id"),
                    progress=progress
                )
                
            except Exception as e:
                await self._push_status(
                    "error",
                    f"⚠️ Saqlashda xatolik: {str(e)[:50]}",
                    progress=progress
                )
        
        return {"ingested": ingested_count, "checked": len(candidates)}
    
    async def _search_lex_uz(self, keyword: str, date_filter: str) -> list[dict]:
        """Search for documents using DuckDuckGo."""
        try:
            from duckduckgo_search import DDGS
            
            query = f"site:lex.uz {keyword} {date_filter}"
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self.max_results))
            
            documents = []
            for r in results:
                url = r.get("href", "")
                title = r.get("title", "")
                
                # Extract decree ID from URL or title
                decree_id = self._extract_decree_id(url) or self._extract_decree_id(title)
                
                documents.append({
                    "url": url,
                    "title": title,
                    "snippet": r.get("body", ""),
                    "decree_id": decree_id
                })
            
            return documents
            
        except ImportError:
            # Fallback if duckduckgo_search not installed
            return []
        except Exception:
            return []
    
    def _extract_decree_id(self, text: str) -> Optional[str]:
        """Extract decree ID (PQ-xxx, PD-xxx) from text."""
        patterns = [
            r'(PQ[-–]?\d+)',
            r'(PD[-–]?\d+)',
            r'(ПҚ[-–]?\d+)',
            r'(ПФ[-–]?\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).upper().replace('–', '-')
        
        return None
    
    def _deduplicate(self, candidates: list[dict]) -> list[dict]:
        """Remove duplicate documents by URL."""
        seen_urls = set()
        unique = []
        
        for doc in candidates:
            url = doc.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(doc)
        
        return unique
    
    def _is_already_indexed(self, url: str) -> bool:
        """Check if URL is already in the collection."""
        if not self.collection or not url:
            return False
        
        try:
            results = self.collection.get(
                where={"source_url": url},
                limit=1
            )
            return len(results.get("ids", [])) > 0
        except Exception:
            return False
    
    async def _judge_relevance(self, title: str) -> bool:
        """Use LLM to determine if document title is relevant."""
        if not title:
            return False
        
        prompt = f"""Analyze this legal document title from Uzbekistan:
Title: "{title}"

Is this document relevant to BUSINESS FINANCIAL BENEFITS such as:
- Subsidies (subsidiya)
- Grants (grant)
- Tax holidays (soliq ta'tili)
- Preferential loans (imtiyozli kredit)
- Government financial support for entrepreneurs

Answer with ONLY one word: YES or NO"""

        try:
            if self.settings.llm_provider == "groq":
                from groq import AsyncGroq
                
                client = AsyncGroq(api_key=self.settings.groq_api_key)
                response = await client.chat.completions.create(
                    model=self.settings.llm_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=5,
                    temperature=0
                )
                answer = response.choices[0].message.content.strip().upper()
                
            else:  # Gemini
                import google.generativeai as genai
                
                genai.configure(api_key=self.settings.google_api_key)
                model = genai.GenerativeModel(self.settings.llm_model)
                response = await model.generate_content_async(prompt)
                answer = response.text.strip().upper()
            
            return "YES" in answer
            
        except Exception:
            # Default to including document if LLM fails
            return True
    
    async def _scrape_document(self, url: str) -> Optional[str]:
        """Scrape full document content from lex.uz."""
        if not url:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "lxml")
                
                # Try to find the main content area
                content_selectors = [
                    "div.doc-body",
                    "div.document-content",
                    "article",
                    "main",
                    "div.content"
                ]
                
                content = None
                for selector in content_selectors:
                    element = soup.select_one(selector)
                    if element:
                        content = element.get_text(separator="\n", strip=True)
                        break
                
                if not content:
                    # Fallback: get all text
                    content = soup.get_text(separator="\n", strip=True)
                
                # Clean up
                content = re.sub(r'\n{3,}', '\n\n', content)
                content = re.sub(r' {2,}', ' ', content)
                
                return content[:50000]  # Limit size
                
        except Exception:
            return None
    
    async def _push_status(
        self,
        event_type: str,
        message: str,
        document_id: Optional[str] = None,
        progress: int = 0
    ):
        """Push status update to the queue."""
        await self.status_queue.put({
            "event_type": event_type,
            "message": message,
            "details": {
                "document_id": document_id,
                "progress": progress
            },
            "timestamp": datetime.now().isoformat()
        })
