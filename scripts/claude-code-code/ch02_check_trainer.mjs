// Проверка тренажёра без браузера: берём <script> из index.html,
// подставляем простой объект document и нажимаем «Дальше» 5 раз.
import { readFileSync } from "node:fs";
const html = readFileSync(new URL("./ch02_lyrics_trainer/index.html", import.meta.url), "utf8");
const code = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const els = {};
const document = {
  getElementById(id) {
    return (els[id] ??= { textContent: "", handlers: {}, addEventListener(t, f) { this.handlers[t] = f; } });
  },
};
new Function("document", code)(document);
const print = () => console.log(`${els.counter.textContent} | ${els.line.textContent}`);
print();
for (let i = 0; i < 5; i++) { els.next.handlers.click(); print(); }
