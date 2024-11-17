from dataclasses import dataclass
from typing import Optional

from users_orm import UsersOrm

@dataclass
class Lang:

    lang_code: str
    lang_name: str

    help_command_text: str

    help_command_start_playing_button: str

    review_command_success_text: str
    review_command_text: str
    review_command_button_yourself: str
    review_command_button_world: str
    review_since_last_time: str
    review_paused_text: str
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
    start_game_prompt: str

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
    menu_feedback: str

    feedback_text: str

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

    penalty_text: str

    badge_unhappy_cat: str
    badge_new: str
    view_badges_button: str
    locked_achievements: str
    cooldown_msg: str

    kicking_out_grumpy_cat: str
    grumpy_cat_kicked_out: str
    remained_grumpy_cats: str
    achievements_unblocked: str
    achievements_link_regenerated: str

    autopause_on_msg: str
    autopause_resumed_msg: str

fr = Lang(
    lang_code='fr',
    lang_name='Français',

    help_command_text = f"""Hey, étranger ! 👋 Bienvenue sur le bot du <a href="https://mindwarriorgame.org/faq.fr.html">jeu MindWarrior</a> ! 🥷  

🧪 Créez votre "<a href="https://mindwarriorgame.org/faq.fr.html#formula">Formule de Résolution Ferme</a>", un message inspirant pour vous-même.

💫 <a href="https://mindwarriorgame.org/faq.fr.html#review">Révisez-le</a> tout au long de la journée pour rester motivé et gagnez des récompenses ! <a href="https://mindwarriorgame.org/faq.fr.html#forgot">Et si j'oublie ?</a>

 ‣ <a href="https://mindwarriorgame.org/quick-start.fr.html">Guide de démarrage rapide</a>
 ‣ <a href="https://mindwarriorgame.org/faq.fr.html">FAQ</a>
 ‣ <a href="https://mindwarriorgame.org/privacy-policy.fr.html">Politique de confidentialité</a>

Appuyez sur le bouton ci-dessous pour commencer le jeu.""",

    menu_review = "💫️réviser la Formule",
    menu_pause = "⏸️ mettre le jeu en pause",
    menu_stats = "📊 progression du jeu",
    menu_formula = "️🧪mettre à jour la Formule",
    menu_difficulty = "💪changer la difficulté",
    menu_data = "💾 voir vos données brutes",
    menu_feedback = "📢 envoyer des commentaires",

    feedback_text = "Des questions, des suggestions ou des commentaires? "
                    "N'hésitez pas à créer un <a href=\"https://github.com/mindwarriorgame/mindwarrior-telegram-bot/issues\">problème GitHub</a> pour en discuter! 😉",

    help_command_start_playing_button = "Écrivez \"Formule\" et commencez à jouer ! 🏁",
    start_game_prompt="Veuillez appuyer sur le bouton ci-dessous pour entrer votre <i>Formule</i> et démarrer le jeu.",

    review_command_text = "Révisez votre <i> Formule</i> 💫\n"
                          "\n"
                          "<a href='https://mindwarriorgame.org/faq.fr#name.betterworld'>Appuyez sur un bouton ci-dessous</a> pour réviser votre <i>Formule</i>.",


    review_command_button_yourself="Améliore-toi 💪",
    review_command_button_world="Améliore le monde 🙌",

    review_command_success_text="<i>Formule</i> a été consultée 🎉\n"
                                "{maybe_achievement}"
                                "\n"
                                "Prochaine consultation avant {next_review}\n"
                                "\n"
                                " ‣ /pause - mettre le jeu en pause",

    review_since_last_time="Temps écoulé depuis la dernière consultation : {duration}",

    days_short="j",
    hours_short="h",
    minutes_short="m",
    seconds_short="s",

    difficulty_level_changed="Le niveau de difficulté a été modifié 💪\n"
                             "Le jeu a été redémarré en raison du changement de niveau de difficulté.\n"
                             "\n"
                             "<b>{old} -> {new}</b>\n"
                             "\n"
                             "🏆 Niveau : 1\n"
                             "⏳ Temps de jeu : 0j 0h 0m\n"
                             "\n"
                             "Prochaine consultation avant {next_review}\n",

    formula_changed="La <i>Formule</i> a été mise à jour!",

    difficulties=["Débutant", "Facile", "Moyen", "Difficile", "Expert"],

    review_paused_text="Le jeu est en pause",

    paused_command="Le jeu est en pause ⏸️\n"
                   "\n"
                   "Vous ne recevrez pas de rappels concernant votre <i>Formule</i>, "
                   "et le compteur de temps de jeu actif <a href=\"https://mindwarriorgame.org/faq.fr#pause\">est gelé</a>.\n"
                   "\n"
                   "Pour reprendre le jeu, "
                   "il vous suffit de revoir votre <i>Formule</i> en utilisant le bouton ci-dessous.",

    stats_command=("🏆 Niveau : {level}\n"
                   "⌛ Temps de jeu actif : {time}\n"
                   "💪 <a href=\"https://mindwarriorgame.org/faq.fr.html#difficulty\">Difficulté</a> : {difficulty} ({difficulty_details})\n"
                   "⏸️ <a href=\"https://mindwarriorgame.org/faq.fr.html#pause\">En pause ?</a> {paused}\n"
                   "❄️ Temps de <a href=\"https://mindwarriorgame.org/faq.fr.html#difficulty:~:text=sera%20récompensé%20(-,%22règle%20de%20refroidissement%22,-).\">refroidissement</a> avant la prochaine récompense : {cooldown}\n"
                   "⏰ Temps avant le prochain <a href=\"https://mindwarriorgame.org/faq.fr.html#forgot\">rappel</a> : {punishment}"),

    resumed="Le jeu est repris.",
    already_paused="Le jeu est déjà en pause ⏸️\n"
                   "\n"
                   "Pour reprendre le jeu, il vous suffit de revoir votre <i>Formule</i> avec le bouton ci-dessous.",
    game_started="Le jeu a commencé 🏁\n"
                 "{maybe_achievement}"
                 "\n"
                 "💪<a href=\"https://mindwarriorgame.org/faq.fr.html#difficulty\">Niveau de difficulté</a> : {difficulty}\n"
                 "\n"
                 "Revoir votre <i>Formule</i> avant {next_review}\n"
                 "\n"
                 " ‣ /difficulty - changer la difficulté",
    review_btn="Passez en revue votre \"Formule\" 💫",

    difficulty_command_text="Changer le niveau de difficulté💪\n"
                            "\n"
                            "Sélectionnez un nouveau <a href=\"https://mindwarriorgame.org/faq.fr.html#difficulty\">niveau de difficulté</a> en utilisant les boutons ci-dessous.\n"
                            "\n"
                            "<b>⚠️Cela réinitialisera votre progression dans le jeu !</b>\n",

    current_difficulty="niveau actuel",

    formula_command_text="Mettre à jour votre <i>Formule</i> 🧪\n"
                         "\n"
                         "Utilisez le bouton ci-dessous pour mettre à jour votre <i><a href=\"https://mindwarriorgame.org/faq.fr.html#formula\">Formule</a></i>.",
    formula_command_button="Mettre à jour la Formule 🧪",
    review_command_timeout="Délai expiré, veuillez réessayer.🤷",
    graph_header="Intervalles entre les revues (min)",
    graph_penalty_threshold="Seuil d'intervalle de révision : {difficulty_threshold_mins} min (difficulté={difficulty_str})",
    graph_mean_threshold="Médiane : {mean_mins} min",
    graph_xlabel="Temps",
    graph_ylabel="Intervalle entre les revues (min)",
    graph_xmax='Maintenant',
    graph_xmin='Il y a 6 jours',
    graph_paused="En pause",

    data_view="<a href=\"https://mindwarriorgame.org/privacy-policy.fr\">Nous respectons votre vie privée</a> et souhaitons traiter vos "
              "données de la manière la plus transparente possible. Ci-dessous, vous pouvez trouver toutes vos données "
              "que le jeu stocke sur son serveur:",
    data_view_localstorage_button="Voir les données du localStorage 🔎",
    data_delete_button="SUPPRIMER TOUTES LES DONNÉES ❌",

    data_deleted="Toutes vos données ont été supprimées. Veuillez effacer l'historique de discussion pour supprimer les données du chat Telegram.",

    reminder_text="N'oubliez pas de consulter votre <i>Formule</i> ! ⏰\n"
                  "\n"
                  "L'heure limite est dans 15 minutes, dépêchez-vous !\n"
                  "\n"
                  " ‣ /pause - mettre le jeu en pause",

    penalty_text = "Vous avez oublié de consulter votre <i>Formule</i> 🟥\n"
                   "{maybe_achievement}"
                   "\n"
                   " ‣ /pause - mettre le jeu en pause",

    badge_unhappy_cat = "😾 Oups ! Un chat grincheux s'est faufilé !\nAppuyez sur le bouton \"Voir les réussites\" ci-dessous.",
    badge_new = "🏆 Vous avez un nouvel accomplissement !\nAppuyez sur le bouton \"Voir les réussites\" ci-dessous.",
    view_badges_button = "Voir les réussites 🏆",
    locked_achievements = "⛔🏆😾 Un chat grincheux bloque de nouvelles réussites !",
    cooldown_msg="❄️ Les révisions anticipées ne sont pas récompensées.",

    kicking_out_grumpy_cat="🧹😾 Expulsion du chat grincheux...",
    grumpy_cat_kicked_out="🧹 Le chat grincheux a été expulsé !",
    remained_grumpy_cats="😾 Chats grincheux restants : {count}",
    achievements_unblocked="🏆 Les réussites sont débloquées !",
    achievements_link_regenerated="Le lien vers la page des réussites a été régénéré. Veuillez utiliser le bouton ci-dessous pour l'ouvrir.",

    autopause_on_msg = "Il est temps de dormir 💤\n"
                       "\n"
                       "Le jeu est automatiquement mis en pause jusqu'à {until_time}. Faites de beaux rêves! 🌙\n"
                       "\n"
                       " ‣ /sleep - configurer le planificateur de sommeil",

    autopause_resumed_msg = "Bonjour! ☀️\n"
                            "\n"
                            "Le jeu reprend. Passez une bonne journée! 🌞\n"
                            "\n"
                            " ‣ /sleep - configurer le planificateur de sommeil",

)


es = Lang(
    lang_code='es',
    lang_name='Español',

    help_command_text=f"""¡Hola, desconocido! 👋 ¡Bienvenido al bot del <a href="https://mindwarriorgame.org/faq.es.html">juego MindWarrior</a>! 🥷  

🧪 Crea tu "<a href="https://mindwarriorgame.org/faq.es.html#formula">Fórmula de Firme Resolución</a>", un mensaje inspirador para ti mismo.

💫 <a href="https://mindwarriorgame.org/faq.es.html#review">Revísala</a> a lo largo del día para mantenerte motivado y ganar recompensas. <a href="https://mindwarriorgame.org/faq.es.html#forgot">¿Qué pasa si olvido?</a>

 ‣ <a href="https://mindwarriorgame.org/quick-start.es.html">Guía rápida</a>
 ‣ <a href="https://mindwarriorgame.org/faq.es.html">Preguntas frecuentes</a>
 ‣ <a href="https://mindwarriorgame.org/privacy-policy.es.html">Política de privacidad</a>

Presiona el botón de abajo para comenzar el juego.""",

    menu_review="💫️revisar Fórmula",
    menu_pause="⏸️ pausar el juego",
    menu_stats="📊 progreso del juego",
    menu_formula="🧪actualizar Fórmula",
    menu_difficulty="💪cambiar dificultad",
    menu_data="💾 ver tus datos sin procesar",
    menu_feedback = "📢 enviar comentarios",

    feedback_text = "¿Tienes preguntas, sugerencias o comentarios?"
                    "¡No dudes en plantear un <a href=\"https://github.com/mindwarriorgame/mindwarrior-telegram-bot/issues\">problema de GitHub</a> para discutirlo! 😉",

    help_command_start_playing_button="¡Escribe \"Fórmula\" y comienza a jugar! 🏁",
    start_game_prompt="Por favor, presiona el botón de abajo para ingresar tu <i>Fórmula</i> y comenzar el juego.",

    review_command_text="Revisa tu <i>Fórmula</i> 💫\n"
                        "\n"
                        "<a href='https://mindwarriorgame.org/faq.es#name.betterworld'>Presiona cualquier botón de abajo</a> para revisar tu <i>Fórmula</i>.",

    review_command_button_yourself="Mejora a ti mismo 💪",
    review_command_button_world="Mejora el mundo 🙌",

    review_command_success_text="<i>Fórmula</i> ha sido revisada 🎉\n"
                                "{maybe_achievement}"
                                "\n"
                                "Próxima revisión antes de {next_review}\n"
                                "\n"
                                " ‣ /pause - pausar el juego",

    review_since_last_time="Tiempo desde la última revisión: {duration}",

    days_short="d",
    hours_short="h",
    minutes_short="m",
    seconds_short="s",

    difficulty_level_changed="El nivel de dificultad ha cambiado 💪\n"
                             "El juego se reinició debido al cambio de nivel de dificultad.\n"
                             "\n"
                             "<b>{old} -> {new}</b>\n"
                             "\n"
                             "🏆 Nivel: 1\n"
                             "⏳ Tiempo de juego: 0d 0h 0m\n"
                             "\n"
                             "Próxima revisión antes de {next_review}\n",

    formula_changed="La <i>Fórmula</i> ha sido actualizada!",

    difficulties=["Principiante", "Fácil", "Intermedio", "Difícil", "Experto"],

    review_paused_text="El juego está en pausa",

    paused_command="El juego está en pausa ⏸️\n"
                   "\n"
                   "No recibirás recordatorios sobre tu <i>Fórmula</i>, "
                   "y el contador de tiempo de juego activo <a href=\"https://mindwarriorgame.org/faq.es#pause\">está congelado</a>.\n"
                   "\n"
                   "Para reanudar el juego, "
                   "simplemente revisa tu <i>Fórmula</i> usando el botón de abajo.",

    stats_command=("🏆 Nivel: {level}\n"
                   "⌛ Tiempo de juego activo: {time}\n"
                   "💪 <a href=\"https://mindwarriorgame.org/faq.es.html#difficulty\">Dificultad</a>: {difficulty} ({difficulty_details})\n"
                   "⏸️ <a href=\"https://mindwarriorgame.org/faq.es.html#pause\">¿Pausado?</a> {paused}\n"
                   "❄️ <a href=\"https://mindwarriorgame.org/faq.es.html#difficulty:~:text=will%20be%20rewarded%20(-,%22cool%2Ddown%22%20rule,-).\">Tiempo de espera</a> antes de la próxima recompensa: {cooldown}\n"
                   "⏰ Tiempo antes del próximo <a href=\"https://mindwarriorgame.org/faq.es.html#forgot\">recordatorio</a>: {punishment}"),

    resumed="El juego se ha reanudado.",
    already_paused="El juego ya está en pausa ⏸️\n"
                   "\n"
                   "Para reanudar el juego, simplemente revisa tu <i>Fórmula</i> con el botón de abajo.",
    game_started="El juego ha comenzado 🏁\n"
                 "{maybe_achievement}"
                 "\n"
                 "💪<a href=\"https://mindwarriorgame.org/faq.es.html#difficulty\">Nivel de dificultad</a>: {difficulty}\n"
                 "\n"
                 "Revisa tu <i>Fórmula</i> antes de {next_review}\n"
                 "\n"
                 " ‣ /difficulty - cambiar la dificultad",

    review_btn="Revisa tu \"Fórmula\" 💫",

    difficulty_command_text="Cambiar el nivel de dificultad💪\n"
                            "\n"
                            "Selecciona un nuevo <a href=\"https://mindwarriorgame.org/faq.es.html#difficulty\">nivel de dificultad</a> usando los botones de abajo.\n"
                            "\n"
                            "<b>⚠️¡Esto reiniciará tu progreso en el juego!</b>\n",

    current_difficulty="nivel actual",

    formula_command_text="Actualiza tu <i>Fórmula</i> 🧪\n"
                         "\n"
                         "Usa el botón de abajo para actualizar tu <i><a href=\"https://mindwarriorgame.org/faq.es.html#formula\">Fórmula</a></i>.",
    formula_command_button="Actualiza tu Fórmula 🧪",
    review_command_timeout="Tiempo de espera agotado, por favor intenta de nuevo.🤷",
    graph_header="Intervalos entre revisiones (minutos)",
    graph_penalty_threshold="Umbral de intervalo de revisión: {difficulty_threshold_mins} minutos (dificultad={difficulty_str})",
    graph_mean_threshold="Mediana: {mean_mins} minutos",
    graph_xlabel="Tiempo",
    graph_ylabel="Intervalo entre revisiones (minutos)",
    graph_xmax='Ahora',

    graph_xmin='hace 6 días',
    graph_paused="Pausado",

    data_view="<a href=\"https://mindwarriorgame.org/privacy-policy.es\">Respetamos tu privacidad</a> y queremos tratar tus "
              "datos de la manera más transparente posible. A continuación, puedes encontrar todos los datos que "
              "el juego almacena en su servidor:",

    data_view_localstorage_button="Ver datos de localStorage 🔎",
    data_delete_button="ELIMINAR TODOS LOS DATOS ❌",
    data_deleted="Todos tus datos han sido eliminados. Por favor, limpia el historial de chat para eliminar los datos del chat de Telegram.",

    reminder_text="¡No olvides revisar tu <i>Fórmula</i>! ⏰\n"
                  "\n"
                  "La hora de revisión es en 15 minutos, ¡apúrate!\n"
                  "\n"
                  " ‣ /pause - pausar el juego",

    penalty_text = "Olvidaste revisar tu <i>Fórmula</i> 🟥\n"
                   "{maybe_achievement}"
                   "\n"
                   " ‣ /pause - pausar el juego",

    badge_unhappy_cat = "😾 ¡Ups! ¡Un gato gruñón se coló!\nPresiona el botón \"Ver logros\" abajo.",
    badge_new = "🏆 ¡Tienes un nuevo logro!\nPresiona el botón \"Ver logros\" abajo.",
    view_badges_button = "Ver logros 🏆",
    locked_achievements = "⛔🏆😾 ¡Un gato gruñón bloquea nuevos logros!",
    cooldown_msg="❄️ Las revisiones tempranas no se recompensan.",

    kicking_out_grumpy_cat="🧹😾 Expulsando al gato gruñón...",
    grumpy_cat_kicked_out="🧹 ¡El gato gruñón ha sido expulsado!",
    remained_grumpy_cats="😾 Gatos gruñones restantes: {count}",
    achievements_unblocked="🏆 ¡Logros desbloqueados!",
    achievements_link_regenerated="El enlace a la página de logros ha sido regenerado. Por favor, usa el botón de abajo para abrirlo.",

    autopause_on_msg = "Hora de dormir 💤\n"
                       "\n"
                       "El juego se pausa automáticamente hasta {until_time}. ¡Dulces sueños! 🌙\n"
                       "\n"
                       " ‣ /sleep - configurar el programador de sueño",

    autopause_resumed_msg = "¡Buenos días! ☀️\n"
                            "\n"
                            "El juego se reanuda. ¡Que tengas un buen día! 🌞\n"
                            "\n"
                            " ‣ /sleep - configurar el programador de sueño",

)



en = Lang(
    lang_code='en',
    lang_name='English',
    help_command_text=f"""Hey, stranger! 👋 Welcome to <a href="https://mindwarriorgame.org/faq.en.html">MindWarrior game</a> bot! 🥷  

🧪 Craft your "<a href="https://mindwarriorgame.org/faq.en.html#formula">Formula of Firm Resolution</a>", an inspirational message to yourself.

💫 <a href="https://mindwarriorgame.org/faq.en.html#review">Review it</a> throughout your day to stay motivated, and earn rewards! <a href="https://mindwarriorgame.org/faq.en.html#forgot">What if I forget?</a>

 ‣ <a href="https://mindwarriorgame.org/quick-start.en.html">Quick-start guide</a>
 ‣ <a href="https://mindwarriorgame.org/faq.en.html">FAQs</a>
 ‣ <a href="https://mindwarriorgame.org/privacy-policy.en.html">Privacy policy</a>

Press the button below to start the game.""",

    menu_review="💫️review Formula",
    menu_pause="⏸️ pause the game",
    menu_stats="📊 game progress",
    menu_formula="️🧪update Formula",
    menu_difficulty="💪change difficulty",
    menu_data = "💾 view your raw data",
    menu_feedback = "📢 send feedback",

    feedback_text = "Questions, suggestions, or feedback? "
                    "Please feel free to raise a <a href=\"https://github.com/mindwarriorgame/mindwarrior-telegram-bot/issues\">GitHub issue</a> to discuss! 😉",

    help_command_start_playing_button="Write \"Formula\" and start playing! 🏁",

    start_game_prompt="Please press the button below to enter your <i>Formula</i> and start the game.",

    review_command_text="Review your <i> Formula</i> 💫\n"
                        "\n"
                        "<a href='https://mindwarriorgame.org/faq.en#name.betterworld'>Press any button below</a> to review your <i>Formula</i>.",

    review_command_button_yourself="Improve yourself 💪",
    review_command_button_world="Improve the world 🙌",

    review_command_success_text="<i>Formula</i> has been reviewed 🎉\n"
                                "{maybe_achievement}"
                                "\n"
                                "Next review before {next_review}\n"
                                "\n"
                                " ‣ /pause - pause the game",


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
                             "🏆 Level: 1\n"
                             "⏳ Play time: 0d 0h 0m\n"
                             "\n"
                             "Next review before {next_review}\n",

    formula_changed="The <i>Formula</i> has been updated!",

    difficulties=["Beginner", "Easy", "Medium", "Hard", "Expert"],

    review_paused_text="The game is paused",

    paused_command="The game is paused ⏸️\n"
                   "\n"
                   "You will not be receiving reminders about your <i>Formula</i>, "
                   "and the active play time counter <a href=\"https://mindwarriorgame.org/faq.en#pause\">are frozen</a>.\n"
                   "\n"
                   "To resume the game, "
                   "simply review your <i>Formula</i> using the button below.",

    stats_command=("🏆 Level : {level}\n"
                   "⌛ Active play time: {time}\n"
                   "💪 <a href=\"https://mindwarriorgame.org/faq.en.html#difficulty\">Difficulty</a>: {difficulty} ({difficulty_details})\n"
                   "⏸️ <a href=\"https://mindwarriorgame.org/faq.en.html#pause\">Paused?</a> {paused}\n"
                   "❄️ <a href=\"https://mindwarriorgame.org/faq.en.html#difficulty:~:text=will%20be%20rewarded%20(-,%22cool%2Ddown%22%20rule,-).\">Cool-down</a> time before next reward: {cooldown}\n"
                   "⏰ Time before next <a href=\"https://mindwarriorgame.org/faq.en.html#forgot\">reminder</a>: {punishment}"),

    resumed="The game is resumed.",
    already_paused="The game is already paused ⏸️\n"
                   "\n"
                   "To resume the game, simply review your <i>Formula</i> with the button below.",
    game_started="The game has started 🏁\n"
                 "{maybe_achievement}"
                 "\n"
                 "💪<a href=\"https://mindwarriorgame.org/faq.en.html#difficulty\">Difficulty level</a>: {difficulty}\n"
                 "\n"
                 "Review your <i>Formula</i> before {next_review}\n"
                 "\n"
                 " ‣ /difficulty - change the difficulty",

    review_btn="Review your \"Formula\" 💫",

    difficulty_command_text="Change the difficulty level💪\n"
                            "\n"
                            "Select a new <a href=\"https://mindwarriorgame.org/faq.en.html#difficulty\">difficulty level</a> using the buttons below.\n"
                            "\n"
                            "<b>⚠️This will reset your game progress!</b>\n",

    current_difficulty="current level",

    formula_command_text="Update your <i>Formula</i> 🧪\n"
                         "\n"
                         "Use the button below to update your <i><a href=\"https://mindwarriorgame.org/faq.en.html#formula\">Formula</a></i>.",
    formula_command_button="Update your Formula 🧪",
    review_command_timeout="Timeout, please try again.🤷",
    graph_header="Intervals between review (mins)",
    graph_penalty_threshold="Review interval threshold: {difficulty_threshold_mins} mins (difficulty={difficulty_str})",
    graph_mean_threshold="Median: {mean_mins} mins",
    graph_xlabel="Time",
    graph_ylabel="Interval between reviews (mins)",
    graph_xmax='Now',
    graph_xmin='6 days ago',
    graph_paused="Paused",

    data_view="<a href=\"https://mindwarriorgame.org/privacy-policy.en\">We respect your privacy</a> and want to treat your "
              "data as transparent as possible. Below you can find all your data that "
              "the game stores on its server:",
    data_view_localstorage_button="View localStorage data 🔎",
    data_delete_button="DELETE ALL DATA ❌",
    data_deleted="All your data has been deleted. Please clear the chat history to remove the data from Telegram chat.",

    reminder_text="Don't forget to review your <i>Formula</i>! ⏰\n"
                  "\n"
                  "The due time is in 15 minutes, hurry up!\n"
                  "\n"
                  " ‣ /pause - pause the game",

    penalty_text = "You forgot to review your <i>Formula</i> 🟥\n"
                   "{maybe_achievement}"
                   "\n"
                   " ‣ /pause - pause the game",

    badge_unhappy_cat = "😾 Oops! A grumpy cat sneaked in!\nPress \"View achievements\" button below.",
    badge_new = "🏆 You've got a new achievement!\nPress \"View achievements\" button below.",
    view_badges_button = "View achievements 🏆",
    locked_achievements = "⛔🏆😾 A grumpy cat is blocking new achievements!",
    cooldown_msg="❄️ Early reviews are not rewarded.",

    kicking_out_grumpy_cat="🧹😾 Kicking out the grumpy cat...",
    grumpy_cat_kicked_out="🧹 The grumpy cat has been kicked out!",
    remained_grumpy_cats="😾 Grumpy cats remaining: {count}",
    achievements_unblocked="🏆 Achievements are unlocked!",
    achievements_link_regenerated="The link to the achievements page has been regenerated. Please use the button below to open it.",

    autopause_on_msg = "Time to sleep 💤\n"
                       "\n"
                       "The game is automatically paused until {until_time}. Sweet dreams! 🌙\n"
                       "\n"
                       " ‣ /sleep - configure sleep scheduler",

    autopause_resumed_msg = "Good morning! ☀️\n"
                            "\n"        
                            "The game is resumed. Have a great day! 🌞\n"
                            "\n"    
                            " ‣ /sleep - configure sleep scheduler",
)

de = Lang(
    lang_code='de',
    lang_name='Deutsch',

    help_command_text=f"""Hey, Fremder! 👋 Willkommen beim <a href="https://mindwarriorgame.org/faq.de.html">MindWarrior-Spiel</a> Bot! 🥷  

🧪 Erstelle deine "<a href="https://mindwarriorgame.org/faq.de.html#formula">Formel der festen Entschlossenheit</a>", eine inspirierende Nachricht an dich selbst.

💫 <a href="https://mindwarriorgame.org/faq.de.html#review">Überprüfe sie</a> im Laufe des Tages, um motiviert zu bleiben und Belohnungen zu verdienen! <a href="https://mindwarriorgame.org/faq.de.html#forgot">Was, wenn ich es vergesse?</a>

 ‣ <a href="https://mindwarriorgame.org/quick-start.de.html">Schnellstart-Anleitung</a>
 ‣ <a href="https://mindwarriorgame.org/faq.de.html">Häufige Fragen</a>
 ‣ <a href="https://mindwarriorgame.org/privacy-policy.de.html">Datenschutzerklärung</a>

Drücke den Button unten, um das Spiel zu starten.""",

    menu_review="💫️Formel überprüfen",
    menu_pause="⏸️ Spiel pausieren",
    menu_stats="📊 Spielfortschritt",
    menu_formula="️🧪Formel aktualisieren",
    menu_difficulty="💪Schwierigkeitsgrad ändern",
    menu_data = "💾 Rohdaten anzeigen",
    menu_feedback = "📢 Feedback senden",

    feedback_text = "Fragen, Vorschläge oder Feedback? "
                    "Bitte melden Sie gerne ein <a href=\"https://github.com/mindwarriorgame/mindwarrior-telegram-bot/issues\">GitHub-Problem</a> zur Diskussion! 😉",

    help_command_start_playing_button="Schreibe \"Formel\" und starte das Spiel! 🏁",
    start_game_prompt="Bitte drücken Sie die Schaltfläche unten, um Ihre <i>Formel</i> einzugeben und das Spiel zu starten.",

    review_command_text="Überprüfe deine <i>Formel</i> 💫\n"
                        "\n"
                        "<a href='https://mindwarriorgame.org/faq.de#name.betterworld'>Drücke einen Button unten</a>, um deine <i>Formel</i> zu überprüfen.",

    review_command_button_yourself="Verbessere dich selbst 💪",
    review_command_button_world="Verbessere die Welt 🙌",

    review_command_success_text="<i>Formel</i> wurde überprüft 🎉\n"
                                "{maybe_achievement}"
                                "\n"
                                "Nächste Überprüfung vor {next_review}\n"
                                "\n"
                                " ‣ /pause - Spiel pausieren",


    review_since_last_time="Zeit seit der letzten Überprüfung: {duration}",

    days_short="T",
    hours_short="h",
    minutes_short="m",
    seconds_short="s",

    difficulty_level_changed="Der Schwierigkeitsgrad wurde geändert 💪\n"
                             "Das Spiel wurde aufgrund der Änderung des Schwierigkeitsgrads neu gestartet.\n"
                             "\n"
                             "<b>{old} -> {new}</b>\n"
                             "\n"
                             "🏆 Level: 1\n"
                             "⏳ Spielzeit: 0d 0h 0m\n"
                             "\n"
                             "Nächste Überprüfung vor {next_review}\n",

    formula_changed="Die <i>Formel</i> wurde aktualisiert!",

    difficulties=["Anfänger", "Einfach", "Mittel", "Schwer", "Experte"],

    review_paused_text="Das Spiel ist pausiert",

    paused_command="Das Spiel ist pausiert ⏸️\n"
                   "\n"
                   "Du wirst keine Erinnerungen an deine <i>Formel</i> erhalten, "
                   "und der aktive Spielzeit-Zähler <a href=\"https://mindwarriorgame.org/faq.de.html#pause\">ist eingefroren</a>.\n"
                   "\n"
                   "Um das Spiel fortzusetzen, "
                   "überprüfe einfach deine <i>Formel</i> mit dem Button unten.",

    stats_command=("🏆 Level : {level}\n"
                   "⌛ Aktive Spielzeit: {time}\n"
                   "💪 <a href=\"https://mindwarriorgame.org/faq.de.html#difficulty\">Schwierigkeitsgrad</a>: {difficulty} ({difficulty_details})\n"
                   "⏸️ <a href=\"https://mindwarriorgame.org/faq.de.html#pause\">Pausiert?</a> {paused}\n"
                   "❄️ <a href=\"https://mindwarriorgame.org/faq.de.html#difficulty:~:text=will%20be%20rewarded%20(-,%22cool%2Ddown%22%20rule,-).\">Abkühlzeit</a> vor der nächsten Belohnung: {cooldown}\n"
                   "⏰ Zeit bis zur nächsten <a href=\"https://mindwarriorgame.org/faq.de.html#forgot\">Erinnerung</a>: {punishment}"),

    resumed="Das Spiel wurde fortgesetzt.",
    already_paused="Das Spiel ist bereits pausiert ⏸️\n"
                   "\n"
                   "Um das Spiel fortzusetzen, überprüfe einfach deine <i>Formel</i> mit dem Button unten.",
    game_started="Das Spiel hat begonnen 🏁\n"
                 "{maybe_achievement}"
                 "\n"
                 "💪<a href=\"https://mindwarriorgame.org/faq.de.html#difficulty\">Schwierigkeitsgrad</a>: {difficulty}\n"
                 "\n"
                 "Überprüfe deine <i>Formel</i> vor {next_review}\n"
                 "\n"
                 " ‣ /difficulty - ändere den Schwierigkeitsgrad",
    review_btn="Überprüfe deine \"Formel\" 💫",

    difficulty_command_text="Ändere den Schwierigkeitsgrad💪\n"
                            "\n"
                            "Wähle einen neuen <a href=\"https://mindwarriorgame.org/faq.de.html#difficulty\">Schwierigkeitsgrad</a> mit den untenstehenden Buttons aus.\n"
                            "\n"
                            "<b>⚠️Dies setzt deinen Spielfortschritt zurück!</b>\n",

    current_difficulty="aktueller Level",

    formula_command_text="Aktualisiere deine <i>Formel</i> 🧪\n"
                         "\n"
                         "Verwende den untenstehenden Button, um deine <i><a href=\"https://mindwarriorgame.org/faq.de.html#formula\">Formel</a></i> zu aktualisieren.",
    formula_command_button="Aktualisiere deine Formel 🧪",
    review_command_timeout="Zeitüberschreitung, bitte versuche es erneut.🤷",
    graph_header="Intervalle zwischen den Überprüfungen (Minuten)",
    graph_penalty_threshold="Schwellenwert für das Überprüfungsintervall: {difficulty_threshold_mins} Minuten (Schwierigkeitsgrad={difficulty_str})",
    graph_mean_threshold="Median: {mean_mins} Minuten",
    graph_xlabel="Zeit",
    graph_ylabel="Intervall zwischen den Überprüfungen (Minuten)",
    graph_xmax='Jetzt',
    graph_xmin='Vor 6 Tagen',
    graph_paused="Pausiert",

    data_view = "<a href=\"https://mindwarriorgame.org/privacy-policy.de\">Wir respektieren Ihre Privatsphäre</a> "
                "und möchten Ihre Daten so transparent wie möglich behandeln. Unten finden Sie alle Daten, die das "
                "Spiel auf seinem Server speichert:",

    data_view_localstorage_button="Sieh dir die localStorage-Daten an 🔎",
    data_delete_button="ALLE DATEN LÖSCHEN ❌",
    data_deleted="Alle deine Daten wurden gelöscht. Bitte lösche den Chatverlauf, um die Daten aus dem Telegram-Chat zu entfernen.",

    reminder_text="Vergiss nicht, deine <i>Formel</i> zu überprüfen! ⏰\n"
                  "\n"
                  "Die Fälligkeitszeit ist in 15 Minuten, beeile dich!\n"
                  "\n"
                  " ‣ /pause - Spiel pausieren",

    penalty_text = "Du hast vergessen, deine <i>Formel</i> zu überprüfen 🟥\n"
                   "{maybe_achievement}"
                   "\n"
                   " ‣ /pause - Spiel pausieren",

    badge_unhappy_cat = "😾 Ups! Eine grimmige Katze hat sich eingeschlichen!\nDrücke den Button \"Erfolge ansehen\" unten.",
    badge_new = "🏆 Du hast einen neuen Erfolg erzielt!\nDrücke den Button \"Erfolge ansehen\" unten.",
    view_badges_button = "Erfolge ansehen 🏆",
    locked_achievements = "⛔🏆😾 Eine grimmige Katze blockiert neue Erfolge!",
    cooldown_msg="❄️ Frühe Überprüfungen werden nicht belohnt.",

    kicking_out_grumpy_cat="🧹😾 Die grimmige Katze wird hinausgeworfen...",
    grumpy_cat_kicked_out="🧹 Die grimmige Katze wurde hinausgeworfen!",
    remained_grumpy_cats="😾 Verbliebene grimmige Katzen: {count}",
    achievements_unblocked="🏆 Erfolge wurden freigeschaltet!",
    achievements_link_regenerated="Der Link zur Erfolgsseite wurde neu generiert. Bitte benutze den Button unten, um ihn zu öffnen.",

    autopause_on_msg = "Zeit zum Schlafen 💤\n"
                       "\n"
                       "Das Spiel wird automatisch bis {until_time} pausiert. Süße Träume! 🌙\n"
                       "\n"
                       " ‣ /sleep - Schlafplaner konfigurieren",

    autopause_resumed_msg = "Guten Morgen! ☀️\n"
                            "\n"
                            "Das Spiel wird fortgesetzt. Hab einen schönen Tag! 🌞\n"
                            "\n"
                            " ‣ /sleep - Schlafplaner konfigurieren",

)



ru = Lang(
    lang_code='ru',
    lang_name='Русский',
    help_command_text=f"""👋 Приветствуем тебя, о, Cтранник! Добро пожаловать в игру <a href="https://mindwarriorgame.org/faq.ru.html">MindWarrior</a>! 🥷  

🧪 Создай свою "<a href="https://mindwarriorgame.org/faq.ru.html#formula">Формулу Твердой Решимости</a>", мотивирующее послание самому себе.

💫 <a href="https://mindwarriorgame.org/faq.ru.html#review">Просматривай ее</a> в течение дня, поддерживай мотивацию и фокус, зарабатывай награды! <a href="https://mindwarriorgame.org/faq.ru.html#forgot">Что будет, если я забуду?</a>

 ‣ <a href="https://mindwarriorgame.org/quick-start.ru.html">Краткое руководство</a>
 ‣ <a href="https://mindwarriorgame.org/faq.ru.html">Вопросы и ответы</a>
 ‣ <a href="https://mindwarriorgame.org/privacy-policy.ru.html">Политика конфиденциальности</a>

Нажмите кнопку ниже, чтобы начать игру.""",

    menu_review="💫️просмотреть Формулу",
    menu_pause="⏸️ поставить игру на паузу",
    menu_stats="📊 статистика игры",
    menu_formula="🧪 изменить Формулу",
    menu_difficulty="💪 изменить сложность",
    menu_data = "💾 просмотреть свои данные",
    menu_feedback = "📢 обратная связь",

    feedback_text = "Вопросы? Предложения? Обратная связь? "
                    "Давайте обсудим это в <a href=\"https://github.com/mindwarriorgame/mindwarrior-telegram-bot/issues\">GitHub-е</a>! 😉",


    help_command_start_playing_button="Написать \"Формулу\" и начать игру! 🏁",
    start_game_prompt="Нажмите на кнопку ниже для ввода <i>Формулы</i> и начала игры.",

    review_command_text="Просмотрите свою <i>Формулу</i> 💫\n"
                        "\n"
                        "<a href='https://mindwarriorgame.org/faq.ru#name.betterworld'>Нажмите любую кнопку ниже</a>, чтобы просмотреть свою <i>Формулу</i>.",

    review_command_button_yourself="Улучшить себя 💪",
    review_command_button_world="Улучшить мир 🙌",

    review_command_success_text="<i>Формула</i> просмотрена 🎉\n"
                                "{maybe_achievement}"
                                "\n"
                                "Следующий просмотр не позже {next_review}\n"
                                "\n"
                                " ‣ /pause - игру на паузу",


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
                             "🏆 Уровень: 1\n"
                             "⏳ Время игры: 0d 0h 0m\n"
                             "\n"
                             "Следующий просмотр не позже {next_review}\n",

    formula_changed="<i>Формула</i> обновлена!",

    difficulties=["Новичок", "Легко", "Средне", "Сложно", "Эксперт"],

    review_paused_text="Игра на паузе",

    paused_command="Игра на паузе ⏸️\n"
                   "\n"
                   "Напоминания о просмотрах <i>Формулы</i> и счетчик "
                   "времени активной игры <a href=\"https://mindwarriorgame.org/faq.ru#pause\">остановлены</a>.\n"
                   "\n"
                   "Для снятия с паузы просмотрите свою <i>Формулу</i> с помощью кнопки ниже.",

    stats_command=("🏆 Уровень: {level}\n"
                   "⌛ Время активной игры: {time}\n"
                   "💪 <a href=\"https://mindwarriorgame.org/faq.ru.html#difficulty\">Сложность игры</a>: {difficulty} ({difficulty_details})\n"
                   "⏸️ <a href=\"https://mindwarriorgame.org/faq.ru.html#pause\">На паузе?</a> {paused}\n"
                   "❄️ <a href=\"https://mindwarriorgame.org/faq.ru.html#difficulty:~:text=will%20be%20rewarded%20(-,%22cool%2Ddown%22%20rule,-).\">Время до следующей награды</a>: {cooldown}\n"
                   "⏰ Время до <a href=\"https://mindwarriorgame.org/faq.ru.html#forgot\">напоминания</a>: {punishment}"),
    resumed="Игра снята с паузы.",
    already_paused="Игра уже на паузе ⏸️\n"
                   "\n"
                   "Чтобы продолжить игру, просмотрите свою <i>Формулу</i> с помощью кнопки ниже.",

    game_started="Игра начата 🏁\n"
                 "{maybe_achievement}"
                 "\n"
                 "💪<a href=\"https://mindwarriorgame.org/faq.ru.html#difficulty\">Уровень сложности</a>: {difficulty}\n"
                 "\n"
                 "Просмотрите свою <i>Формулу</i> не позже {next_review}\n"
                 "\n"
                 " ‣ /difficulty - изменить сложность",

    review_btn="Просмотреть свою \"Формулу\" 💫",

    difficulty_command_text="Изменить сложность 💪\n"
                            "\n"
                            "Выберите новый <a href=\"https://mindwarriorgame.org/faq.ru.html#difficulty\">уровень сложности</a>.\n"
                            "\n"
                            "<b>⚠️Это обнулит ваш игровой прогресс!</b>",

    current_difficulty="текущий уровень",

    formula_command_text="️Обновите свою <i>Формулу</i> 🧪\n"
                         "\n"
                         "Используйте кнопку ниже, чтобы обновить свою <i><a href=\"https://mindwarriorgame.org/faq.ru.html#formula\">Формулу</a></i>.",

    formula_command_button="Обновить Формулу 🧪",
    review_command_timeout="Таймаут, попробуйте еще раз.🤷",
    graph_header="Время между просмотрами (мин)",
    graph_penalty_threshold="Штрафной порог: {difficulty_threshold_mins} мин (сложность={difficulty_str})",
    graph_mean_threshold="Медиана: {mean_mins} мин",
    graph_xlabel="Время",
    graph_ylabel="Интервал между просмотрами (мин)",
    graph_xmax='Сейчас',
    graph_xmin='6 дней назад',
    graph_paused="Пауза",

    data_view="<a href=\"https://mindwarriorgame.org/privacy-policy.ru\">Мы уважаем вашу конфиденциальность</a> и "
              "стремимся максимально прозрачно обрабатывать ваши данные. Ниже вы можете найти все ваши данные, "
              "которые игра хранит на своем сервере:",
    data_view_localstorage_button="Посмотреть данные localStorage 🔎",
    data_delete_button="УДАЛИТЬ ВСЕ ДАННЫЕ ❌",
    data_deleted="Все ваши данные удалены. Пожалуйста, удалите историю чата, чтобы удалить данные из Telegram-а.",

    reminder_text="Не забудьте просмотреть свою <i>Формулу</i>! ⏰\n"
                  "\n"
                  "Время истекает через 15 минут, поторопитесь!\n"
                  "\n"
                  " ‣ /pause - игру на паузу",

    penalty_text = "Вы забыли вовремя просмотреть свою <i>Формулу</i> 🟥\n"
                   "{maybe_achievement}"
                   "\n"
                   " ‣ /pause - игру на паузу",

    badge_unhappy_cat = "😾 Ой! Похоже, к вам забрался недовольный кот!\nНажмите кнопку \"Посмотреть достижения\" снизу.",
    badge_new = "🏆 Вы получили новое достижение\nНажмите кнопку \"Посмотреть достижения\" снизу.",
    view_badges_button = "Посмотреть достижения 🏆",
    locked_achievements = "⛔🏆😾 Недовольный кот блокирует достижения!",
    cooldown_msg="❄️ Слишком частые просмотры не вознаграждаются.",

    kicking_out_grumpy_cat="🧹😾 Выгоняем недовольного кота...",
    grumpy_cat_kicked_out="🧹 Вы выгнали недовольного кота!",
    remained_grumpy_cats="😾 Осталось недовольных котов: {count}",
    achievements_unblocked="🏆 Достижения разблокированы!",
    achievements_link_regenerated="Ссылка на страницу с достижениями обновлена. Нажмите на кнопку ниже, чтобы открыть ее.",

    autopause_on_msg = "Пора спать 💤\n"
                       "\n"
                       "Игра автоматически поставлена на паузу до {until_time}. Сладких снов! 🌙\n"
                       "\n"
                       " ‣ /sleep - настроить планировщик сна",

    autopause_resumed_msg = "Доброе утро! ☀️\n"
                            "\n"
                            "Игра возобновлена. Хорошего дня! 🌞\n"
                            "\n"
                            " ‣ /sleep - настроить планировщик сна",
)


class LangProvider:

    @staticmethod
    def get_available_languages() -> dict[str, Lang]:
        return {
            en.lang_code: en,
            ru.lang_code: ru,
            fr.lang_code: fr,
            de.lang_code: de,
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
