export function clamp(n, min, max){ return Math.max(min, Math.min(max, n)) }
export function fmtPct(n){ return `${Math.round(n)}%` }
export function nowISO(){ return new Date().toISOString() }

export function downloadText(filename, text){
  const a = document.createElement('a')
  a.href = 'data:text/plain;charset=utf-8,' + encodeURIComponent(text)
  a.download = filename
  a.click()
}

export function el(tag, attrs={}, children=[]){
  const e = document.createElement(tag)
  Object.entries(attrs).forEach(([k,v])=>{
    if(k === 'class') e.className = v
    else if(k === 'html') e.innerHTML = v
    else if(k.startsWith('on') && typeof v === 'function') e.addEventListener(k.slice(2), v)
    else e.setAttribute(k, v)
  })
  ;(Array.isArray(children) ? children : [children]).forEach(c=>{
    if(c === null || c === undefined) return
    if(typeof c === 'string') e.appendChild(document.createTextNode(c))
    else e.appendChild(c)
  })
  return e
}
