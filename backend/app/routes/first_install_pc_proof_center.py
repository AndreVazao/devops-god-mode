from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.services.first_install_pc_proof_center_service import first_install_pc_proof_center_service

router = APIRouter(prefix="/api/first-install-pc-proof-center", tags=["first-install-pc-proof-center"])


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return first_install_pc_proof_center_service.status()


@router.get("/artifacts")
@router.post("/artifacts")
def artifacts() -> dict[str, Any]:
    return first_install_pc_proof_center_service.artifact_links()


@router.get("/commands")
@router.post("/commands")
def commands() -> dict[str, Any]:
    return first_install_pc_proof_center_service.pc_proof_commands()


@router.get("/checklist")
@router.post("/checklist")
def checklist() -> dict[str, Any]:
    return {"ok": True, "checklist": first_install_pc_proof_center_service.checklist()}


@router.get("/cards")
@router.post("/cards")
def cards() -> dict[str, Any]:
    return {"ok": True, "cards": first_install_pc_proof_center_service.operator_cards()}


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return first_install_pc_proof_center_service.package()


@router.get("/app", response_class=HTMLResponse)
def app_page() -> HTMLResponse:
    return HTMLResponse(_html())


def _html() -> str:
    return """<!doctype html>
<html lang="pt">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>God Mode — First Install PC Proof</title>
  <style>
    :root { color-scheme: dark; font-family: Inter, Segoe UI, system-ui, sans-serif; background:#080b12; color:#e8edf7; }
    body { margin:0; padding:18px; background:linear-gradient(180deg,#08111f,#05070c); }
    .wrap { max-width:1180px; margin:0 auto; }
    .hero { border:1px solid #1d2a44; background:#0d1424; border-radius:22px; padding:22px; box-shadow:0 16px 60px rgba(0,0,0,.35); }
    h1 { margin:0 0 8px; font-size:28px; }
    p { color:#b8c4d9; line-height:1.5; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:14px; margin-top:16px; }
    .card { border:1px solid #1d2a44; background:#0b1020; border-radius:18px; padding:16px; }
    .ready { color:#65e09c; }
    .operator_action_required { color:#ffd166; }
    .needs_attention { color:#ff6b6b; }
    a, button { color:#e8edf7; }
    button, .linkbtn { display:inline-block; border:0; background:#2358ff; padding:10px 12px; border-radius:12px; text-decoration:none; font-weight:700; margin:4px 4px 0 0; }
    code { display:block; white-space:pre-wrap; word-break:break-word; background:#050814; border:1px solid #1d2a44; padding:10px; border-radius:12px; color:#dbe7ff; }
    .small { font-size:13px; }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>God Mode — First Install PC Proof</h1>
      <p>Painel direto para a primeira instalação real no PC: artifacts, checklist, Playwright, providers IA, proofs e inventário.</p>
      <a class="linkbtn" href="/app/home">Abrir Home</a>
      <a class="linkbtn" href="/api/first-install-pc-proof-center/package">Ver JSON completo</a>
      <a class="linkbtn" href="https://github.com/AndreVazao/devops-god-mode/actions">GitHub Actions</a>
    </section>
    <div id="app" class="grid"></div>
  </div>
<script>
async function load(){
  const root = document.getElementById('app');
  try{
    const res = await fetch('/api/first-install-pc-proof-center/package');
    const data = await res.json();
    const checklist = data.checklist || [];
    const cards = data.operator_cards || [];
    const commands = (((data.pc_provider_commands||{}).commands)||[]);
    root.innerHTML = '';
    root.append(card('Missão', `<p>${data.mission?.goal || ''}</p><p class="small">${(data.mission?.tomorrow_success_definition||[]).join('<br>')}</p>`));
    root.append(card('Checklist', checklist.map(x=>`<p><b class="${x.status}">${x.status}</b> — ${x.label}<br><span class="small">${x.detail}</span></p>`).join('')));
    root.append(card('Ações rápidas', cards.map(x=>`<p><b>${x.title}</b><br><span class="small">${x.description}</span><br>${x.url?`<a href="${x.url}">Abrir</a>`:''}${x.route?`<a href="${x.route}">Abrir</a>`:''}${x.endpoint?`<a href="${x.endpoint}">Abrir</a>`:''}</p>`).join('')));
    root.append(card('Comandos provider proof', commands.map(x=>`<p><b>${x.provider}</b><code>${x.command}</code></p>`).join('')));
  }catch(e){ root.innerHTML = `<div class="card"><b>Erro</b><p>${e}</p></div>`; }
}
function card(title, html){ const el=document.createElement('div'); el.className='card'; el.innerHTML=`<h2>${title}</h2>${html}`; return el; }
load();
</script>
</body>
</html>"""
