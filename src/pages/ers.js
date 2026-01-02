import { el, clamp, downloadText, nowISO } from '../lib/util.js'

const LS_KEY = 'yusen_demo_ers_v1'

function defaultState(){
  return {
    inputs: {
      cog: 70, phy: 55, sta: 60, foc: 65,
      uncertainty: 40, adversary: 20, time: 35, stakes: 50,
      sleep: 60, calm: 55, resilience: 60,
    },
    history: [],
  }
}

function load(){
  try{
    const raw = localStorage.getItem(LS_KEY)
    return raw ? JSON.parse(raw) : defaultState()
  }catch{
    return defaultState()
  }
}
function save(state){ localStorage.setItem(LS_KEY, JSON.stringify(state)) }

function scoreERS(x){
  // Core energy (0-100): normalize sum of 4 signals
  const core = clamp((x.cog + x.phy + x.sta + x.foc) / 4, 0, 100)

  // Risk (0-100): uncertainty + adversary + time + stakes (weights)
  const risk = clamp(0.35*x.uncertainty + 0.25*x.adversary + 0.20*x.time + 0.20*x.stakes, 0, 100)

  // Stability (0-100): sleep + calm + resilience + sta (weights)
  const stability = clamp(0.30*x.sleep + 0.25*x.calm + 0.20*x.resilience + 0.25*x.sta, 0, 100)

  // ERS index: energy * stability / (risk+1) re-scaled
  const ers = clamp((core * (0.6 + stability/250)) - (risk*0.55), 0, 100)

  // Recommendation
  let mode = 'Sentinel 哨兵模式'
  let action = '以監測與小步試探為主，先做資訊增益與風險下降。'
  if (ers >= 80 && risk <= 55){
    mode = 'Sniper 狙擊模式'
    action = '可鎖定單一關鍵目標，集中資源推進，避免分散。'
  } else if (ers >= 65 && risk <= 70){
    mode = '3MOR 模式'
    action = '可做結構化拆解與中等強度輸出，保持迭代節奏。'
  } else if (risk >= 80 || stability <= 35){
    mode = 'Freezing 極凍模式'
    action = '暫停重大決策，只保留維持與安全行為；先回復穩定度。'
  } else if (ers <= 35){
    mode = 'Recovery / Hole'
    action = '低負載：恢復、整理、情緒排壓，避免做不可逆決策。'
  }

  // Risk gate (traffic light)
  const gate = risk < 40 ? 'GREEN' : risk < 65 ? 'YELLOW' : risk < 80 ? 'ORANGE' : 'RED'

  return { core, risk, stability, ers, mode, action, gate }
}

function paintBar(div, v){
  div.style.width = `${clamp(v,0,100)}%`
  if (v >= 75) div.style.background = 'var(--good)'
  else if (v >= 55) div.style.background = 'var(--warn)'
  else div.style.background = 'var(--bad)'
}

export function renderERS(mount){
  const state = load()

  const header = el('div', { class:'card' }, [
    el('div', { class:'row' }, [
      el('span', { class:'badge' }, 'AI-assisted Decision Risk & Stability System'),
      el('span', { class:'badge' }, 'ERS Calculator'),
    ]),
    el('div', { class:'small', style:'margin-top:8px' }, '輸入「能量/穩定/注意」與「風險四因子」後，輸出 ERS 指數、風險閘門與推薦模式。互動形式參考你提供的宇森 OS 儀表板與 EU 計算器的「卡片 + 即時摘要」結構。'),
  ])

  const kpi = el('div', { class:'kpi' }, [
    el('div', { class:'box' }, [ el('div',{class:'name'},'ERS Index'), el('div',{class:'val', id:'ersVal'},'—'), el('div',{class:'hint', id:'ersHint'},'') ]),
    el('div', { class:'box' }, [ el('div',{class:'name'},'Risk Gate'), el('div',{class:'val', id:'gateVal'},'—'), el('div',{class:'hint', id:'gateHint'},'') ]),
    el('div', { class:'box' }, [ el('div',{class:'name'},'Recommended Mode'), el('div',{class:'val', id:'modeVal', style:'font-size:18px;margin-top:8px'},'—'), el('div',{class:'hint', id:'modeHint'},'') ]),
  ])

  const controls = el('div', { class:'card' }, [
    el('details', { open:'' }, [
      el('summary', {}, 'Inputs'),
      el('div',{class:'hr'}),
      el('div', { class:'grid' }, [
        slider('ERS 腦力 (Cog)', 'cog'),
        slider('ERS 體力 (Phy)', 'phy'),
        slider('ERS 穩定度 (Stability)', 'sta'),
        slider('ERS 注意力 (Focus)', 'foc'),

        slider('不確定性 (Uncertainty)', 'uncertainty'),
        slider('對手/干擾 (Adversary)', 'adversary'),
        slider('時間壓力 (Time)', 'time'),
        slider('代價/賭注 (Stakes)', 'stakes'),

        slider('睡眠恢復 (Sleep)', 'sleep'),
        slider('平靜度 (Calm)', 'calm'),
        slider('韌性/復原 (Resilience)', 'resilience'),
      ]),
      el('div',{class:'row', style:'margin-top:12px'},[
        el('button',{class:'btn primary', onclick:()=>calcAndRender(true)},'Calculate'),
        el('button',{class:'btn', onclick:()=>applyPreset('high')},'Preset: High-Output'),
        el('button',{class:'btn', onclick:()=>applyPreset('balanced')},'Preset: Balanced'),
        el('button',{class:'btn', onclick:()=>applyPreset('freezing')},'Preset: High-Risk'),
        el('button',{class:'btn danger', onclick:resetAll},'Reset'),
        el('button',{class:'btn info', onclick:exportJSON},'Export JSON'),
      ]),
      el('div',{class:'small', style:'margin-top:10px'},'說明：ERS Index 用「核心能量×穩定度 - 風險懲罰」的可視化代理，便於 demo；你可以再替換成你正式的 ERS 方程/權重。'),
    ])
  ])

  const gauges = el('div', { class:'card' }, [
    el('details', { open:'' }, [
      el('summary', {}, 'Signal Gauges'),
      el('div',{class:'hr'}),
      gauge('Core Energy', 'coreBar', 'coreNum'),
      gauge('Stability', 'stbBar', 'stbNum'),
      gauge('Risk', 'riskBar', 'riskNum'),
      el('div',{class:'small', style:'margin-top:10px'}, 'Risk gate 參考宇森 OS 儀表板的 Def9R 類似概念：綠/黃/橘/紅用於快速限制決策。'),
    ])
  ])

  const history = el('div', { class:'card' }, [
    el('details', {}, [
      el('summary', {}, 'Session History'),
      el('div',{class:'small', style:'margin-top:8px'},'每次 Calculate 會寫入一筆（留在本機 localStorage）。'),
      el('div',{class:'hr'}),
      el('div', { id:'histWrap' }, ''),
    ])
  ])

  const consoleCard = el('div', { class:'card' }, [
    el('details', { open:'' }, [
      el('summary', {}, 'Console (Command Simulation)'),
      el('div',{class:'hr'}),
      el('div', { class:'row' }, [
        el('input', { id:'cmd', placeholder:'Try: def9 scan / sniper / sentinel / freezing / 3mor / recovery', style:'flex:1;min-width:260px' }),
        el('button', { class:'btn', onclick:runCmd }, 'Run'),
      ]),
      el('pre', { class:'console', id:'cmdOut', style:'margin-top:10px' }, '—'),
    ])
  ])

  mount.appendChild(header)
  mount.appendChild(kpi)
  mount.appendChild(controls)
  mount.appendChild(gauges)
  mount.appendChild(consoleCard)
  mount.appendChild(history)

  // initial render
  bindInputs()
  calcAndRender(false)

  function bindInputs(){
    Object.keys(state.inputs).forEach(k=>{
      const elx = document.getElementById(`in_${k}`)
      const out = document.getElementById(`v_${k}`)
      if (!elx) return
      elx.value = state.inputs[k]
      out.textContent = String(state.inputs[k])
      elx.addEventListener('input', ()=>{
        state.inputs[k] = Number(elx.value)
        out.textContent = String(elx.value)
        save(state)
        calcAndRender(false)
      })
    })
  }

  function applyPreset(name){
    const p = {
      high: { cog:85, phy:70, sta:75, foc:80, uncertainty:35, adversary:25, time:45, stakes:55, sleep:70, calm:60, resilience:70 },
      balanced: { cog:70, phy:55, sta:60, foc:65, uncertainty:40, adversary:20, time:35, stakes:50, sleep:60, calm:55, resilience:60 },
      freezing: { cog:55, phy:45, sta:35, foc:50, uncertainty:75, adversary:70, time:80, stakes:85, sleep:40, calm:35, resilience:40 },
    }[name]
    Object.assign(state.inputs, p)
    save(state)
    bindInputs()
    calcAndRender(false)
  }

  function resetAll(){
    const d = defaultState()
    state.inputs = d.inputs
    state.history = []
    save(state)
    bindInputs()
    calcAndRender(false)
    renderHist()
  }

  function exportJSON(){
    const snap = { when: nowISO(), ...scoreERS(state.inputs), inputs: state.inputs, history: state.history.slice(-50) }
    downloadText(`ers_session_${Date.now()}.json`, JSON.stringify(snap, null, 2))
  }

  function calcAndRender(pushHistory){
    const r = scoreERS(state.inputs)

    document.getElementById('ersVal').textContent = String(Math.round(r.ers))
    document.getElementById('ersHint').textContent = `Core ${Math.round(r.core)} | Stability ${Math.round(r.stability)} | Risk ${Math.round(r.risk)}`
    document.getElementById('modeVal').textContent = r.mode
    document.getElementById('modeHint').textContent = r.action

    const gateVal = document.getElementById('gateVal')
    const gateHint = document.getElementById('gateHint')
    gateVal.textContent = r.gate
    gateHint.textContent =
      r.gate==='GREEN' ? '低風險：可正常行動。' :
      r.gate==='YELLOW' ? '中風險：提高警戒，保持可逆性。' :
      r.gate==='ORANGE' ? '高風險：小步試探，避免承諾。' :
      '極高風險：暫停重大行動。'

    gateVal.style.color =
      r.gate==='GREEN' ? 'var(--good)' :
      r.gate==='YELLOW' ? 'var(--warn)' :
      r.gate==='ORANGE' ? '#FF9800' :
      'var(--bad)'

    paintBar(document.getElementById('coreBar'), r.core)
    paintBar(document.getElementById('stbBar'), r.stability)
    // risk bar: invert color semantics (risk higher => bad)
    const rb = document.getElementById('riskBar')
    rb.style.width = `${clamp(r.risk,0,100)}%`
    rb.style.background = r.risk < 40 ? 'var(--good)' : r.risk < 65 ? 'var(--warn)' : 'var(--bad)'
    document.getElementById('coreNum').textContent = String(Math.round(r.core))
    document.getElementById('stbNum').textContent = String(Math.round(r.stability))
    document.getElementById('riskNum').textContent = String(Math.round(r.risk))

    if (pushHistory){
      state.history.push({ when: nowISO(), ers: r.ers, risk: r.risk, stability: r.stability, mode: r.mode, gate: r.gate })
      state.history = state.history.slice(-30)
      save(state)
      renderHist()
    } else {
      renderHist()
    }
  }

  function renderHist(){
    const wrap = document.getElementById('histWrap')
    if (!wrap) return
    if (!state.history.length){
      wrap.innerHTML = '<div class="small">No history yet.</div>'
      return
    }
    const rows = state.history.slice().reverse().map(h=>(
      `<tr>
        <td>${h.when.replace('T',' ').slice(0,19)}</td>
        <td>${Math.round(h.ers)}</td>
        <td>${Math.round(h.risk)}</td>
        <td>${Math.round(h.stability)}</td>
        <td>${h.gate}</td>
        <td>${h.mode}</td>
      </tr>`
    )).join('')
    wrap.innerHTML = `
      <table style="width:100%;border-collapse:collapse">
        <thead>
          <tr style="background:#111">
            <th style="border:1px solid #222;padding:8px;font-size:12px;text-align:left">Time</th>
            <th style="border:1px solid #222;padding:8px;font-size:12px;text-align:left">ERS</th>
            <th style="border:1px solid #222;padding:8px;font-size:12px;text-align:left">Risk</th>
            <th style="border:1px solid #222;padding:8px;font-size:12px;text-align:left">Stability</th>
            <th style="border:1px solid #222;padding:8px;font-size:12px;text-align:left">Gate</th>
            <th style="border:1px solid #222;padding:8px;font-size:12px;text-align:left">Mode</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    `
  }

  function runCmd(){
    const raw = document.getElementById('cmd').value.trim()
    const s = raw.toLowerCase()
    let out = 'Unknown command.'
    if (!raw) out = '尚未輸入任何指令。'
    else if (s.includes('def9')) out = 'Def9 Scan: 風險閘門掃描 → 若 gate=ORANGE/RED，建議暫緩行動並降低不可逆承諾。'
    else if (s.includes('sniper')) out = 'Sniper: 鎖定單一關鍵目標，集中資源；避免 context switching。'
    else if (s.includes('sentinel')) out = 'Sentinel: 降低輸出、提高監測；補充情報與風險感知。'
    else if (s.includes('freezing')) out = 'Freezing: 暫停重大決策，只做維持與安全行為。'
    else if (s.includes('3mor')) out = '3MOR: Macro/Meso/Maintenance/Operational/Recovery 分層安排，控制負載。'
    else if (s.includes('recovery') || s.includes('hole')) out = 'Recovery/Hole: 排壓與恢復，不做不可逆決策。'
    document.getElementById('cmdOut').textContent = out
  }

  function slider(title, key){
    return el('div', {}, [
      el('label', {}, title),
      el('input', { id:`in_${key}`, type:'range', min:'0', max:'100', step:'1' }),
      el('div', { class:'row' }, [
        el('span',{class:'small'},'Value:'),
        el('span',{class:'badge', id:`v_${key}`},'0'),
      ])
    ])
  }

  function gauge(name, barId, numId){
    return el('div', { style:'margin-top:10px' }, [
      el('div',{class:'row', style:'justify-content:space-between'},[
        el('div',{class:'small'},name),
        el('div',{class:'badge', id:numId},'0')
      ]),
      el('div',{class:'progress'},[ el('div',{id:barId},'') ])
    ])
  }
}
