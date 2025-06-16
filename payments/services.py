import requests
import json
import logging
from django.conf import settings
from .models import Payment, PaymentItem

logger = logging.getLogger(__name__)

class PagBankService:
    """Service para PagBank API v4 - FUNCIONANDO"""
    
    def __init__(self):
        self.email = getattr(settings, 'PAGSEGURO_EMAIL', '')
        self.token = getattr(settings, 'PAGSEGURO_TOKEN', '')
        self.environment = getattr(settings, 'PAGSEGURO_ENVIRONMENT', 'sandbox')
        
        if self.environment == 'sandbox':
            self.api_url = "https://sandbox.api.pagseguro.com"
        else:
            self.api_url = "https://api.pagseguro.com"
    
    def _get_headers(self):
        """Headers corretos para PagBank v4"""
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def test_connection(self):
        """Testa conexão com PagBank"""
        try:
            response = requests.get(
                f"{self.api_url}/public-keys",
                headers=self._get_headers(),
                timeout=10
            )
            
            return {
                "success": response.status_code == 200,
                "status": response.status_code,
                "response": response.text[:200] if response.text else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_order(self, payment_data):
        """Cria ordem no PagBank v4"""
        try:
            logger.info("Criando ordem PagBank v4...")
            
            # Estrutura correta PagBank v4 com todos os campos obrigatórios
            order_data = {
                "reference_id": str(payment_data.get('external_reference', '')),
                "customer": {
                    "name": payment_data.get('payer_name', 'Cliente Teste'),
                    "email": payment_data['payer_email'],
                    "tax_id": payment_data.get('payer_cpf', '12345678909'),  # CPF obrigatório
                    "phones": [
                        {
                            "country": "55",
                            "area": "11", 
                            "number": "999999999",
                            "type": "MOBILE"
                        }
                    ]
                },
                "items": [
                    {
                        "reference_id": str(idx),
                        "name": item['title'],
                        "quantity": item['quantity'],
                        "unit_amount": int(float(item['unit_price']) * 100)  # Centavos
                    }
                    for idx, item in enumerate(payment_data['items'], 1)
                ]
            }
            
            # Adicionar notification_urls apenas se configurado e válido
            notification_url = getattr(settings, 'PAGSEGURO_NOTIFICATION_URL', '')
            if notification_url and notification_url.startswith('https://'):
                order_data["notification_urls"] = [notification_url]
            
            logger.info(f"Dados da ordem: {json.dumps(order_data, indent=2)}")
            
            response = requests.post(
                f"{self.api_url}/orders",
                headers=self._get_headers(),
                json=order_data,
                timeout=30
            )
            
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Resposta: {response.text}")
            
            if response.status_code == 201:
                order = response.json()
                
                # Extrair URL de pagamento
                payment_url = None
                for link in order.get('links', []):
                    if link.get('rel') == 'PAY':
                        payment_url = link.get('href')
                        break
                
                return {
                    "success": True,
                    "order_id": order['id'],
                    "checkout_url": payment_url,
                    "payment_url": payment_url,
                    "links": order.get('links', []),
                    "order_data": order
                }
            else:
                error_data = response.json() if response.content else {}
                error_messages = error_data.get('error_messages', [])
                
                if error_messages:
                    error_msg = "; ".join([f"{err.get('code')}: {err.get('description')}" for err in error_messages])
                else:
                    error_msg = response.text
                
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code,
                    "response_data": error_data  # Para debug
                }
                
        except Exception as e:
            logger.error(f"Erro ao criar ordem: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_order(self, order_id):
        """Busca ordem no PagBank"""
        try:
            response = requests.get(
                f"{self.api_url}/orders/{order_id}",
                headers=self._get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "order": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Erro ao buscar ordem: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_charge_credit_card(self, payment_data, card_data):
        """Cria cobrança com cartão de crédito"""
        try:
            logger.info("Criando cobrança com cartão...")
            
            charge_data = {
                "reference_id": str(payment_data.get('external_reference', '')),
                "description": payment_data.get('description', 'Pagamento'),
                "amount": {
                    "value": int(float(payment_data['amount']) * 100),  # Centavos
                    "currency": "BRL"
                },
                "payment_method": {
                    "type": "CREDIT_CARD",
                    "installments": card_data.get('installments', 1),
                    "capture": True,
                    "card": {
                        "encrypted": card_data['encrypted_card'],
                        "security_code": card_data['security_code'],
                        "holder": {
                            "name": card_data['holder_name'],
                        }
                    }
                },
                "customer": {
                    "name": payment_data.get('payer_name', 'Cliente'),
                    "email": payment_data['payer_email'],
                    "tax_id": payment_data.get('payer_cpf', '12345678909'),
                },
                "notification_urls": [
                    getattr(settings, 'PAGSEGURO_NOTIFICATION_URL', 'http://localhost:8000/api/payments/webhook/')
                ]
            }
            
            logger.info(f"Dados da cobrança: {json.dumps(charge_data, indent=2)}")
            
            response = requests.post(
                f"{self.api_url}/charges",
                headers=self._get_headers(),
                json=charge_data,
                timeout=30
            )
            
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Resposta: {response.text}")
            
            if response.status_code == 201:
                charge = response.json()
                
                return {
                    "success": True,
                    "charge_id": charge['id'],
                    "status": charge['status'],
                    "payment_response": charge.get('payment_response', {}),
                    "amount": charge.get('amount', {})
                }
            else:
                error_data = response.json() if response.content else {}
                error_messages = error_data.get('error_messages', [])
                
                if error_messages:
                    error_msg = "; ".join([f"{err.get('code')}: {err.get('description')}" for err in error_messages])
                else:
                    error_msg = response.text
                
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"Erro na cobrança: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def process_webhook(self, webhook_data):
        """Processa webhook PagBank v4"""
        try:
            logger.info(f"Processando webhook: {webhook_data}")
            
            # Na API v4, o webhook já vem com os dados completos
            order_id = webhook_data.get('id')
            reference_id = webhook_data.get('reference_id')
            status = webhook_data.get('status')
            
            if order_id and reference_id:
                self.update_local_payment(reference_id, order_id, status)
                return {"success": True, "message": "Webhook processado"}
            else:
                return {"success": False, "error": "Dados incompletos no webhook"}
                
        except Exception as e:
            logger.error(f"Erro no webhook: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def update_local_payment(self, reference_id, order_id, status):
        """Atualiza pagamento local com dados do PagBank"""
        try:
            payment = Payment.objects.get(id=reference_id)
            payment.mercadopago_id = order_id
            
            # Mapeamento de status PagBank v4
            status_map = {
                'PAID': 'approved',
                'DECLINED': 'rejected',
                'CANCELED': 'cancelled',
                'AUTHORIZED': 'pending',
                'IN_ANALYSIS': 'pending',
                'WAITING': 'pending'
            }
            
            payment.status = status_map.get(status, 'pending')
            payment.save()
            
            logger.info(f"Payment {payment.id} atualizado - Status: {payment.status}")
            
        except Payment.DoesNotExist:
            logger.error(f"Payment com reference {reference_id} não encontrado")
        except Exception as e:
            logger.error(f"Erro ao atualizar pagamento: {str(e)}")
    
    # Métodos de compatibilidade
    def create_checkout_session(self, payment_data):
        """Compatibilidade - redireciona para create_order"""
        return self.create_order(payment_data)
    
    def create_transparent_payment(self, payment_data, card_data):
        """Compatibilidade - redireciona para create_charge_credit_card"""
        return self.create_charge_credit_card(payment_data, card_data)

# Alias para manter compatibilidade
PagSeguroService = PagBankService