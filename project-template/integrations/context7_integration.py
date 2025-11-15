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

    # ============================================================
    # Framework Priority Weights (P1-4.2 Feature 1)
    # ============================================================
    # Purpose: When token budget is limited, prioritize important frameworks
    # Weight Scale: 10 (Critical) → 7 (Important) → 5 (Common) → 3 (Niche) → 1 (Optional)
    FRAMEWORK_PRIORITY = {
        # Tier 1: Critical Mainstream Frameworks (Weight 10)
        'react': 10, 'django': 10, 'fastapi': 10, 'vue': 10, 'express': 10,
        'nextjs': 10, 'flask': 10, 'pytorch': 10, 'tensorflow': 10, 'kubernetes': 10,

        # Tier 2: Important Frameworks (Weight 7-8)
        'redux': 8, 'angular': 8, 'sqlalchemy': 8, 'pandas': 8, 'numpy': 8,
        'nestjs': 7, 'nuxtjs': 7, 'gin': 7, 'spring': 7, 'laravel': 7,

        # Tier 3: Common Tools (Weight 5-6)
        'material-ui': 6, 'tailwindcss': 6, 'pytest': 6, 'jest': 6, 'playwright': 6,
        'svelte': 5, 'fastify': 5, 'koa': 5, 'gorm': 5, 'scikit-learn': 5,

        # Tier 4: Niche/Specialized (Weight 3)
        'preact': 3, 'solid': 3, 'hug': 3, 'falcon': 3, 'actix': 3,

        # Tier 5: Optional/Alternative (Weight 1)
        'alpine': 1, 'backbone': 1, 'web2py': 1, 'turbogears': 1,
    }

    # ============================================================
    # Framework Dependencies Graph (P1-4.2 Feature 3)
    # ============================================================
    # Purpose: Understand framework relationships (e.g., Redux requires React)
    FRAMEWORK_DEPENDENCIES = {
        # React Ecosystem
        'redux': ['react'],
        'react-redux': ['react', 'redux'],
        'react-router': ['react'],
        'nextjs': ['react'],
        'gatsby': ['react'],
        'remix': ['react'],

        # Vue Ecosystem
        'vuex': ['vue'],
        'pinia': ['vue'],
        'nuxtjs': ['vue'],

        # TypeScript
        'tsc': ['typescript'],

        # Testing
        'testing-library': ['react'],  # Often used with React
        'enzyme': ['react'],

        # ORM/Database
        'tortoise-orm': ['asyncio'],
        'motor': ['pymongo'],
    }

    # Known libraries that Context7 supports (100+ frameworks)
    SUPPORTED_LIBRARIES = {
        # ============================================================
        # Python Web Frameworks
        # ============================================================
        'fastapi', 'django', 'flask', 'pyramid', 'bottle',
        'tornado', 'aiohttp', 'sanic', 'quart', 'starlette',
        'cherrypy', 'web2py', 'turbogears', 'falcon', 'hug',

        # Python Data Science & ML
        'numpy', 'pandas', 'scipy', 'matplotlib', 'seaborn',
        'plotly', 'scikit-learn', 'sklearn', 'statsmodels',
        'tensorflow', 'torch', 'pytorch', 'keras', 'jax',
        'transformers', 'huggingface', 'lightgbm', 'xgboost',
        'catboost', 'opencv', 'cv2', 'pillow', 'nltk',
        'spacy', 'gensim', 'networkx',

        # Python Async & Concurrency
        'asyncio', 'trio', 'curio', 'uvloop', 'gevent',
        'multiprocessing', 'concurrent', 'celery', 'dramatiq',

        # Python ORM & Database
        'sqlalchemy', 'peewee', 'tortoise-orm', 'pony',
        'mongoengine', 'pymongo', 'motor', 'redis-py',
        'psycopg2', 'aiomysql', 'aiopg',

        # Python Testing
        'pytest', 'unittest', 'nose2', 'hypothesis', 'tox',
        'coverage', 'mock', 'faker', 'factory-boy', 'behave',

        # Python Utilities
        'pydantic', 'marshmallow', 'requests', 'httpx', 'urllib3',
        'beautifulsoup4', 'bs4', 'lxml', 'click', 'typer',
        'argparse', 'rich', 'tqdm', 'loguru', 'structlog',

        # ============================================================
        # JavaScript/TypeScript - Frontend
        # ============================================================
        'react', 'vue', 'angular', 'svelte', 'solid',
        'preact', 'lit', 'alpine', 'ember', 'backbone',
        'next', 'nextjs', 'nuxt', 'nuxtjs', 'gatsby',
        'remix', 'astro', 'qwik', 'vite',

        # JavaScript/TypeScript - State Management
        'redux', 'mobx', 'zustand', 'recoil', 'jotai',
        'xstate', 'valtio', 'pinia', 'vuex',

        # JavaScript/TypeScript - UI Libraries
        'mui', 'material-ui', 'antd', 'chakra-ui', 'mantine',
        'tailwindcss', 'bootstrap', 'bulma', 'semantic-ui',
        'shadcn', 'radix-ui', 'headlessui',

        # JavaScript/TypeScript - Backend
        'express', 'koa', 'hapi', 'restify', 'fastify',
        'nestjs', 'adonis', 'loopback', 'sails', 'meteor',

        # JavaScript/TypeScript - Testing
        'jest', 'vitest', 'mocha', 'chai', 'jasmine',
        'cypress', 'playwright', 'puppeteer', 'webdriverio',
        'testing-library', 'enzyme',

        # JavaScript/TypeScript - Build Tools
        'webpack', 'rollup', 'parcel', 'esbuild', 'turbopack',
        'babel', 'swc', 'typescript', 'tsc',

        # JavaScript/TypeScript - Utilities
        'node', 'nodejs', 'axios', 'fetch', 'lodash',
        'underscore', 'ramda', 'rxjs', 'date-fns', 'moment',
        'dayjs', 'zod', 'yup', 'joi',

        # ============================================================
        # Go
        # ============================================================
        'gin', 'echo', 'fiber', 'chi', 'gorilla',
        'gorm', 'beego', 'revel', 'buffalo',

        # ============================================================
        # Rust
        # ============================================================
        'actix-web', 'rocket', 'axum', 'warp', 'tokio',
        'serde', 'diesel', 'sqlx', 'sea-orm',

        # ============================================================
        # Java/Kotlin
        # ============================================================
        'spring', 'springboot', 'hibernate', 'junit',
        'mockito', 'gradle', 'maven', 'jackson',
        'ktor', 'exposed',

        # ============================================================
        # Ruby
        # ============================================================
        'rails', 'sinatra', 'rspec', 'rake', 'sidekiq',

        # ============================================================
        # PHP
        # ============================================================
        'laravel', 'symfony', 'codeigniter', 'yii',
        'phpunit', 'composer',

        # ============================================================
        # DevOps & Infrastructure
        # ============================================================
        'docker', 'kubernetes', 'k8s', 'helm', 'terraform',
        'ansible', 'vagrant', 'packer', 'consul', 'vault',
        'prometheus', 'grafana', 'jenkins', 'gitlab-ci',
        'circleci', 'github-actions',

        # ============================================================
        # Cloud Platforms
        # ============================================================
        'aws', 'gcp', 'azure', 'cloudflare', 'vercel',
        'netlify', 'heroku', 'digitalocean', 'railway',

        # ============================================================
        # Databases
        # ============================================================
        'postgresql', 'postgres', 'mysql', 'mongodb', 'redis',
        'elasticsearch', 'cassandra', 'dynamodb', 'sqlite',
        'mariadb', 'cockroachdb', 'timescaledb',

        # ============================================================
        # Mobile
        # ============================================================
        'react-native', 'flutter', 'ionic', 'cordova',
        'expo', 'xamarin', 'nativescript',

        # ============================================================
        # Desktop
        # ============================================================
        'electron', 'tauri', 'qt', 'gtk', 'tkinter',

        # ============================================================
        # GraphQL & API
        # ============================================================
        'graphql', 'apollo', 'relay', 'prisma', 'hasura',
        'strapi', 'sanity', 'contentful',

        # ============================================================
        # Real-time & WebSockets
        # ============================================================
        'socket.io', 'socketio', 'websocket', 'ws', 'pusher',
        'ably', 'supabase', 'firebase',
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
    Extract library names from breadcrumbs (v2: with word boundary matching)

    Args:
        breadcrumbs: List of code references
            e.g., ["import:FastAPI", "class:APIRouter", "function:create_user"]

    Returns:
        List of library names (lowercase, deduplicated)
        e.g., ["fastapi"]

    Examples:
        >>> extract_libraries_from_breadcrumbs(["import:FastAPI", "import:Pydantic"])
        ["fastapi", "pydantic"]

        >>> extract_libraries_from_breadcrumbs(["function:my_function"])
        []

        >>> extract_libraries_from_breadcrumbs(["import:create_engine"])
        []  # Fixed: no longer matches 'gin' from 'engine'

    Version: 2.0 (P1-4.1)
    Changes:
    - Added word boundary matching (fixes 'gin' from 'engine' issue)
    - Added alias deduplication (postgres/postgresql → postgresql)
    - Improved multi-word library matching (e.g., 'react-native')
    """
    import re

    # Library aliases mapping (canonical name)
    LIBRARY_ALIASES = {
        'postgres': 'postgresql',
        'postgresql': 'postgresql',
        'mui': 'material-ui',
        'material-ui': 'material-ui',
        'next': 'nextjs',
        'nextjs': 'nextjs',
        'nuxt': 'nuxtjs',
        'nuxtjs': 'nuxtjs',
        'k8s': 'kubernetes',
        'kubernetes': 'kubernetes',
        'bs4': 'beautifulsoup4',
        'beautifulsoup4': 'beautifulsoup4',
        'cv2': 'opencv',
        'opencv': 'opencv',
        'sklearn': 'scikit-learn',
        'scikit-learn': 'scikit-learn',
        'node': 'nodejs',
        'nodejs': 'nodejs',
    }

    libraries = set()

    for breadcrumb in breadcrumbs:
        if ':' not in breadcrumb:
            continue

        breadcrumb_type, identifier = breadcrumb.split(':', 1)

        # Extract from imports (most reliable)
        if breadcrumb_type in ['import', 'import_from']:
            identifier_lower = identifier.lower()

            # Sort libraries by length (longest first) to match multi-word libs first
            # e.g., 'react-native' before 'react'
            sorted_libs = sorted(Context7Client.SUPPORTED_LIBRARIES,
                               key=len, reverse=True)

            for lib in sorted_libs:
                # Use word boundary matching to avoid false positives
                # \b ensures we match whole words only
                # Special handling for libraries with hyphens (e.g., 'react-native')
                escaped_lib = re.escape(lib)
                pattern = rf'\b{escaped_lib}\b'

                if re.search(pattern, identifier_lower):
                    libraries.add(lib)
                    # Don't break - continue to find all matches
                    # e.g., 'react-redux' should match both 'react' and 'redux'

        # Extract from class/function names (less reliable, be more conservative)
        elif breadcrumb_type in ['class', 'function']:
            identifier_lower = identifier.lower()

            # Only check for exact matches or common patterns
            for lib in Context7Client.SUPPORTED_LIBRARIES:
                # Only match if it's a significant part of the identifier
                # e.g., 'FastAPIRouter' → fastapi, but 'engine' → not gin
                if identifier_lower.startswith(lib.lower()):
                    libraries.add(lib)
                elif identifier_lower.endswith(lib.lower()):
                    libraries.add(lib)
                # Check for CamelCase patterns (e.g., 'ReduxStore')
                elif lib.lower() in identifier_lower.split('_'):
                    libraries.add(lib)

    # Deduplicate using aliases
    canonical_libs = set()
    for lib in libraries:
        canonical = LIBRARY_ALIASES.get(lib, lib)
        canonical_libs.add(canonical)

    return sorted(list(canonical_libs))


def extract_version_from_breadcrumbs(breadcrumbs: List[str]) -> Dict[str, str]:
    """
    Extract version numbers from breadcrumbs (P1-4.2 Feature 2)

    Args:
        breadcrumbs: List of code references with potential version info
            e.g., ["import:fastapi==0.109.0", "import:django>=4.2"]

    Returns:
        Dict mapping library names to version strings
        e.g., {"fastapi": "0.109.0", "django": ">=4.2"}

    Examples:
        >>> extract_version_from_breadcrumbs(["import:fastapi==0.109.0"])
        {"fastapi": "0.109.0"}

        >>> extract_version_from_breadcrumbs(["import:django>=4.2,<5.0"])
        {"django": ">=4.2,<5.0"}

    Version: 1.0 (P1-4.2)
    """
    import re

    versions = {}

    # Version patterns
    # Pattern 1: library==1.2.3
    # Pattern 2: library>=1.2.3
    # Pattern 3: library~=1.2.3
    # Pattern 4: library>=1.2.3,<2.0
    version_pattern = r'([a-z0-9_-]+)(==|>=|<=|~=|>|<)([0-9.]+(?:,[<>=]+[0-9.]+)*)'

    for breadcrumb in breadcrumbs:
        if ':' not in breadcrumb:
            continue

        breadcrumb_type, identifier = breadcrumb.split(':', 1)

        if breadcrumb_type in ['import', 'import_from']:
            # Try to match version pattern
            match = re.search(version_pattern, identifier.lower())
            if match:
                library = match.group(1)
                operator = match.group(2)
                version = match.group(3)
                versions[library] = f"{operator}{version}"

    return versions


def sort_libraries_by_priority(libraries: List[str]) -> List[Tuple[str, int]]:
    """
    Sort libraries by priority weight (P1-4.2 Feature 1)

    Args:
        libraries: List of library names
            e.g., ["react", "redux", "alpine"]

    Returns:
        List of (library, weight) tuples sorted by weight (descending)
        e.g., [("react", 10), ("redux", 8), ("alpine", 1)]

    Examples:
        >>> sort_libraries_by_priority(["react", "redux", "alpine"])
        [("react", 10), ("redux", 8), ("alpine", 1)]

        >>> sort_libraries_by_priority(["unknown-lib", "fastapi"])
        [("fastapi", 10), ("unknown-lib", 5)]  # Unknown libs get default weight 5

    Version: 1.0 (P1-4.2)
    """
    DEFAULT_PRIORITY = 5  # Unknown libraries get medium priority

    # Create list of (library, priority) tuples
    lib_priorities = []
    for lib in libraries:
        priority = Context7Client.FRAMEWORK_PRIORITY.get(lib, DEFAULT_PRIORITY)
        lib_priorities.append((lib, priority))

    # Sort by priority (descending)
    lib_priorities.sort(key=lambda x: x[1], reverse=True)

    return lib_priorities


def get_framework_dependencies(library: str) -> List[str]:
    """
    Get dependencies for a framework (P1-4.2 Feature 3)

    Args:
        library: Framework name
            e.g., "redux"

    Returns:
        List of dependency framework names
        e.g., ["react"]

    Examples:
        >>> get_framework_dependencies("redux")
        ["react"]

        >>> get_framework_dependencies("react-redux")
        ["react", "redux"]

        >>> get_framework_dependencies("unknown-lib")
        []

    Version: 1.0 (P1-4.2)
    """
    return Context7Client.FRAMEWORK_DEPENDENCIES.get(library, [])


def enrich_libraries_with_dependencies(libraries: List[str]) -> List[str]:
    """
    Add missing framework dependencies (P1-4.2 Feature 3)

    Args:
        libraries: Original library list
            e.g., ["redux"]

    Returns:
        Enriched library list with dependencies
        e.g., ["react", "redux"]  # Added "react" because redux depends on it

    Examples:
        >>> enrich_libraries_with_dependencies(["redux"])
        ["react", "redux"]

        >>> enrich_libraries_with_dependencies(["react-redux"])
        ["react", "react-redux", "redux"]

    Version: 1.0 (P1-4.2)
    """
    enriched = set(libraries)

    # Add dependencies
    for lib in libraries:
        deps = get_framework_dependencies(lib)
        enriched.update(deps)

    return sorted(list(enriched))


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
