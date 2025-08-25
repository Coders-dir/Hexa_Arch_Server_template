// Tiny vanilla JS admin UI prototype - no build step
const $ = sel => document.querySelector(sel)
const root = $('#result')
let token = localStorage.getItem('admin_token') || ''
$('#token').value = token
$('#btn-save-token').onclick = ()=>{ token = $('#token').value; localStorage.setItem('admin_token', token); alert('token saved') }

const api = {
  get: async (path)=>{
    const res = await fetch(path, {headers: token?{Authorization:`Bearer ${token}`}:undefined})
    return res
  }
}

function renderList(list){
  root.innerHTML = ''
  if(!Array.isArray(list)){
    root.textContent = JSON.stringify(list, null, 2)
    return
  }
  list.forEach(k=>{
    const d = document.createElement('div')
    d.className = 'key-row'
    d.innerHTML = `<input type=checkbox data-id='${k.id}'/><strong>${k.id}</strong> ${k.label||''} <small>created:${k.created_at||k.created}</small>`
    root.appendChild(d)
  })
}

$('#btn-list').onclick = async ()=>{
  const r = await api.get('/api/admin/api-keys')
  if(r.status===200){ const j=await r.json(); renderList(j) }
  else { root.textContent = 'Error: '+r.status }
}

$('#btn-create').onclick = async ()=>{
  const name = prompt('Key label (optional)')
  const res = await fetch('/api/admin/api-keys', {method:'POST', headers: {'Content-Type':'application/json', Authorization: token?`Bearer ${token}`:undefined}, body: JSON.stringify({label:name||''})})
  if(res.status===201){ alert('created'); $('#btn-list').click() } else { alert('err '+res.status) }
}

$('#btn-revoke').onclick = async ()=>{
  const checked = Array.from(document.querySelectorAll('.key-row input:checked')).map(i=>i.dataset.id)
  if(!checked.length){ alert('select keys to revoke'); return }
  for(const id of checked){
    const res = await fetch('/api/admin/api-keys/'+id, {method:'DELETE', headers: {Authorization: token?`Bearer ${token}`:undefined}})
    if(res.status!==204) { alert('failed revoke '+id) }
  }
  $('#btn-list').click()
}

// initial
$('#btn-list').click()
