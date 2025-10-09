"""Extract knowledge graph entities and relationships from text."""

import re
from typing import List, Dict, Tuple, Optional, Set
import openai
import os


class KnowledgeGraphExtractor:
    """Extract entities and relationships from text to build knowledge graphs."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize knowledge graph extractor.

        Args:
            api_key: OpenAI API key for LLM-based extraction
            model: Model to use for extraction
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = None
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)

    def extract_entities_and_relations(self, text: str, use_llm: bool = True) -> Dict:
        """
        Extract entities and relationships from text.

        Args:
            text: Input text to analyze
            use_llm: Whether to use LLM for extraction (True) or simple pattern matching (False)

        Returns:
            Dict with 'entities' (list of dicts) and 'relations' (list of tuples)
        """
        if use_llm and self.client:
            return self._extract_with_llm(text)
        else:
            return self._extract_with_patterns(text)

    def _extract_with_llm(self, text: str) -> Dict:
        """Use LLM to extract structured knowledge graph information."""
        prompt = f"""Extract entities and relationships from the following text.

Return a JSON object with:
1. "entities": list of objects with "name", "type" (person, organization, location, concept, etc.)
2. "relations": list of objects with "source", "relation", "target"

Text: {text}

Return ONLY valid JSON, no markdown formatting."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a knowledge graph extraction expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)

            # Normalize the result format
            entities = result.get("entities", [])
            relations_raw = result.get("relations", [])

            # Convert relations to tuples
            relations = [
                (r.get("source", ""), r.get("relation", ""), r.get("target", ""))
                for r in relations_raw
            ]

            return {
                "entities": entities,
                "relations": relations
            }

        except Exception as e:
            print(f"LLM extraction failed: {e}, falling back to pattern matching")
            return self._extract_with_patterns(text)

    def _extract_with_patterns(self, text: str) -> Dict:
        """Simple pattern-based extraction (fallback when no LLM available)."""
        # Extract capitalized phrases as potential entities
        entities = []
        entity_set: Set[str] = set()

        # Pattern: capitalized words (potential named entities)
        capitalized_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        matches = re.findall(capitalized_pattern, text)

        for match in matches:
            if match not in entity_set and len(match) > 2:
                entity_set.add(match)
                entities.append({
                    "name": match,
                    "type": "entity"
                })

        # Extract simple relations (X is Y, X has Y, X uses Y, etc.)
        relations = []
        relation_patterns = [
            (r'(\w+(?:\s+\w+)?)\s+is\s+(?:a|an)\s+(\w+(?:\s+\w+)?)', 'is_a'),
            (r'(\w+(?:\s+\w+)?)\s+has\s+(\w+(?:\s+\w+)?)', 'has'),
            (r'(\w+(?:\s+\w+)?)\s+uses\s+(\w+(?:\s+\w+)?)', 'uses'),
            (r'(\w+(?:\s+\w+)?)\s+contains\s+(\w+(?:\s+\w+)?)', 'contains'),
            (r'(\w+(?:\s+\w+)?)\s+requires\s+(\w+(?:\s+\w+)?)', 'requires'),
        ]

        for pattern, relation_type in relation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for source, target in matches:
                relations.append((source.strip(), relation_type, target.strip()))

        return {
            "entities": entities,
            "relations": relations
        }

    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """
        Extract key terms/concepts from text.

        Args:
            text: Input text
            top_k: Number of keywords to return

        Returns:
            List of keywords
        """
        # Simple frequency-based extraction
        # Remove common stop words
        stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'to', 'for', 'of', 'as', 'by', 'this', 'that', 'it', 'from', 'be', 'are', 'was', 'were'}

        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        word_freq = {}

        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:top_k]]

    def build_graph_metadata(self, text: str, chunk_id: str) -> Dict:
        """
        Build comprehensive graph metadata for a text chunk.

        Args:
            text: Text content
            chunk_id: Unique identifier for this chunk

        Returns:
            Dict containing graph metadata
        """
        graph_info = self.extract_entities_and_relations(text)

        return {
            "chunk_id": chunk_id,
            "entities": [e["name"] for e in graph_info["entities"]],
            "entity_types": [e.get("type", "unknown") for e in graph_info["entities"]],
            "relations": [f"{s}|{r}|{t}" for s, r, t in graph_info["relations"]],
            "keywords": self.extract_keywords(text),
            "has_graph_data": len(graph_info["entities"]) > 0 or len(graph_info["relations"]) > 0
        }
