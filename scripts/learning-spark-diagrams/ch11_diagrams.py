#!/usr/bin/env python3
"""Chapter 11 (Managing, Deploying, and Scaling ML Pipelines) diagrams. Usage: ch11_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Fig 11-1 (+11-2): four MLflow components and how a model moves between them
D["ch11-mlflow-components"] = dict(items=[
    N("proj", "Projects\nкод и зависимости\nв одном описании (YAML)", 0, 0, "n", 300, 110),
    N("run", "Запуск обучения\nnotebook, приложение\nили облачный job", 480, 0, "p", 300, 110),
    N("trk", "Tracking\nparams, metrics,\nartifacts, версия кода", 1000, 0, "g", 300, 110),
    N("mdl", "Models\nмодель в стандартном\nформате (flavors)", 480, 250, "y", 300, 110),
    N("reg", "Registry\nверсии, стадии,\nпометки", 1000, 250, "q", 300, 110),
    N("dep", "Развёртывание\nbatch, streaming,\nREST-сервис", 1000, 500, "pu", 300, 110),
], edges=[E("proj", "run", "запуск"), E("run", "trk", "логирует"),
          E("run", "mdl", "сохраняет"), E("mdl", "reg", "регистрирует"),
          E("reg", "dep", "отдаёт версию")])

# Fig 11-5: batch / streaming / real-time and where MLlib fits
D["ch11-deploy-options"] = dict(items=[
    T("Задержка падает слева направо, пропускная способность тоже", 0, -50, 20, "#495057"),
    N("b", "Batch\nпрогноз по расписанию\nчасы - дни\nMLlib: подходит", 0, 0, "g", 280, 150),
    N("s", "Streaming\nmicro-batch\nсекунды - минуты\nMLlib: подходит", 360, 0, "g", 280, 150),
    N("n", "Near real-time\nсервер с MLlib\nсотни мс - секунды\nMLlib: с оговорками", 720, 0, "y", 280, 150),
    N("r", "Real-time\nпрогноз за\nмиллисекунды\nMLlib: не успевает", 1080, 0, "r", 280, 150),
    N("x", "Экспорт модели из Spark:\nONNX, XGBoost (native), свой код", 1030, 300, "pu", 380, 100),
    N("sv", "Сервис с низкой задержкой:\nSageMaker, Azure ML", 1030, 520, "db", 380, 100),
], edges=[E("b", "s"), E("s", "n"), E("n", "r"), E("r", "x", "вынести"), E("x", "sv", "развернуть")])

# Fig 11-7: distributed hyperparameter search with SparkTrials / Joblib
D["ch11-hyperparam-search"] = dict(items=[
    N("drv", "Driver\nHyperopt fmin\nпредлагает наборы гиперпараметров", 420, 0, "p", 420, 110),
    N("e1", "Executor 1\nобучает одну модель\nна своей копии данных", 0, 280, "g", 340, 110),
    N("e2", "Executor 2\nобучает одну модель\nна своей копии данных", 460, 280, "g", 340, 110),
    N("e3", "Executor 3\nобучает одну модель\nна своей копии данных", 920, 280, "g", 340, 110),
    N("res", "Driver получает loss\nкаждой модели", 420, 560, "y", 420, 100),
    T("Hyperopt берёт loss, предлагает лучшие наборы - и цикл повторяется", 160, 720, 20, "#495057"),
], edges=[E("drv", "e1", "1. набор"), E("drv", "e2", "1. набор"), E("drv", "e3", "1. набор"),
          E("e1", "res", "2. loss"), E("e2", "res", "2. loss"), E("e3", "res", "2. loss")])

if __name__ == "__main__":
    run_all(D)
