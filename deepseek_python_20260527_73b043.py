import sqlite3
from aiogram import types

class Database:
    def __init__(self, path="portfolio.db"):
        self.conn = sqlite3.connect(path)
        self._init_db()

    def _init_db(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS sections (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                section TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS awaiting_input (
                user_id INTEGER PRIMARY KEY,
                section TEXT
            );
        """)
        defaults = {
            "checkers": "🛡️ <b>Чекеры (проверка и анализ)</b>\n\n🔹 <b>Dota 2 Inventory Checker</b>\nСмотрит инвентарь всех игроков в матче в реальном времени и показывает его стоимость.\nИспользует Game State Integration + Steam API.\n\n🔹 <b>Steam Account Checker</b>\nПроверяет аккаунты на валидность, наличие игр, VAC-баны, уровень Steam.\nМассовый прогон с прокси.\n\n🔹 <b>CS2 Float Checker</b>\nОценивает износ скинов (float value) прямо из инвентаря или базы данных.\nПомогает трейдерам быстро находить выгодные позиции.",
            "parsers": "📊 <b>Парсеры и сбор данных</b>\n\n🔹 <b>Telegram User Parser</b>\nСобирает всех участников каналов/чатов: ID, username, телефон, активность.\nВыгрузка в CSV/Excel.\n\n🔹 <b>Steam Market Parser</b>\nМониторит цены на скины, кейсы, стикеры. Отправляет уведомления при падении цены.\nМожно использовать для снайпинга.\n\n🔹 <b>Dota 2 Match Parser</b>\nСобирает историю матчей, статистику героев, винрейты. Полезно для аналитики.",
            "farms": "🎮 <b>Игровые фермы</b>\n\n🔹 <b>CS2 Case Farm</b>\nФарм кейсов и скинов на сотнях аккаунтов одновременно.\nПоддержка прокси, авто-принятие дропа.\n\n🔹 <b>Steam Card Farmer</b>\nФарм коллекционных карточек без установки игр.\nПовышение уровня Steam, продажа карточек на маркете.\n\n🔹 <b>Индивидуальные фермы под заказ</b>\nРазрабатываем любые игровые фермы по вашему ТЗ.\nDota 2, Rust, GTA V и другие игры.",
            "auto": "🤖 <b>Автоматизация</b>\n\n🔹 <b>Telegram Auto-Poster</b>\nАвтопостинг из VK, Twitter, YouTube в Telegram-каналы.\nЧистит водяные знаки, ставит хештеги, работает по расписанию.\n\n🔹 <b>Discord Auto-Moderator</b>\nАвто-модерация чатов: бан спамеров, фильтр мата, капча для новеньких.\n\n🔹 <b>Crypto Trading Bot</b>\nАвто-трейдинг на Binance, Bybit. Арбитраж, мониторинг курсов.",
            "price": "💰 <b>Примерные цены</b>\n\n• Простой бот/парсер — от 3 000 ₽\n• Средний проект — от 10 000 ₽\n• Комплексная система — от 30 000 ₽\n\nСроки:\n• Простое — 1-2 дня\n• Среднее — 3-5 дней\n• Крупное — от недели\n\nТочная цена после обсуждения ТЗ.",
            "contact": "📞 <b>Связаться со мной</b>\n\nTelegram: @nullbyte211\nПо вопросам разработки и сотрудничества.\n\nПиши, обсудим твой проект."
        }
        for key, value in defaults.items():
            self.conn.execute("INSERT OR IGNORE INTO sections (id, text) VALUES (?, ?)", (key, value))
        self.conn.commit()

    def get_text(self, section_id: str) -> str:
        cursor = self.conn.execute("SELECT text FROM sections WHERE id = ?", (section_id,))
        row = cursor.fetchone()
        return row[0] if row else "Раздел не найден."

    def update_text(self, section_id: str, new_text: str):
        self.conn.execute("INSERT OR REPLACE INTO sections (id, text) VALUES (?, ?)", (section_id, new_text))
        self.conn.commit()

    def log_click(self, user: types.User, section: str):
        self.conn.execute(
            "INSERT INTO stats (user_id, username, first_name, last_name, section) VALUES (?, ?, ?, ?, ?)",
            (user.id, user.username, user.first_name, user.last_name, section)
        )
        self.conn.commit()

    def get_stats(self, limit: int = 50) -> str:
        cursor = self.conn.execute(
            "SELECT user_id, username, first_name, last_name, section, created_at FROM stats ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        if not rows:
            return "Нет данных о посещениях."
        lines = ["Последние посещения:"]
        for row in rows:
            uid, username, first_name, last_name, section, created_at = row
            name = first_name or "Не указано"
            uname = f"@{username}" if username else "нет"
            lines.append(f"• {name} {uname} ({uid}) → {section} ({created_at})")
        return "\n".join(lines)

    def set_awaiting_input(self, user_id: int, section: str):
        self.conn.execute("INSERT OR REPLACE INTO awaiting_input (user_id, section) VALUES (?, ?)", (user_id, section))
        self.conn.commit()

    def get_awaiting_input(self, user_id: int) -> str:
        cursor = self.conn.execute("SELECT section FROM awaiting_input WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return row[0] if row else ""

    def clear_awaiting_input(self, user_id: int):
        self.conn.execute("DELETE FROM awaiting_input WHERE user_id = ?", (user_id,))
        self.conn.commit()