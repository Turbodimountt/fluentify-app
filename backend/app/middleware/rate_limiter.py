"""
Fluentify — Rate Limiting Middleware
RNF-09: 60 req/min global, 20 req/min on auth endpoints.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
