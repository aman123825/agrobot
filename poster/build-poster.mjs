// Renders poster.html to a print-ready A4 PDF (plus a PNG proof).
//
//   npm i puppeteer-core
//   npx @puppeteer/browsers install chrome-headless-shell@stable
//   CHROME=<path to chrome-headless-shell> node poster/build-poster.mjs
//
import puppeteer from "puppeteer-core"
import path from "node:path"
import { fileURLToPath } from "node:url"

const dir = process.env.POSTER_DIR || path.dirname(fileURLToPath(import.meta.url))
const src = "file://" + path.join(dir, "poster.html")

const browser = await puppeteer.launch({
  executablePath: process.env.CHROME,
  args: ["--no-sandbox", "--font-render-hinting=none"],
})
const page = await browser.newPage()
await page.setViewport({ width: 794, height: 1123, deviceScaleFactor: 2 })
await page.goto(src, { waitUntil: "networkidle0", timeout: 120000 })
await page.evaluate(() => document.fonts.ready)
await new Promise((r) => setTimeout(r, 600))

await page.screenshot({ path: path.join(dir, "proof.png"), fullPage: true })
await page.pdf({
  path: path.join(dir, "AgriRover_ITSP_Poster.pdf"),
  format: "A4",
  printBackground: true,
  margin: { top: "0", right: "0", bottom: "0", left: "0" },
})

await browser.close()
console.log("[v0] poster built")
