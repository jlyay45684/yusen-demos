import './styles.css'
import { renderERS } from './pages/ers.js'
import { renderAgents } from './pages/agents.js'
import { renderCooking } from './pages/cooking.js'
import { el } from './lib/util.js'

const routes = {
  '#/ers': { name: 'ERS 計算器', render: renderERS },
  '#/agents': { name: 'Multi-agent Calibration', render: renderAgents },
  '#/cooking': { name: 'Workflow Orchestration (Cooking)', render: renderCooking },
}

function getRoute(){
  const h = location.hash || '#/ers'
  return routes[h] ? h : '#/ers'
}

function renderLayout(){
  const root = document.getElementById('app')
  root.innerHTML = ''

  const header = el('header', {}, [
    el('div', { class: 'title' }, 'YUSEN Interactive Demos'),
    el('div', { class: 'sub' }, '三個可互動展示：ERS 風險×穩定度決策 / 5-Agent 協作校準 / Multi-step Cooking 工作流編排。使用 Hash Route，適合 GitHub Pages。'),
  ])

  const sidebar = el('aside', { class: 'sidebar' }, [
    el('div', { class: 'groupTitle' }, 'Demos'),
    el('nav', { class: 'nav', id: 'nav' }, []),
    el('div', { class: 'hr' }),
    el('div', { class: 'groupTitle' }, 'Ops'),
    el('div', {
      class: 'small',
      html: `
        <div>• Export 會下載 JSON（本機）。</div>
        <div>• 狀態會寫入 localStorage（可重整保留）。</div>
        <div>• 若要改成多頁（/ers.html 等），也可再分 entry。</div>
  `
})
  ])

  const main = el('main', { class: 'main', id: 'main' }, [])

  const container = el('div', { class: 'container' }, [sidebar, main])
  root.appendChild(header)
  root.appendChild(container)

  // nav links
  const nav = document.getElementById('nav')
  Object.entries(routes).forEach(([hash, r])=>{
    nav.appendChild(el('a', { href: hash, 'data-h': hash }, r.name))
  })
}

function renderRoute(){
  const hash = getRoute()
  const main = document.getElementById('main')
  main.innerHTML = ''
  routes[hash].render(main)

  document.querySelectorAll('.nav a').forEach(a=>{
    a.classList.toggle('active', a.getAttribute('data-h') === hash)
  })
}

window.addEventListener('hashchange', renderRoute)
renderLayout()
renderRoute()
