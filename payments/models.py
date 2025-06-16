from django.db import models
import uuid

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
        ('cancelled', 'Cancelado'),
        ('refunded', 'Reembolsado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # SUGESTÃO: Renomear para ser mais genérico
    # mercadopago_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    payment_gateway_id = models.CharField(
        max_length=100, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="ID da transação no gateway de pagamento (PagBank/PagSeguro)"
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    payer_email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    preference_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SUGESTÕES DE MELHORIAS OPCIONAIS:
    
    # 1. Adicionar campo para o gateway usado
    # gateway_type = models.CharField(
    #     max_length=20, 
    #     choices=[('pagseguro', 'PagSeguro'), ('pagbank', 'PagBank')],
    #     default='pagbank'
    # )
    
    # 2. Adicionar metadados JSON para flexibilidade
    # metadata = models.JSONField(default=dict, blank=True)
    
    # 3. Adicionar índices para performance
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['payer_email']),
            models.Index(fields=['payment_gateway_id']),  # ou mercadopago_id
            models.Index(fields=['preference_id']),
        ]
    
    def __str__(self):
        return f"Payment {self.id} - {self.status}"
    
    # PROPRIEDADE PARA COMPATIBILIDADE
    @property
    def mercadopago_id(self):
        """Compatibilidade com código existente"""
        return self.payment_gateway_id
    
    @mercadopago_id.setter
    def mercadopago_id(self, value):
        """Compatibilidade com código existente"""
        self.payment_gateway_id = value

class PaymentItem(models.Model):
    payment = models.ForeignKey(Payment, related_name='items', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # SUGESTÃO: Adicionar campo de SKU/código do produto
    # sku = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} - {self.quantity}x R${self.unit_price}"
    
    @property
    def total_price(self):
        """Calcula o preço total do item"""
        return self.quantity * self.unit_price