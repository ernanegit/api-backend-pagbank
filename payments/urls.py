from django.urls import path
from .views import (
    # Views principais
    PaymentListCreateView,
    PaymentDetailView,
    PagSeguroWebhookView,
    payment_status,
    create_transparent_payment,
    
    # Health checks e documentação
    health_check,
    pagbank_health_check,
    api_documentation,
    
    # Testes de configuração
    test_config,
    test_pagbank_auth,
    test_pagbank_order,
    test_pagseguro,
    test_mercadopago,
)

urlpatterns = [
    # ===============================
    # ENDPOINTS PRINCIPAIS
    # ===============================
    
    # Health check simples
    path('', health_check, name='health-check'),
    
    # Documentação da API
    path('docs/', api_documentation, name='api-docs'),
    
    # Operações de pagamento
    path('payments/', PaymentListCreateView.as_view(), name='payment-list-create'),
    path('payments/<uuid:payment_id>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('payments/<uuid:payment_id>/status/', payment_status, name='payment-status'),
    path('payments/transparent/', create_transparent_payment, name='transparent-payment'),
    
    # Webhook
    path('payments/webhook/', PagSeguroWebhookView.as_view(), name='pagbank-webhook'),
    
    # ===============================
    # ENDPOINTS DE TESTE E DIAGNÓSTICO
    # ===============================
    
    # Health check detalhado
    path('pagbank-health/', pagbank_health_check, name='pagbank-health-detailed'),
    
    # Testes de autenticação
    path('test-pagbank-auth/', test_pagbank_auth, name='test-pagbank-auth'),
    path('test-pagbank-order/', test_pagbank_order, name='test-pagbank-order'),
    
    # Teste de configuração
    path('test-config/', test_config, name='test-config'),
    
    # ===============================
    # COMPATIBILIDADE (manter para não quebrar código existente)
    # ===============================
    
    # Aliases para PagSeguro (legado)
    path('test-pagseguro/', test_pagseguro, name='test-pagseguro'),
    path('test-mercadopago/', test_mercadopago, name='test-mercadopago-compat'),
    
    # Webhook aliases
    path('webhook/pagseguro/', PagSeguroWebhookView.as_view(), name='pagseguro-webhook-compat'),
    path('webhook/pagbank/', PagSeguroWebhookView.as_view(), name='pagbank-webhook-compat'),
]

# URLs organizadas por categoria para facilitar manutenção
MAIN_ENDPOINTS = [
    'health-check',
    'api-docs', 
    'payment-list-create',
    'payment-detail',
    'payment-status',
    'transparent-payment',
    'pagbank-webhook'
]

TEST_ENDPOINTS = [
    'pagbank-health-detailed',
    'test-pagbank-auth',
    'test-pagbank-order', 
    'test-config'
]

COMPATIBILITY_ENDPOINTS = [
    'test-pagseguro',
    'test-mercadopago-compat',
    'pagseguro-webhook-compat',
    'pagbank-webhook-compat'
]