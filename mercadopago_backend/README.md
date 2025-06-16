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