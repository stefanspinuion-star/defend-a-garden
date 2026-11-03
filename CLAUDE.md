# Website — сайт игры Defend a Garden

Статичный сайт на GitHub Pages: https://stefanspinuion-star.github.io/defend-a-garden/ (репозиторий
`stefanspinuion-star/defend-a-garden`, ветка `main`, Pages раздаёт папку `docs/`). План и стратегия —
`RobloxProject/growth/plans/2026-11-03-website-and-forums.md`.

- Собрать: `python build.py` (только стандартная библиотека). Картинки: `sh tools/images.sh` (ffmpeg).
- Тексты только в `content/`: `site.json` (ссылки, id пассов, цены, дорожная карта, коды), `i18n/{en,ro,ru}.json`,
  `news.json`. В `docs/` руками не править — перезаписывается сборкой.
- Языки en (корень), ro, ru. Ключи всех трёх `i18n` должны совпадать — сборка падает, если нет.
- Продажи только через Roblox: витрина ведёт на страницы пассов, платёжных форм на сайте нет (правила Roblox).
- Ничего не собираем: без cookie, аналитики и форм. Переходы считаем Share Link у кнопки Play (`site.json` → `playUrl`).
- Кадры игры: `RobloxProject/store-assets/2026-11-03-site/raw`, снимались в Play со скрытым HUD; в углу каждого кадра
  кнопка Roblox, кадрирование её обходит.
- Коммиты от `stefanspinuion-star@users.noreply.github.com` (настроено в репозитории): личная почта не публикуется.
