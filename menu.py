MENU_STRUCTURE = {
    "main": {
        "text": "Главное меню",
        "buttons": [
            {"text": "Пункт 1", "action": "goto", "data": "m1"},
            {"text": "Показать статистику", "action": "func", "data": "show_stats"},
        ]
    },
    "m1": {
        "text": "Меню 1",
        "buttons": [
            {"text": "Достать из БД", "action": "func", "data": "get_from_db"},
            {"action": "additems", "data": "get_my_items",},
            {"text": "Назад", "action": "goto", "data": "main"}
        ]
    }
}