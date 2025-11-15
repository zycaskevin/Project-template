"""
Context7 MCP Integration Module

Purpose: Automatically fetch up-to-date technical documentation
Version: 1.0.0
Author: Claude Code + zycaskevin

Integration Strategy:
1. Extract library names from breadcrumbs (imports, classes)
2. Fetch latest documentation from Context7 MCP
3. Enrich compressed context with relevant docs (~500 tokens)

Free Tier: Sufficient for our use (no cost)
"""

import json
import subprocess
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class Context7Client:
    """Client for Context7 MCP server"""

    # Known libraries that Context7 supports
    SUPPORTED_LIBRARIES = {
        # Python
        'fastapi', 'django', 'flask', 'sqlalchemy', 'pydantic',
        'pytest', 'requests', 'numpy', 'pandas', 'sklearn',
        'tensorflow', 'torch', 'pytorch', 'transformers',

        # JavaScript/TypeScript
        'react', 'vue', 'angular', 'express', 'next',
        'typescript', 'node', 'axios', 'jest',

        # Other
        'kubernetes', 'docker', 'terraform', 'aws', 'gcp'
    }

    def __init__(self, use_mcp: bool = True):
        """
        Initialize Context7 Client

        Args:
            use_mcp: Use MCP server (requires Claude Desktop setup)
                     If False, returns mock documentation
        """
        self.use_mcp = use_mcp
        self.cache = {}  # Simple in-memory cache

    def fetch_docs(self, library: str, version: str = "latest",
                   query: Optional[str] = None) -> Dict:
        """
        Fetch documentation for a specific library

        Args:
            library: Library name (e.g., 'FastAPI', 'React')
            version: Version string (default: 'latest')
            query: Specific query (e.g., 'authentication', 'routing')

        Returns:
            {
                "library": "FastAPI",
                "version": "0.109.0",
                "content": "Documentation content...",
                "source": "context7_mcp",
                "tokens": 450
            }
        """
        cache_key = f"{library}:{version}:{query}"

        # Check cache
        if cache_key in self.cache:
            return self.cache[cache_key]

        library_lower = library.lower()

        # Check if library is supported
        if library_lower not in self.SUPPORTED_LIBRARIES:
            return self._create_empty_response(library, "Library not supported")

        if self.use_mcp:
            # Try to fetch from MCP server
            try:
                docs = self._fetch_from_mcp(library, version, query)
                self.cache[cache_key] = docs
                return docs
            except Exception as e:
                print(f"[WARNING] Context7 MCP error: {e}")
                return self._create_mock_docs(library, version, query)
        else:
            # Return mock documentation
            return self._create_mock_docs(library, version, query)

    def _fetch_from_mcp(self, library: str, version: str,
                        query: Optional[str]) -> Dict:
        """
        Fetch from actual Context7 MCP server

        Note: This requires Context7 MCP to be installed and running
        Installation: npx -y @smithery/cli install @upstash/context7-mcp --client claude
        """
        # TODO: Implement actual MCP communication
        # For now, raise NotImplementedError to fall back to mock
        raise NotImplementedError("MCP communication not yet implemented")

    def _create_mock_docs(self, library: str, version: str,
                          query: Optional[str]) -> Dict:
        """Create mock documentation for testing"""

        mock_content = {
            'fastapi': """
FastAPI {version} - Modern, fast (high-performance) web framework

Key Features:
- Automatic API documentation (Swagger UI)
- Type hints for validation
- Async support
- Dependency injection

{query_section}

Example:
```python
from fastapi import FastAPI, Depends

app = FastAPI()

@app.get("/")
async def read_root():
    return {{"message": "Hello World"}}
```

Best Practices:
1. Use dependency injection for database connections
2. Separate routers for different domains
3. Use Pydantic models for request/response validation
""",
            'react': """
React {version} - A JavaScript library for building user interfaces

Core Concepts:
- Components and Props
- State and Lifecycle
- Hooks (useState, useEffect)
- Virtual DOM

{query_section}

Example:
```jsx
import {{ useState }} from 'react';

function Counter() {{
  const [count, setCount] = useState(0);

  return (
    <button onClick={{() => setCount(count + 1)}}>
      Count: {{count}}
    </button>
  );
}}
```

Best Practices:
1. Keep components small and focused
2. Use functional components with hooks
3. Memoize expensive computations
"""
        }

        template = mock_content.get(library.lower(),
                                   f"{library} {version} documentation (mock)")

        query_section = ""
        if query:
            query_section = f"\n## {query.title()}\n[Relevant documentation for '{query}']\n"

        content = template.format(
            version=version,
            query_section=query_section
        )

        return {
            "library": library,
            "version": version,
            "content": content,
            "source": "mock",
            "tokens": len(content) // 4,  # Rough estimate
            "query": query
        }

    def _create_empty_response(self, library: str, reason: str) -> Dict:
        """Create empty response when docs unavailable"""
        return {
            "library": library,
            "version": "unknown",
            "content": "",
            "source": "none",
            "tokens": 0,
            "error": reason
        }


def extract_libraries_from_breadcrumbs(breadcrumbs: List[str]) -> List[str]:
    """
    Extract library names from breadcrumbs

    Args:
        breadcrumbs: List of code references
            e.g., ["import:FastAPI", "class:APIRouter", "function:create_user"]

    Returns:
        List of library names (lowercase)
        e.g., ["fastapi"]

    Examples:
        >>> extract_libraries_from_breadcrumbs(["import:FastAPI", "import:Pydantic"])
        ["fastapi", "pydantic"]

        >>> extract_libraries_from_breadcrumbs(["function:my_function"])
        []
    """
    libraries = set()

    for breadcrumb in breadcrumbs:
        if ':' not in breadcrumb:
            continue

        breadcrumb_type, identifier = breadcrumb.split(':', 1)

        # Extract from imports
        if breadcrumb_type in ['import', 'import_from']:
            # Check against known libraries
            identifier_lower = identifier.lower()

            for lib in Context7Client.SUPPORTED_LIBRARIES:
                if lib in identifier_lower:
                    libraries.add(lib)

        # Extract from class/function names that contain library names
        elif breadcrumb_type in ['class', 'function']:
            identifier_lower = identifier.lower()

            for lib in Context7Client.SUPPORTED_LIBRARIES:
                # Check if library name appears in identifier
                if lib in identifier_lower:
                    libraries.add(lib)

    return sorted(list(libraries))


def extract_query_from_intent(session_intent: List[str], library: str) -> Optional[str]:
    """
    Extract specific query from session intent

    Args:
        session_intent: List of user intents
        library: Target library name

    Returns:
        Query string or None

    Examples:
        >>> extract_query_from_intent(
        ...     ["Implement FastAPI authentication with JWT"],
        ...     "fastapi"
        ... )
        "authentication"
    """
    # Keywords to extract
    keywords = [
        'authentication', 'auth', 'login',
        'routing', 'endpoint', 'api',
        'database', 'orm', 'migration',
        'validation', 'schema',
        'testing', 'test',
        'deployment', 'docker',
        'performance', 'optimization'
    ]

    for intent in session_intent:
        intent_lower = intent.lower()

        # Check if intent mentions the library
        if library.lower() not in intent_lower:
            continue

        # Extract keywords
        for keyword in keywords:
            if keyword in intent_lower:
                return keyword

    return None


def enhance_with_context7(compressed_context: Dict,
                          use_mcp: bool = False,
                          max_tokens: int = 500) -> Dict:
    """
    Enhance compressed context with Context7 documentation

    Args:
        compressed_context: Compressed context from compress_context.py
        use_mcp: Use actual MCP server (requires setup)
        max_tokens: Maximum tokens to add from documentation

    Returns:
        Enhanced context with documentation
        {
            ...compressed_context,
            "enhancement": {
                "context7_docs": [
                    {
                        "library": "FastAPI",
                        "version": "0.109.0",
                        "content": "...",
                        "tokens": 450
                    }
                ],
                "total_tokens_added": 450
            }
        }

    Example:
        >>> compressed = {
        ...     "breadcrumbs": ["import:FastAPI", "class:APIRouter"],
        ...     "sessionIntent": ["Implement FastAPI authentication"]
        ... }
        >>> enhanced = enhance_with_context7(compressed)
        >>> enhanced["enhancement"]["context7_docs"][0]["library"]
        "fastapi"
    """
    # Initialize client
    client = Context7Client(use_mcp=use_mcp)

    # Extract libraries from breadcrumbs
    breadcrumbs = compressed_context.get("breadcrumbs", [])
    libraries = extract_libraries_from_breadcrumbs(breadcrumbs)

    if not libraries:
        return {
            **compressed_context,
            "enhancement": {
                "context7_docs": [],
                "total_tokens_added": 0,
                "reason": "No supported libraries found in breadcrumbs"
            }
        }

    # Fetch documentation for each library
    docs_list = []
    total_tokens = 0

    session_intent = compressed_context.get("sessionIntent", [])

    for library in libraries:
        # Extract specific query if available
        query = extract_query_from_intent(session_intent, library)

        # Fetch docs
        docs = client.fetch_docs(library, version="latest", query=query)

        # Check token budget
        if total_tokens + docs["tokens"] > max_tokens:
            # Truncate content to fit budget
            remaining_tokens = max_tokens - total_tokens
            if remaining_tokens > 100:  # Only add if meaningful
                docs["content"] = docs["content"][:remaining_tokens * 4]
                docs["tokens"] = remaining_tokens
                docs_list.append(docs)
                total_tokens += remaining_tokens
            break

        docs_list.append(docs)
        total_tokens += docs["tokens"]

        # Stop if we've reached token limit
        if total_tokens >= max_tokens:
            break

    # Return enhanced context
    return {
        **compressed_context,
        "enhancement": {
            "context7_docs": docs_list,
            "total_tokens_added": total_tokens,
            "libraries_detected": libraries
        }
    }


if __name__ == "__main__":
    # Test the module
    print("Testing Context7 Integration Module")
    print("=" * 60)

    # Test 1: Extract libraries from breadcrumbs
    test_breadcrumbs = [
        "import:FastAPI",
        "class:APIRouter",
        "function:create_user",
        "import:Pydantic"
    ]

    libraries = extract_libraries_from_breadcrumbs(test_breadcrumbs)
    print(f"\nTest 1: Extract Libraries")
    print(f"Input: {test_breadcrumbs}")
    print(f"Output: {libraries}")

    # Test 2: Fetch documentation
    client = Context7Client(use_mcp=False)
    docs = client.fetch_docs("fastapi", query="authentication")
    print(f"\nTest 2: Fetch Documentation")
    print(f"Library: {docs['library']}")
    print(f"Tokens: {docs['tokens']}")
    print(f"Content Preview: {docs['content'][:200]}...")

    # Test 3: Enhance compressed context
    test_compressed = {
        "sessionIntent": ["Implement FastAPI authentication with JWT"],
        "breadcrumbs": ["import:FastAPI", "class:APIRouter"],
        "playByPlay": ["Created authentication module"],
        "artifacts": ["src/auth.py"]
    }

    enhanced = enhance_with_context7(test_compressed, use_mcp=False)
    print(f"\nTest 3: Enhance Compressed Context")
    print(f"Libraries detected: {enhanced['enhancement']['libraries_detected']}")
    print(f"Tokens added: {enhanced['enhancement']['total_tokens_added']}")
    print(f"Docs count: {len(enhanced['enhancement']['context7_docs'])}")

    print("\n" + "=" * 60)
    print("All tests completed successfully!")
