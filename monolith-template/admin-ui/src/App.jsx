import React, {useState, useEffect} from 'react'

export default function App(){
  const [token, setToken] = useState(localStorage.getItem('admin_token')||'')
  const [keys, setKeys] = useState([])
  const headers = token? {Authorization: `Bearer ${token}`} : {}

  useEffect(()=>{ if(token) localStorage.setItem('admin_token', token) }, [token])

  async function list(){
    const res = await fetch('/api/admin/api-keys', {headers})
    if(res.ok) setKeys(await res.json())
  }

  async function create(){
    const name = prompt('Key label')
    const res = await fetch('/api/admin/api-keys', {method:'POST', headers:{'Content-Type':'application/json', ...headers}, body: JSON.stringify({name, owner:'ops'})})
    if(res.ok) list()
  }

  async function revoke(kid){
    const res = await fetch(`/api/admin/api-keys/${kid}/revoke`, {method:'POST', headers})
    if(res.ok) list()
  }

  return (
    <div style={{padding:20,fontFamily:'Inter,Arial'}}>
      <h1>Hexa Admin (React prototype)</h1>
      <div>
        <input value={token} onChange={e=>setToken(e.target.value)} style={{width:'60%'}} placeholder='Paste admin token' />
        <button onClick={list}>List</button>
        <button onClick={create}>Create</button>
      </div>
      <div style={{marginTop:12}}>
        {keys.map(k=> (
          <div key={k.kid} style={{borderBottom:'1px solid #eee',padding:8}}>
            <strong>{k.kid}</strong> {k.name} {k.revoked_at? <em>revoked</em>: <button onClick={()=>revoke(k.kid)}>Revoke</button>}
          </div>
        ))}
      </div>
    </div>
  )
}
