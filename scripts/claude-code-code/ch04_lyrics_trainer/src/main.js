// DOM glue: находит элементы, вешает обработчик, зовёт ядро. Своей логики нет.
import { createLineTrainer } from "./lineTrainer.js";
import { loadSavedIndex, saveIndex } from "./storage.js";
import { lines } from "./texts.js";

const trainer = createLineTrainer(lines, loadSavedIndex(localStorage, lines.length));

const lineEl = document.getElementById("line");
const counterEl = document.getElementById("counter");
const nextBtn = document.getElementById("next");

function render() {
  lineEl.textContent = trainer.currentLine();
  counterEl.textContent = `Строка ${trainer.currentIndex() + 1} из ${lines.length}`;
}

nextBtn.addEventListener("click", () => {
  trainer.next();
  saveIndex(localStorage, trainer.currentIndex());
  render();
});

render();
