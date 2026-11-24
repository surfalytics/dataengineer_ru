// Put many PNG diagrams on one image, with file names, so an agent looks at all of them with one Read.
//   node scripts/book-tools/contact_sheet.mjs <out.png> <a.png> [b.png ...]
// 3 columns, 500x300 per cell. At most 12 images per sheet: more files give <out>-2.png, <out>-3.png ...
import sharp from 'sharp'
import path from 'path'

const [out, ...files] = process.argv.slice(2)
if (!out || !files.length) { console.error('usage: contact_sheet.mjs <out.png> <a.png> [b.png ...]'); process.exit(1) }
const W = 500, H = 300, C = 3, PER = 12
const esc = s => s.replace(/[<>&]/g, c => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' }[c]))
const outs = []
for (let s = 0; s * PER < files.length; s++) {
  const chunk = files.slice(s * PER, (s + 1) * PER)
  const rows = Math.ceil(chunk.length / C)
  const comps = await Promise.all(chunk.map(async (f, i) => ({
    input: await sharp(f).resize(W, H - 24, { fit: 'contain', background: '#fff' })
      .extend({ top: 24, background: '#fff' })
      .composite([{ input: Buffer.from(`<svg width="${W}" height="24"><text x="4" y="17" font-size="15">${esc(path.basename(f))}</text></svg>`), top: 0, left: 0 }])
      .png().toBuffer(),
    left: (i % C) * W, top: Math.floor(i / C) * H,
  })))
  const name = s === 0 ? out : out.replace(/\.png$/, `-${s + 1}.png`)
  await sharp({ create: { width: C * W, height: rows * H, channels: 3, background: '#ddd' } }).composite(comps).png().toFile(name)
  outs.push(name)
}
console.log(outs.join('\n'))
