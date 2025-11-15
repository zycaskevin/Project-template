"""
Exa API Integration Module

Purpose: Search for best practices and technical insights using Exa AI search
Version: 1.0.0
Author: Claude Code + zycaskevin

Integration Strategy:
1. Extract search queries from session intent
2. Use Exa API to search for best practices
3. Enrich compressed context with search results (~300 tokens)

Free Tier: $10 credits = 2,000 searches (sufficient for development)
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class ExaSearchClient:
    """Client for Exa AI search API"""

    def __init__(self, api_key: Optional[str] = None, use_api: bool = False):
        """
        Initialize Exa Search Client

        Args:
            api_key: Exa API key (get from https://exa.ai)
            use_api: Use actual Exa API (requires API key)
                     If False, returns mock search results
        """
        self.api_key = api_key or os.environ.get('EXA_API_KEY')
        self.use_api = use_api and self.api_key is not None
        self.cache = {}  # Simple in-memory cache

        if self.use_api:
            try:
                from exa_py import Exa
                self.client = Exa(api_key=self.api_key)
            except ImportError:
                print("[WARNING] exa-py not installed. Install with: pip install exa-py")
                self.use_api = False

    def search(self, query: str, num_results: int = 3,
               start_date: Optional[str] = None) -> Dict:
        """
        Search for best practices using Exa

        Args:
            query: Search query (e.g., "FastAPI authentication best practices 2025")
            num_results: Number of results to return (default: 3)
            start_date: Start date filter (YYYY-MM-DD) for recent content

        Returns:
            {
                "query": "FastAPI authentication best practices 2025",
                "results": [
                    {
                        "title": "...",
                        "url": "...",
                        "summary": "...",
                        "score": 0.95
                    }
                ],
                "source": "exa_api",
                "tokens": 250
            }
        """
        cache_key = f"{query}:{num_results}"

        # Check cache
        if cache_key in self.cache:
            return self.cache[cache_key]

        if self.use_api:
            # Use actual Exa API
            try:
                result = self._search_exa_api(query, num_results, start_date)
                self.cache[cache_key] = result
                return result
            except Exception as e:
                print(f"[WARNING] Exa API error: {e}")
                return self._create_mock_results(query, num_results)
        else:
            # Return mock results
            return self._create_mock_results(query, num_results)

    def _search_exa_api(self, query: str, num_results: int,
                        start_date: Optional[str]) -> Dict:
        """
        Search using actual Exa API

        Note: Requires exa-py package and API key
        Installation: pip install exa-py
        """
        search_params = {
            "query": query,
            "num_results": num_results,
            "use_autoprompt": True  # Let Exa optimize the query
        }

        if start_date:
            search_params["start_published_date"] = start_date

        # Perform search
        response = self.client.search_and_contents(**search_params)

        # Extract results
        results = []
        total_text = ""

        for result in response.results:
            summary = result.text[:300] if result.text else result.summary
            results.append({
                "title": result.title,
                "url": result.url,
                "summary": summary,
                "score": result.score if hasattr(result, 'score') else 0.8
            })
            total_text += summary + "\n"

        return {
            "query": query,
            "results": results,
            "source": "exa_api",
            "tokens": len(total_text) // 4,  # Rough estimate
            "num_results": len(results)
        }

    def _create_mock_results(self, query: str, num_results: int) -> Dict:
        """Create mock search results for testing"""

        # Mock results database
        mock_db = {
            'fastapi authentication': [
                {
                    "title": "FastAPI Authentication Best Practices (2025)",
                    "url": "https://fastapi.tiangolo.com/tutorial/security/",
                    "summary": "Use OAuth2 with Password and Bearer tokens. Implement dependency injection for authentication. Store hashed passwords with bcrypt. Use JWT tokens for stateless authentication.",
                    "score": 0.95
                },
                {
                    "title": "Securing FastAPI Applications",
                    "url": "https://testdriven.io/blog/fastapi-security/",
                    "summary": "Implement role-based access control (RBAC). Use API keys for service-to-service communication. Enable CORS properly. Use HTTPS in production.",
                    "score": 0.92
                },
                {
                    "title": "FastAPI + JWT Authentication Tutorial",
                    "url": "https://realpython.com/fastapi-jwt/",
                    "summary": "Create access and refresh tokens. Set appropriate expiration times. Use secure secret keys from environment variables. Implement token refresh endpoints.",
                    "score": 0.89
                }
            ],
            'react hooks': [
                {
                    "title": "React Hooks Best Practices (2025)",
                    "url": "https://react.dev/learn/hooks",
                    "summary": "Use useState for component state. Use useEffect for side effects. Use useMemo and useCallback for performance optimization. Create custom hooks for reusable logic.",
                    "score": 0.94
                },
                {
                    "title": "Advanced React Hooks Patterns",
                    "url": "https://kentcdodds.com/blog/react-hooks",
                    "summary": "Use useReducer for complex state. Use useContext for global state. Avoid excessive re-renders with proper dependencies. Test hooks with React Testing Library.",
                    "score": 0.91
                }
            ],
            'default': [
                {
                    "title": f"Best Practices for {query}",
                    "url": "https://example.com/best-practices",
                    "summary": f"Follow industry standards for {query}. Use type safety and validation. Write comprehensive tests. Document your code properly.",
                    "score": 0.85
                }
            ]
        }

        # Find matching results
        query_lower = query.lower()
        results = None

        for key in mock_db:
            if key in query_lower:
                results = mock_db[key][:num_results]
                break

        if results is None:
            results = mock_db['default']

        # Calculate total tokens
        total_text = "\n".join([r["summary"] for r in results])

        return {
            "query": query,
            "results": results,
            "source": "mock",
            "tokens": len(total_text) // 4,
            "num_results": len(results)
        }


def extract_search_queries_from_intent(session_intent: List[str],
                                       libraries: Optional[List[str]] = None,
                                       max_queries: int = 2) -> List[str]:
    """
    Extract search queries from session intent

    Args:
        session_intent: List of user intents
        libraries: Detected libraries (optional, for context)
        max_queries: Maximum number of queries to generate

    Returns:
        List of search queries optimized for Exa

    Examples:
        >>> extract_search_queries_from_intent(
        ...     ["Implement FastAPI authentication with JWT"],
        ...     libraries=["fastapi"]
        ... )
        ["FastAPI authentication best practices 2025"]

        >>> extract_search_queries_from_intent(
        ...     ["Optimize React rendering performance"],
        ...     libraries=["react"]
        ... )
        ["React rendering optimization best practices 2025"]
    """
    queries = []

    # Keywords to include in search
    enhancement_keywords = {
        'authentication': 'authentication best practices',
        'auth': 'authentication best practices',
        'login': 'authentication best practices',
        'security': 'security best practices',
        'testing': 'testing strategies',
        'test': 'testing strategies',
        'performance': 'performance optimization',
        'optimization': 'performance optimization',
        'deployment': 'deployment strategies',
        'database': 'database design patterns',
        'api': 'API design best practices',
        'routing': 'routing patterns'
    }

    current_year = datetime.now().year

    for intent in session_intent:
        if len(queries) >= max_queries:
            break

        intent_lower = intent.lower()

        # Extract library and topic
        library = None
        if libraries:
            for lib in libraries:
                if lib.lower() in intent_lower:
                    library = lib
                    break

        # Find enhancement keywords
        topic = None
        for keyword, enhancement in enhancement_keywords.items():
            if keyword in intent_lower:
                topic = enhancement
                break

        # Construct query
        if library and topic:
            query = f"{library} {topic} {current_year}"
            queries.append(query)
        elif library:
            query = f"{library} best practices {current_year}"
            queries.append(query)
        elif topic:
            query = f"{topic} {current_year}"
            queries.append(query)

    # If no queries generated, create a generic one from first intent
    if not queries and session_intent:
        first_intent = session_intent[0]
        # Remove common words
        cleaned = first_intent.replace("Implement", "").replace("Create", "").strip()
        queries.append(f"{cleaned} best practices {current_year}")

    return queries[:max_queries]


def enhance_with_exa(compressed_context: Dict,
                     api_key: Optional[str] = None,
                     use_api: bool = False,
                     max_tokens: int = 300) -> Dict:
    """
    Enhance compressed context with Exa search results

    Args:
        compressed_context: Compressed context (with or without Context7 enhancement)
        api_key: Exa API key (optional)
        use_api: Use actual Exa API (requires API key)
        max_tokens: Maximum tokens to add from search results

    Returns:
        Enhanced context with search results
        {
            ...compressed_context,
            "enhancement": {
                ...existing_enhancement,
                "exa_search": [
                    {
                        "query": "...",
                        "results": [...],
                        "tokens": 250
                    }
                ],
                "total_tokens_added": 700  # Context7 + Exa
            }
        }

    Example:
        >>> compressed = {
        ...     "sessionIntent": ["Implement FastAPI authentication"],
        ...     "breadcrumbs": ["import:FastAPI"]
        ... }
        >>> enhanced = enhance_with_exa(compressed)
        >>> enhanced["enhancement"]["exa_search"][0]["query"]
        "FastAPI authentication best practices 2025"
    """
    # Initialize client
    client = ExaSearchClient(api_key=api_key, use_api=use_api)

    # Extract search queries
    session_intent = compressed_context.get("sessionIntent", [])

    # Get libraries from existing enhancement or breadcrumbs
    libraries = None
    if "enhancement" in compressed_context:
        libraries = compressed_context["enhancement"].get("libraries_detected")

    if not libraries:
        # Try to extract from breadcrumbs
        from context7_integration import extract_libraries_from_breadcrumbs
        breadcrumbs = compressed_context.get("breadcrumbs", [])
        libraries = extract_libraries_from_breadcrumbs(breadcrumbs)

    queries = extract_search_queries_from_intent(session_intent, libraries)

    if not queries:
        return {
            **compressed_context,
            "enhancement": {
                **compressed_context.get("enhancement", {}),
                "exa_search": [],
                "reason": "No search queries could be extracted from session intent"
            }
        }

    # Perform searches
    search_results = []
    total_tokens = 0

    for query in queries:
        # Adjust num_results based on remaining token budget
        remaining_budget = max_tokens - total_tokens
        if remaining_budget < 50:  # Not enough for meaningful results
            break

        # Estimate 3 results = ~100 tokens each
        num_results = min(3, remaining_budget // 100)
        if num_results < 1:
            num_results = 1

        # Perform search
        result = client.search(query, num_results=num_results, start_date="2024-01-01")

        # Check token budget
        if total_tokens + result["tokens"] > max_tokens:
            # Truncate results to fit budget
            remaining_tokens = max_tokens - total_tokens
            if remaining_tokens > 50:
                # Keep fewer results
                results_to_keep = max(1, remaining_tokens // 80)
                result["results"] = result["results"][:results_to_keep]
                result["tokens"] = remaining_tokens
                result["num_results"] = len(result["results"])

                search_results.append(result)
                total_tokens += remaining_tokens
            break

        search_results.append(result)
        total_tokens += result["tokens"]

        if total_tokens >= max_tokens:
            break

    # Merge with existing enhancement
    existing_enhancement = compressed_context.get("enhancement", {})
    existing_tokens = existing_enhancement.get("total_tokens_added", 0)

    return {
        **compressed_context,
        "enhancement": {
            **existing_enhancement,
            "exa_search": search_results,
            "total_tokens_added": existing_tokens + total_tokens,
            "exa_tokens_added": total_tokens
        }
    }


if __name__ == "__main__":
    # Test the module
    print("Testing Exa Integration Module")
    print("=" * 60)

    # Test 1: Extract search queries
    test_intent = [
        "Implement FastAPI authentication with JWT",
        "Optimize database queries"
    ]
    test_libraries = ["fastapi"]

    queries = extract_search_queries_from_intent(test_intent, test_libraries)
    print(f"\nTest 1: Extract Search Queries")
    print(f"Input Intent: {test_intent}")
    print(f"Libraries: {test_libraries}")
    print(f"Output Queries: {queries}")

    # Test 2: Perform search
    client = ExaSearchClient(use_api=False)
    result = client.search("FastAPI authentication best practices 2025", num_results=3)
    print(f"\nTest 2: Perform Search")
    print(f"Query: {result['query']}")
    print(f"Num Results: {result['num_results']}")
    print(f"Tokens: {result['tokens']}")
    print(f"First Result: {result['results'][0]['title']}")

    # Test 3: Enhance compressed context
    test_compressed = {
        "sessionIntent": ["Implement FastAPI authentication with JWT"],
        "breadcrumbs": ["import:FastAPI", "class:APIRouter"],
        "playByPlay": ["Created authentication module"],
        "artifacts": ["src/auth.py"],
        "enhancement": {
            "context7_docs": [],
            "total_tokens_added": 144,
            "libraries_detected": ["fastapi"]
        }
    }

    enhanced = enhance_with_exa(test_compressed, use_api=False)
    print(f"\nTest 3: Enhance Compressed Context")
    print(f"Search queries: {[s['query'] for s in enhanced['enhancement']['exa_search']]}")
    print(f"Exa tokens added: {enhanced['enhancement']['exa_tokens_added']}")
    print(f"Total tokens: {enhanced['enhancement']['total_tokens_added']}")

    print("\n" + "=" * 60)
    print("All tests completed successfully!")
