# Большие деньги в большом футболе

Дашборд: рыночная стоимость топ-25 клубов мира по данным Transfermarkt, 2019—2026.
Исторические значения восстановлены по архивным снапшотам Wayback Machine.

## Запуск локально

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python collect.py            # сбор данных из Wayback в data/clubs.csv
streamlit run dashboard.py
```

Откроется на `http://localhost:8501`. После первого `python collect.py` сырой HTML
кешируется в `data/html/` — повторные запуски работают только с кешем.

## Обновление данных

`python collect.py` ходит в Wayback Machine, берёт по одному снапшоту на каждый
квартал (январь / апрель / июль / октябрь) и парсит первую страницу рейтинга
(топ-25 клубов). Новые снапшоты добавятся автоматически, уже скачанные не
запрашиваются повторно.

Если на каком-то снапшоте парсер выдал `EMPTY` — соответствующий HTML лежит в
`data/html/{timestamp}.html`, можно посмотреть и поправить селекторы в `collect.py`.

## Деплой на Streamlit Community Cloud

1. Создай публичный репозиторий на GitHub и запушь в него весь проект **вместе с
   `data/clubs.csv`** (`data/html/` исключён через `.gitignore`):

   ```bash
   cd "/home/ar4i/Рабочий стол/price-fot"
   git init -b main
   git add .
   git commit -m "Initial dashboard"
   git remote add origin git@github.com:<USERNAME>/price-fot.git
   git push -u origin main
   ```

2. Открой [share.streamlit.io](https://share.streamlit.io) → **New app** →
   подключи репозиторий, укажи `dashboard.py` как точку входа.
3. Деплой автоматический, через 1–2 минуты будет ссылка вида
   `https://<app-name>.streamlit.app`.

При обновлении `data/clubs.csv` в репозитории Streamlit Cloud автоматически
переразвернёт приложение.

## Структура

```
.
├── dashboard.py        — Streamlit-дашборд
├── collect.py          — сбор данных из Wayback Machine
├── requirements.txt
├── data/
│   ├── clubs.csv       — итоговые данные
│   └── html/           — кеш сырого HTML (не коммитится)
└── .streamlit/
    └── config.toml     — тема и настройки сервера
```
