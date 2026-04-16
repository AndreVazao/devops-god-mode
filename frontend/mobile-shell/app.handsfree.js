const PRESETS={render:{label:'Render',backend:'https://devops-god-mode-backend.onrender.com',shell:''},local_pc:{label:'PC local',backend:'http://127.0.0.1:8787',shell:'http://127.0.0.1:4173'},private_tunnel:{label:'Túnel privado/free',backend:'',shell:''},manual:{label:'Manual',backend:'',shell:''}};
const KEY_API='god_mode_api_base';
const KEY_SHELL='god_mode_shell_url';
const KEY_MODE='god_mode_shell_mode';
const KEY_PRESET='god_mode_backend_preset';
const q=s=>document.querySelector(s);
const api=q('#apiBaseInput');
const shellUrl=q('#shellUrlInput');
const preset=q('#backendPresetSelect');
const presetValue=q('#backendPresetValue');
const badge=q('#connectionBadge');
const profile=q('#profileBadge');
const bs=q('#backendStatusValue');
const bp=q('#backendProfileValue');
const db=q('#decisionBadge');
const hb=q('#headlineBox');
const cc=q('#compactCards');
const ms=q('#modeSummary');
const af=q('#assistedFields');
const eo=q('#executionOutput');
const co=q('#cockpitOutput');
const qs=q('#quickSummaryOutput');
function base(){return (api.value||localStorage.getItem(KEY_API)||PRESETS.render.backend).trim().replace(/\/$/,'')}
function rel(){return q('#relatedReposInput').value.split(/\n+/).map(v=>v.trim()).filter(Boolean)}
function saveUrls(){localStorage.setItem(KEY_API,api.value.trim());localStorage.setItem(KEY_SHELL,shellUrl.value.trim());localStorage.setItem(KEY_PRESET,preset.value)}
function applyPreset(){const p=PRESETS[preset.value]||PRESETS.render;if(p.backend)api.value=p.backend;if(p.shell)shellUrl.value=p.shell;presetValue.textContent=preset.value;saveUrls();status()}
function payload(){return {text:q('#textInput').value,repo_full_name:q('#repoInput').value,preferred_path:q('#pathInput').value,proposed_branch:q('#branchInput').value,registry_context:{ecosystem_key:'baribudos-ecosystem',related_repos:rel()},desired_visibility:q('#visibilityInput').value,lifecycle_mode:q('#lifecycleInput').value,build_strategy:'github_actions_free_public',product_ready:false,base_branch:q('#baseBranchInput').value}}
async function fj(u,o={}){const r=await fetch(u,{headers:{'Content-Type':'application/json'},...o});const t=await r.text();let d=null;try{d=t?JSON.parse(t):null}catch{d={raw:t}}if(!r.ok)throw new Error(JSON.stringify(d));return d}
function cards(a){cc.innerHTML='';a.forEach(c=>{const x=document.createElement('article');x.className='compact-card';x.innerHTML='<p class="label">'+c.title+'</p><p class="value">'+(c.value||'—')+'</p>';cc.appendChild(x)})}
function dec(v){db.textContent=v||'sem decisão';db.className='badge '+(v==='ok'?'badge-success':v==='altera'?'badge-warning':v==='rejeita'?'badge-danger':'badge-neutral')}
function quick(s){qs.textContent=s}
function mode(v){localStorage.setItem(KEY_MODE,v);q('#drivingModeBtn').classList.toggle('mode-btn-active',v==='driving');q('#assistedModeBtn').classList.toggle('mode-btn-active',v==='assisted');af.style.display=v==='assisted'?'block':'none';ms.textContent=v==='driving'?'Driving: menos distração, headline curta e decisão rápida.':'Assisted: mais campos, mais contexto e mais controlo manual.'}
async function status(){badge.textContent='a validar';badge.className='badge badge-warning';presetValue.textContent=preset.value;try{const r=await fj(base()+'/');const o=await fj(base()+'/ops/status');bs.textContent=r.status||'ok';bp.textContent=o.profile||r.profile||'desconhecido';profile.textContent=o.profile||'backend';badge.textContent='online';badge.className='badge badge-success';quick('Ligação OK em '+base())}catch(e){bs.textContent='erro';bp.textContent=String(e.message).slice(0,80);badge.textContent='offline';badge.className='badge badge-danger';quick('Falha na ligação a '+base())}}
async function cockpit(){const d=await fj(base()+'/ops/mobile-cockpit',{method:'POST',body:JSON.stringify(payload())});co.textContent=JSON.stringify(d,null,2);hb.textContent=d.headline||d.next_step||'Ainda sem resposta.';dec(d.decision);cards(d.compact_cards||[]);quick((d.headline||'Cockpit gerado')+' | preset: '+preset.value)}
async function execp(){const d=await fj(base()+'/ops/execution-pipeline',{method:'POST',body:JSON.stringify(payload())});eo.textContent=JSON.stringify(d,null,2);hb.textContent=d.next_step||((d.approval_shell||{}).headline)||'Pipeline gerado.';dec(((d.approval_shell||{}).decision));const s=(d.approval_shell||{}).compact_summary||{};cards([{title:'Repo alvo',value:s.repo},{title:'Ficheiro alvo',value:s.path},{title:'Branch',value:s.branch},{title:'Operação',value:s.operation}]);quick('Pipeline gerado para '+(s.repo||'repo desconhecida'))}
function copySummary(){const t=[hb.textContent,qs.textContent,'Backend: '+base(),'Shell: '+(shellUrl.value||localStorage.getItem(KEY_SHELL)||'—'),'Preset: '+preset.value].join('\n');navigator.clipboard?.writeText(t).then(()=>quick('Resumo copiado.')).catch(()=>quick('Não foi possível copiar o resumo.'))}
api.value=localStorage.getItem(KEY_API)||PRESETS.render.backend;
shellUrl.value=localStorage.getItem(KEY_SHELL)||PRESETS.local_pc.shell;
preset.value=localStorage.getItem(KEY_PRESET)||'render';
mode(localStorage.getItem(KEY_MODE)||'driving');
status();
q('#refreshStatusBtn').onclick=status;
q('#applyPresetBtn').onclick=applyPreset;
q('#saveApiBtn').onclick=()=>{saveUrls();status()};
q('#statusBtn').onclick=status;
q('#drivingModeBtn').onclick=()=>mode('driving');
q('#assistedModeBtn').onclick=()=>mode('assisted');
q('#mobileCockpitBtn').onclick=()=>cockpit().catch(e=>{co.textContent=e.message;hb.textContent=e.message;dec('rejeita');cards([]);quick('Erro ao gerar cockpit.')});
q('#executionBtn').onclick=()=>execp().catch(e=>{eo.textContent=e.message;hb.textContent=e.message;dec('rejeita');cards([]);quick('Erro ao gerar pipeline.')});
q('#copySummaryBtn').onclick=copySummary;
q('#approveOkBtn').onclick=()=>quick('Aprovação rápida: OK');
q('#approveChangeBtn').onclick=()=>quick('Aprovação rápida: ALTERA');
q('#approveRejectBtn').onclick=()=>quick('Aprovação rápida: REJEITA');
