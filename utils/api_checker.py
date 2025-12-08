#!/usr/bin/env python3
"""
API Availability Checker
========================

Utilities for checking API availability and health across different providers.
"""

import asyncio
import aiohttp
import os
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging


@dataclass
class APIHealthResult:
    """Result of API health check."""
    provider: str
    available: bool
    response_time: float
    status_code: Optional[int]
    error_message: Optional[str]
    timestamp: float


class APIChecker:
    """Check API availability for different providers."""
    
    # API health check endpoints
    HEALTH_ENDPOINTS = {
        "anthropic": "https://api.anthropic.com/v1/messages",
        "openai": "https://api.openai.com/v1/models",
        "azure": None,  # Varies by deployment
    }
    
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
    
    async def check_provider_health(self, provider: str) -> APIHealthResult:
        """Check health of specific provider."""
        start_time = time.time()
        
        try:
            if provider not in self.HEALTH_ENDPOINTS:
                return APIHealthResult(
                    provider=provider,
                    available=False,
                    response_time=0.0,
                    status_code=None,
                    error_message=f"Unknown provider: {provider}",
                    timestamp=start_time
                )
            
            endpoint = self.HEALTH_ENDPOINTS[provider]
            if not endpoint:
                # For providers without public health endpoints
                return await self._check_api_key_validity(provider)
            
            headers = self._get_auth_headers(provider)
            if not headers:
                return APIHealthResult(
                    provider=provider,
                    available=False,
                    response_time=0.0,
                    status_code=None,
                    error_message="No API key configured",
                    timestamp=start_time
                )
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(endpoint, headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    # Consider 200-299 and some 4xx as "available" (API is responding)
                    available = response.status < 500
                    error_msg = None if available else f"HTTP {response.status}"
                    
                    return APIHealthResult(
                        provider=provider,
                        available=available,
                        response_time=response_time,
                        status_code=response.status,
                        error_message=error_msg,
                        timestamp=start_time
                    )
        
        except asyncio.TimeoutError:
            return APIHealthResult(
                provider=provider,
                available=False,
                response_time=self.timeout,
                status_code=None,
                error_message="Request timeout",
                timestamp=start_time
            )
        except Exception as e:
            return APIHealthResult(
                provider=provider,
                available=False,
                response_time=time.time() - start_time,
                status_code=None,
                error_message=str(e),
                timestamp=start_time
            )
    
    async def _check_api_key_validity(self, provider: str) -> APIHealthResult:
        """Check if API key is configured for provider."""
        start_time = time.time()
        
        env_vars = {
            "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY", 
            "azure": "AZURE_OPENAI_API_KEY"
        }
        
        env_var = env_vars.get(provider)
        if not env_var:
            return APIHealthResult(
                provider=provider,
                available=False,
                response_time=0.0,
                status_code=None,
                error_message="Unknown provider",
                timestamp=start_time
            )
        
        api_key = os.environ.get(env_var)
        available = bool(api_key and len(api_key.strip()) > 10)
        error_msg = None if available else f"No valid {env_var} configured"
        
        return APIHealthResult(
            provider=provider,
            available=available,
            response_time=time.time() - start_time,
            status_code=None,
            error_message=error_msg,
            timestamp=start_time
        )
    
    def _get_auth_headers(self, provider: str) -> Optional[Dict[str, str]]:
        """Get authentication headers for provider."""
        if provider == "anthropic":
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if api_key:
                return {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
        
        elif provider == "openai":
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                return {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
        
        elif provider == "azure":
            api_key = os.environ.get("AZURE_OPENAI_API_KEY")
            if api_key:
                return {
                    "api-key": api_key,
                    "Content-Type": "application/json"
                }
        
        return None
    
    async def check_all_providers(self) -> Dict[str, APIHealthResult]:
        """Check health of all configured providers."""
        providers = ["anthropic", "openai", "azure"]
        tasks = [self.check_provider_health(provider) for provider in providers]
        results = await asyncio.gather(*tasks)
        
        return {result.provider: result for result in results}
    
    async def wait_for_api_recovery(self, provider: str, max_wait: float = 300.0, 
                                  check_interval: float = 30.0) -> bool:
        """Wait for API to recover, checking periodically."""
        start_time = time.time()
        
        self.logger.info(f"Waiting for {provider} API recovery (max {max_wait}s)")
        
        while time.time() - start_time < max_wait:
            result = await self.check_provider_health(provider)
            
            if result.available:
                recovery_time = time.time() - start_time
                self.logger.info(f"{provider} API recovered after {recovery_time:.1f}s")
                return True
            
            self.logger.debug(f"{provider} still unavailable: {result.error_message}")
            await asyncio.sleep(check_interval)
        
        self.logger.warning(f"{provider} API did not recover within {max_wait}s")
        return False


async def quick_health_check(providers: list = None) -> Dict[str, bool]:
    """Quick health check returning simple availability status."""
    if providers is None:
        providers = ["anthropic", "openai"]
    
    checker = APIChecker(timeout=5.0)
    results = {}
    
    for provider in providers:
        result = await checker.check_provider_health(provider)
        results[provider] = result.available
    
    return results