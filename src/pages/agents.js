import { el, clamp, downloadText, nowISO } from '../lib/util.js'

const LS_KEY = 'yusen_demo_agents_v1'
const AGENTS = [
  { id:'planner', name:'Planner', role:'Goal decomposition / constraints' },
  { id:'builder', name:'Builder', role:'Implementation plan / tooling' },
  { id:'critic', name:'Critic', role:'Failure modes / risk' },
  { id:'researcher', name:'Researcher', role:'Assumptions / evidence' },
  { id:'operator', name:'Operator', role:'Execution / rollback' },
]

function defaultState(){
  const a = {}
  AGENTS.forEach(x=>{
    a[x.id] = { alignment: 70, confidence: 65, latency: 40, cost: 35 }
  })
  return { agents: a, rounds: [] }
}
function load(){
  try{ const raw = localStorage.getItem(LS_KEY); return raw ? JSON.parse(raw) : defaultState() }
  catch{ return defaultState() }
}
function save(s){ localStorage.setItem(LS_KEY, JSON.stringify(s)) }

function compute(state){
  const rows = AGENTS.map(a=>{
    const x = state.agents[a.id]
    // local score: alignment & confidence positive; latency/cost negative
    const score = clamp(0.45*x.alignment + 0.45*x.confidence - 0.05*x.latency - 0.05*x.cost, 0, 100)
    return { ...a, ...x, score }
  })
  const consensus = clamp(rows.reduce((m,r)=>m+r.score,0)/rows.length, 0, 100)
  const dispersion = Math.sqrt(rows.reduce((m,r)=>m+Math.pow(r.score-consensus,2),0)/rows.length)
  // conflict proxy: high confidence but low alignment
  const conflicts = rows
    .map(r=>({ id:r.id, name:r.name, v: clamp((r.confidence - r.alignment + 100)/2, 0, 100) }))
    .sort((a,b)=>b.v-a.v)
  return { rows, consensus, dispersion, conflicts }
}

function draw(canvas, rows){
  const ctx = canvas.getContext('2d')
  const w = canvas.width = canvas.clientWidth * devicePixelRatio
  const h = canvas.height = 220 * devicePixelRatio
  ctx.clearRect(0,0,w,h)

  const pad = 18 * devicePixelRatio
  const barH = 20 * devicePixelRatio
  const gap = 12 * devicePixelRatio
  const maxW = w - pad*2 - 90*devicePixelRatio

  ctx.font = `${12*devicePixelRatio}px system-ui`
  ctx.fillStyle = '#e6e6e6'

  rows.forEach((r,i)=>{
    const y = pad + i*(barH+gap)
    // label
    ctx.fillStyle = '#a3a3a3'
    ctx.fillText(r.name, pad, y + barH*0.75)
    // bar bg
    ctx.fillStyle = '#222'
    ctx.fillRect(pad + 80*devicePixelRatio, y, maxW, barH)
    // bar fill (no custom colors in instructions only apply to matplotlib, canvas ok; still keep minimal)
    const bw = maxW * (r.score/100)
    ctx.fillStyle = r.score>=75 ? '#4CAF50' : r.score>=55 ? '#FFC107' : '#F44336'
    ctx.fillRect(pad + 80*devicePixelRatio, y, bw, barH)
    // value
    ctx.fillStyle = '#e6e6e6'
    ctx.fillText(String(Math.round(r.score)), pad + 80*devicePixelRatio + maxW + 8*devicePixelRatio, y + barH*0.75)
  })
}

export function renderAgents(mount){
  const state = load()

  const intro = el('div',{class:'card'},[
    el('div',{class:'row'},[
      el('span',{class:'badge'},'Multi-agent Collaboration Calibration System'),
      el('span',{class:'badge'},'5 Agents'),
    ]),
    el('div',{class:'small', style:'margin-top:8px'},'此 demo 模擬「協作校準」：每個 agent 有 alignment/confidence/latency/cost 四維度，系統輸出 consensus、dispersion、conflict 指標；並提供 round-based 協商（belief update）來展示互動。')
  ])

  const kpi = el('div',{class:'kpi'},[
    kpiBox('Consensus', 'consensusVal', 'consensusHint'),
    kpiBox('Dispersion', 'dispVal', 'dispHint'),
    kpiBox('Top Conflict', 'confVal', 'confHint'),
  ])

  const controls = el('div',{class:'card'},[
    el('details',{open:''},[
      el('summary',{},'Agent Controls'),
      el('div',{class:'hr'}),
      el('div',{id:'agentGrid'},''),
      el('div',{class:'row', style:'margin-top:12px'},[
        el('button',{class:'btn primary', onclick:()=>runRound('negotiate')},'Run Round: Negotiate'),
        el('button',{class:'btn', onclick:()=>runRound('stress')},'Run Round: Stress Test'),
        el('button',{class:'btn info', onclick:exportJSON},'Export JSON'),
        el('button',{class:'btn danger', onclick:resetAll},'Reset'),
      ]),
      el('div',{class:'small', style:'margin-top:10px'},'Round 規則（可替換）：Negotiate 會把低 alignment 的 agent 往 consensus 拉；Stress Test 會提高 cost/latency 並降低 confidence。'),
    ])
  ])

  const viz = el('div',{class:'card'},[
    el('details',{open:''},[
      el('summary',{},'Consensus Visualization'),
      el('div',{class:'hr'}),
      el('canvas',{id:'cv', style:'height:220px'}),
      el('div',{class:'small', style:'margin-top:10px'},'每條 bar 是該 agent 的 calibration score（alignment/confidence 正向，latency/cost 負向）。')
    ])
  ])

  const rounds = el('div',{class:'card'},[
    el('details',{},[
      el('summary',{},'Round Log'),
      el('div',{class:'small', style:'margin-top:8px'},'保留最近 20 回合（localStorage）。'),
      el('div',{class:'hr'}),
      el('pre',{class:'console', id:'roundLog'},'—')
    ])
  ])

  mount.appendChild(intro)
  mount.appendChild(kpi)
  mount.appendChild(controls)
  mount.appendChild(viz)
  mount.appendChild(rounds)

  renderAgentGrid()
  recalc()

  function renderAgentGrid(){
    const grid = el('div',{class:'grid'},[])
    AGENTS.forEach(a=>{
      grid.appendChild(el('div',{},[
        el('div',{class:'small', style:'font-weight:800;color:#e6e6e6'},`${a.name} — ${a.role}`),
        el('div',{class:'hr'}),
        slider(a.id,'alignment','Alignment'),
        slider(a.id,'confidence','Confidence'),
        slider(a.id,'latency','Latency'),
        slider(a.id,'cost','Cost'),
      ]))
    })
    const host = document.getElementById('agentGrid')
    host.innerHTML = ''
    host.appendChild(grid)

    // bind
    AGENTS.forEach(a=>{
      ;['alignment','confidence','latency','cost'].forEach(k=>{
        const input = document.getElementById(`a_${a.id}_${k}`)
        const out = document.getElementById(`v_${a.id}_${k}`)
        input.value = state.agents[a.id][k]
        out.textContent = String(state.agents[a.id][k])
        input.addEventListener('input', ()=>{
          state.agents[a.id][k] = Number(input.value)
          out.textContent = String(input.value)
          save(state)
          recalc()
        })
      })
    })
  }

  function recalc(){
    const r = compute(state)
    document.getElementById('consensusVal').textContent = String(Math.round(r.consensus))
    document.getElementById('consensusHint').textContent = '共同可用決策空間的近似量化'
    document.getElementById('dispVal').textContent = String(Math.round(r.dispersion))
    document.getElementById('dispHint').textContent = '分歧越大，越需要校準/裁決'
    document.getElementById('confVal').textContent = r.conflicts[0]?.name ?? '—'
    document.getElementById('confHint').textContent = `conflict=${Math.round(r.conflicts[0]?.v ?? 0)}（高信心+低對齊）`
    draw(document.getElementById('cv'), r.rows)
    renderLog()
  }

  function runRound(kind){
    const r = compute(state)
    const c = r.consensus

    AGENTS.forEach(a=>{
      const x = state.agents[a.id]
      if (kind === 'negotiate'){
        // align towards consensus: increase alignment for low-score agents; slight confidence damping when conflict high
        const local = clamp(0.45*x.alignment + 0.45*x.confidence - 0.05*x.latency - 0.05*x.cost, 0, 100)
        const delta = clamp((c - local) * 0.08, -6, 6)
        x.alignment = clamp(x.alignment + delta, 0, 100)
        // conflict reduction: if confidence much higher than alignment, reduce confidence slightly
        if (x.confidence - x.alignment > 20) x.confidence = clamp(x.confidence - 2, 0, 100)
      } else {
        // stress: cost/latency up; confidence down; alignment slightly down
        x.cost = clamp(x.cost + 6, 0, 100)
        x.latency = clamp(x.latency + 6, 0, 100)
        x.confidence = clamp(x.confidence - 4, 0, 100)
        x.alignment = clamp(x.alignment - 2, 0, 100)
      }
    })

    const after = compute(state)
    state.rounds.push({
      when: nowISO(),
      kind,
      before: { consensus: r.consensus, dispersion: r.dispersion },
      after: { consensus: after.consensus, dispersion: after.dispersion },
    })
    state.rounds = state.rounds.slice(-20)
    save(state)
    renderAgentGrid()
    recalc()
  }

  function renderLog(){
    const lines = state.rounds.slice().reverse().map(x=>{
      const t = x.when.replace('T',' ').slice(0,19)
      return `${t}  [${x.kind}]  consensus ${Math.round(x.before.consensus)}→${Math.round(x.after.consensus)}  |  dispersion ${Math.round(x.before.dispersion)}→${Math.round(x.after.dispersion)}`
    })
    document.getElementById('roundLog').textContent = lines.length ? lines.join('\n') : '—'
  }

  function exportJSON(){
    const snap = { when: nowISO(), ...compute(state), state }
    downloadText(`agents_session_${Date.now()}.json`, JSON.stringify(snap, null, 2))
  }

  function resetAll(){
    const d = defaultState()
    state.agents = d.agents
    state.rounds = []
    save(state)
    renderAgentGrid()
    recalc()
  }

  function slider(agentId, key, labelName){
    return el('div',{style:'margin-top:10px'},[
      el('label',{},labelName),
      el('input',{id:`a_${agentId}_${key}`, type:'range', min:'0', max:'100', step:'1'}),
      el('div',{class:'row'},[
        el('span',{class:'small'},'Value:'),
        el('span',{class:'badge', id:`v_${agentId}_${key}`},'0'),
      ])
    ])
  }

  function kpiBox(name, idVal, idHint){
    return el('div',{class:'box'},[
      el('div',{class:'name'},name),
      el('div',{class:'val', id:idVal},'—'),
      el('div',{class:'hint', id:idHint},''),
    ])
  }
}
