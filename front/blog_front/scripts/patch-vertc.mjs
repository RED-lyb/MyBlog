import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const file = path.join(path.dirname(fileURLToPath(import.meta.url)), '../public/vendor/vertc-4.66.min.js')
let content = fs.readFileSync(file, 'utf8')

const targets = [
  'console.log("[LoggerReportor.constructor] console upload switch ON")',
  'console.log("[LoggerReportor.constructor] console upload switch OFF")',
]

for (const target of targets) {
  const count = content.split(target).length - 1
  content = content.split(target).join('void 0')
  console.log(`removed ${count}x: ${target}`)
}

fs.writeFileSync(file, content)
