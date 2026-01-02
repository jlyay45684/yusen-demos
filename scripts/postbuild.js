import fs from 'node:fs'
import path from 'node:path'

const dist = path.resolve('dist')
const src = path.join(dist, 'index.html')
const dst = path.join(dist, '404.html')

// SPA / hash-route 仍建議加 404.html，以避免部分情境 refresh 404
if (fs.existsSync(src)) {
  fs.copyFileSync(src, dst)
  console.log('postbuild: dist/404.html generated')
}
