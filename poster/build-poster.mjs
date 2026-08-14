// Renders a poster HTML file to a print-ready A4 PDF (plus a PNG proof).
//
//   npm i puppeteer-core
//   npx @puppeteer/browsers install chrome-headless-shell@stable
//   CHROME=<path to chrome-headless-shell> node poster/build-poster.mjs
//
// Which poster gets built (default: the full AI rover poster):
//   POSTER_FILE=basic-bot-poster.html POSTER_OUT=AgriRover_BasicBot_Poster \
//     CHROME=<path> node poster/build-poster.mjs
//
import puppeteer from "puppeteer-core"
import path from "node:path"
import { fileURLToPath } from "node:url"

const dir = process.env.POSTER_DIR || path.dirname(fileURLToPath(import.meta.url))
const file = process.env.POSTER_FILE || "poster.html"
const out = process.env.POSTER_OUT || "AgriRover_ITSP_Poster"
const src = "file://" + path.join(dir, file)

const browser = await puppeteer.launch({
  executablePath: process.env.CHROME,
  args: ["--no-sandbox", "--font-render-hinting=none"],
})
const page = await browser.newPage()
await page.setViewport({ width: 794, height: 1123, deviceScaleFactor: 2 })
await page.goto(src, { waitUntil: "networkidle0", timeout: 120000 })
await page.evaluate(() => document.fonts.ready)
await new Promise((r) => setTimeout(r, 600))

// Guard against silent page-2 spill: the poster must fit exactly one A4 sheet.
const fit = await page.evaluate(() => {
  const page = document.querySelector(".page")
  const body = document.querySelector(".body")
  return {
    pageH: page.getBoundingClientRect().height,
    contentH: page.scrollHeight,
    bodyOverflow: body.scrollHeight - body.clientHeight,
  }
})
console.log("[v0] fit check", file, fit)

await page.screenshot({ path: path.join(dir, out + "_proof.png"), fullPage: true })
await page.pdf({
  path: path.join(dir, out + ".pdf"),
  format: "A4",
  printBackground: true,
  margin: { top: "0", right: "0", bottom: "0", left: "0" },
})

await browser.close()
console.log("[v0] poster built ->", out + ".pdf")
