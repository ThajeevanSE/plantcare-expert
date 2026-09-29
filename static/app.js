/* Presentation only. All rule evaluation happens in Python on the local server. */
let config, answers = {}, groupIndex = 0, lastResult = null;
const $ = id => document.getElementById(id);
const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function sourceLinks(ids) {return ids.map(id => `<a href="${esc(config.sources[id].url)}" target="_blank" rel="noopener">${esc(id)} · ${esc(config.sources[id].publisher)}</a>`).join(' · ');}
function showError(message) {$('error').textContent=message; $('error').hidden=false;}
function clearResults() {lastResult=null;$('results').hidden=true;}
function renderQuestions() {
  const g=config.groups[groupIndex];
  $('steps').innerHTML=config.groups.map((item,i)=>`<button class="step ${i===groupIndex?'active':''}" data-step="${i}" ${i===groupIndex?'aria-current="step"':''}><span class="num">${i+1}</span>${esc(item.title)}</button>`).join('');
  $('group-title').textContent=g.title;$('group-description').textContent=g.description;$('step-label').textContent=`Section ${groupIndex+1} of ${config.groups.length}`;
  $('questions').innerHTML=config.questions.filter(q=>q.group===g.id).map(q=>`<div class="question"><div><label for="${q.key}">${esc(q.label)}</label>${q.help?`<small id="help-${q.key}">${esc(q.help)}</small>`:''}</div><select id="${q.key}" name="${q.key}" ${q.help?`aria-describedby="help-${q.key}"`:''}>${q.choices.map(([v,t])=>`<option value="${v}" ${answers[q.key]===v?'selected':''}>${esc(t)}</option>`).join('')}</select></div>`).join('');
  $('previous').disabled=groupIndex===0;$('next').disabled=groupIndex===config.groups.length-1;
  const n=Object.values(answers).filter(v=>v!=='unknown').length;
  $('progress-text').textContent=`${n} of ${config.questions.length} answered`;$('progress').max=config.questions.length;$('progress').value=n;
}
function renderResult(result) {
  lastResult=result; $('results').hidden=false;
  $('result-title').textContent=result.trace.length?'What the observations suggest':'More information is needed';
  $('result-message').textContent=`${result.message} ${result.answered} observations answered · ${result.trace.length} rules matched.`;
  $('result-cards').innerHTML=result.trace.map(t=>`<article class="result-card"><div class="card-top"><span class="tag">${esc(t.kind)}</span><span class="rule-id">${esc(t.rule_id)} · Round ${t.round}</span></div><h3>${esc(t.title)}</h3><p>${esc(t.advice)}</p><div class="evidence"><strong>Why this appeared</strong><ul>${t.evidence.map(e=>`<li>${esc(e)}</li>`).join('')}${t.parents.length?`<li>Derived from ${t.parents.map(esc).join(', ')}.</li>`:''}</ul></div><div class="source-links">${sourceLinks(t.sources)}<br>Section: ${esc(t.source_section)}</div></article>`).join('');
  $('trace').innerHTML=result.trace.length?result.trace.map(t=>`<div class="trace-row"><strong>Round ${t.round} · ${esc(t.rule_id)} · ${esc(t.title)}</strong><p>${t.evidence.map(esc).join(' AND ')}</p><p>Added facts: ${esc(Object.entries(t.derived).map(([k,v])=>`${k} = ${v}`).join(', '))}${t.parents.length?` · Supporting rules: ${t.parents.join(', ')}`:''}</p></div>`).join(''):'No rule fired. Unknown answers were not treated as No.';
  $('results').scrollIntoView({behavior:'smooth',block:'start'});
}
async function analyse() {
  const snapshot={...answers};$('analyse').disabled=true;$('error').hidden=true;
  try {const response=await fetch('/api/diagnose',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({answers:snapshot})});const result=await response.json();if(!response.ok)throw new Error(result.error||'The consultation could not be completed.');if(JSON.stringify(snapshot)===JSON.stringify(answers))renderResult(result);}
  catch(error){showError(`Could not analyse the answers. Check that the Python server is running. ${error.message}`);}
  finally{$('analyse').disabled=false;}
}
function reset() {answers=Object.fromEntries(config.questions.map(q=>[q.key,'unknown']));groupIndex=0;clearResults();$('error').hidden=true;renderQuestions();}
function renderKnowledge() {
  $('rules').innerHTML=config.rules.map(r=>`<details class="rule-row"><summary><span>${r.id}</span>${esc(r.title)}</summary><p><strong>IF</strong> ${esc(r.condition_text)}</p><p><strong>THEN</strong> ${esc(r.advice)}</p><p>${sourceLinks(r.sources)}<br>Section: ${esc(r.source_section)}</p></details>`).join('');
  $('sources').innerHTML=Object.entries(config.sources).map(([id,s])=>`<div class="source-item"><a href="${esc(s.url)}" target="_blank" rel="noopener">${id} · ${esc(s.title)}</a><small>${esc(s.publisher)} · Accessed ${s.accessed}</small></div>`).join('');
}
document.querySelectorAll('[data-view]').forEach(button=>button.addEventListener('click',()=>{if(!config)return;document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b===button));$('consult').hidden=button.dataset.view!=='consult';$('knowledge').hidden=button.dataset.view!=='knowledge';}));
$('steps').addEventListener('click',e=>{const b=e.target.closest('[data-step]');if(b){groupIndex=Number(b.dataset.step);renderQuestions();}});
$('questions').addEventListener('submit',e=>e.preventDefault());
$('questions').addEventListener('change',e=>{if(!e.target.matches('select'))return;answers[e.target.name]=e.target.value;clearResults();const n=Object.values(answers).filter(v=>v!=='unknown').length;$('progress-text').textContent=`${n} of ${config.questions.length} answered`;$('progress').value=n;});
$('previous').addEventListener('click',()=>{groupIndex=Math.max(0,groupIndex-1);renderQuestions();});
$('next').addEventListener('click',()=>{groupIndex=Math.min(config.groups.length-1,groupIndex+1);renderQuestions();});
$('analyse').addEventListener('click',analyse);$('reset').addEventListener('click',reset);
$('download').addEventListener('click',()=>{if(!lastResult)return;const payload={system:'PlantCare Expert',created_at:new Date().toISOString(),answers,result:lastResult};const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='plantcare_consultation.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
(async()=>{try{const response=await fetch('/api/config');if(!response.ok)throw new Error('Configuration unavailable');config=await response.json();reset();renderKnowledge();$('loading').hidden=true;$('consult').hidden=false;}catch(error){$('loading').hidden=true;showError(`Could not load PlantCare Expert. ${error.message}`);}})();
