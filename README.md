# 🏦 PagBank Payment Gateway API

Gateway de pagamento completo integrado com PagBank (PagSeguro) desenvolvido em Django REST Framework.

## ✨ Funcionalidades

- ✅ Integração completa com PagBank API v4
- ✅ Criação de pagamentos e checkout
- ✅ Pagamento transparente (cartão de crédito)
- ✅ Webhook para notificações automáticas
- ✅ Health checks e monitoramento
- ✅ Testes automatizados
- ✅ API RESTful completa
- ✅ Documentação integrada

## 🚀 Tecnologias

- **Backend**: Django 5.2 + Django REST Framework
- **Banco**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Gateway**: PagBank (PagSeguro) API v4
- **Autenticação**: Bearer Token
- **Documentação**: OpenAPI/Swagger

## 📦 Instalação

### **Pré-requisitos**
- Python 3.8+
- pip
- Conta PagBank (sandbox ou produção)

### **1. Clonar o repositório**
```bash
git clone https://github.com/ernanegit/api-pagbank-frontend.git
cd api-pagbank-frontend
```

### **2. Criar ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### **3. Instalar dependências**
```bash
pip install -r requirements.txt
```

### **4. Configurar variáveis de ambiente**
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Configure suas credenciais PagBank
PAGSEGURO_EMAIL=seu-email@pagbank.com
PAGSEGURO_TOKEN=seu-token-pagbank
PAGSEGURO_ENVIRONMENT=sandbox
```

### **5. Executar migrações**
```bash
python manage.py migrate
```

### **6. Iniciar servidor**
```bash
python manage.py runserver
```

## 📚 Documentação da API

### **Endpoints Principais**

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/` | GET | Health check básico |
| `/api/docs/` | GET | Documentação completa |
| `/api/payments/` | GET/POST | CRUD de pagamentos |
| `/api/payments/{id}/` | GET | Detalhes do pagamento |
| `/api/payments/{id}/status/` | GET | Status do pagamento |
| `/api/payments/webhook/` | POST | Webhook PagBank |

### **Endpoints de Teste**

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/pagbank-health/` | GET | Health check detalhado |
| `/api/test-pagbank-auth/` | GET | Testar autenticação |
| `/api/test-pagbank-order/` | POST | Testar criação de ordem |
| `/api/test-config/` | GET | Verificar configurações |

### **Exemplo de Uso**

```bash
# Criar pagamento
curl -X POST http://localhost:8000/api/payments/ \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 99.90,
    "description": "Produto Premium",
    "payer_email": "cliente@email.com",
    "items": [
      {
        "title": "Produto",
        "quantity": 1,
        "unit_price": 99.90
      }
    ]
  }'
```

**Resposta:**
```json
{
  "payment_id": "4c9ec945-c1bb-4d98-a265-c2ce85abe311",
  "checkout_url": "https://sandbox.api.pagseguro.com/orders/ORDE_D0CB38A7/pay"
}
```

## 🧪 Testes

### **Health Check**
```bash
curl http://localhost:8000/api/pagbank-health/
```

### **Testar Autenticação**
```bash
curl http://localhost:8000/api/test-pagbank-auth/
```

### **Criar Pagamento de Teste**
```bash
curl -X POST http://localhost:8000/api/test-pagbank-order/
```

### **Listar Pagamentos**
```bash
curl http://localhost:8000/api/payments/
```

### **Testes por Bandeira de Cartão**

O PagBank oferece cartões de teste para cada bandeira. Você pode simular pagamentos para diferentes bandeiras:

#### **Teste Visa**
```powershell
$headers = @{ 'Content-Type' = 'application/json' }
$body = @{
    amount = 199.90
    description = "Teste Visa"
    payer_email = "visa@teste.com"
    items = @(
        @{
            title = "Produto Teste Visa"
            quantity = 1
            unit_price = 199.90
        }
    )
} | ConvertTo-Json -Depth 3

Invoke-WebRequest -Uri "http://localhost:8000/api/payments/" -Method POST -Headers $headers -Body $body
```

#### **Teste Mastercard**
```powershell
$headers = @{ 'Content-Type' = 'application/json' }
$body = @{
    amount = 299.90
    description = "Teste Mastercard"
    payer_email = "mastercard@teste.com"
    items = @(
        @{
            title = "Produto Teste Mastercard"
            quantity = 1
            unit_price = 299.90
        }
    )
} | ConvertTo-Json -Depth 3

Invoke-WebRequest -Uri "http://localhost:8000/api/payments/" -Method POST -Headers $headers -Body $body
```

#### **Teste American Express**
```powershell
$headers = @{ 'Content-Type' = 'application/json' }
$body = @{
    amount = 399.90
    description = "Teste American Express"
    payer_email = "amex@teste.com"
    items = @(
        @{
            title = "Produto Teste Amex"
            quantity = 1
            unit_price = 399.90
        }
    )
} | ConvertTo-Json -Depth 3

Invoke-WebRequest -Uri "http://localhost:8000/api/payments/" -Method POST -Headers $headers -Body $body
```

#### **Teste Elo**
```powershell
$headers = @{ 'Content-Type' = 'application/json' }
$body = @{
    amount = 499.90
    description = "Teste Elo"
    payer_email = "elo@teste.com"
    items = @(
        @{
            title = "Produto Teste Elo"
            quantity = 1
            unit_price = 499.90
        }
    )
} | ConvertTo-Json -Depth 3

Invoke-WebRequest -Uri "http://localhost:8000/api/payments/" -Method POST -Headers $headers -Body $body
```

### **Cartões de Teste PagBank**

Para testes em ambiente sandbox, use estes cartões fornecidos pelo PagBank:

| Bandeira | Número | CVV | Expiração | Resultado Esperado |
|----------|--------|-----|-----------|-------------------|
| **Visa** | `4539620659922097` | 123 | 12/2030 | ✅ Aprovado |
| **Mastercard** | `5240082975622454` | 123 | 12/2030 | ✅ Aprovado |
| **American Express** | `345817690311361` | 123 | 12/2030 | ✅ Aprovado |
| **Elo** | `4514161122113757` | 123 | 12/2030 | ✅ Aprovado |
| **Hipercard** | `6062828598919021` | 123 | 12/2030 | ✅ Aprovado |

### **Valores de Teste**

Para diferentes cenários de teste:

| Valor | Resultado Esperado |
|-------|-------------------|
| R$ 1,00 - R$ 50,00 | ✅ Aprovado automaticamente |
| R$ 50,01 - R$ 100,00 | ⏳ Fica pendente para análise |
| R$ 100,01 - R$ 200,00 | ❌ Rejeitado automaticamente |
| > R$ 200,00 | ✅ Aprovado (conforme configuração) |

> **Nota**: Estes cartões são fornecidos pelo PagBank para testes em ambiente sandbox. Para pagamento transparente, os números devem ser criptografados usando a chave pública.

### **Resultados Esperados**

Após executar os testes, você deve ver:

1. **Status 201** em todos os pagamentos
2. **payment_id** único para cada transação
3. **checkout_url** válida do PagBank
4. **Transações** aparecendo no Portal do Desenvolvedor PagBank

### **Teste Completo - Todas as Bandeiras**

Script PowerShell para testar todas as bandeiras automaticamente:

```powershell
# Função para criar pagamento
function New-Payment($amount, $description, $email, $title) {
    $headers = @{ 'Content-Type' = 'application/json' }
    $body = @{
        amount = $amount
        description = $description
        payer_email = $email
        items = @(
            @{
                title = $title
                quantity = 1
                unit_price = $amount
            }
        )
    } | ConvertTo-Json -Depth 3
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/payments/" -Method POST -Headers $headers -Body $body
        $result = $response.Content | ConvertFrom-Json
        Write-Host "✅ $description - Payment ID: $($result.payment_id)" -ForegroundColor Green
        return $result
    } catch {
        Write-Host "❌ Erro em $description`: $_" -ForegroundColor Red
    }
}

# Testar todas as bandeiras
Write-Host "🧪 Iniciando testes de todas as bandeiras..." -ForegroundColor Cyan

$visa = New-Payment 199.90 "Teste Visa" "visa@teste.com" "Produto Teste Visa"
$mastercard = New-Payment 299.90 "Teste Mastercard" "mastercard@teste.com" "Produto Teste Mastercard"  
$amex = New-Payment 399.90 "Teste American Express" "amex@teste.com" "Produto Teste Amex"
$elo = New-Payment 499.90 "Teste Elo" "elo@teste.com" "Produto Teste Elo"
$hipercard = New-Payment 599.90 "Teste Hipercard" "hipercard@teste.com" "Produto Teste Hipercard"

Write-Host "`n📊 Resumo dos Testes:" -ForegroundColor Yellow
Write-Host "- Visa: $($visa.payment_id)"
Write-Host "- Mastercard: $($mastercard.payment_id)"  
Write-Host "- Amex: $($amex.payment_id)"
Write-Host "- Elo: $($elo.payment_id)"
Write-Host "- Hipercard: $($hipercard.payment_id)"

Write-Host "`n🎯 Verificar transações em: https://portaldev.pagbank.com.br/transacoes" -ForegroundColor Magenta
```

## 💳 Fluxo de Pagamento

1. **Frontend** cria pagamento via `POST /api/payments/`
2. **API** retorna `checkout_url` do PagBank
3. **Cliente** é redirecionado para página de pagamento
4. **PagBank** processa pagamento e envia webhook
5. **API** atualiza status via `POST /api/payments/webhook/`
6. **Frontend** consulta status via `GET /api/payments/{id}/status/`

## 🔧 Configuração de Produção

### **1. Variáveis de Ambiente**
```bash
DEBUG=False
PAGSEGURO_ENVIRONMENT=production
PAGSEGURO_EMAIL=seu-email-producao@empresa.com
PAGSEGURO_TOKEN=seu-token-producao
ALLOWED_HOSTS=seudominio.com,www.seudominio.com
```

### **2. Banco de Dados PostgreSQL**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/pagbank_prod
```

### **3. HTTPS e Webhook**
```bash
PAGSEGURO_NOTIFICATION_URL=https://seudominio.com/api/payments/webhook/
```

### **4. Deploy Heroku/Railway**
```bash
# Adicionar ao requirements.txt
gunicorn==21.2.0
whitenoise==6.6.0
psycopg2-binary==2.9.9

# Criar Procfile
echo "web: gunicorn mercadopago_backend.wsgi" > Procfile
```

## 📊 Monitoramento

### **Health Check Detalhado**
```bash
GET /api/pagbank-health/
```

**Resposta:**
```json
{
  "status": "OK",
  "health_score": "100.0%",
  "configuration": {
    "email_configured": true,
    "token_configured": true,
    "environment": "sandbox"
  },
  "connectivity": {
    "api_reachable": true
  }
}
```

### **Logs**
- **Arquivo**: `logs/pagbank.log`
- **Formato**: JSON estruturado
- **Níveis**: INFO, WARNING, ERROR

## 🎯 Status de Pagamento

| Status PagBank | Status Local | Descrição |
|----------------|--------------|-----------|
| `PAID` | `approved` | Pagamento aprovado |
| `DECLINED` | `rejected` | Pagamento recusado |
| `CANCELED` | `cancelled` | Pagamento cancelado |
| `WAITING` | `pending` | Aguardando pagamento |
| `IN_ANALYSIS` | `pending` | Em análise |

## 🛡️ Segurança

- ✅ **CORS** configurado
- ✅ **CSRF** protection
- ✅ **SQL Injection** protection (Django ORM)
- ✅ **XSS** protection
- ✅ **Rate limiting** (produção)
- ✅ **HTTPS** obrigatório (produção)

## 📱 Integração Frontend

### **React Exemplo**
```javascript
// Criar pagamento
const createPayment = async (paymentData) => {
  const response = await fetch('/api/payments/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(paymentData)
  });
  
  const data = await response.json();
  
  if (data.checkout_url) {
    window.location.href = data.checkout_url;
  }
};

// Verificar status
const checkStatus = async (paymentId) => {
  const response = await fetch(`/api/payments/${paymentId}/status/`);
  return await response.json();
};
```

### **Vue.js Exemplo**
```javascript
// Composable para pagamentos
export const usePayments = () => {
  const createPayment = async (data) => {
    try {
      const response = await $fetch('/api/payments/', {
        method: 'POST',
        body: data
      });
      return response;
    } catch (error) {
      console.error('Erro ao criar pagamento:', error);
      throw error;
    }
  };

  return { createPayment };
};
```

## 🧪 Testes Automatizados

```bash
# Executar testes
python manage.py test

# Coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 📸 Screenshots

### 🏦 Portal do Desenvolvedor PagBank

#### Logs de API
![Logs da API](docs/images/screenshots/01-portal-logs.png)

#### Transações Criadas
![Lista de Transações](docs/images/screenshots/02-transacoes-lista.png)

#### Cartões de Teste Disponíveis
![Cartões de Teste](docs/images/screenshots/03-cartoes-teste.png)

#### Interface do Portal
![Primeiros Passos](docs/images/screenshots/04-primeiros-passos.png)

### 📊 Resultados dos Testes

As imagens acima mostram:
- ✅ **6 transações** criadas com sucesso
- ✅ **Logs HTTP 201** confirmando criação
- ✅ **Todas as bandeiras** testadas (Visa, Mastercard, Amex, Elo)
- ✅ **Portal sincronizado** em tempo real

### 🎯 Validação da Integração

O Portal do Desenvolvedor PagBank confirma que:
1. **API está funcionando** (logs com status 201)
2. **Transações sendo registradas** (6 ordens criadas)
3. **Diferentes horários** (16:04, 16:02, 16:01, 14:30, 14:12)
4. **Ambiente de teste** funcionando perfeitamente



## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📋 Roadmap

- [ ] **PIX** - Integração com PIX
- [ ] **Boleto** - Pagamento via boleto
- [ ] **Recorrência** - Pagamentos recorrentes
- [ ] **Dashboard** - Painel administrativo
- [ ] **Analytics** - Relatórios e métricas
- [ ] **Multi-tenant** - Suporte a múltiplas contas

## ❓ FAQ

### **Como obter credenciais PagBank?**
1. Acesse o [Portal do Desenvolvedor](https://developer.pagbank.com.br/)
2. Crie uma conta ou faça login
3. Gere um token de sandbox para testes
4. Para produção, solicite homologação

### **Como configurar webhook em produção?**
1. Configure HTTPS no seu servidor
2. Defina `PAGSEGURO_NOTIFICATION_URL=https://seudominio.com/api/payments/webhook/`
3. Teste o webhook com ferramentas como ngrok

### **Como debugar problemas de pagamento?**
1. Verifique `/api/pagbank-health/`
2. Execute `/api/test-pagbank-auth/`
3. Consulte `logs/pagbank.log`
4. Verifique transações no portal PagBank

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**Ernane Alexandre Freitas**
- Email: ernane1974@gmail.com
- GitHub: [@ernanegit](https://github.com/ernanegit)
- LinkedIn: [Ernane Freitas](https://linkedin.com/in/ernane-freitas)

## 🙏 Agradecimentos

- **PagBank** pela excelente documentação da API
- **Django** e **DRF** pela framework robusta
- **Comunidade Python** pelo suporte contínuo

---

⭐ **Se este projeto foi útil, deixe uma estrela!**

📢 **Encontrou um bug? Abra uma [issue](https://github.com/ernanegit/api-pagbank-frontend/issues)**

🚀 **Quer contribuir? Veja nosso [guia de contribuição](CONTRIBUTING.md)**