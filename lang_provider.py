from dataclasses import dataclass
from typing import Optional

from users_orm import UsersOrm

@dataclass
class Lang:

    lang_code: str
    lang_name: str

    help_command_text: str

    help_command_start_playing_button: str

    review_reward_msg_very_happy: str
    review_reward_msg: str
    review_command_success_text: str
    review_command_success_no_rewards_text: str
    review_command_text: str
    review_command_button_yourself: str
    review_command_button_world: str
    review_since_last_time: str
    days_short: str
    hours_short: str
    minutes_short: str
    seconds_short: str

    difficulty_level_changed: str
    formula_changed: str

    difficulties: list[str]

    paused_command: str

    stats_command: str
    resumed: str
    already_paused: str

    game_started: str

    difficulty_command_text: str
    current_difficulty: str

    formula_command_text: str
    formula_command_button: str

    menu_review: str
    menu_pause: str
    menu_stats: str
    menu_formula: str
    menu_difficulty: str
    menu_data: str
    review_command_timeout: str

    graph_header: str
    graph_penalty_threshold: str
    graph_mean_threshold: str
    graph_xlabel: str
    graph_ylabel: str
    graph_xmax: str
    graph_xmin: str
    graph_paused: str

    data_view: str
    data_view_localstorage_button: str
    data_delete_button: str
    data_deleted: str

    review_btn: str

    reminder_text: str

    penalty_msg_no_penalty_for_level: str
    penalty_msg_no_penalty_first_time: str
    penalty_msg_first_time: str
    penalty_msg_generic_small: str
    penalty_msg_generic_full: str

    penalty_text: str

es = Lang(
    lang_code='es',
    lang_name='Español',
    help_command_text=f"""¡Hola, extraño! 👋 ¡Bienvenido al bot del juego <a href="https://mindwarriorgame.org/faq.es.html">MindWarrior</a>! 🥷
    
🧪 Crea tu "<a href="https://mindwarriorgame.org/faq.es.html#formula">Fórmula de Firme Resolución</a>", un mensaje inspirador para ti mismo.

💫 <a href="https://mindwarriorgame.org/faq.es.html#review">Revísala</a> a lo largo del día para mantenerte motivado y enfocado, ¡y gana recompensas! <a href="https://mindwarriorgame.org/faq.es.html#forgot">¿Qué pasa si me olvido?</a>

 ‣ <a href="https://mindwarriorgame.org/quick-start.es.html">Guía de inicio rápido</a>
 ‣ <a href="https://mindwarriorgame.org/faq.es.html">Preguntas frecuentes</a> 
 ‣ <a href="https://mindwarriorgame.org/privacy-policy.es.html">Política de privacidad</a>""",

    menu_review="💫️revisar Fórmula",
    menu_pause="⏸️ pausar el juego",
    menu_stats="🌟 ver progreso del juego",
    menu_formula="️🧪actualizar Fórmula",
    menu_difficulty="💪cambiar dificultad",
    menu_data = "🗂 ver tus datos crudos",

    help_command_start_playing_button="¡Escribe \"Fórmula\" y comienza a jugar!",

    review_command_text="Revisa tu <i>Fórmula</i> 💫\n"
                        "\n"
                        "Presiona cualquier botón a continuación para revisar tu <i>Fórmula</i>.",

    review_command_button_yourself="Mejórate a ti mismo 💪",
    review_command_button_world="Mejora el mundo 🙌",

    review_reward_msg_very_happy="😻 ¡Has ganado 2 nuevas estrellas!",
    review_reward_msg="😺 ¡Has ganado una nueva estrella!",
    review_command_success_text="<i>Fórmula</i> revisada 🎉\n"
                                "\n"
                                "<b>{reward_msg}</b>\n"
                                "\n"
                                "🌟Estrellas totales: {score}\n"
                                "⏳Tiempo de juego: {time}\n"
                                "\n"
                                "Próxima revisión antes de {next_review}\n"
                                "\n"
                                "/pause - pausar el juego",

    review_command_success_no_rewards_text="<i>Fórmula</i> revisada 🎉\n"
                                "\n"
                                "Sin recompensa (<a href=\"https://mindwarriorgame.org/faq.es.html#difficulty:~:text=ser%C3%A1%20recompensado%20(-,%22regla%20de%20enfriamiento%22,-).\">regla de enfriamiento</a>)\n" 
                                "\n"    
                                "🌟Estrellas totales: {score}\n"
                                "⏳Tiempo de juego: {time}\n"
                                "\n"
                                "Próxima revisión antes de {next_review}\n"
                                "\n"
                                "/pause - pausar el juego",

    review_since_last_time="Tiempo desde la última revisión: {duration}",

    days_short="d",
    hours_short="h",
    minutes_short="m",
    seconds_short="s",

    difficulty_level_changed="La dificultad ha sido cambiada 💪\n"
                                "El juego se reinició debido al cambio de la dificultad.\n"
                                "\n"    
                                "<b>{old} -> {new}</b>\n"   
                                "\n"
                                "🌟Estrellas totales: 0\n"
                                "⏳Tiempo de juego: 0d 0h 0m\n"
                                "\n"
                                "Próxima revisión antes de {next_review}\n",

    formula_changed="¡La <i>Fórmula</i> ha sido actualizada!",

    difficulties=["Principiante", "Fácil", "Medio", "Difícil", "Experto"],

    paused_command="El juego está pausado ⏸️\n"
                    "\n"    
                    "No recibirás recordatorios sobre tu <i>Fórmula</i>, "
                    "y el contador de tiempo de juego activo <a href=\"https://mindwarriorgame.org/faq.es#pause\">está congelado</a>.\n"    
                    "\n"    
                    "Para reanudar el juego, "
                    "simplemente revisa tu <i>Fórmula</i> con el botón a continuación.",

    stats_command=("🌟 <a href=\"https://mindwarriorgame.org/faq.es.html#review\">Estrellas ganadas</a>: {score}\n"
                    "⌛ Tiempo de juego activo: {time}\n"
                    "💪 <a href=\"https://mindwarriorgame.org/faq.es.html#difficulty\">Dificultad</a>: {difficulty} ({difficulty_details})\n"
                    "⏸️ <a href=\"https://mindwarriorgame.org/faq.es.html#pause\">¿Pausado?</a> {paused}\n"
                    "❄️ <a href=\"https://mindwarriorgame.org/faq.es.html#difficulty:~:text=ser%C3%A1%20recompensado%20(-,%22regla%20de%20enfriamiento%22,-).\">Tiempo de enfriamiento</a> antes de la próxima recompensa: {cooldown}\n"
                    "⏰ Tiempo antes del próximo <a href=\"https://mindwarriorgame.org/faq.es.html#forgot\">recordatorio</a>: {punishment}"),

    resumed="El juego ha sido reanudado.",
    already_paused="El juego ya está pausado ⏸️\n"
                    "\n"
                    "Para reanudar el juego, simplemente revisa tu <i>Fórmula</i> con el botón a continuación.",
    game_started="El juego ha comenzado 🏁\n"
        "\n"
        "💪<a href=\"https://mindwarriorgame.org/faq.es.html#difficulty\">Nivel de dificultad</a>: {difficulty}\n"
        "\n"
        "Revisa tu <i>Fórmula</i> antes de {next_review}\n"
        "\n"
        "/difficulty - cambiar la dificultad\n"
        "/pause - pausar el juego",

    review_btn="Revisar tu \"Fórmula\"",

    difficulty_command_text="Cambiar el nivel de dificultad💪\n"
                            "\n"
                            "Selecciona un nuevo <a href=\"https://mindwarriorgame.org/faq.es.html#difficulty\">nivel de dificultad</a> usando los botones a continuación.\n"
                            "\n"    
                            "<b>⚠️¡Esto reiniciará tu progreso en el juego!</b>\n",

    current_difficulty="nivel actual",

    formula_command_text="Actualizar tu <i>Fórmula</i> 🧪\n"
                            "\n"
                            "Utiliza el botón a continuación para actualizar tu <i><a href=\"https://mindwarriorgame.org/faq.es.html#formula\">Fórmula</a></i>.",
    formula_command_button="Actualizar tu Fórmula",
    review_command_timeout="Tiempo agotado, por favor inténtalo de nuevo.🤷",
    graph_header="Intervalos entre revisiones (mins)",
    graph_penalty_threshold="Umbral de penalización: {difficulty_threshold_mins} mins (dificultad={difficulty_str})",
    graph_mean_threshold="Mediana: {mean_mins} mins",
    graph_xlabel="Tiempo",
    graph_ylabel="Intervalo entre revisiones (mins)",
    graph_xmax='Ahora',
    graph_xmin='Hace 6 días',
    graph_paused="Pausado",

    data_view="Tus datos crudos:",
    data_view_localstorage_button="Ver datos de localStorage",
    data_delete_button="ELIMINAR TODOS LOS DATOS",
    data_deleted="Todos tus datos han sido eliminados. Por favor, borra el historial del chat para eliminar los datos del chat de Telegram.",

    reminder_text="¡No olvides revisar tu <i>Fórmula</i>! ⏰\n"
                    "\n"
                    "¡El tiempo límite es en 15 minutos, date prisa!",

    penalty_msg_no_penalty_for_level = "😼 Sin penalización (nivel <a href=\"https://mindwarriorgame.org/faq.es.html#difficulty\">\"{difficulty}\"</a>)",
    penalty_msg_no_penalty_first_time = "😼 Sin penalización (<a href=\"https://mindwarriorgame.org/faq.es.html#difficulty\">nivel \"Fácil\", primer fallo</a> 😬)\n",
    penalty_msg_first_time = "😿 Has perdido {penalty} estrellas (primera vez que se pierde) ❗\n"
                            "\n"
                            "🌟 Estrellas restantes: {score}",
    penalty_msg_generic_small = "😿 Has perdido {penalty} estrellas ❗\n"
                                "\n"
                                "🌟 Estrellas restantes: {score}",
    penalty_msg_generic_full = "🙀 Has perdido {penalty} estrellas ❗\n"
                               "\n"
                                 "🌟 Estrellas restantes: {score}",
    penalty_text = "Olvidaste revisar tu <i>Fórmula</i> a tiempo 🟥\n"
                   "\n"
                   "{penalty_msg}"
)



en = Lang(
    lang_code='en',
    lang_name='English',
    help_command_text=f"""Hey, stranger! 👋 Welcome to <a href="https://mindwarriorgame.org/faq.en.html">MindWarrior game</a> bot! 🥷  

🧪 Craft your "<a href="https://mindwarriorgame.org/faq.en.html#formula">Formula of Firm Resolution</a>", an inspirational message to yourself.

💫 <a href="https://mindwarriorgame.org/faq.en.html#review">Review it</a> throughout your day to stay motivated, and earn rewards! <a href="https://mindwarriorgame.org/faq.en.html#forgot">What if I forget?</a>

 ‣ <a href="https://mindwarriorgame.org/quick-start.en.html">Quick-start guide</a>
 ‣ <a href="https://mindwarriorgame.org/faq.en.html">FAQs</a>
 ‣ <a href="https://mindwarriorgame.org/privacy-policy.en.html">Privacy policy</a>""",

    menu_review="💫️review Formula",
    menu_pause="⏸️ pause the game",
    menu_stats="🌟 view game progress",
    menu_formula="️🧪update Formula",
    menu_difficulty="💪change difficulty",
    menu_data = "🗂 view your raw data",

    help_command_start_playing_button="Write \"Formula\" and start playing!",

    review_command_text="Review your <i> Formula</i> 💫\n"
                        "\n"
                        "Press any button below to review your <i>Formula</i>.",

    review_command_button_yourself="Improve yourself 💪",
    review_command_button_world="Improve the world 🙌",

    review_reward_msg_very_happy="😻 You've got 2 new stars!",
    review_reward_msg="😺 You've got a new star!",
    review_command_success_text="<i>Formula</i> has been reviewed 🎉\n"
                                "\n"
                                "<b>{reward_msg}</b>\n"
                                "\n"
                                "🌟 Total stars: {score}\n"
                                "⏳ Play time: {time}\n"
                                "\n"
                                "Next review before {next_review}\n"
                                "\n"
                                "/pause - pause the game",

    review_command_success_no_rewards_text="<i>Formula</i> has been reviewed 🎉\n"
                                "\n"
                                "No reward (<a href=\"https://mindwarriorgame.org/faq.en.html#difficulty:~:text=will%20be%20rewarded%20(-,%22cool%2Ddown%22%20rule,-).\">cool-down rule</a>)\n"
                                "\n"
                                "🌟Total stars: {score}\n"
                                "⏳Play time: {time}\n"
                                "\n"
                                "Next review before {next_review}\n"
                                "\n"
                                "/pause - pause the game",

    review_since_last_time="Time since the last review: {duration}",

    days_short="d",
    hours_short="h",
    minutes_short="m",
    seconds_short="s",

    difficulty_level_changed="The difficulty level has been changed 💪\n"
                             "The game was restarted due to the change of the difficulty level.\n"
                             "\n"
                             "<b>{old} -> {new}</b>\n"
                             "\n"
                             "🌟Total stars: 0\n"
                             "⏳Play time: 0d 0h 0m\n"
                             "\n"
                             "Next review before {next_review}\n",

    formula_changed="The <i>Formula</i> has been updated!",

    difficulties=["Beginner", "Easy", "Medium", "Hard", "Expert"],

    paused_command="The game is paused ⏸️\n"
                   "\n"
                   "You will not be receiving reminders about your <i>Formula</i>, "
                   "and the active play time counter <a href=\"https://mindwarriorgame.org/faq.en#pause\">are frozen</a>.\n"
                   "\n"
                   "To resume the game, "
                   "simply review your <i>Formula</i> using the button below.",

    stats_command=("🌟 <a href=\"https://mindwarriorgame.org/faq.en.html#review\">Earned stars</a>: {score}\n"
                   "⌛ Active play time: {time}\n"
                   "💪 <a href=\"https://mindwarriorgame.org/faq.en.html#difficulty\">Difficulty</a>: {difficulty} ({difficulty_details})\n"
                   "⏸️ <a href=\"https://mindwarriorgame.org/faq.en.html#pause\">Paused?</a> {paused}\n"
                   "❄️ <a href=\"https://mindwarriorgame.org/faq.en.html#difficulty:~:text=will%20be%20rewarded%20(-,%22cool%2Ddown%22%20rule,-).\">Cool-down</a> time before next reward: {cooldown}\n"
                   "⏰ Time before next<a href=\"https://mindwarriorgame.org/faq.en.html#forgot\">reminder</a>: {punishment}"),

    resumed="The game is resumed.",
    already_paused="The game is already paused ⏸️\n"
                   "\n"
                   "To resume the game, simply review your <i>Formula</i> with the button below.",
    game_started="The game has started 🏁\n"
        "\n"
        "💪<a href=\"https://mindwarriorgame.org/faq.en.html#difficulty\">Difficulty level</a>: {difficulty}\n"
        "\n"
        "Review your <i>Formula</i> before {next_review}\n"
        "\n"
        "/difficulty - change the difficulty\n"
        "/pause - pause the game",

    review_btn="Review your \"Formula\"",

    difficulty_command_text="Change the difficulty level💪\n"
                            "\n"
                            "Select a new <a href=\"https://mindwarriorgame.org/faq.en.html#difficulty\">difficulty level</a> using the buttons below.\n"
                            "\n"
                            "<b>⚠️This will reset your game progress!</b>\n",

    current_difficulty="current level",

    formula_command_text="Update your <i>Formula</i> 🧪\n"
                         "\n"
                         "Use the button below to update your <i><a href=\"https://mindwarriorgame.org/faq.en.html#formula\">Formula</a></i>.",
    formula_command_button="Update your Formula",
    review_command_timeout="Timeout, please try again.🤷",
    graph_header="Intervals between review (mins)",
    graph_penalty_threshold="Penalty threshold: {difficulty_threshold_mins} mins (difficulty={difficulty_str})",
    graph_mean_threshold="Median: {mean_mins} mins",
    graph_xlabel="Time",
    graph_ylabel="Interval between reviews (mins)",
    graph_xmax='Now',
    graph_xmin='6 days ago',
    graph_paused="Paused",

    data_view="Your raw data:",
    data_view_localstorage_button="View localStorage data",
    data_delete_button="DELETE ALL DATA",
    data_deleted="All your data has been deleted. Please clear the chat history to remove the data from Telegram chat.",

    reminder_text="Don't forget to review your <i>Formula</i>! ⏰\n"
                  "\n"
                  "The due time is in 15 minutes, hurry up!",

    penalty_msg_no_penalty_for_level = "😼 No penalty (<a href=\"https://mindwarriorgame.org/faq.en.html#difficulty\">\"{difficulty}\" level</a>)",
    penalty_msg_no_penalty_first_time = "😼 No penalty (<a href=\"https://mindwarriorgame.org/faq.en.html#difficulty\">\"{difficulty}\" level, first miss</a> 😬)",
    penalty_msg_first_time = "😿 You've lost {penalty} stars (first miss)❗\n"
                             "\n"
                             "🌟 Remaining stars: {score}",
    penalty_msg_generic_small = "😿 You've lost {penalty} stars ❗\n"
                                "\n"
                                "🌟 Remaining stars: {score}",
    penalty_msg_generic_full = "🙀 You've lost {penalty} stars ❗\n"
                               "\n"
                               "🌟 Remaining stars: {score}",
    penalty_text = "You forgot to review your <i>Formula</i> 🟥\n"
                    "\n"   
                    "{penalty_msg}"

)


ru = Lang(
    lang_code='ru',
    lang_name='Русский',
    help_command_text=f"""👋 Приветствуем тебя, о, Cтранник! Добро пожаловать в игру <a href="https://mindwarriorgame.org/faq.ru.html">MindWarrior</a>! 🥷  

🧪 Создай свою "<a href="https://mindwarriorgame.org/faq.ru.html#formula">Формулу Твердой Решимости</a>", мотивирующее послание самому себе.

💫 <a href="https://mindwarriorgame.org/faq.ru.html#review">Просматривай ее</a> в течение дня, поддерживай мотивацию и фокус, зарабатывай игровые очки! <a href="https://mindwarriorgame.org/faq.ru.html#forgot">Что будет, если я забуду?</a>

 ‣ <a href="https://mindwarriorgame.org/quick-start.ru.html">Краткое руководство</a>
 ‣ <a href="https://mindwarriorgame.org/faq.ru.html">Вопросы и ответы</a>
 ‣ <a href="https://mindwarriorgame.org/privacy-policy.ru.html">Политика конфиденциальности</a>""",

    menu_review="💫️просмотреть Формулу",
    menu_pause="⏸️ поставить игру на паузу",
    menu_stats="🌟 просмотреть статистику игры",
    menu_formula="🧪 изменить Формулу",
    menu_difficulty="💪 изменить сложность",
    menu_data = "🗂 просмотреть свои данные",


    help_command_start_playing_button="Написать \"Формулу\" и начать игру!",

    review_command_text="Просмотрите свою <i>Формулу</i> 💫\n"
                        "\n"
                        "Нажмите любую кнопку ниже, чтобы просмотреть свою <i>Формулу</i>.",

    review_command_button_yourself="Улучшить себя 💪",
    review_command_button_world="Улучшить мир 🙌",

    review_reward_msg_very_happy="😻 Вы получили 2 новые звезды!",
    review_reward_msg="😺 Вы получили новую звезду!",
    review_command_success_text="<i>Формула</i> просмотрена 🎉\n"
                                "\n"
                                "<b>{reward_msg}</b>\n"
                                "\n"
                                "🌟 Всего звезд: {score}\n"
                                "⏳ Время игры: {time}\n"
                                "\n"
                                "Следующий просмотр не позже {next_review}\n"
                                "\n"
                                "/pause - игру на паузу",


    review_command_success_no_rewards_text="<i>Формула</i> просмотрена 🎉\n"
                                "\n"
                                "Без награды (<a href=\"https://mindwarriorgame.org/faq.ru.html#difficulty:~:text=%D0%BC%D0%B5%D0%B6%D0%B4%D1%83%20%D0%BA%D0%BE%D1%82%D0%BE%D1%80%D1%8B%D0%BC%D0%B8%20%D0%BF%D1%80%D0%BE%D1%88%D0%BB%D0%BE%20%D1%85%D0%BE%D1%82%D1%8F%20%D0%B1%D1%8B%205%20%D0%BC%D0%B8%D0%BD%D1%83%D1%82\">слишком частые просмотры</a>)\n"
                                "\n"
                                "🌟Всего звезд: {score}\n"
                                "⏳Время игры: {time}\n"
                                "\n"
                                "Следующий просмотр не позже {next_review}\n"
                                "\n"
                                "/pause - игру на паузу",


    review_since_last_time="Прошло с последнего просмотра: {duration}",

    days_short="д",
    hours_short="ч",
    minutes_short="м",
    seconds_short="с",

    difficulty_level_changed="Сложность игры изменена 💪\n"
                             "Игра перезапущена из-за изменения сложности.\n"
                             "\n"
                             "<b>{old} -> {new}</b>\n"
                             "\n"
                             "🌟Всего звезд: 0\n"
                             "⏳Время игры: 0d 0h 0m\n"
                             "\n"
                             "Следующий просмотр не позже {next_review}\n",

    formula_changed="<i>Формула</i> обновлена!",

    difficulties=["Новичок", "Легко", "Средне", "Сложно", "Эксперт"],

    paused_command="Игра на паузе ⏸️\n"
                   "\n"
                   "Напоминания о просмотрах <i>Формулы</i> и счетчик "
                   "времени активной игры <a href=\"https://mindwarriorgame.org/faq.ru#pause\">остановлены</a>.\n"
                   "\n"
                   "Для снятия с паузы просмотрите свою <i>Формулу</i> с помощью кнопки ниже.",

    stats_command=("🌟 <a href=\"https://mindwarriorgame.org/faq.ru.html#review\">Заработано звезд</a>: {score}\n"
                   "⌛ Время активной войны: {time}\n"
                   "💪 <a href=\"https://mindwarriorgame.org/faq.ru.html#difficulty\">Сложность игры</a>: {difficulty} ({difficulty_details})\n"
                   "⏸️ <a href=\"https://mindwarriorgame.org/faq.ru.html#pause\">На паузе?</a> {paused}\n"
                   "❄️ <a href=\"https://mindwarriorgame.org/faq.ru.html#difficulty:~:text=will%20be%20rewarded%20(-,%22cool%2Ddown%22%20rule,-).\">Время до следующей награды</a>: {cooldown}\n"
                   "⏰ Время до <a href=\"https://mindwarriorgame.org/faq.ru.html#forgot\">напоминания</a>: {punishment}"),
    resumed="Игра снята с паузы.",
    already_paused="Игра уже на паузе ⏸️\n"
                   "\n"
                   "Чтобы продолжить игру, просмотрите свою <i>Формулу</i> с помощью кнопки ниже.",

    game_started="Игра начата 🏁\n"
                 "\n"
                 "💪<a href=\"https://mindwarriorgame.org/faq.ru.html#difficulty\">Уровень сложности</a>: {difficulty}\n"
                 "\n"
                 "Просмотрите свою <i>Формулу</i> не позже {next_review}\n"
                 "\n"
                 "/difficulty - изменить сложность\n"
                 "/pause - игру на паузу",

    review_btn="Просмотреть свою \"Формулу\"",

    difficulty_command_text="Изменить сложность 💪\n"
                            "\n"
                            "Выберите новый <a href=\"https://mindwarriorgame.org/faq.ru.html#difficulty\">уровень сложности</a>.\n"
                            "\n"
                            "<b>⚠️Это обнулит ваш игровой прогресс!</b>",

    current_difficulty="текущий уровень",

    formula_command_text="️Обновите свою <i>Формулу</i> 🧪\n"
                         "\n"
                         "Используйте кнопку ниже, чтобы обновить свою <i><a href=\"https://mindwarriorgame.org/faq.ru.html#formula\">Формулу</a></i>.",

    formula_command_button="Обновить Формулу",
    review_command_timeout="Таймаут, попробуйте еще раз.🤷",
    graph_header="Время между просмотрами (мин)",
    graph_penalty_threshold="Штрафной порог: {difficulty_threshold_mins} мин (сложность={difficulty_str})",
    graph_mean_threshold="Медиана: {mean_mins} мин",
    graph_xlabel="Время",
    graph_ylabel="Интервал между просмотрами (мин)",
    graph_xmax='Сейчас',
    graph_xmin='6 дней назад',
    graph_paused="Пауза",

    data_view="Ваши данные:",
    data_view_localstorage_button="Посмотреть данные localStorage",
    data_delete_button="УДАЛИТЬ ВСЕ ДАННЫЕ",
    data_deleted="Все ваши данные удалены. Пожалуйста, удалите историю чата, чтобы удалить данные из Telegram-а.",

    reminder_text="Не забудьте просмотреть свою <i>Формулу</i>! ⏰\n"
                  "\n"
                  "Время истекает через 15 минут, поторопитесь!",

    penalty_msg_no_penalty_for_level = "😼 Без штрафа (уровень <a href=\"https://mindwarriorgame.org/faq.ru.html#difficulty\">\"{difficulty}\"</a>)",
    penalty_msg_no_penalty_first_time = "😼 Без штрафа (уровень <a href=\"https://mindwarriorgame.org/faq.ru.html#difficulty\">\"{difficulty}\", первый пропуск</a> 😬)",
    penalty_msg_first_time = "😿 Вы потеряли {penalty} звезды (первый пропуск)❗\n"
                             "\n"
                             "🌟 Осталось звезд: {score}",
    penalty_msg_generic_small = "😿 Вы потеряли {penalty} звезды ❗\n"
                                "\n"
                                "🌟 Осталось звезд: {score}",
    penalty_msg_generic_full = "🙀 Вы потеряли {penalty} звезд ❗\n"
                               "\n"
                               "🌟 Осталось звезд: {score}",
    penalty_text = "Вы забыли вовремя просмотреть свою <i>Формулу</i> 🟥\n"
                   "\n"
                   "{penalty_msg}"
)

class LangProvider:

    @staticmethod
    def get_available_languages() -> dict[str, Lang]:
        return {
            en.lang_code: en,
            ru.lang_code: ru,
            es.lang_code: es
        }

    def __init__(self, db_file: str):
        self.users_orm = UsersOrm(db_file)

    def get_user_lang(self, chat_id: int) -> Optional[str]:
        return self.users_orm.get_user_by_id(chat_id)['lang_code']

    def set_user_lang(self, chat_id: int, lang_code: str):
        user = self.users_orm.get_user_by_id(chat_id)
        user['lang_code'] = lang_code
        self.users_orm.upsert_user(user)
