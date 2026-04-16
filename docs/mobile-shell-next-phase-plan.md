# Mobile Shell — Next Phase Plan

## Objetivo desta fase
Promover a linha híbrida a direção principal do cockpit mobile, mantendo o `main` protegido e a PR limpa.

## Meta funcional
Nesta fase a shell deve aproximar-se de uso real diário com:
- modo `driving`
- modo `assisted`
- configuração de `API base`
- preparação para backend local no futuro PC
- preparação para túnel privado/free

## O que já existe
- shell estável atual no `main`
- candidato híbrido já integrado
- smoke do híbrido verde
- docs de runtime local híbrido
- política de merge seletivo

## O que deve entrar nesta fase
### 1. Promoção controlada
- decidir se `index.hybrid.html` passa a substituir `index.html`
- decidir se `app.hybrid.js` passa a substituir `app.js`
- decidir se `styles.hybrid.css` passa a substituir `styles.css`

### 2. Backend base configurável
- permitir trocar entre Render, local PC e túnel
- guardar URL local/túnel no browser
- tornar esta escolha simples e visível

### 3. UX híbrida
- driving: menos campos, menos distração, ação curta
- assisted: mais campos, mais contexto, mais botões
- transição clara entre os dois modos

### 4. Preparação PC local
- manter compatibilidade com `127.0.0.1:8787`
- manter compatibilidade com shell local em `127.0.0.1:4173`

## Regra de segurança desta fase
Não alterar ficheiros fora do âmbito mobile shell sem necessidade.

## Checklist de saída
- shell híbrida promovida ou pronta para promoção
- smoke verde da fase
- changed files limpo
- PR pequena
- merge sem squash
