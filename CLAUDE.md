# Foresight Platform — CLAUDE.md

> Regla de oro: **nunca avances sin que el usuario dé autorización explícita.**

---

## Proyecto

Plataforma de mercados de predicción basada en GenLayer Intelligent Contracts.
- **Foresight_markets.py** — contrato principal de mercados
- **The_Signal.py** — contrato de newsletter/señales
- **Frontend**: `C:\Users\randy\Desktop\foresight-ui\` (HTML + JSX vanilla)

Repositorio local contratos: `C:\Users\randy\Desktop\foresight-platform\`
Repositorio local frontend: `C:\Users\randy\Desktop\foresight-ui\`

---

## Red objetivo: Testnet Bradbury

| Parámetro | Valor |
|-----------|-------|
| RPC | `https://rpc-bradbury.genlayer.com` (sin `/api` al final) |
| Chain ID | 4221 (hex: `0x107D`) |
| Explorer | `https://explorer-bradbury.genlayer.com/` |
| Consensus contract | `0x0112Bf6e83497965A5fdD6Dad1E447a6E004271D` |
| GenVM version en Bradbury | `v0.2.11-x86_64-linux-release` |

### Wallet Bradbury
- **Keystore**: `C:\Users\randy\.genlayer\keystores\bradbury.json`
- **Address**: `0x5A013abC96Ce8D65C8Ba9Be814E0bf71C693CEa3`
- **Password**: "foresight"

---

## Contratos deployados en Bradbury ✅

| Contrato | Address | Estado |
|----------|---------|--------|
| `Foresight_markets.py` | `0x43b38042d43dffD570bD561Ac46294785f7E202B` | ✅ Probado |
| `The_Signal.py` | `0xd776B579E21a89C0FC0Ee33E78eda866d9aD5ded` | ✅ Probado |

---

## Runner hash correcto para Bradbury

```python
# { "Depends": "py-genlayer:1j12s63yfjpva9ik2xgnffgrs6v44y1f52jvj9w7xvdn7qckd379" }
```

- `py-genlayer:test` → **BLOQUEADO** en Bradbury (non-debug mode)
- `py-genlayer:1jb45aa8...` (v0.2.16) → **EVM revert** (no registrado en Bradbury)
- `py-genlayer:1j12s63y...` (v0.2.11) → ✅ **FUNCIONA** en Bradbury

---

## APIs correctas (py-genlayer v0.2.11 SDK)

```python
# CORRECTO — verificado en Bradbury:
data = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
if not isinstance(leaders_result, gl.vm.Return):
leader_data = leaders_result.calldata
web_data = gl.nondet.web.render(url, mode="text")
data = gl.nondet.exec_prompt(prompt, response_format="json")
```

```python
# INCORRECTO — no existe en este SDK:
data = advanced.run_nondet(leader_fn, validator_fn)
if not isinstance(leaders_result, advanced.ContractReturn):
leader_data = leaders_result.data
web_data = get_webpage(url, mode="text")
data = exec_prompt(prompt, response_format="json")
```

---

## Bug crítico: Address.lower() en GenVM

En GenVM `v0.2.11`, los parámetros de tipo `Address` se pasan como objetos `Address`,
no como `str`. Cualquier `.lower()` directamente sobre ellos falla.

**Fix**: siempre envolver con `str()` antes de llamar `.lower()`:

```python
# INCORRECTO:
if parts[1].lower() == user_address.lower():
addr = user_address.lower()

# CORRECTO:
if parts[1].lower() == str(user_address).lower():
addr = str(user_address).lower()
```

Foresight_markets.py ya tiene este fix en líneas 53 y 129.
The_Signal.py no tiene comparaciones de address — no aplica.

---

## Reglas de storage GenLayer

- Usar tipos SDK: `TreeMap`, `DynArray`, `Address`, `u256`, etc.
- **NO** usar `dict` o `list` nativos de Python como campos de storage
- Los campos de storage se declaran a nivel de clase

---

## Frontend — genlayer-js

### Chain exports de `genlayer-js/chains`
| Export | Chain ID | RPC |
|--------|----------|-----|
| `localnet` | 61127 | localhost |
| `studionet` | 61999 | `https://studio.genlayer.com/api` |
| `testnetAsimov` | — | — |
| `testnetBradbury` | 4221 | `https://rpc-bradbury.genlayer.com` |

### Diferencia clave Studio vs Bradbury en el SDK
- Studio tiene `isStudio: true` → usa APIs especiales (cancelTransaction, etc.)
- Bradbury tiene `isStudio: false` → usa APIs estándar EVM

### Archivos del frontend actualizados (Studio → Bradbury)
| Archivo | Cambios |
|---------|---------|
| `genlayer-client.js` | `testnetBradbury`, nuevas addresses, RPC Bradbury |
| `chrome.jsx` | chainId `0x107D`, nombre red, RPC, labels UI |
| `signal-app.jsx` | address contrato, labels BRADBURY |

---

## Funciones probadas en Bradbury

### Foresight_markets.py
| Función | Tipo | Estado |
|---------|------|--------|
| `get_summary` | view | ✅ |
| `get_market(id)` | view | ✅ |
| `get_market_count` | view | ✅ |
| `get_my_predictions(addr)` | view | ✅ |
| `get_markets_by_category(cat)` | view | ✅ |
| `get_top_predictors` | view | ✅ |
| `get_predictor_stats(addr)` | view | ✅ |
| `generate_market(url, hint)` | write | ✅ |
| `place_prediction(id, side)` | write | ✅ |
| `resolve_market(id)` | write | ✅ |
| `claim_winnings(id)` | write | ✅ |

### The_Signal.py
| Función | Tipo | Estado |
|---------|------|--------|
| `get_summary` | view | ✅ |
| `get_article(id)` | view | ✅ |
| `get_article_count` | view | ✅ |
| `get_articles_by_category(cat)` | view | ✅ |
| `get_latest(n)` | view | ✅ |
| `publish_article(cat, url1, url2, url3)` | write | ✅ |

---

## Tip para markets que NO entren en DISPUTE

Usar URL de evento ya confirmado (pasado). Ejemplos que funcionan:
- `https://en.wikipedia.org/wiki/2024_United_States_presidential_election`
  + topic_hint: `"Trump 2024 election winner"`
  → Resuelve YES con 90% confidence ✅

Evitar preguntas sobre eventos futuros o no confirmados → resultan en DISPUTE.

---

## Comandos útiles

```bash
# Ver cuenta y balance
genlayer account

# Deploy
echo "foresight" | genlayer deploy --contract Foresight_markets.py

# Leer contrato (view)
genlayer call <address> <method>
genlayer call <address> <method> --args "arg1" "arg2"

# Escribir (transacción)
echo "foresight" | genlayer write <address> <method> --args "arg1" "arg2"

# Ver código de contrato deployado
genlayer code <address>

# Trace de transacción (para debug)
echo "foresight" | genlayer trace <txHash>

# Receipt
echo "foresight" | genlayer receipt <txHash> --retries 30 --interval 5000

# Lint del contrato (usar path completo en Windows)
& "C:\Users\randy\AppData\Local\Programs\Python\Python314\Scripts\genvm-lint.exe" check Foresight_markets.py --json
```

---

## Linter

```bash
# Instalado en:
# C:\Users\randy\AppData\Local\Programs\Python\Python314\Lib\site-packages\genvm_linter\

# Estado actual de los contratos:
# Foresight_markets.py: ✅ ok (lint AST pasa; validate falla por SSL — bug de entorno, no de código)
# The_Signal.py: ✅ ok (mismo)
```

---

## Archivos clave

| Archivo | Ubicación |
|---|---|
| Contrato principal | `C:\Users\randy\Desktop\foresight-platform\Foresight_markets.py` |
| Contrato señales | `C:\Users\randy\Desktop\foresight-platform\The_Signal.py` |
| Frontend client | `C:\Users\randy\Desktop\foresight-ui\genlayer-client.js` |
| Frontend chrome | `C:\Users\randy\Desktop\foresight-ui\chrome.jsx` |
| Frontend signal | `C:\Users\randy\Desktop\foresight-ui\signal-app.jsx` |
| Keystore | `C:\Users\randy\.genlayer\keystores\bradbury.json` |
