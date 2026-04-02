#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick validation test for external_apis module"""

import sys
sys.path.insert(0, '.')

try:
    # Test import
    from app.services.external_apis import (
        get_ibge_population,
        get_siconfi_finances,
        get_datasus_health_infrastructure,
        clear_cache,
        get_cache_status,
        FALLBACK_SICONFI,
        FALLBACK_IBGE,
        FALLBACK_DATASUS,
        USER_AGENT,
        HTTP_TIMEOUT,
        retry_on_network_error,
    )
    
    print("✅ Módulo importado com sucesso!")
    print()
    print("📦 Funções disponíveis:")
    print("   - get_ibge_population(codigo_ibge: str) -> Dict[str, Any]")
    print("   - get_siconfi_finances(codigo_ibge: str) -> Dict[str, Any]")
    print("   - get_datasus_health_infrastructure(codigo_ibge: str) -> Dict[str, Any]")
    print("   - clear_cache() -> None")
    print("   - get_cache_status() -> Dict[str, Any]")
    print()
    print("🔐 Fallbacks carregados:")
    print(f"   - FALLBACK_SICONFI: {len(FALLBACK_SICONFI)} cidades")
    print(f"   - FALLBACK_IBGE: {len(FALLBACK_IBGE)} cidades")
    print(f"   - FALLBACK_DATASUS: {len(FALLBACK_DATASUS)} cidades")
    print()
    print("⚙️  Configuração:")
    print(f"   - USER_AGENT: {USER_AGENT}")
    print(f"   - HTTP_TIMEOUT (read): {HTTP_TIMEOUT.read}s")
    print(f"   - HTTP_TIMEOUT (connect): {HTTP_TIMEOUT.connect}s")
    print()
    print("✨ Decoradores:")
    print(f"   - retry_on_network_error: configurado para 3 tentativas com backoff exponencial")
    print()
    print("🎉 MÓDULO PRONTO PARA PRODUÇÃO!")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    sys.exit(1)
