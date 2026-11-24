#!/usr/bin/env python3
"""Chapter 10 (Machine Learning with MLlib) diagrams. Usage: ch10_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Own: Transformer, Estimator, Pipeline, PipelineModel
D["ch10-pipeline"] = dict(items=[
    T("Жёлтый — estimator (fit), зелёный — transformer (transform)", 0, -50, 20, "#495057"),
    N("tr", "trainDF\nобучающие данные", 0, 80, "db", 220, 100),
    Z("Pipeline — это estimator", 300, 0, 980, 220),
    N("si", "StringIndexer\nestimator", 340, 80, "y", 250, 100),
    N("va", "VectorAssembler\ntransformer", 650, 80, "g", 250, 100),
    N("lr", "LinearRegression\nestimator", 960, 80, "y", 280, 100),
    N("te", "testDF\nновые данные", 340, 330, "db", 250, 100),
    N("pm", "PipelineModel\nэто transformer", 960, 330, "pu", 280, 100),
    N("pr", "predDF\nколонка prediction", 960, 560, "db", 280, 100),
], edges=[E("tr", "si", "fit"), E("si", "va"), E("va", "lr"),
          E("lr", "pm", "fit() создаёт"), E("te", "pm", "transform()"),
          E("pm", "pr", "transform()")])

# Own: one-hot encoding in MLlib (StringIndexer -> OneHotEncoder -> VectorAssembler) + bad mapping
D["ch10-ohe"] = dict(items=[
    T("Три шага превращают строки в один вектор признаков", 0, -10, 20, "#495057"),
    N("s", "room_type\n«Private room»", 0, 60, "db", 200, 100),
    N("si", "StringIndexer", 270, 60, "y", 200, 100),
    N("ix", "индекс\n1.0", 540, 60, "n", 170, 100),
    N("oh", "OneHotEncoder", 780, 60, "y", 200, 100),
    N("bv", "бинарный вектор\n(0.0, 1.0)", 1050, 60, "n", 210, 100),
    N("vs", "VectorAssembler\n+ числовые колонки", 1330, 60, "g", 240, 100),
    T("Идея one-hot encoding на примере животных", 0, 260, 20, "#495057"),
    N("dog", "Dog", 0, 320, "p", 170, 70),
    N("cat", "Cat", 0, 420, "p", 170, 70),
    N("fish", "Fish", 0, 520, "p", 170, 70),
    N("dv", "(1, 0, 0)", 380, 320, "g", 200, 70),
    N("cv", "(0, 1, 0)", 380, 420, "g", 200, 70),
    N("fv", "(0, 0, 1)", 380, 520, "g", 200, 70),
    N("bad", "Плохо: Dog = 1, Cat = 2, Fish = 3\nМодель решит, что Cat вдвое\n«больше» Dog", 800, 390, "r", 440, 130),
], edges=[E("s", "si"), E("si", "ix"), E("ix", "oh"), E("oh", "bv"), E("bv", "vs"),
          E("dog", "dv"), E("cat", "cv"), E("fish", "fv")])

# Fig 10-9: decision tree
D["ch10-tree"] = dict(items=[
    T("Decision tree: цепочка правил if-then-else. Примет ли человек оффер?", 0, -50, 20, "#495057"),
    N("root", "Зарплата больше\n$50 000?", 300, 0, "p", 230, 90),
    N("d1", "Отказ", 0, 180, "r", 230, 90),
    N("n2", "Дорога меньше\nчаса?", 560, 180, "p", 230, 90),
    N("d2", "Отказ", 300, 360, "r", 230, 90),
    N("n3", "Есть бесплатный\nкофе?", 820, 360, "p", 230, 90),
    N("ac", "Принять оффер", 560, 540, "g", 230, 90),
    N("d3", "Отказ", 1080, 540, "r", 230, 90),
    T("← корень (root): самый информативный split", 560, 30, 18, "#1971c2"),
    T("Листья (leaf): splits кончились, здесь ответ", 820, 640, 18, "#868e96"),
], edges=[E("root", "d1", "нет"), E("root", "n2", "да"), E("n2", "d2", "нет"),
          E("n2", "n3", "да"), E("n3", "ac", "да"), E("n3", "d3", "нет")])

# Fig 10-11, 10-12: random forest
D["ch10-forest"] = dict(items=[
    T("1. Строки", 330, -50, 20, "#1971c2"),
    T("2. Столбцы", 700, -50, 20, "#2f9e44"),
    T("3. Ответ", 1080, -50, 20, "#e8590c"),
    N("data", "Обучающие\nданные", 0, 230, "db", 230, 110),
    N("s1", "Bootstrap-выборка 1\n(строки с повтором)", 330, 0, "p", 260, 110),
    N("s2", "Bootstrap-выборка 2", 330, 230, "p", 260, 110),
    N("s3", "Bootstrap-выборка 3", 330, 460, "p", 260, 110),
    N("t1", "Дерево 1\nна каждом split:\nслучайные признаки", 700, 0, "g", 230, 110),
    N("t2", "Дерево 2\nна каждом split:\nслучайные признаки", 700, 230, "g", 230, 110),
    N("t3", "Дерево 3\nна каждом split:\nслучайные признаки", 700, 460, "g", 230, 110),
    N("res", "regression: среднее\nclassification:\nголосование деревьев", 1080, 230, "q", 280, 130),
], edges=[E("data", "s1"), E("data", "s2"), E("data", "s3"),
          E("s1", "t1"), E("s2", "t2"), E("s3", "t3"),
          E("t1", "res"), E("t2", "res"), E("t3", "res")])

# Fig 10-5, 10-13: train/test split and k-fold cross-validation
D["ch10-cv"] = dict(items=[
    N("all", "Все данные", 0, 0, "n", 940, 80),
    N("trn", "Train 80%: делим на 3 fold", 0, 140, "db", 700, 80),
    N("tst", "Test 20%\nне трогаем", 760, 140, "n", 180, 80),
    N("a1", "fold 1\ntrain", 0, 280, "g", 220, 100), N("a2", "fold 2\ntrain", 240, 280, "g", 220, 100),
    N("a3", "fold 3\nvalidation", 480, 280, "y", 220, 100), N("ra", "RMSE 1", 760, 280, "n", 180, 100),
    N("b1", "fold 1\ntrain", 0, 420, "g", 220, 100), N("b2", "fold 2\nvalidation", 240, 420, "y", 220, 100),
    N("b3", "fold 3\ntrain", 480, 420, "g", 220, 100), N("rb", "RMSE 2", 760, 420, "n", 180, 100),
    N("c1", "fold 1\nvalidation", 0, 560, "y", 220, 100), N("c2", "fold 2\ntrain", 240, 560, "g", 220, 100),
    N("c3", "fold 3\ntrain", 480, 560, "g", 220, 100), N("rc", "RMSE 3", 760, 560, "n", 180, 100),
    N("avg", "Среднее RMSE:\nоценка одной\nконфигурации", 1100, 420, "q", 250, 120),
    N("best", "Лучшая конфигурация:\nпереобучить на всём train,\nпроверить на test", 1100, 640, "pu", 300, 120),
], edges=[E("all", "trn"), E("all", "tst"), E("trn", "a1"),
          E("a3", "ra"), E("b3", "rb"), E("c3", "rc"),
          E("ra", "avg"), E("rb", "avg"), E("rc", "avg"), E("avg", "best")])

if __name__ == "__main__":
    run_all(D)
