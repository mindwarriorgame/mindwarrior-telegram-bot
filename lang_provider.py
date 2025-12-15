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
    menu_sleep: str
    menu_stats: str
    menu_shop: str
    menu_formula: str
    menu_difficulty: str
    menu_data: str
    menu_feedback: str
    menu_settings: str

    settings_title: str

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
    diamond_new: str
    view_badges_button: str
    locked_achievements: str
    cooldown_msg: str

    kicking_out_grumpy_cat: str
    grumpy_cat_kicked_out: str
    remained_grumpy_cats: str
    achievements_unblocked: str
    achievements_link_regenerated: str

    kick_grumpy_cat_for_diamonds: str
    buy_next_achievement_for_diamonds: str

    autopause_on_msg: str
    autopause_resumed_msg: str

    pause_prompt: str
    autopause_prompt: str

    sleep_command_button: str
    sleep_command_text: str

    sleep_config_updated: str

    shop_description: str
    shop_button_kick_grumpy_cat: str
    shop_button_next_achivement: str

    shop_no_enough_diamonds: str
    shop_diamonds_left: str
    shop_no_grumpy_cat: str
    shop_button_buy_repeller: str

    menu_change_server: str

    change_server_descr: str
    change_server_done: str
    change_server_current: str

    you_have_grumpy_cat_repeller: str
    you_already_have_grumpy_cat_repeller: str
    you_used_grumpy_cat_repeller: str
    congrats_you_have_repeller: str

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

    menu_review = "💫️ réviser la Formule",
    menu_pause = "⏸️ mettre le jeu en pause",
    menu_stats = "📊 progression du jeu",
    menu_shop = "🛍️ boutique",
    menu_formula = "️🧪 mettre à jour la Formule",
    menu_settings="🔧 paramètres",

    settings_title='Veuillez utiliser les boutons ci-dessous pour configurer le jeu 🔧',

    menu_sleep="💤 Planificateur de sommeil",
    menu_difficulty="💪 Difficulté du jeu",
    menu_data = "💾 Données personnelles",
    menu_feedback = "📢 Commentaires",

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
                                "{pause_prompt}",

    pause_prompt = " ‣ /pause - mettre le jeu en pause",
    autopause_prompt=" ‣ /settings - configurer le planificateur de sommeil",

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
                   "💎 Diamants disponibles : {diamonds}, dépensés : {spent_diamonds}\n"
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
                  "{pause_prompt}",

    penalty_text = "Vous avez oublié de consulter votre <i>Formule</i> 🟥\n"
                   "{maybe_achievement}"
                   "\n"
                   "{pause_prompt}",

    badge_unhappy_cat = "😾 Oups ! Un chat grincheux s'est faufilé !",
    badge_new = "🏆 Vous avez un nouvel accomplissement !",
    diamond_new = "💎 Vous avez reçu un diamant ! 💎 {count} (+1)",
    view_badges_button = "Voir les réussites 🏆",
    locked_achievements = "⛔🏆😾 Un chat grincheux bloque de nouvelles réussites !",
    cooldown_msg="❄️ Les révisions anticipées ne sont pas récompensées.",

    kicking_out_grumpy_cat="🧹😾 Expulsion du chat grincheux...",
    grumpy_cat_kicked_out="🧹 Le chat grincheux a été expulsé !",
    remained_grumpy_cats="😾 Chats grincheux restants : {count}",
    achievements_unblocked="🏆 Les réussites sont débloquées !",
    achievements_link_regenerated="Le lien vers la page des réussites a été régénéré. Veuillez utiliser le bouton ci-dessous pour l'ouvrir.",

    kick_grumpy_cat_for_diamonds="Chasse le chat grincheux pour 💎 {diamonds} /shop",
    buy_next_achievement_for_diamonds="Achète le prochain succès pour 💎 {diamonds} /shop",

    autopause_on_msg = "Il est temps de dormir 💤\n"
                       "\n"
                       "Le jeu est automatiquement mis en pause jusqu'à {until_time}. Faites de beaux rêves! 🌙\n"
                       "\n"
                       " ‣ /settings - configurer le planificateur de sommeil",

    autopause_resumed_msg = "Bonjour! ☀️\n"
                            "\n"
                            "Le jeu reprend. Passez une bonne journée! 🌞\n"
                            "\n"
                            " ‣ /settings - configurer le planificateur de sommeil",

    sleep_command_text="Configurer le planificateur de sommeil 💤\n"
                       "\n"
                       "Appuyez sur le bouton ci-dessous pour configurer votre heure de sommeil. Le jeu sera automatiquement mis en pause pendant cette période.\n"
                       "\n"
                       "Activé? {is_enabled}\n"
                       "Heure de sommeil: {bed_time} - {wakeup_time}\n",

    sleep_command_button="Configurer le planificateur de sommeil 💤",
    sleep_config_updated="La configuration du sommeil a été mise à jour 💤\n"
                         "\n"
                         "Activé? {is_enabled}\n"
                         "Heure de sommeil: {bed_time} - {wakeup_time}\n",
    shop_description = "Bienvenue dans la boutique 🛍️ !\n" \
        "\n" \
        "Dépensez vos diamants durement gagnés pour :\n" \
        "\n"
        " ‣ 🧹😾 Chasser le chat grincheux — maintenant !\n" \
        " ‣ 🏆 Débloquer instantanément le prochain succès\n" \
        " ‣ 🧄 Répulsif à chat à usage unique : bloque la prochaine attaque du chat grincheux et met le jeu en pause.\n" \
        "\n" \
        "Votre solde : 💎 {diamonds}",

    shop_button_kick_grumpy_cat = "🧹😾 Chasser le chat : -💎 {price}",
    shop_button_next_achivement = "🏆 Obtenir un succès : -💎 {price}",
    shop_button_buy_repeller = "🧄 Acheter le répulsif à chat : -💎 {price}",

    shop_no_enough_diamonds = "🚫 Pas assez de diamants pour l'achat",
    shop_diamonds_left = "Diamants restants : 💎 {diamonds}",
    shop_no_grumpy_cat = "🤷 Aucun chat grincheux à chasser",

    you_have_grumpy_cat_repeller = "Vous avez le répulsif 🧄",
    you_already_have_grumpy_cat_repeller = "Vous avez déjà le répulsif 🧄",
    you_used_grumpy_cat_repeller = "🧄😾 Répulsif activé — le chat s'est enfui ! Le jeu est en pause ⏸️\n" \
            "Consultez <i>Formule</i> pour reprendre.",
    congrats_you_have_repeller = "Félicitations ! Tu as maintenant le répulsif 🧄",
    
    menu_change_server = "🌐 Changer de serveur",

    change_server_descr = (
        "🌐 Sélectionnez le serveur de jeu.\n"
        "\n"
        "⚠️ Changer de serveur modifiera également le domaine web de la mini-application. "
        "Votre <i>Formule</i> est stockée dans le localStorage de votre navigateur selon le domaine, "
        "vous devrez donc peut-être restaurer votre ancienne <i>Formule</i> à partir d’une sauvegarde.\n"
        "\n"
        "Par sécurité, copiez votre <i>Formule</i> (« Copy ») avant de changer de serveur, puis allez sur /formula "
        "et collez-la (« Paste ») après le changement."
    ),

    change_server_done = "Le serveur a été changé.",

    change_server_current = "serveur actuel"

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

    menu_review="💫️ revisar Fórmula",
    menu_pause="⏸️ pausar el juego",
    menu_stats="📊 progreso del juego",
    menu_shop="🛍️ comercio",
    menu_formula="🧪 actualizar Fórmula",
    menu_settings="🔧 ajustes",

    settings_title='Utiliza los botones a continuación para configurar el juego 🔧',

    menu_sleep="💤 Planificador de sueño",
    menu_difficulty="💪 Dificultad del juego",
    menu_data = "💾 Datos personales",
    menu_feedback = "📢 Comentarios",

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
                                "{pause_prompt}",
    pause_prompt=" ‣ /pause - pausar el juego",
    autopause_prompt = " ‣ /settings - configurar el programador de sueño",

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
                   "💎 Diamantes disponibles: {diamonds}, gastados: {spent_diamonds}\n"
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
                  "{pause_prompt}",

    penalty_text = "Olvidaste revisar tu <i>Fórmula</i> 🟥\n"
                   "{maybe_achievement}"
                   "\n"
                   "{pause_prompt}",

    badge_unhappy_cat = "😾 ¡Ups! ¡Un gato gruñón se coló!",
    badge_new = "🏆 ¡Tienes un nuevo logro!",
    diamond_new = "💎 ¡Has recibido un diamante! 💎 {count} (+1)",
    view_badges_button = "Ver logros 🏆",
    locked_achievements = "⛔🏆😾 ¡Un gato gruñón bloquea nuevos logros!",
    cooldown_msg="❄️ Las revisiones tempranas no se recompensan.",

    kicking_out_grumpy_cat="🧹😾 Expulsando al gato gruñón...",
    grumpy_cat_kicked_out="🧹 ¡El gato gruñón ha sido expulsado!",
    remained_grumpy_cats="😾 Gatos gruñones restantes: {count}",
    achievements_unblocked="🏆 ¡Logros desbloqueados!",
    achievements_link_regenerated="El enlace a la página de logros ha sido regenerado. Por favor, usa el botón de abajo para abrirlo.",

    kick_grumpy_cat_for_diamonds="Espanta al gato gruñón por 💎 {diamonds} /shop",
    buy_next_achievement_for_diamonds="Compra el siguiente logro por 💎 {diamonds} /shop",

    autopause_on_msg = "Hora de dormir 💤\n"
                       "\n"
                       "El juego se pausa automáticamente hasta {until_time}. ¡Dulces sueños! 🌙\n"
                       "\n"
                       " ‣ /settings - configurar el programador de sueño",

    autopause_resumed_msg = "¡Buenos días! ☀️\n"
                            "\n"
                            "El juego se reanuda. ¡Que tengas un buen día! 🌞\n"
                            "\n"
                            " ‣ /settings - configurar el programador de sueño",

    sleep_command_text="Configurar el programador de sueño 💤\n"
                        "\n"
                        "Presiona el botón de abajo para configurar tu hora de dormir. El juego se pausará automáticamente durante este tiempo.\n"
                        "\n"    
                        "Activado? {is_enabled}\n"
                        "Hora de dormir: {bed_time} - {wakeup_time}\n",

    sleep_command_button="Configurar el programador de sueño 💤",
    sleep_config_updated="La configuración de sueño ha sido actualizada 💤\n"
                         "\n"
                         "Activado? {is_enabled}\n"
                         "Hora de dormir: {bed_time} - {wakeup_time}\n",
    shop_description = "¡Bienvenido a la tienda 🛍️!\n" \
        "\n" \
        "Gasta tus diamantes ganados con esfuerzo en:\n" \
        "\n"
        " ‣ 🧹😾 ¡Ahuyenta al gato gruñón — ahora!\n" \
        " ‣ 🏆 Desbloquea al instante el siguiente logro\n" \
        " ‣ 🧄 Repelente de gato de un solo uso: bloquea el próximo ataque del gato gruñón y pone el juego en pausa.\n" \
        "\n" \
        "Tu saldo: 💎 {diamonds}",

    shop_button_kick_grumpy_cat = "🧹😾 Echar al gato: -💎 {price}",
    shop_button_next_achivement = "🏆 Conseguir un logro: -💎 {price}",
    shop_button_buy_repeller = "🧄 Comprar repelente de gato: -💎 {price}",

    shop_no_enough_diamonds = "🚫 No hay suficientes diamantes para la compra",
    shop_diamonds_left = "Diamantes restantes: 💎 {diamonds}",
    shop_no_grumpy_cat = "🤷 No hay gato gruñón que espantar",

    you_have_grumpy_cat_repeller = "Tienes el repelente 🧄",
    you_already_have_grumpy_cat_repeller = "Ya tienes el repelente 🧄",
    you_used_grumpy_cat_repeller = "🧄😾 Repelente activado — ¡el gato salió corriendo! El juego está en pausa ⏸️\n" \
            "Revisa <i>Fórmula</i> para reanudar.",
    congrats_you_have_repeller = "¡Felicidades! Ahora tienes el repelente 🧄",

    menu_change_server = "🌐 Cambiar servidor",

    change_server_descr = (
        "🌐 Selecciona el servidor del juego.\n"
        "\n"
        "⚠️ Al cambiar de servidor también cambiará el dominio web de la mini app. "
        "Tu <i>Fórmula</i> se guarda en el localStorage del navegador por dominio, "
        "así que puede que tengas que restaurar tu antigua <i>Fórmula</i> desde una copia de seguridad.\n"
        "\n"
        "Para estar seguro, copia tu <i>Fórmula</i> («Copy») antes de cambiar de servidor; luego ve a /formula "
        "y pégala allí («Paste») después del cambio."
    ),

    change_server_done = "El servidor se ha cambiado.",

    change_server_current = "servidor actual"

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

    menu_review="💫️ review Formula",
    menu_pause="⏸️ pause the game",
    menu_stats="📊 game progress",
    menu_shop = "🛍️ shop",
    menu_formula="️🧪 update Formula",
    menu_settings="🔧 settings",

    settings_title='Please use the buttons below to configure the game 🔧',

    menu_sleep="💤 Sleep Scheduler",
    menu_difficulty="💪 Game Difficulty",
    menu_data = "💾 Personal Data",
    menu_feedback = "📢 Feedback",

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
                                "{pause_prompt}",

    pause_prompt = " ‣ /pause - pause the game",
    autopause_prompt=" ‣ /settings - configure sleep scheduler",


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
                   "💎 Diamonds available: {diamonds}, spent: {spent_diamonds}\n"
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
                  "{pause_prompt}",

    penalty_text = "You forgot to review your <i>Formula</i> 🟥\n"
                   "{maybe_achievement}"
                   "\n"
                   "{pause_prompt}",

    badge_unhappy_cat = "😾 Oops! A grumpy cat sneaked in!",
    badge_new = "🏆 You've got a new achievement!",
    diamond_new = "💎 You've got a new diamond! 💎 {count} (+1)", 
    view_badges_button = "View achievements 🏆",
    locked_achievements = "⛔🏆😾 A grumpy cat is blocking new achievements!",
    cooldown_msg="❄️ Early reviews are not rewarded.",

    kicking_out_grumpy_cat="🧹😾 Kicking out the grumpy cat...",
    grumpy_cat_kicked_out="🧹 The grumpy cat has been kicked out!",
    remained_grumpy_cats="😾 Grumpy cats remaining: {count}",
    achievements_unblocked="🏆 Achievements are unlocked!",
    achievements_link_regenerated="The link to the achievements page has been regenerated. Please use the button below to open it.",

    kick_grumpy_cat_for_diamonds="Shoo the grumpy cat for 💎 {diamonds} /shop",
    buy_next_achievement_for_diamonds="Buy next achievement for 💎 {diamonds} /shop",
    
    autopause_on_msg = "Time to sleep 💤\n"
                       "\n"
                       "The game is automatically paused until {until_time}. Sweet dreams! 🌙\n"
                       "\n"
                       " ‣ /settings - configure sleep scheduler",

    autopause_resumed_msg = "Good morning! ☀️\n"
                            "\n"        
                            "The game is resumed. Have a great day! 🌞\n"
                            "\n"    
                            " ‣ /settings - configure sleep scheduler",

    sleep_command_text="Configure sleep scheduler 💤\n"
                         "\n"
                         "Press the button below to set up your sleep time. The game will be automatically paused for this period, daily.\n"
                         "\n"
                         "Enabled? {is_enabled}\n"
                         "Sleep time: {bed_time} - {wakeup_time}\n",

    sleep_command_button="Configure sleep scheduler 💤",

    sleep_config_updated="Sleep scheduler has been updated 💤\n"
                         "\n"
                         "Enabled? {is_enabled}\n"
                         "Sleep time: {bed_time} - {wakeup_time}\n",
    shop_description = "Welcome to the shop 🛍️!\n"
        "\n"
        "Spend your hard-earned diamonds on:\n"
        "\n"
        " ‣ 🧹😾 Shoo the grumpy cat away — now!\n"
        " ‣ 🏆 Instantly unlock the next achievement\n"
        " ‣ 🧄 One-time cat repeller: blocks the next grumpy cat attack and pauses the game.\n"
        "\n"
        "Your balance: 💎 {diamonds}",

    shop_button_kick_grumpy_cat = "🧹😾 Shoo the cat away: -💎 {price}",
    shop_button_next_achivement = "🏆 Get an achievement: -💎 {price}",
    shop_button_buy_repeller = "🧄 Buy cat repeller: -💎 {price}",

    shop_no_enough_diamonds = "🚫 Not enough diamonds for the purchase",
    shop_diamonds_left = "Diamonds left: 💎 {diamonds}",
    shop_no_grumpy_cat = "🤷 No grumpy cat to shoo",

    you_have_grumpy_cat_repeller = "You have the repeller 🧄",
    you_already_have_grumpy_cat_repeller = "You already have the repeller 🧄",
    you_used_grumpy_cat_repeller = "🧄😾 Repeller activated — the cat ran away! The game is paused ⏸️\n" \
        "Review your <i>Formula</i> to resume.",
    congrats_you_have_repeller = "Congratulations! Now you have the repeller 🧄",
    menu_change_server = "🌐 Change server",

    change_server_descr = (
        "🌐 Select the game server.\n"
        "\n"
        "⚠️ Changing the server will also change the mini app's web domain. "
        "Your <i>Formula</i> is stored in your browser's localStorage per domain, "
        "so you might need to restore your old <i>Formula</i> from a backup.\n"
        "\n"
        "To be safe, copy your <i>Formula</i> (\"Copy\") before switching the server, then go to /formula "
        "and paste it (\"Paste\") there after the switch."
    ),

    change_server_done="The server has been changed.",

    change_server_current = "current server"
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

    menu_review="💫️ Formel überprüfen",
    menu_pause="⏸️ Spiel pausieren",
    menu_stats="📊 Spielfortschritt",
    menu_shop = "🛍️ Geschäft",
    menu_formula="️🧪 Formel aktualisieren",
    menu_settings = "🔧 Einstellungen",

    menu_sleep="💤 Schlafplaner",
    menu_difficulty="💪 Spielschwierigkeit",
    menu_data = "💾 Persönliche Daten",
    menu_feedback = "📢 Feedback",

    settings_title='Bitte verwenden Sie die untenstehenden Schaltflächen, um das Spiel zu konfigurieren 🔧',

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
                                "{pause_prompt}",

    pause_prompt = " ‣ /pause - Spiel pausieren",
    autopause_prompt=" ‣ /settings - Schlafplaner konfigurieren",


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
                   "💎 Diamanten verfügbar: {diamonds}, ausgegeben: {spent_diamonds}\n"
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
                  "{pause_prompt}",

    penalty_text = "Du hast vergessen, deine <i>Formel</i> zu überprüfen 🟥\n"
                   "{maybe_achievement}"
                   "\n"
                   "{pause_prompt}",

    badge_unhappy_cat = "😾 Ups! Eine grimmige Katze hat sich eingeschlichen!",
    badge_new = "🏆 Du hast einen neuen Erfolg erzielt!",
    diamond_new = "💎 Du hast einen Diamanten erhalten! 💎 {count}",
    view_badges_button = "Erfolge ansehen 🏆",
    locked_achievements = "⛔🏆😾 Eine grimmige Katze blockiert neue Erfolge!",
    cooldown_msg="❄️ Frühe Überprüfungen werden nicht belohnt.",

    kicking_out_grumpy_cat="🧹😾 Die grimmige Katze wird hinausgeworfen...",
    grumpy_cat_kicked_out="🧹 Die grimmige Katze wurde hinausgeworfen!",
    remained_grumpy_cats="😾 Verbliebene grimmige Katzen: {count}",
    achievements_unblocked="🏆 Erfolge wurden freigeschaltet!",
    achievements_link_regenerated="Der Link zur Erfolgsseite wurde neu generiert. Bitte benutze den Button unten, um ihn zu öffnen.",

    kick_grumpy_cat_for_diamonds="Verjage die mürrische Katze für 💎 {diamonds} /shop",
    buy_next_achievement_for_diamonds="Kaufe den nächsten Erfolg für 💎 {diamonds} /shop",

    autopause_on_msg = "Zeit zum Schlafen 💤\n"
                       "\n"
                       "Das Spiel wird automatisch bis {until_time} pausiert. Süße Träume! 🌙\n"
                       "\n"
                       " ‣ /settings - Schlafplaner konfigurieren",

    autopause_resumed_msg = "Guten Morgen! ☀️\n"
                            "\n"
                            "Das Spiel wird fortgesetzt. Hab einen schönen Tag! 🌞\n"
                            "\n"
                            " ‣ /settings - Schlafplaner konfigurieren",

    sleep_command_text="Schlafplaner konfigurieren 💤\n"
                        "\n"
                        "Drücke den Button unten, um deine Schlafenszeit einzustellen. Das Spiel wird automatisch für diesen Zeitraum pausiert.\n"
                        "\n"    
                        "Aktiviert? {is_enabled}\n" 
                        "Schlafenszeit: {bed_time} - {wakeup_time}\n",

    sleep_command_button="Schlafplaner konfigurieren 💤",

    sleep_config_updated="Der Schlafplaner wurde aktualisiert 💤\n"
                         "\n"
                         "Aktiviert? {is_enabled}\n"
                         "Schlafenszeit: {bed_time} - {wakeup_time}\n",
    shop_description = "Willkommen im Shop 🛍️!\n" \
        "\n" \
        "Gib deine hart verdienten Diamanten aus für:\n" \
        "\n"
        " ‣ 🧹😾 Verjage die grummelige Katze — sofort!\n" \
        " ‣ 🏆 Schalte sofort die nächste Errungenschaft frei\n" \
        " ‣ 🧄 Einmaliger Katzen-Abwehrer: blockiert den nächsten Angriff der grummeligen Katze und pausiert das Spiel.\n" \
        "\n" \
        "Dein Kontostand: 💎 {diamonds}",

    shop_button_kick_grumpy_cat = "🧹😾 Katze verjagen: -💎 {price}",
    shop_button_next_achivement = "🏆 Erfolg freischalten: -💎 {price}",
    shop_button_buy_repeller = "🧄 Katzen-Abwehrer kaufen: -💎 {price}",

    shop_no_enough_diamonds = "🚫 Nicht genug Diamanten für den Kauf",
    shop_diamonds_left = "Verbleibende Diamanten: 💎 {diamonds}",
    shop_no_grumpy_cat = "🤷 Keine mürrische Katze zum Wegscheuchen",

    you_have_grumpy_cat_repeller = "Du hast den Abwehrer 🧄",
    you_already_have_grumpy_cat_repeller = "Du hast den Abwehrer bereits 🧄",
    you_used_grumpy_cat_repeller = "🧄😾 Abwehrer aktiviert — die Katze ist abgehauen! Das Spiel ist pausiert ⏸️\n" \
            "Sieh dir <i>Formel</i> an, um fortzufahren.",
    congrats_you_have_repeller = "Herzlichen Glückwunsch! Jetzt hast du den Abwehrer 🧄",
    
    menu_change_server = "🌐 Server wechseln",

    change_server_descr = (
        "🌐 Wähle den Spielserver aus.\n"
        "\n"
        "⚠️ Beim Wechsel des Servers ändert sich auch die Web-Domain der Mini-App. "
        "Deine <i>Formel</i> wird im localStorage deines Browsers pro Domain gespeichert, "
        "daher musst du deine alte <i>Formel</i> eventuell aus einem Backup wiederherstellen.\n"
        "\n"
        "Zur Sicherheit kopiere deine <i>Formel</i> („Copy“), bevor du den Server wechselst, wechsle dann zu /formula "
        "und füge sie dort („Paste“) nach dem Wechsel wieder ein."
    ),

    change_server_done = "Der Server wurde geändert.",

    change_server_current = "aktueller Server"

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

    menu_review="💫️ просмотреть Формулу",
    menu_pause="⏸️ поставить игру на паузу",
    menu_stats="📊 статистика игры",
    menu_shop="🛍️ магазин",
    menu_formula="🧪 изменить Формулу",

    menu_settings = "🔧 настройки",
    settings_title='Используйте кнопки ниже, чтобы настроить игру 🔧',

    menu_sleep="💤 Планировщик сна",
    menu_difficulty="💪 Сложность игры",
    menu_data = "💾 Личные данные",
    menu_feedback = "📢 Обратная связь",

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
                                "{pause_prompt}",

    pause_prompt = " ‣ /pause - игру на паузу",
    autopause_prompt=" ‣ /settings - настроить планировщик сна",


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
                   "💎 Алмазов доступно: {diamonds}, потрачено: {spent_diamonds}\n"
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
                  "{pause_prompt}",

    penalty_text = "Вы забыли вовремя просмотреть свою <i>Формулу</i> 🟥\n"
                   "{maybe_achievement}"
                   "\n"
                   "{pause_prompt}",

    badge_unhappy_cat = "😾 Ой! Похоже, к вам забрался недовольный кот!",
    badge_new = "🏆 Вы получили новое достижение!",
    diamond_new = "💎 Вы получили алмаз! 💎 {count} (+1)",
    view_badges_button = "Посмотреть достижения 🏆",
    locked_achievements = "⛔🏆😾 Недовольный кот блокирует достижения!",
    cooldown_msg="❄️ Слишком частые просмотры не вознаграждаются.",

    kicking_out_grumpy_cat="🧹😾 Выгоняем недовольного кота...",
    grumpy_cat_kicked_out="🧹 Вы выгнали недовольного кота!",
    remained_grumpy_cats="😾 Осталось недовольных котов: {count}",
    achievements_unblocked="🏆 Достижения разблокированы!",
    achievements_link_regenerated="Ссылка на страницу с достижениями обновлена. Нажмите на кнопку ниже, чтобы открыть ее.",

    kick_grumpy_cat_for_diamonds="Прогнать сердитого кота за 💎 {diamonds} /shop",
    buy_next_achievement_for_diamonds="Купить следующее достижение за 💎 {diamonds} /shop",

    autopause_on_msg = "Пора спать 💤\n"
                       "\n"
                       "Игра автоматически поставлена на паузу до {until_time}. Сладких снов! 🌙\n"
                       "\n"
                       " ‣ /settings - настроить планировщик сна",

    autopause_resumed_msg = "Доброе утро! ☀️\n"
                            "\n"
                            "Игра возобновлена. Хорошего дня! 🌞\n"
                            "\n"
                            " ‣ /settings - настроить планировщик сна",

    sleep_command_text="Настроить планировщик сна 💤\n"
                        "\n"
                        "Нажмите на кнопку ниже, чтобы установить время вашего сна. Игра будет автоматически ставиться на паузу на этот промежуток времени.\n"
                        "\n"
                        "Включено? {is_enabled}\n"  
                        "Время сна: {bed_time} - {wakeup_time}\n",
    sleep_command_button = "Настроить планировщик сна 💤",
    sleep_config_updated="Настройки планировщика сна обновлены 💤\n"
                         "\n"
                         "Включено? {is_enabled}\n"
                         "Время сна: {bed_time} - {wakeup_time}\n",
    
    shop_description = "Добро пожаловать в магазин 🛍️!\n" \
        "\n" \
        "Здесь вы можете потратить свои алмазы на:\n" \
        "\n"
        " ‣ 🧹😾 Прогнать недовольного кота — прямо сейчас!\n" \
        " ‣ 🏆 Мгновенно открыть следующее достижение\n" \
        " ‣ 🧄 Одноразовый отпугиватель кота: блокирует очередную атаку недовольного кота и ставит игру на паузу.\n" \
        "\n" \
        "Ваш баланс: 💎 {diamonds}",

    shop_button_kick_grumpy_cat="🧹😾 Прогнать кота: -💎 {price}",
    shop_button_next_achivement="🏆 Получить достижение: -💎 {price}",
    shop_button_buy_repeller = "🧄 Купить отпугиватель кота: -💎 {price}",

    shop_no_enough_diamonds = "🚫 Недостаточно алмазов для покупки",
    shop_diamonds_left = "Осталось алмазов: 💎 {diamonds}",
    shop_no_grumpy_cat = "🤷 Нет сердитого кота, которого можно прогнать",

    you_have_grumpy_cat_repeller = "У вас есть отпугиватель 🧄",
    you_already_have_grumpy_cat_repeller = "У вас уже есть отпугиватель 🧄",
    you_used_grumpy_cat_repeller = "🧄😾 Отпугиватель активирован — кот убежал! Игра на паузе ⏸️\n" \
            "Просмотрите <i>Формулу</i>, чтобы продолжить.",
    congrats_you_have_repeller = "Поздравляем! Теперь у вас есть отпугиватель 🧄",

    menu_change_server = "🌐 Сменить сервер",

    change_server_descr = (
        "🌐 Выберите игровой сервер.\n"
        "\n"
        "⚠️ При смене сервера также изменится веб-домен мини-приложения. "
        "Ваша <i>Формула</i> хранится в localStorage браузера отдельно для каждого домена, "
        "поэтому, возможно, вам придётся восстановить старую <i>Формулу</i> из резервной копии.\n"
        "\n"
        "На всякий случай скопируйте <i>Формулу</i> («Copy») перед сменой сервера, затем перейдите на /formula "
        "и нажмите вставьте ее («Paste») после переключения."
    ),

    change_server_done = "Сервер изменён.",

    change_server_current = "текущий сервер"


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
