#!/usr/bin/env python3
"""
Serviços da aplicação Viemar Garantia 70k
"""

from .firebird_service import FirebirdService, get_firebird_service

__all__ = [
    'FirebirdService',
    'get_firebird_service'
]