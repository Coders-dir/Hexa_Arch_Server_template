// Prebuilt minimal admin UI (vanilla JS) — behaves like the earlier prototype
(function(){
  const root = document.getElementById('root')
  root.innerHTML = `
    <div style="padding:20px;font-family:Inter,Arial">
      <h1>Hexa Admin (Prebuilt)</h1>
      <div>
        <input id="token" placeholder="Paste admin token" style="width:60%" />
        <button id="btn-list">List</button>
        <button id="btn-create">Create</button>
      </div>
      <div id="keys" style="margin-top:12px"></div>
    </div>
  `

  const tokenInput = document.getElementById('token')
  const keysDiv = document.getElementById('keys')
  tokenInput.value = localStorage.getItem('admin_token') || ''
  tokenInput.addEventListener('change', ()=> localStorage.setItem('admin_token', tokenInput.value))

  async function api(path, opts={}){
    const t = localStorage.getItem('admin_token')
    opts.headers = opts.headers || {}
    if(t) opts.headers['Authorization'] = 'Bearer '+t
    const res = await fetch(path, opts)
    return res
  }

  async function list(){
    const r = await api('/api/admin/api-keys')
    if(r.status===200){
      const arr = await r.json()
      keysDiv.innerHTML = ''
      arr.forEach(k=>{
        const d = document.createElement('div')
        d.style.borderBottom='1px solid #eee'
        d.style.padding='8px'
        d.innerHTML = `<strong>${k.kid}</strong> ${k.name||''} ${k.revoked_at?'<em>revoked</em>':'<button data-kid="'+k.kid+'">Revoke</button>'}`
        keysDiv.appendChild(d)
      })
      keysDiv.querySelectorAll('button[data-kid]').forEach(b=> b.addEventListener('click', async (e)=>{ const kid=e.target.dataset.kid; await api('/api/admin/api-keys/'+kid+'/revoke',{method:'POST'}); list() }))
    } else {
      keysDiv.textContent = 'Error: '+r.status
    }
  }

  document.getElementById('btn-list').addEventListener('click', list)
  document.getElementById('btn-create').addEventListener('click', async ()=>{ const name=prompt('label')||''; const r=await api('/api/admin/api-keys',{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name})}); if(r.status===200) list(); else alert('err '+r.status) })

  // initial
  list()
})()
