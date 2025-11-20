"""
Vector store module for retrieving relevant astrological text from a corpus.
Uses a mock vector store with simulated embeddings for demonstration.
Can be extended with real vector databases (Pinecone, Weaviate, Chroma, etc.)
"""
from typing import List, Dict, Optional, Tuple
import logging
import hashlib
import json

logger = logging.getLogger(__name__)


# Mock astrological text corpus
ASTROLOGICAL_CORPUS = [
    {
        "id": "leo_leadership",
        "text": "Leo individuals possess natural leadership qualities. Their warmth and charisma inspire others. Today, embrace your innate ability to guide and motivate.",
        "zodiac": "Leo",
        "theme": "leadership",
        "keywords": ["leadership", "charisma", "warmth", "inspire"]
    },
    {
        "id": "taurus_grounded",
        "text": "Taurus signs are known for their grounded nature and practical approach. Your reliability helps you handle unexpected work pressure with stability.",
        "zodiac": "Taurus",
        "theme": "stability",
        "keywords": ["grounded", "practical", "reliable", "stability"]
    },
    {
        "id": "aries_energy",
        "text": "Aries brings bold energy and pioneering spirit. Your courage drives you forward. Take initiative on projects that matter to you.",
        "zodiac": "Aries",
        "theme": "energy",
        "keywords": ["bold", "energetic", "courage", "initiative"]
    },
    {
        "id": "gemini_communication",
        "text": "Gemini excels in communication and adaptability. Share your ideas freely and connect with others. Your curiosity opens new doors.",
        "zodiac": "Gemini",
        "theme": "communication",
        "keywords": ["communication", "adaptable", "curiosity", "ideas"]
    },
    {
        "id": "cancer_intuition",
        "text": "Cancer signs are intuitive and nurturing. Trust your inner voice and nurture relationships. Your empathy creates deep connections.",
        "zodiac": "Cancer",
        "theme": "intuition",
        "keywords": ["intuitive", "nurturing", "empathy", "relationships"]
    },
    {
        "id": "virgo_analysis",
        "text": "Virgo's analytical mind helps solve complex problems. Focus on details but maintain the bigger picture. Your precision is valuable.",
        "zodiac": "Virgo",
        "theme": "analysis",
        "keywords": ["analytical", "precision", "details", "problems"]
    },
    {
        "id": "libra_balance",
        "text": "Libra seeks harmony and balance. Your diplomatic nature helps find equilibrium. Seek harmony in relationships and decisions.",
        "zodiac": "Libra",
        "theme": "balance",
        "keywords": ["harmony", "balance", "diplomatic", "equilibrium"]
    },
    {
        "id": "scorpio_intensity",
        "text": "Scorpio's intensity and passion fuel meaningful pursuits. Channel determination into goals. Your depth of feeling is a gift.",
        "zodiac": "Scorpio",
        "theme": "intensity",
        "keywords": ["intense", "passion", "determination", "depth"]
    },
    {
        "id": "sagittarius_adventure",
        "text": "Sagittarius brings adventurous spirit and optimism. Stay open to learning and new opportunities. Your enthusiasm is contagious.",
        "zodiac": "Sagittarius",
        "theme": "adventure",
        "keywords": ["adventurous", "optimistic", "learning", "enthusiasm"]
    },
    {
        "id": "capricorn_ambition",
        "text": "Capricorn's ambition and discipline drive achievement. Stay organized and focused. Your perseverance will pay off.",
        "zodiac": "Capricorn",
        "theme": "ambition",
        "keywords": ["ambition", "discipline", "organized", "perseverance"]
    },
    {
        "id": "aquarius_innovation",
        "text": "Aquarius brings innovative thinking and independence. Embrace your unique ideas and share them. Your idealism inspires others.",
        "zodiac": "Aquarius",
        "theme": "innovation",
        "keywords": ["innovative", "independent", "unique", "idealism"]
    },
    {
        "id": "pisces_compassion",
        "text": "Pisces shows compassion and creativity. Trust your artistic instincts and help those in need. Your empathy makes a difference.",
        "zodiac": "Pisces",
        "theme": "compassion",
        "keywords": ["compassion", "creativity", "artistic", "empathy"]
    }
]


class MockVectorStore:
    """
    Mock vector store for astrological text retrieval.
    Simulates vector similarity search without requiring actual embeddings.
    """
    
    def __init__(self):
        """Initialize the mock vector store."""
        self.corpus = ASTROLOGICAL_CORPUS
        self._embeddings_cache = {}
    
    def _simple_embedding(self, text: str) -> str:
        """
        Generate a simple hash-based "embedding" for mock purposes.
        In production, use real embeddings (sentence-transformers, OpenAI, etc.)
        
        Args:
            text: Text to embed
            
        Returns:
            Hash-based representation
        """
        # Simple hash-based embedding (mock)
        return hashlib.md5(text.lower().encode()).hexdigest()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple similarity score between two texts.
        Uses keyword overlap and zodiac matching.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Simple keyword-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def search(
        self,
        query: str,
        zodiac_sign: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, any]]:
        """
        Search the astrological corpus for relevant texts.
        
        Args:
            query: Search query (e.g., zodiac traits, keywords)
            zodiac_sign: Optional zodiac sign to filter results
            top_k: Number of results to return
            
        Returns:
            List of relevant corpus entries with similarity scores
        """
        results = []
        
        for entry in self.corpus:
            # Filter by zodiac if specified
            if zodiac_sign and entry.get("zodiac") != zodiac_sign:
                continue
            
            # Calculate similarity
            similarity = self._calculate_similarity(query.lower(), entry["text"].lower())
            
            # Boost score if zodiac matches
            if zodiac_sign and entry.get("zodiac") == zodiac_sign:
                similarity += 0.3
            
            # Boost score if keywords match
            query_words = set(query.lower().split())
            entry_keywords = set([k.lower() for k in entry.get("keywords", [])])
            keyword_overlap = len(query_words.intersection(entry_keywords))
            if keyword_overlap > 0:
                similarity += 0.2 * keyword_overlap
            
            # Cap similarity at 1.0
            similarity = min(similarity, 1.0)
            
            if similarity > 0.1:  # Only include relevant results
                results.append({
                    **entry,
                    "similarity": similarity
                })
        
        # Sort by similarity (descending)
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Return top_k results
        return results[:top_k]
    
    def get_by_zodiac(self, zodiac_sign: str) -> List[Dict[str, any]]:
        """
        Get all corpus entries for a specific zodiac sign.
        
        Args:
            zodiac_sign: Zodiac sign name
            
        Returns:
            List of corpus entries for the zodiac sign
        """
        return [
            entry for entry in self.corpus
            if entry.get("zodiac") == zodiac_sign
        ]


# Global vector store instance
_vector_store = None


def get_vector_store() -> MockVectorStore:
    """
    Get or create the global vector store instance.
    
    Returns:
        MockVectorStore instance
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = MockVectorStore()
    return _vector_store


def retrieve_astrological_context(
    zodiac_sign: str,
    traits: str,
    top_k: int = 2
) -> List[str]:
    """
    Retrieve relevant astrological context from the corpus.
    
    Args:
        zodiac_sign: Zodiac sign
        traits: Zodiac traits (for query)
        top_k: Number of contexts to retrieve
        
    Returns:
        List of relevant text snippets
    """
    store = get_vector_store()
    
    # Search with zodiac and traits
    query = f"{zodiac_sign} {traits}"
    results = store.search(query, zodiac_sign=zodiac_sign, top_k=top_k)
    
    # Extract text snippets
    contexts = [result["text"] for result in results]
    
    logger.info(f"Retrieved {len(contexts)} contexts for {zodiac_sign}")
    
    return contexts

