from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import logging
import requests
import time
from django.conf import settings

from .models import Payment, PaymentItem
from .serializers import PaymentSerializer, CreatePaymentSerializer
from .services import PagSeguroService

logger = logging.getLogger(__name__)

class PaymentListCreateView(APIView):
    def get(self, request):
        """Lista todos os pagamentos"""
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Cria um novo pagamento"""
        serializer = CreatePaymentSerializer(data=request.data)
        
        if serializer.is_valid():
            # Criar pagamento no banco local
            payment = Payment.objects.create(
                amount=serializer.validated_data['amount'],
                description=serializer.validated_data['description'],
                payer_email=serializer.validated_data['payer_email']
            )
            
            # Criar itens do pagamento
            for item_data in serializer.validated_data['items']:
                PaymentItem.objects.create(
                    payment=payment,
                    **item_data
                )
            
            # Criar checkout no PagSeguro/PagBank
            ps_service = PagSeguroService()
            
            checkout_data = {
                'items': serializer.validated_data['items'],
                'payer_email': serializer.validated_data['payer_email'],
                'payer_name': 'Cliente',  # Pode ser passado no request se necessário
                'external_reference': str(payment.id)
            }
            
            ps_result = ps_service.create_checkout_session(checkout_data)
            
            if ps_result['success']:
                payment.preference_id = ps_result.get('checkout_code', '')
                payment.save()
                
                return Response({
                    'payment_id': payment.id,
                    'checkout_code': ps_result.get('checkout_code'),
                    'checkout_url': ps_result.get('checkout_url'),
                    'payment_url': ps_result.get('payment_url')
                }, status=status.HTTP_201_CREATED)
            else:
                payment.delete()  # Remove pagamento se falhou na criação do checkout
                return Response({
                    'error': 'Erro ao criar checkout PagBank',
                    'details': ps_result.get('error')
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentDetailView(APIView):
    def get(self, request, payment_id):
        """Busca detalhes de um pagamento específico"""
        try:
            payment = Payment.objects.get(id=payment_id)
            serializer = PaymentSerializer(payment)
            return Response(serializer.data)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

@method_decorator(csrf_exempt, name='dispatch')
class PagSeguroWebhookView(APIView):
    def post(self, request):
        """Processa notificações do webhook do PagSeguro/PagBank"""
        try:
            # PagSeguro envia notificationCode via POST
            notification_code = request.data.get('notificationCode') or request.POST.get('notificationCode')
            notification_type = request.data.get('notificationType') or request.POST.get('notificationType')
            
            logger.info(f"Webhook recebido - Tipo: {notification_type}, Código: {notification_code}")
            
            if notification_code and notification_type == 'transaction':
                ps_service = PagSeguroService()
                result = ps_service.process_notification(notification_code)
                
                if result['success']:
                    return HttpResponse(status=200)
                else:
                    logger.error(f"Erro ao processar notificação: {result.get('error')}")
                    return HttpResponse(status=400)
            else:
                logger.warning("Notificação inválida ou tipo não suportado")
                return HttpResponse(status=400)
                
        except Exception as e:
            logger.error(f"Erro no webhook: {str(e)}")
            return HttpResponse(status=500)

@api_view(['GET'])
def payment_status(request, payment_id):
    """Verifica o status atual de um pagamento"""
    try:
        payment = Payment.objects.get(id=payment_id)
        
        # Se o pagamento tem código de transação, busca status atualizado
        if payment.mercadopago_id:  # Reutilizando campo para armazenar transaction_code
            ps_service = PagSeguroService()
            ps_result = ps_service.get_transaction(payment.mercadopago_id)
            
            if ps_result['success']:
                # Atualiza status local se necessário
                transaction_data = ps_result['transaction']
                new_status = transaction_data['status']
                
                # Converter status do PagSeguro/PagBank
                status_map = {
                    '1': 'pending',    # Aguardando pagamento
                    '2': 'pending',    # Em análise
                    '3': 'approved',   # Paga
                    '4': 'approved',   # Disponível
                    '5': 'pending',    # Em disputa
                    '6': 'refunded',   # Devolvida
                    '7': 'cancelled',  # Cancelada
                    # Status PagBank v4
                    'PAID': 'approved',
                    'DECLINED': 'rejected',
                    'CANCELED': 'cancelled',
                    'AUTHORIZED': 'pending',
                    'IN_ANALYSIS': 'pending',
                    'WAITING': 'pending'
                }
                
                mapped_status = status_map.get(new_status, 'pending')
                if payment.status != mapped_status:
                    payment.status = mapped_status
                    payment.save()
        
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
        
    except Payment.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def create_transparent_payment(request):
    """Cria um pagamento transparente com cartão de crédito"""
    try:
        payment_data = request.data.get('payment', {})
        card_data = request.data.get('card', {})
        
        if not payment_data or not card_data:
            return Response({
                'error': 'Dados de pagamento e cartão são obrigatórios'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Criar pagamento no banco local
        payment = Payment.objects.create(
            amount=payment_data['amount'],
            description=payment_data.get('description', 'Pagamento transparente'),
            payer_email=payment_data['payer_email']
        )
        
        # Adicionar referência externa
        payment_data['external_reference'] = str(payment.id)
        
        # Criar pagamento transparente
        ps_service = PagSeguroService()
        result = ps_service.create_transparent_payment(payment_data, card_data)
        
        if result['success']:
            payment.mercadopago_id = result.get('transaction_code', '')
            payment.save()
            
            return Response({
                'success': True,
                'payment_id': payment.id,
                'transaction_code': result.get('transaction_code'),
                'status': result.get('status')
            }, status=status.HTTP_201_CREATED)
        else:
            payment.delete()
            return Response({
                'success': False,
                'error': result.get('error')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Erro no pagamento transparente: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def health_check(request):
    """Endpoint para verificar se a API está funcionando"""
    return Response({
        'status': 'OK',
        'message': 'API PagBank funcionando',
        'environment': getattr(settings, 'PAGBANK_ENVIRONMENT', 'sandbox'),
        'timestamp': int(time.time())
    })

@api_view(['GET'])
def test_config(request):
    """Teste de configuração PagBank"""
    return Response({
        'email_exists': bool(getattr(settings, 'PAGBANK_EMAIL', None)),
        'token_exists': bool(getattr(settings, 'PAGBANK_TOKEN', None)),
        'environment': getattr(settings, 'PAGBANK_ENVIRONMENT', 'not_set'),
        'email': getattr(settings, 'PAGBANK_EMAIL', 'not_set'),
        'token_prefix': str(getattr(settings, 'PAGBANK_TOKEN', ''))[:15] + '...',
        'notification_url': getattr(settings, 'PAGBANK_NOTIFICATION_URL', 'not_set'),
        'success_url': getattr(settings, 'PAGBANK_SUCCESS_URL', 'not_set'),
    })

@api_view(['GET'])
def test_pagbank_auth(request):
    """Testa autenticação PagBank com email + token"""
    try:
        email = settings.PAGBANK_EMAIL
        token = settings.PAGBANK_TOKEN
        environment = settings.PAGBANK_ENVIRONMENT
        
        # URLs baseadas no ambiente
        if environment == 'sandbox':
            api_url = "https://sandbox.api.pagseguro.com"
            legacy_url = "https://ws.sandbox.pagseguro.uol.com.br"
        else:
            api_url = "https://api.pagseguro.com"
            legacy_url = "https://ws.pagseguro.uol.com.br"
        
        # Teste 1: Tentar com Bearer token (PagBank v4)
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response_bearer = requests.get(
                f"{api_url}/public-keys",
                headers=headers,
                timeout=10
            )
        except Exception as e:
            response_bearer = type('MockResponse', (), {'status_code': 0, 'text': str(e)})()
        
        # Teste 2: Tentar com email/token nos parâmetros (API híbrida)
        params = {
            'email': email,
            'token': token
        }
        
        try:
            response_params = requests.get(
                f"{api_url}/public-keys",
                params=params,
                timeout=10
            )
        except Exception as e:
            response_params = type('MockResponse', (), {'status_code': 0, 'text': str(e)})()
        
        # Teste 3: Verificar se é API legada (v2/v3)
        try:
            response_legacy = requests.post(
                f"{legacy_url}/v2/sessions",
                data={'email': email, 'token': token},
                timeout=10
            )
        except Exception as e:
            response_legacy = type('MockResponse', (), {'status_code': 0, 'text': str(e)})()
        
        return Response({
            'email': email[:5] + '***',
            'token_length': len(token),
            'environment': environment,
            'tests': {
                'bearer_auth': {
                    'url': f"{api_url}/public-keys",
                    'method': 'Bearer Token',
                    'status': response_bearer.status_code,
                    'success': response_bearer.status_code == 200,
                    'response': response_bearer.text[:200] if hasattr(response_bearer, 'text') and response_bearer.text else None
                },
                'params_auth': {
                    'url': f"{api_url}/public-keys",
                    'method': 'Email/Token params',
                    'status': response_params.status_code,
                    'success': response_params.status_code == 200,
                    'response': response_params.text[:200] if hasattr(response_params, 'text') and response_params.text else None
                },
                'legacy_api': {
                    'url': f"{legacy_url}/v2/sessions",
                    'method': 'Legacy API v2/v3',
                    'status': response_legacy.status_code,
                    'success': response_legacy.status_code == 200,
                    'response': response_legacy.text[:200] if hasattr(response_legacy, 'text') and response_legacy.text else None
                }
            },
            'recommendation': get_api_recommendation(response_bearer, response_params, response_legacy),
            'next_steps': get_next_steps(response_bearer, response_params, response_legacy)
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'type': type(e).__name__,
            'message': 'Erro ao testar autenticação. Verifique as configurações no .env'
        })

def get_api_recommendation(bearer_resp, params_resp, legacy_resp):
    """Determina qual API usar baseado nos testes"""
    if bearer_resp.status_code == 200:
        return "✅ Use PagBank v4 com Bearer token (mais moderno)"
    elif params_resp.status_code == 200:
        return "✅ Use PagBank híbrido com email/token nos parâmetros"
    elif legacy_resp.status_code == 200:
        return "✅ Use PagSeguro legado v2/v3 (seu código atual)"
    else:
        return "❌ Verificar credenciais - nenhuma API respondeu corretamente"

def get_next_steps(bearer_resp, params_resp, legacy_resp):
    """Retorna próximos passos baseado nos testes"""
    if bearer_resp.status_code == 200:
        return ["Implementar PagBankService com Bearer token", "Testar criação de ordem", "Atualizar webhooks"]
    elif params_resp.status_code == 200:
        return ["Implementar PagBankService híbrido", "Testar com params auth", "Validar webhooks"]
    elif legacy_resp.status_code == 200:
        return ["Manter PagSeguroService atual", "Testar checkout session", "Verificar webhooks"]
    else:
        return ["Verificar email e token no .env", "Confirmar ambiente (sandbox/production)", "Contactar suporte PagBank"]

@api_view(['POST'])
def test_pagbank_order(request):
    """Teste completo de criação de ordem"""
    try:
        # Dados de teste padrão
        test_data = {
            'items': [
                {
                    'title': 'Produto Teste PagBank',
                    'quantity': 1,
                    'unit_price': 29.90
                }
            ],
            'payer_email': 'cliente.teste@email.com',
            'payer_name': 'Cliente Teste PagBank',
            'external_reference': f'test-{int(time.time())}'
        }
        
        # Usar dados do request se fornecidos
        if request.data:
            test_data.update(request.data)
        
        # Testar criação de ordem
        ps_service = PagSeguroService()
        result = ps_service.create_checkout_session(test_data)
        
        return Response({
            'test_data': test_data,
            'api_response': result,
            'timestamp': int(time.time()),
            'success': result.get('success', False),
            'recommendations': [
                "Se success=True, suas credenciais estão funcionando!",
                "Use a checkout_url para testar o pagamento",
                "Implemente o webhook para receber notificações"
            ] if result.get('success') else [
                "Verificar credenciais no .env",
                "Executar /test-pagbank-auth/ primeiro",
                "Verificar logs para mais detalhes"
            ]
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'type': type(e).__name__,
            'message': 'Erro ao testar criação de ordem'
        })

@api_view(['GET'])
def pagbank_health_check(request):
    """Health check detalhado do PagBank"""
    try:
        # Verificar configurações obrigatórias
        config_check = {
            'email_configured': bool(getattr(settings, 'PAGBANK_EMAIL', None)),
            'token_configured': bool(getattr(settings, 'PAGBANK_TOKEN', None)),
            'environment': getattr(settings, 'PAGBANK_ENVIRONMENT', 'not_set'),
            'notification_url': getattr(settings, 'PAGBANK_NOTIFICATION_URL', 'not_set'),
            'success_url': getattr(settings, 'PAGBANK_SUCCESS_URL', 'not_set'),
        }
        
        # Teste básico de conectividade
        environment = getattr(settings, 'PAGBANK_ENVIRONMENT', 'sandbox')
        if environment == 'sandbox':
            test_url = "https://sandbox.api.pagseguro.com"
        else:
            test_url = "https://api.pagseguro.com"
        
        try:
            connectivity_test = requests.get(test_url, timeout=5)
            connectivity_ok = True
            connectivity_status = connectivity_test.status_code
        except Exception as e:
            connectivity_ok = False
            connectivity_status = f"Error: {str(e)}"
        
        # Calcular score de saúde
        health_score = sum([
            config_check['email_configured'],
            config_check['token_configured'],
            config_check['environment'] != 'not_set',
            connectivity_ok
        ]) / 4 * 100
        
        overall_status = "OK" if health_score == 100 else "WARNING" if health_score >= 75 else "ERROR"
        
        return Response({
            'status': overall_status,
            'health_score': f"{health_score:.1f}%",
            'service': 'PagBank Gateway',
            'timestamp': int(time.time()),
            'configuration': config_check,
            'connectivity': {
                'api_reachable': connectivity_ok,
                'test_url': test_url,
                'status': connectivity_status
            },
            'recommendations': get_health_recommendations(config_check, connectivity_ok),
            'next_actions': [
                "Execute /test-pagbank-auth/ para validar credenciais",
                "Execute /test-pagbank-order/ para testar criação de ordem",
                "Configure webhook endpoint em produção"
            ] if health_score == 100 else []
        })
        
    except Exception as e:
        return Response({
            'status': 'ERROR',
            'error': str(e),
            'message': 'Erro no health check'
        })

def get_health_recommendations(config, connectivity):
    """Gera recomendações baseadas no health check"""
    recommendations = []
    
    if not config['email_configured']:
        recommendations.append("⚠️ Configure PAGBANK_EMAIL no arquivo .env")
    
    if not config['token_configured']:
        recommendations.append("⚠️ Configure PAGBANK_TOKEN no arquivo .env")
    
    if config['environment'] == 'not_set':
        recommendations.append("⚠️ Configure PAGBANK_ENVIRONMENT (sandbox ou production)")
    
    if config['notification_url'] == 'not_set':
        recommendations.append("💡 Configure PAGBANK_NOTIFICATION_URL para webhooks")
    
    if not connectivity:
        recommendations.append("🌐 Verificar conectividade com a internet")
    
    if not recommendations:
        recommendations.append("✅ Configuração completa! Sistema pronto para uso.")
    
    return recommendations

@api_view(['GET'])
def test_pagseguro(request):
    """Teste da integração PagSeguro (compatibilidade)"""
    try:
        # Redirecionar para o teste do PagBank
        return test_pagbank_order(request)
        
    except Exception as e:
        return Response({
            'error': str(e),
            'type': type(e).__name__,
            'message': 'Use /test-pagbank-order/ para testes mais completos'
        })

# Compatibilidade com código existente
test_mercadopago = test_pagseguro

@api_view(['GET'])
def api_documentation(request):
    """Documentação básica da API"""
    return Response({
        'api_name': 'PagBank Payment Gateway',
        'version': '1.0.0',
        'endpoints': {
            'payments': {
                'list_create': 'GET/POST /api/payments/',
                'detail': 'GET /api/payments/{id}/',
                'status': 'GET /api/payments/{id}/status/',
                'transparent': 'POST /api/payments/transparent/'
            },
            'webhooks': {
                'pagbank': 'POST /api/payments/webhook/'
            },
            'testing': {
                'health': 'GET /api/pagbank-health/',
                'auth_test': 'GET /api/test-pagbank-auth/',
                'order_test': 'POST /api/test-pagbank-order/',
                'config': 'GET /api/test-config/'
            },
            'utils': {
                'health_simple': 'GET /api/',
                'docs': 'GET /api/docs/'
            }
        },
        'flow': {
            '1': 'Execute /api/pagbank-health/ para verificar configuração',
            '2': 'Execute /api/test-pagbank-auth/ para validar credenciais',
            '3': 'Execute /api/test-pagbank-order/ para testar criação',
            '4': 'Use /api/payments/ para operações reais'
        }
    })

# Adicionar ao final para evitar erros de importação
try:
    from .services import PagBankService
except ImportError:
    logger.warning("PagBankService não encontrado, usando PagSeguroService")
    PagBankService = PagSeguroService