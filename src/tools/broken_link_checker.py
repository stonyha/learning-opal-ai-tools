"""Broken link checker tool implementation for Opal AI platform."""

import asyncio
from typing import List, Optional
from datetime import datetime

import httpx
from pydantic import BaseModel, Field, field_validator
from opal_tools_sdk import tool


class URLCheckParameters(BaseModel):
    """Parameters for the broken link checker tool."""

    urls: List[str] = Field(
        ...,
        description="List of URLs to check for broken links",
        min_length=1,
    )
    timeout: float = Field(
        default=10.0,
        description="Request timeout in seconds",
        gt=0,
        le=60,
    )
    follow_redirects: bool = Field(
        default=True,
        description="Whether to follow HTTP redirects",
    )

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, v: List[str]) -> List[str]:
        """Validate that URLs list is not empty and contains valid URL strings."""
        if not v:
            raise ValueError("URLs list cannot be empty")
        for url in v:
            if not isinstance(url, str) or not url.strip():
                raise ValueError(f"Invalid URL: {url}")
        return v


class URLCheckResult(BaseModel):
    """Result for a single URL check."""

    url: str
    status_code: Optional[int] = None
    is_dead: bool
    error_message: Optional[str] = None
    elapsed_time: float
    reason: Optional[str] = None
    checked_at: str


async def check_single_url(
    client: httpx.AsyncClient,
    url: str,
    timeout: float,
    follow_redirects: bool,
) -> URLCheckResult:
    """
    Check a single URL and return the result.

    Args:
        client: HTTP client instance
        url: URL to check
        timeout: Request timeout in seconds
        follow_redirects: Whether to follow redirects

    Returns:
        URLCheckResult with the check results
    """
    start_time = datetime.utcnow()
    checked_at = start_time.isoformat()

    try:
        response = await client.get(
            url,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )
        elapsed_time = (datetime.utcnow() - start_time).total_seconds()

        # Consider 4xx and 5xx status codes as dead links
        is_dead = response.status_code >= 400

        return URLCheckResult(
            url=url,
            status_code=response.status_code,
            is_dead=is_dead,
            error_message=None,
            elapsed_time=elapsed_time,
            reason=response.reason_phrase,
            checked_at=checked_at,
        )

    except httpx.TimeoutException as e:
        elapsed_time = (datetime.utcnow() - start_time).total_seconds()
        return URLCheckResult(
            url=url,
            status_code=None,
            is_dead=True,
            error_message=f"Request timeout after {timeout} seconds: {str(e)}",
            elapsed_time=elapsed_time,
            reason=None,
            checked_at=checked_at,
        )

    except httpx.ConnectError as e:
        elapsed_time = (datetime.utcnow() - start_time).total_seconds()
        return URLCheckResult(
            url=url,
            status_code=None,
            is_dead=True,
            error_message=f"Connection error: {str(e)}",
            elapsed_time=elapsed_time,
            reason=None,
            checked_at=checked_at,
        )

    except httpx.RequestError as e:
        elapsed_time = (datetime.utcnow() - start_time).total_seconds()
        return URLCheckResult(
            url=url,
            status_code=None,
            is_dead=True,
            error_message=f"Request error: {str(e)}",
            elapsed_time=elapsed_time,
            reason=None,
            checked_at=checked_at,
        )

    except Exception as e:
        elapsed_time = (datetime.utcnow() - start_time).total_seconds()
        return URLCheckResult(
            url=url,
            status_code=None,
            is_dead=True,
            error_message=f"Unexpected error: {str(e)}",
            elapsed_time=elapsed_time,
            reason=None,
            checked_at=checked_at,
        )


@tool(
    name="broken_link_checker",
    description=(
        "Validates and checks multiple URLs to identify broken or dead links. "
        "Use this tool when you need to verify if URLs are accessible, check website health, "
        "or identify broken links in a list of URLs. The tool performs asynchronous checks "
        "and returns comprehensive results including HTTP status codes, response times, "
        "error messages, and whether each link is dead. It detects various types of broken links "
        "including 404 Not Found errors, 5xx server errors, connection timeouts, network errors, "
        "and other request failures. Useful for website maintenance, link validation, "
        "and quality assurance tasks."
    ),
)
async def broken_link_checker(params: URLCheckParameters) -> List[URLCheckResult]:
    """
    Check multiple URLs for broken links concurrently.

    This tool accepts a list of URLs and checks each one asynchronously.
    It identifies dead links including:
    - HTTP 4xx and 5xx status codes (404, 500, etc.)
    - Timeout errors
    - Connection errors
    - Other request failures

    Args:
        params: URLCheckParameters containing:
            - urls: List of URLs to check
            - timeout: Request timeout in seconds (default: 10.0)
            - follow_redirects: Whether to follow redirects (default: True)

    Returns:
        List of URLCheckResult objects, one for each URL, containing:
            - url: The checked URL
            - status_code: HTTP status code (if available)
            - is_dead: Boolean indicating if the link is broken
            - error_message: Error description (if any)
            - elapsed_time: Response time in seconds
            - reason: HTTP reason phrase (if available)
            - checked_at: ISO timestamp of when the check was performed
    """
    # Create HTTP client with appropriate limits
    limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
    timeout_config = httpx.Timeout(
        connect=params.timeout,
        read=params.timeout,
        write=params.timeout,
        pool=params.timeout,
    )

    async with httpx.AsyncClient(
        limits=limits,
        timeout=timeout_config,
        follow_redirects=params.follow_redirects,
    ) as client:
        # Check all URLs concurrently
        tasks = [
            check_single_url(client, url, params.timeout, params.follow_redirects)
            for url in params.urls
        ]
        results = await asyncio.gather(*tasks)

    return list(results)

