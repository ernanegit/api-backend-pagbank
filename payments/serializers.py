from rest_framework import serializers
from decimal import Decimal
from .models import Payment, PaymentItem

class PaymentItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentItem
        fields = ['title', 'quantity', 'unit_price', 'total_price']
    
    def get_total_price(self, obj):
        """Calcula o preço total do item"""
        return float(obj.quantity * obj.unit_price)

class PaymentSerializer(serializers.ModelSerializer):
    items = PaymentItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'description', 'payer_email', 'status', 'status_display',
            'preference_id', 'payment_gateway_id', 'created_at', 'updated_at', 
            'items', 'total_amount'
        ]
        read_only_fields = [
            'id', 'status', 'preference_id', 'payment_gateway_id', 
            'created_at', 'updated_at'
        ]
    
    def get_total_amount(self, obj):
        """Calcula o valor total baseado nos itens"""
        return float(sum(item.quantity * item.unit_price for item in obj.items.all()))

class CreatePaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField(max_length=255)
    payer_email = serializers.EmailField()
    items = PaymentItemSerializer(many=True)
    
    # Campos opcionais para pagamento transparente
    payer_name = serializers.CharField(max_length=100, required=False)
    payer_cpf = serializers.CharField(max_length=14, required=False)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("O valor deve ser maior que zero.")
        return value
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Deve haver pelo menos um item.")
        
        # CORREÇÃO: Usar Decimal para todos os cálculos
        items_total = sum(
            Decimal(str(item['quantity'])) * Decimal(str(item['unit_price'])) 
            for item in value
        )
        
        if 'amount' in self.initial_data:
            # CORREÇÃO: Converter para Decimal também
            declared_amount = Decimal(str(self.initial_data['amount']))
            tolerance = Decimal('0.01')  # Tolerância de 1 centavo
            
            if abs(items_total - declared_amount) > tolerance:
                raise serializers.ValidationError(
                    f"Total dos itens (R$ {items_total:.2f}) não confere "
                    f"com o valor declarado (R$ {declared_amount:.2f})"
                )
        
        return value
    
    def validate_payer_cpf(self, value):
        """Validação básica de CPF (opcional)"""
        if value:
            # Remove caracteres não numéricos
            cpf = ''.join(filter(str.isdigit, value))
            if len(cpf) != 11:
                raise serializers.ValidationError("CPF deve ter 11 dígitos")
        return value

class TransparentPaymentSerializer(serializers.Serializer):
    """Serializer específico para pagamento transparente"""
    payment = CreatePaymentSerializer()
    card = serializers.DictField(child=serializers.CharField())
    
    def validate_card(self, value):
        required_fields = ['token', 'security_code', 'holder_name', 'holder_cpf']
        missing_fields = [field for field in required_fields if field not in value]
        
        if missing_fields:
            raise serializers.ValidationError(
                f"Campos obrigatórios do cartão: {', '.join(missing_fields)}"
            )
        
        return value