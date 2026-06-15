import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const srcRoot = path.join(path.dirname(fileURLToPath(import.meta.url)), '../src')
const methods = ['log', 'warn', 'debug', 'info']

function walk(dir, files = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) walk(full, files)
    else if (/\.(js|vue|ts)$/.test(entry.name)) files.push(full)
  }
  return files
}

const patterns = methods.map((method) => ({
  method,
  // 单行 console.xxx(...)
  line: new RegExp(`^\\s*console\\.${method}\\([^;\\n]*\\);?\\s*$`, 'gm'),
  // 链式 .catch((e) => console.xxx(...))
  catchInline: new RegExp(`console\\.${method}\\([^)]*\\)`, 'g'),
}))

let total = 0
for (const file of walk(srcRoot)) {
  let content = fs.readFileSync(file, 'utf8')
  const original = content

  for (const { line, catchInline } of patterns) {
    content = content.replace(line, '')
    content = content.replace(catchInline, 'void 0')
  }

  if (content !== original) {
    fs.writeFileSync(file, content)
    total += 1
  }
}

console.log(`stripped console debug calls in ${total} files`)
