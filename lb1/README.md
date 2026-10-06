# Лабораторна робота № 1 — варіант 15

Тема: розгортання робочого середовища Python, VS Code, Jupyter та Git. Індивідуальне завдання — вивести фактичні характеристики числових типів CPython через `sys.float_info` і `sys.int_info`.

## Склад каталогу

- `system_diagnostics.py` — головний скрипт, який друкує реальні параметри `float` та `int` запущеного CPython;
- `exploration_notebook.ipynb` — блокнот для справжнього виконання в ядрі Jupyter;
- `environment.yml` — відтворювана специфікація `ce_lab_env` з Python 3.10 та `ipykernel`;
- `.vscode/launch.json` — конфігурація запуску/налагодження, якщо у VS Code відкрито саме каталог `lb1`;
- `.gitignore` — локальні правила виключення кешів, середовищ і тимчасових артефактів.

## Підготовка та запуск

Створіть середовище один раз за `environment.yml`, або скористайтеся вже створеним `ce_lab_env`:

```bash
conda env create -f environment.yml
conda activate ce_lab_env
python system_diagnostics.py
```

Якщо репозиторій відкрито з кореня, перейдіть до каталогу лабораторної перед запуском:

```bash
cd /шлях/до/python-labs/lb1
conda activate ce_lab_env
python system_diagnostics.py
```

Для блокнота відкрийте `exploration_notebook.ipynb` у VS Code, оберіть ядро **Python (ce_lab_env)** та виконайте усі комірки (`Run All`). Файл у репозиторії не містить згенерованих виведень: вони мають виникнути під час справжнього запуску на вашій машині.
