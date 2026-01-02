import { el, clamp, downloadText, nowISO } from '../lib/util.js'

const LS_KEY = 'yusen_demo_cooking_v1'

function defaultState(){
  return {
    goal: 'Deploy 3 interactive demos to GitHub Pages',
    constraints: 'Timebox: today; prefer Vite + vanilla JS; keep UX consistent',
    eu: 65, // energy budget
    steps: [],
    log: [],
  }
}
function load(){
  try{ const raw = localStorage.getItem(LS_KEY); return raw ? JSON.parse(raw) : defaultState() }
  catch{ return defaultState() }
}
function save(s){ localStorage.setItem(LS_KEY, JSON.stringify(s)) }

function proposeSteps(goal, constraints){
  // Minimal "Cooking Mode" skeleton, inspired by your dashboard's runCookingFlow text flow
  // (抽象化→骨架→路徑→EU對齊→可執行方案) fileciteturn1file0
  const g = goal.trim() || 'Untitled Goal'
  const c = constraints.trim()
  return [
    { id: cryptoId(), stage:'Abstract', name:'問題抽象化', detail:`將目標抽象成可驗證的輸出：${g}` },
    { id: cryptoId(), stage:'Structure', name:'建立架構骨架', detail:`拆成 3-5 個模組；釐清 I/O、依賴與界面。${c?`Constraints: ${c}`:''}` },
    { id: cryptoId(), stage:'Path', name:'生成候選路徑', detail:'提供 A/B/C 三條路徑（快/穩/擴展），各自標註風險與回滾點。' },
    { id: cryptoId(), stage:'EU', name:'EU 負載對齊', detail:'用 EU（能量/注意）限制步驟粒度：高 EU 可做不可逆輸出；低 EU 只做整理與可逆行為。' },
    { id: cryptoId(), stage:'Exec', name:'產生可執行方案', detail:'輸出：今日行動清單 + Done 定義 + 最小驗證 demo。' },
  ]
}

function recommendByEU(eu){
  if (eu >= 80) return { depth:'High', note:'可跑 Cooking 3.0：多變量拆解與路徑推演；適合推進到可公開版本。' }
  if (eu >= 60) return { depth:'Mid', note:'可跑 Cooking 2.0：確認意圖→骨架→步驟→檢查負載；適合完成 MVP。' }
  if (eu >= 40) return { depth:'Low', note:'只做骨架與可逆行為：整理、文件化、拆 tasks，不做高風險承諾。' }
  return { depth:'Recovery', note:'暫停重大決策：恢復、降負載、只做維持。' }
}

function cryptoId(){
  return Math.random().toString(16).slice(2,10)
}

export function renderCooking(mount){
  const state = load()

  const intro = el('div',{class:'card'},[
    el('div',{class:'row'},[
      el('span',{class:'badge'},'Multi-step AI Workflow Orchestration Framework'),
      el('span',{class:'badge'},'Cooking Mode'),
    ]),
    el('div',{class:'small', style:'margin-top:8px'},'此 demo 用「可編輯 steps + EU 限制 + 一鍵執行（模擬）」展示多步工作流編排；流程段落命名與順序參考你提供的 Cooking 自動流描述。'),
  ])

  const kpi = el('div',{class:'kpi'},[
    kpiBox('EU Budget', 'euVal', 'euHint'),
    kpiBox('Recommended Depth', 'depthVal', 'depthHint'),
    kpiBox('Steps', 'stepsVal', 'stepsHint'),
  ])

  const inputs = el('div',{class:'card'},[
    el('details',{open:''},[
      el('summary',{},'Inputs'),
      el('div',{class:'hr'}),
      el('div',{class:'grid'},[
        el('div',{},[
          el('label',{},'Goal'),
          el('textarea',{id:'goal'}),
        ]),
        el('div',{},[
          el('label',{},'Constraints / Context'),
          el('textarea',{id:'constraints'}),
        ]),
      ]),
      el('div',{style:'margin-top:12px'},[
        el('label',{},'EU (0-100)'),
        el('input',{id:'eu', type:'range', min:'0', max:'100', step:'1'}),
        el('div',{class:'row'},[
          el('span',{class:'small'},'Value:'),
          el('span',{class:'badge', id:'euBadge'},'0'),
        ])
      ]),
      el('div',{class:'row', style:'margin-top:12px'},[
        el('button',{class:'btn primary', onclick:generate},'Generate Steps'),
        el('button',{class:'btn', onclick:run},'Run Simulation'),
        el('button',{class:'btn info', onclick:exportJSON},'Export JSON'),
        el('button',{class:'btn danger', onclick:resetAll},'Reset'),
      ]),
      el('div',{class:'small', style:'margin-top:10px'},'Generate Steps 會覆蓋現有 steps（可用 Export 先備份）。Run Simulation 會把 steps 依 EU 限制轉成「今日可執行清單」。'),
    ])
  ])

  const stepsCard = el('div',{class:'card'},[
    el('details',{open:''},[
      el('summary',{},'Workflow Steps (Editable)'),
      el('div',{class:'hr'}),
      el('div',{id:'steps'},''),
      el('div',{class:'row', style:'margin-top:10px'},[
        el('button',{class:'btn', onclick:addStep},'Add Step'),
      ])
    ])
  ])

  const logCard = el('div',{class:'card'},[
    el('details',{open:''},[
      el('summary',{},'Execution Log'),
      el('div',{class:'hr'}),
      el('pre',{class:'console', id:'log'},'—')
    ])
  ])

  mount.appendChild(intro)
  mount.appendChild(kpi)
  mount.appendChild(inputs)
  mount.appendChild(stepsCard)
  mount.appendChild(logCard)

  // bind initial
  const goalEl = document.getElementById('goal')
  const conEl = document.getElementById('constraints')
  const euEl = document.getElementById('eu')
  goalEl.value = state.goal
  conEl.value = state.constraints
  euEl.value = state.eu
  document.getElementById('euBadge').textContent = String(state.eu)

  goalEl.addEventListener('input', ()=>{ state.goal = goalEl.value; save(state); recalc() })
  conEl.addEventListener('input', ()=>{ state.constraints = conEl.value; save(state); recalc() })
  euEl.addEventListener('input', ()=>{
    state.eu = Number(euEl.value)
    document.getElementById('euBadge').textContent = String(state.eu)
    save(state)
    recalc()
  })

  if (!state.steps.length) state.steps = proposeSteps(state.goal, state.constraints)
  renderSteps()
  recalc()
  renderLog()

  function recalc(){
    const r = recommendByEU(state.eu)
    document.getElementById('euVal').textContent = String(state.eu)
    document.getElementById('euHint').textContent = '能量/注意預算（控制工作流深度）'
    document.getElementById('depthVal').textContent = r.depth
    document.getElementById('depthHint').textContent = r.note
    document.getElementById('stepsVal').textContent = String(state.steps.length)
    document.getElementById('stepsHint').textContent = '可編輯 steps；Run 會產生今日清單'
  }

  function generate(){
    state.steps = proposeSteps(state.goal, state.constraints)
    state.log.unshift({ when: nowISO(), kind:'generate', msg:`Generated ${state.steps.length} steps.` })
    state.log = state.log.slice(-50)
    save(state)
    renderSteps()
    recalc()
    renderLog()
  }

  function addStep(){
    state.steps.push({ id: cryptoId_prof(), stage:'Custom', name:'New Step', detail:'' })
    save(state)
    renderSteps()
    recalc()
  }

  function delStep(id){
    state.steps = state.steps.filter(s=>s.id!==id)
    save(state)
    renderSteps()
    recalc()
  }

  function run(){
    const r = recommendByEU(state.eu)
    const doable = state.steps.map(s=>{
      // EU gating: reduce detail when low EU
      let detail = s.detail
      if (state.eu < 40 && s.stage !== 'Exec') detail = '低 EU：延後。本步驟只保留標題與最小筆記。'
      else if (state.eu < 60 && s.stage === 'Path') detail = '中低 EU：只保留 1 條路徑，避免展開過多候選。'
      else if (state.eu < 80 && s.stage === 'EU') detail = '中 EU：做一次 EU 對齊，明確今日負載上限與回滾點。'
      return { ...s, detail }
    })

    const today = buildTodayChecklist(doable, state.eu)

    state.log.unshift({ when: nowISO(), kind:'run', msg:`Run simulation @EU=${state.eu} (${r.depth})` })
    today.forEach(x=> state.log.unshift({ when: nowISO(), kind:'todo', msg:`[${x.stage}] ${x.item}` }))
    state.log = state.log.slice(-80)
    save(state)
    renderLog()
  }

  function buildTodayChecklist(steps, eu){
    const items = []
    if (eu >= 80){
      items.push({ stage:'Exec', item:'完成可公開 demo 版本（含 Export / Reset / Presets）' })
      items.push({ stage:'Ops', item:'Push → GitHub Actions → Pages，確認 /dist 載入正常' })
    } else if (eu >= 60){
      items.push({ stage:'Exec', item:'完成 MVP：至少 1 個完整互動 loop（input→compute→viz/log）' })
      items.push({ stage:'Ops', item:'部署流程跑通；再補文案與截圖' })
    } else if (eu >= 40){
      items.push({ stage:'Prep', item:'整理需求/介面/資料結構；留好可擴充的 state schema' })
      items.push({ stage:'Prep', item:'把 UI 骨架先上線（空殼也要能操作）' })
    } else {
      items.push({ stage:'Recovery', item:'只做低成本整理：README、TODO、把現有 HTML 備份與對照' })
    }
    // attach step names as trace
    steps.forEach(s=> items.push({ stage:s.stage, item:`Step ready: ${s.name}` }))
    return items.slice(0, 18)
  }

  function renderSteps(){
    const host = document.getElementById('steps')
    host.innerHTML = ''
    state.steps.forEach(s=>{
      host.appendChild(el('div',{class:'card', style:'background:#141414;border-color:#222'},[
        el('div',{class:'row', style:'justify-content:space-between'},[
          el('div',{},[
            el('span',{class:'badge'},s.stage),
            el('span',{style:'margin-left:8px;font-weight:800'},s.name),
          ]),
          el('button',{class:'btn danger', onclick:()=>delStep(s.id)},'Delete'),
        ]),
        el('div',{style:'margin-top:10px'},[
          el('label',{},'Name'),
          el('input',{value:s.name, oninput:(e)=>{ s.name=e.target.value; save(state); recalc() }}),
        ]),
        el('div',{style:'margin-top:10px'},[
          el('label',{},'Detail'),
          el('textarea',{oninput:(e)=>{ s.detail=e.target.value; save(state) }}, s.detail),
        ]),
      ]))
    })
  }

  function renderLog(){
    const lines = state.log.slice().reverse().map(x=>{
      const t = x.when.replace('T',' ').slice(0,19)
      return `${t}  [${x.kind}]  ${x.msg}`
    })
    document.getElementById('log').textContent = lines.length ? lines.join('\n') : '—'
  }

  function exportJSON(){
    const snap = { when: nowISO(), recommend: recommendByEU(state.eu), state }
    downloadText(`cooking_session_${Date.now()}.json`, JSON.stringify(snap, null, 2))
  }

  function resetAll(){
    const d = defaultState()
    Object.assign(state, d)
    state.steps = proposeSteps(state.goal, state.constraints)
    save(state)
    // rebind UI (simplest: reload route)
    location.reload()
  }

  function kpiBox(name, idVal, idHint){
    return el('div',{class:'box'},[
      el('div',{class:'name'},name),
      el('div',{class:'val', id:idVal},'—'),
      el('div',{class:'hint', id:idHint},''),
    ])
  }

  function cryptoId_prof(){ return Math.random().toString(16).slice(2,10) }
}
