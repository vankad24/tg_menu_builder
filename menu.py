MENU_STRUCTURE = {
    "main": {
        "text": "@welcome",
        "buttons": [
            {"text": "Пункт 1", "action": "goto", "data": "m1"},
            {"text": "Пункт 2", "action": "goto", "data": "m2"},
            {"text": "Пустой пункт", "action": "nothing"},
            {"text": "Показать статистику", "action": "func", "data": "show_stats"},
        ]
    },
    "m1": {
        "text": "Меню 1",
        "buttons": [
            {"text": "Достать из БД", "action": "func", "data": "get_from_db"},
            {"action": "gen", "data": "get_vars", "pattern": {"text": "$text", "action":"func", "data":"$funname"}},
            {"text": "Назад", "action": "goto", "data": "main"}
        ]
    },
    "m2": {
        "text": "Меню 2",
        "buttons": [
            {"action": "gen_manual", "data": "get_my_items"},
            {"text": "Назад", "action": "goto", "data": "main"}
        ]
    }
}