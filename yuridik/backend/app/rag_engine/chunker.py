"""
Uzbek Legal Text Chunker
Intelligent chunking strategy for legal documents that respects
the natural structure of Uzbek decrees and resolutions.
"""

import re
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Chunk:
    """Represents a chunk of legal text."""
    text: str
    index: int
    document_id: str
    article: Optional[str] = None
    chunk_type: str = "text"
    metadata: dict = field(default_factory=dict)


class UzbekLegalChunker:
    """
    Intelligent chunker for Uzbek/Russian legal documents.
    Respects the natural structure of decrees and resolutions.
    
    Chunking Hierarchy:
    1. Split by Articles (Modda) - highest priority
    2. Split by numbered sections within articles
    3. Recursive character splitting for very long sections
    """
    
    # Uzbek legal document patterns
    ARTICLE_PATTERNS = [
        r'(\d+)\s*[-–—]\s*(modda|Modda|MODDA)',  # "1-modda" (Article 1)
        r'(Modda|MODDA)\s+(\d+)',                 # "Modda 1"
        r'^(\d+)\.\s+(?=\S)',                     # "1. Belgilash..." at line start
    ]
    
    SECTION_PATTERNS = [
        r'^(I{1,3}V?|V?I{0,3})\.\s+',            # Roman numerals at start
        r'^(\d+)\)\s+',                           # "1) text..."
        r'^([а-яa-z])\)\s+',                      # "a) text..."
    ]
    
    # Chunk size settings (in characters, ~4 chars per token)
    TARGET_CHUNK_SIZE = 2048      # ~512 tokens
    MAX_CHUNK_SIZE = 3200         # ~800 tokens
    MIN_CHUNK_SIZE = 200          # ~50 tokens
    OVERLAP_SIZE = 400            # ~100 tokens
    
    def __init__(
        self,
        target_size: int = 2048,
        max_size: int = 3200,
        overlap: int = 400
    ):
        self.target_size = target_size
        self.max_size = max_size
        self.overlap = overlap
    
    def chunk_document(
        self,
        text: str,
        document_id: str,
        title: str = "",
        metadata: Optional[dict] = None
    ) -> list[Chunk]:
        """
        Main chunking method.
        
        Args:
            text: The full document text
            document_id: Identifier like "PQ-60"
            title: Document title
            metadata: Additional metadata to attach
        
        Returns:
            List of Chunk objects
        """
        if not text or not text.strip():
            return []
        
        base_metadata = metadata or {}
        base_metadata["document_id"] = document_id
        base_metadata["title"] = title
        
        # Clean the text
        text = self._clean_text(text)
        
        # Step 1: Try to split by articles
        articles = self._split_by_articles(text)
        
        chunks = []
        chunk_index = 0
        
        for article_num, article_text in articles:
            # Check if article fits in one chunk
            if len(article_text) <= self.target_size:
                chunks.append(Chunk(
                    text=article_text,
                    index=chunk_index,
                    document_id=document_id,
                    article=article_num,
                    chunk_type="full_article",
                    metadata={**base_metadata, "article": article_num}
                ))
                chunk_index += 1
            else:
                # Split large articles by sections
                sections = self._split_by_sections(article_text)
                
                for section_text in sections:
                    if len(section_text) <= self.target_size:
                        chunks.append(Chunk(
                            text=section_text,
                            index=chunk_index,
                            document_id=document_id,
                            article=article_num,
                            chunk_type="section",
                            metadata={**base_metadata, "article": article_num}
                        ))
                        chunk_index += 1
                    else:
                        # Recursive split for very long sections
                        sub_chunks = self._recursive_split(section_text)
                        for sub in sub_chunks:
                            chunks.append(Chunk(
                                text=sub,
                                index=chunk_index,
                                document_id=document_id,
                                article=article_num,
                                chunk_type="sub_section",
                                metadata={**base_metadata, "article": article_num}
                            ))
                            chunk_index += 1
        
        # Add overlap
        chunks = self._add_overlap(chunks)
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    
    def _split_by_articles(self, text: str) -> list[tuple[str, str]]:
        """
        Split text by article markers.
        Returns list of (article_number, article_text) tuples.
        """
        # Combined pattern for all article formats
        pattern = r'(?:(\d+)\s*[-–—]\s*(?:modda|Modda|MODDA)|(?:Modda|MODDA)\s+(\d+))'
        
        matches = list(re.finditer(pattern, text))
        
        if not matches:
            # No articles found, return as single chunk
            return [("general", text)]
        
        articles = []
        for i, match in enumerate(matches):
            article_num = match.group(1) or match.group(2)
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            
            article_text = text[start:end].strip()
            if article_text:
                articles.append((f"{article_num}-modda", article_text))
        
        # Handle text before first article
        if matches and matches[0].start() > self.MIN_CHUNK_SIZE:
            preamble = text[:matches[0].start()].strip()
            if preamble:
                articles.insert(0, ("preamble", preamble))
        
        return articles
    
    def _split_by_sections(self, text: str) -> list[str]:
        """Split text by numbered/lettered sections."""
        # Try paragraph splits first
        paragraphs = text.split('\n\n')
        
        if len(paragraphs) > 1:
            # Merge small paragraphs
            sections = []
            current = []
            current_len = 0
            
            for para in paragraphs:
                if current_len + len(para) <= self.target_size:
                    current.append(para)
                    current_len += len(para)
                else:
                    if current:
                        sections.append('\n\n'.join(current))
                    current = [para]
                    current_len = len(para)
            
            if current:
                sections.append('\n\n'.join(current))
            
            return sections
        
        return [text]
    
    def _recursive_split(self, text: str) -> list[str]:
        """
        Recursively split text using hierarchical separators.
        Similar to LangChain's RecursiveCharacterTextSplitter.
        """
        separators = ['\n\n', '\n', '. ', ', ', ' ']
        
        for sep in separators:
            if sep in text:
                parts = text.split(sep)
                result = []
                current = []
                current_len = 0
                
                for part in parts:
                    part_with_sep = part + sep if sep != ' ' else part + ' '
                    
                    if current_len + len(part_with_sep) <= self.target_size:
                        current.append(part)
                        current_len += len(part_with_sep)
                    else:
                        if current:
                            result.append(sep.join(current))
                        current = [part]
                        current_len = len(part_with_sep)
                
                if current:
                    result.append(sep.join(current))
                
                if result:
                    return result
        
        # Fallback: hard split by character count
        return [text[i:i+self.target_size] for i in range(0, len(text), self.target_size)]
    
    def _add_overlap(self, chunks: list[Chunk]) -> list[Chunk]:
        """Add overlap text from previous chunk to maintain context."""
        if len(chunks) <= 1:
            return chunks
        
        for i in range(1, len(chunks)):
            prev_text = chunks[i-1].text
            if len(prev_text) > self.overlap:
                overlap_text = prev_text[-self.overlap:]
                # Start overlap at a word boundary
                space_idx = overlap_text.find(' ')
                if space_idx > 0:
                    overlap_text = overlap_text[space_idx+1:]
                chunks[i].text = f"...{overlap_text}\n\n{chunks[i].text}"
        
        return chunks


# Convenience function
def chunk_legal_document(
    text: str,
    document_id: str,
    title: str = "",
    metadata: Optional[dict] = None
) -> list[Chunk]:
    """Chunk a legal document using the default chunker settings."""
    chunker = UzbekLegalChunker()
    return chunker.chunk_document(text, document_id, title, metadata)
