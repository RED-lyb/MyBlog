import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const srcRoot = path.join(path.dirname(fileURLToPath(import.meta.url)), '../src')
const linePattern = /^\s*console\.(log|warn|error|debug|info)\(.*\);?\s*$/

function walk(dir, files = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) walk(full, files)
    else if (/\.(js|vue|ts)$/.test(entry.name)) files.push(full)
  }
  return files
}

let total = 0
let removed = 0
for (const file of walk(srcRoot)) {
  const lines = fs.readFileSync(file, 'utf8').split('\n')
  const next = lines.filter((line) => {
    if (linePattern.test(line)) {
      removed += 1
      return false
    }
    return true
  })
  if (next.length !== lines.length) {
    fs.writeFileSync(file, next.join('\n'))
    total += 1
  }
}

console.log(`removed ${removed} console lines from ${total} files`)
