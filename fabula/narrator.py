"""The narrator. It turns the fabula into a syuzhet.

Nothing here invents anything. The narrator reads the event log, picks
the threads worth telling (reversals, betrayals, reconciliations) and
renders them with templates. If the chronicle says the tale had grown
in the telling, it is because the simulation recorded the distortion.
"""

import random

from .model import TICKS_PER_SEASON, season_index, year_of
from .names import VILLAGE_NAMES

ARC_KINDS = {"GIFT", "REFUSAL", "OFFENSE", "QUARREL", "MEDIATION",
             "REPAYMENT", "INGRATITUDE", "RESENTMENT", "BOND", "WIDOWING"}

TEXT = {
    "en": {
        "seasons": ("spring", "summer", "autumn", "winter"),
        "traits": {
            "diligence": ("tireless", "idle"),
            "generosity": ("open-handed", "tight-fisted"),
            "pride": ("proud", "humble"),
            "openness": ("talkative", "reserved"),
        },
        "intro": ["{name} was {adjs}.",
                  "{name}, {adjs}, was known to everyone."],
        "and": "and",
        "opening": ["It began in {season}.",
                    "The first anyone knew of it was in {season}."],
        "later_season": ["{season} came.", "By then it was {season}."],
        "soon_after": ["Not many days passed.", "Soon afterwards."],
        "GIFT": ["When {b}'s stores ran low, {a} filled the basket without being asked.",
                 "{a} shared bread with {b} in a lean stretch, and it was not forgotten."],
        "REFUSAL": ["{a} went hungry to {b}'s door and came back with nothing.",
                    "{b} turned {a} away empty-handed, and the whole village felt colder for it."],
        "OFFENSE": ["Word reached {a} that {b} had been speaking of the matter behind closed doors.",
                    "Someone let {a} know what {b} had been saying."],
        "QUARREL": ["{a} and {b} quarreled where everyone could hear, and the village pretended not to listen.",
                    "It came to hard words between {a} and {b}, in the open street."],
        "MEDIATION": ["{c} sat them both at one table and would not let either leave angry. Something loosened.",
                      "It took {c}, whom they both trusted, to make them speak again."],
        "REPAYMENT": ["{a} had not forgotten the old kindness, and when want came to {b}'s house, it was returned without a word about it.",
                      "The bread {b} once gave came back to {b}'s own door, and it was {a} who carried it."],
        "INGRATITUDE": ["{a} had once filled {b}'s basket; when {a}'s own ran empty, {b}'s door stayed shut. The village keeps accounts no ledger ever sees, and that one was entered in every head in it.",
                        "{b} owed {a} the kind of debt nobody writes down, and paid it with a closed door. Nobody said anything. Everybody counted it."],
        "RESENTMENT": ["The favor sat heavy on {a}. It is a hard thing to owe, and {a} took to avoiding {b}'s eye.",
                       "{a} had never returned what {b} once gave, and the owing curdled, the way gratitude does when it is carried too long."],
        "BOND": ["{a} and {b} chose each other before the season turned. The village knew before either of them said a word about it.",
                 "What had grown between {a} and {b} became something declared. They shared bread and hearth after that."],
        "WIDOWING": ["{a} outlived {b}. The village did not leave {a} alone with it, which is how grief is carried in a place like that.",
                     "When {b} died, {a} lost more than a person loses when what remains is only loneliness."],
        "carried_by": " It was {c} who carried the tale.",
        "grown": " The tale had grown in the telling.",
        "repeat_one": "It happened once more after that.",
        "repeat_many": "It happened {n} more times after that, as if grudges kept a calendar of their own.",
        "repeat_good_one": "And it happened again, quietly, when it was needed.",
        "repeat_good_many": "And it happened {n} more times, without anyone making a fuss of it; kindness keeps a calendar too.",
        "repeat_endless": "And so it went on, season after season, until counting lost its point.",
        "repeat_good_endless": "And so it went on, season after season; some things do not need remarking to continue.",
        "seasons_later": [
            "Some seasons passed. By the time {season} came, the matter had not been resolved.",
            "When {season} came again, the story had not ended.",
        ],
        "year_later": "A year went by. By {season} nothing had been resolved.",
        "years_later": "{n} years had passed. By {season} the village was still carrying it.",
        "repeat_quarrel_one": "They fought again, as if the first time had been practice.",
        "repeat_quarrel_many": "They fought {n} more times. It never seemed to settle anything.",
        "repeat_quarrel_endless": "And so the fighting went on, season after season; some things need a witness more than a resolution.",
        "repeat_refusal_one": "The door stayed shut one more time.",
        "repeat_refusal_many": "The door stayed shut {n} more times. The village counted each one.",
        "repeat_gift_one": "The bread came again, without a word about it.",
        "repeat_gift_many": "The bread came {n} more times, without ceremony; that is what makes it bread.",
        "close_relapse": "The peace that was made did not keep; some cracks want to stay open.",
        "close_broken": "No one mended it. By the end they passed each other without a word.",
        "close_uneasy": "An uneasy peace held between them, thin as spring ice.",
        "close_mended": "Whatever had been broken, they mended it better than new.",
        "close_warm": "They were lucky in each other, and they knew it.",
        "close_widowed": "They had been lucky in each other. The ending was a sad one, but it was a sadness the village recognized.",
        "close_departed": "Before the record closed, {a} was gone — pushed out by a coldness the village never quite named.",
        "close_departed_bonded": "What {a} and their partner built did not survive the village's coldness. {a} left; the bond did not outlast the leaving.",
        "title_reconciliation": "{a} and {b}: a reconciliation",
        "title_estrangement": "{a} and {b}: an estrangement",
        "title_feud": "{a} and {b}: a feud",
        "title_bond": "{a} and {b}: a friendship",
        "title_love": "{a} and {b}: a love",
        "title_open": "{a} and {b}: an unfinished business",
        "title_debt": "{a} and {b}: a debt unpaid",
        "chronicle_title": ["The Chronicle of {village}",
                            "A Record of {village}",
                            "What Happened in {village}"],
        "arrivals_note_1_named": "{name} came to {village} as someone the village did not know yet. The village is always uncertain what to make of someone with no history here.",
        "prologue": [("{village} held {n} souls at the opening of this record, "
                      "and it covers {days} days of them. "
                      "Nothing in it was invented; it was only watched, and told."),
                     ("This is the record of {village}, which held {n} people at its opening. "
                      "It covers {days} of their days. "
                      "None of it was made up."),
                    ],
        "epilogue": [("When the record ends, {a} and {b} were as close as two people get in {village}; "
                      "{c} and {d} still were not speaking."),
                     ("In the end, {a} and {b} were still finding reasons to cross each other's paths "
                      "in {village}. {c} and {d} were still finding reasons not to."),
                    ],
        "pride_note": "{count} times, someone in {village} went hungry rather than ask for help. Pride is its own kind of famine.",
        "debt_note": "When the record closes, {count} favors in {village} had still not been returned. The village kept those accounts in no book, which is why none of them were ever lost.",
        "deaths_note_1": "One soul in {village} did not live through these years. A village carries its dead quietly, which is how the dead end up carrying the village.",
        "deaths_note_n": "{count} souls in {village} did not live through these years. A village carries its dead quietly, which is how the dead end up carrying the village.",
        "arrivals_note_1": "One stranger came to {village} in this time. The village is always uncertain what to make of someone with no history.",
        "arrivals_note_n": "{count} strangers came to {village} in this time. The village is always uncertain what to make of someone with no history.",
        "bonds_note_1": "One bond was made in {village} in this time. Most lasting things begin without anyone marking the moment.",
        "bonds_note_n": "{count} bonds were made in {village} in this time. Most lasting things begin without anyone marking the moment.",
        "births_note_1": "One child was born in {village} in this time.",
        "births_note_n": "{count} children were born in {village} in this time.",
        "growth_note": "By the close of this record, {village} counted more souls than it had at the opening.",
        "famine_note": "Year {year} was a year of hunger in {village}.",
        "birth_intro": ["{name}, who grew up here, was {adjs}.",
                        "{name} had been raised in {village} and was {adjs}."],
        "refusal_pride": [
            "Pride is its own kind of famine.",
            "Some people would rather suffer than be seen to suffer.",
        ],
        "gift_unexpected": [
            "Generosity is not always a matter of character.",
            "Even tight fists open, sometimes.",
        ],
        "MEDIATION_elder": [
            "It fell to {c} — who had seen enough winters to know how grudges end — to sit them at one table. Something mended.",
            "{c}, who had been in the village long enough to remember the last time this had happened, made them speak. Something loosened.",
        ],
        "died_starvation": "{a} did not outlive this chronicle. A long winter took them before the account closed.",
        "died_misfortune": "{a} did not outlive this chronicle; a sudden blow, when there was nothing left to absorb it.",
        "died_old_age": [
            "{a} did not outlive this chronicle. They had lived in {village} long enough to be part of its memory; then they became only that.",
            "{a} lived a long life in {village} and the village changed around them several times over. A different kind of ending from the others.",
        ],
        "died_leaving": "They left behind {names}.",
        "BIRTH": [
            "A child — {c} — came to them. There are things that arrive without ceremony and are felt for years.",
            "{c} was born. The village received them the way it always receives what arrives without asking.",
        ],
        "COMING_OF_AGE": "{c} grew up. The village counted one more among its own.",
        "elder_intro": [
            "{name}, who had been here longest and remembered what others had forgotten, was {adjs}.",
            "Everyone had come to {name} at least once. {name} was {adjs}.",
        ],
        "QUARREL_private": [
            "{a} and {b} had it out where no one could hear. By morning the village knew anyway.",
            "Whatever passed between {a} and {b} passed without witnesses. Private fights have a way of lasting longer.",
        ],
        "winter_later": [
            "Winter came back, and with it the old matter came back too.",
            "Another winter settled in. The cold version of everything returned.",
        ],
        "dead_section": "## After",
        "legacy_generous": [
            "{name} was the most open-handed soul {village} had. The village was colder for the absence.",
            "{name} had never turned anyone away empty-handed. That kind of person is not replaced; they are noticed as gone.",
        ],
        "legacy_proud": [
            "{name} went with accounts settled. The proud do not like leaving debts behind.",
            "{name} had kept everything balanced to the last. A complicated kind of person to lose.",
        ],
        "legacy_diligent": [
            "{name} had worked harder than anyone. What {name} kept running was invisible until it stopped.",
            "The fields {name} tended were the best-kept in {village}. That kind of knowledge does not write itself down.",
        ],
        "legacy_mediator": [
            "{name} had sat more quarreling neighbors at the same table than anyone. The village felt the absence the way a room feels it when its peacemaker is gone.",
            "People had gone to {name} with things they could not say elsewhere. After, there was no one quite like that.",
        ],
        "legacy_bonded": [
            "{name} had made a life with {partner} in {village}. That bond became part of the village's story too.",
            "What {name} built here — the years, the bond with {partner} — outlasted them. It tends to.",
        ],
        "legacy_newcomer": [
            "{name} arrived without a history in {village} and left with one. That is what belonging looks like.",
            "{name} came from outside and became part of the place anyway. The village carries that kind quietly.",
        ],
        "legacy_quiet": [
            "{name} did not leave a loud mark. The quiet ones rarely do, but the place shifts when they go.",
            "{name} was part of the background that makes a place feel inhabited. The silence afterward was specific.",
        ],
        "legacy_long_life": [
            "{name} had lived in {village} long enough to remember things no one else could. That kind of witness is not replaced; it is lost.",
            "The years {name} spent in {village} outlasted several versions of the place. When they went, something the village had known about itself went too.",
        ],
        "arrival_arc_title": "{name}: a stranger",
        "arrival_intro": [
            "{name} arrived in {season}. {village} had not been expecting anyone.",
            "{name} came to {village} in {season}, without a history anyone here knew.",
        ],
        "arrival_settled": [
            "By the end of this record, {name} was part of {village} the way a stone is part of a wall — quietly, but there.",
            "{name} had arrived knowing no one and left a member of {village}, in whatever way that word applies.",
        ],
        "arrival_cold": [
            "{name} remained something the village had not quite resolved by the time this record closes.",
            "The village and {name} reached a kind of armed truce: present together, never entirely easy.",
        ],
        "arrival_died": [
            "{name} did not stay long enough to become fully known. The village noted the loss the way it notes all brief things.",
            "{name} arrived and did not outlive these years. Some stories begin and end before the telling finds them.",
        ],
        "village_section": "## The Village",
        "LEAN_SEASON": [
            "The {season} was a hungry one. More than half the houses in {village} had lean pantries, and no one pretended otherwise.",
            "Want spread through {village} that {season} — not one house at a time, but all at once. That kind of lean is different.",
            "That {season}, most of {village} counted its stores by the day. The ovens were careful and the children got the most of what was left.",
        ],
        "LEAN_SEASON_solidarity": [
            " Those who still had something to spare gave without being asked. The village at its best looks like that.",
            " A few generous souls emptied part of their own shelves into their neighbors'. Nobody mentioned it afterward.",
        ],
        "BOUNTY": [
            "The {season} was generous. Most of {village} had more than enough, and surplus food finds its way out the door.",
            "{village} came through that {season} with full stores. Those who remember the lean years never quite take it for granted.",
            "That {season}, the village was well-fed and it showed — in longer evenings, in more visiting, in quarrels that did not quite start.",
        ],
        "DEPARTURE": [
            "{a} left {village}. No announcement, no formal goodbye — one morning the absence was simply there.",
            "The news that {a} had left reached the village the way all news does: someone noticed an absence, and then someone told someone.",
        ],
        "departed_note": [
            "{a} left {village} before this record closed. The village had grown cold to {a}, or {a} to it — by the end, the order no longer mattered.",
            "{a} was gone before the end. Some people do not wait for a village to make up its mind about them.",
        ],
        "departure_arc_title": "{name}: a departure",
        "departure_section": "## Those Who Left",
        "departures_note_1": "One person left {village} during this time, before the record closed.",
        "departures_note_n": "{count} people left {village} during this time, before the record closed.",
        "colophon": "*(world seed {seed} — run it again and the same things will happen, in the same order, to the same people)*",
    },
    "es": {
        "seasons": ("la primavera", "el verano", "el otoño", "el invierno"),
        "seasons_in": ("primavera", "verano", "otoño", "invierno"),
        "traits": {
            "diligence": (("incansable", "incansable"), ("holgazán", "holgazana")),
            "generosity": (("desprendido", "desprendida"), ("agarrado", "agarrada")),
            "pride": (("orgulloso", "orgullosa"), ("humilde", "humilde")),
            "openness": (("parlanchín", "parlanchina"), ("reservado", "reservada")),
        },
        "intro": ["{name} era {adjs}.",
                  "A {name}, {adjs}, la conocía todo el mundo."],
        "intro_m": ["{name} era {adjs}.",
                    "A {name}, {adjs}, lo conocía todo el mundo."],
        "and": "y",
        "opening": ["Todo empezó en {season}.",
                    "Lo primero que se supo fue en {season}."],
        "later_season": ["Llegó {season}.", "Para entonces ya era {season}."],
        "soon_after": ["No pasaron muchos días.", "Poco después."],
        "GIFT": ["Cuando a {b} se le vació la despensa, {a} le llenó el cesto sin que nadie se lo pidiera.",
                 "{a} compartió el pan con {b} en una mala racha, y no se olvidó."],
        "REFUSAL": ["{a} llamó con hambre a la puerta de {b} y volvió con las manos vacías.",
                    "{b} despidió a {a} sin nada, y toda la aldea se sintió más fría."],
        "OFFENSE": ["A {a} le llegó el cuento de que {b} andaba hablando del asunto a puerta cerrada.",
                    "Alguien se encargó de que {a} supiera lo que {b} iba diciendo."],
        "QUARREL": ["{a} y {b} discutieron donde todos podían oírlos, y la aldea fingió no escuchar.",
                    "Entre {a} y {b} hubo palabras mayores, en mitad de la calle."],
        "MEDIATION": ["{c} los sentó a los dos a la misma mesa y no dejó que ninguno se levantara enfadado. Algo se aflojó.",
                      "Hizo falta {c}, de quien ambos se fiaban, para que volvieran a hablarse."],
        "REPAYMENT": ["{a} no había olvidado aquel favor, y cuando la necesidad llamó a casa de {b}, lo devolvió sin decir una palabra.",
                      "El pan que {b} dio un día volvió a su propia puerta, y fue {a} quien lo trajo."],
        "INGRATITUDE": ["{a} le había llenado el cesto a {b} una vez; cuando el suyo quedó vacío, la puerta de {b} no se abrió. La aldea lleva cuentas que ningún libro ve, y esa quedó apuntada en todas las cabezas.",
                        "{b} le debía a {a} una de esas deudas que nadie escribe, y la pagó con la puerta cerrada. Nadie dijo nada. Todos la contaron."],
        "RESENTMENT": ["El favor le pesaba a {a}. Deber es cosa dura, y {a} empezó a esquivarle la mirada a {b}.",
                       "{a} nunca devolvió lo que {b} le dio un día, y la deuda se agrió, como se agria la gratitud cuando se carga demasiado tiempo."],
        "BOND": ["{a} y {b} se eligieron mutuamente antes de que cambiara la estación. La aldea lo supo antes de que ninguno de los dos dijera una palabra al respecto.",
                 "Lo que había crecido entre {a} y {b} se convirtió en algo declarado. Compartieron pan y lumbre a partir de entonces."],
        "WIDOWING": ["{a} sobrevivió a {b}. La aldea no dejó a {a} {solo} con ello, que es como se lleva el duelo en un lugar así.",
                     "Cuando {b} murió, {a} perdió algo que va más allá de lo que se pierde cuando lo que queda es solo la soledad."],
        "carried_by": " Fue {c} quien trajo el cuento.",
        "grown": " El cuento había engordado por el camino.",
        "repeat_one": "Volvió a pasar una vez más.",
        "repeat_many": "Volvió a pasar {n} veces más, como si los rencores llevaran su propio calendario.",
        "repeat_good_one": "Y volvió a pasar, sin ruido, cuando hizo falta.",
        "repeat_good_many": "Y volvió a pasar {n} veces más, sin que nadie le diera importancia; también la bondad lleva su calendario.",
        "repeat_endless": "Y así siguió, estación tras estación, hasta que contar dejó de tener sentido.",
        "repeat_good_endless": "Y así siguió, estación tras estación; hay cosas que no necesitan que nadie las señale para continuar.",
        "seasons_later": [
            "Pasaron las estaciones. Para cuando llegó {season}, el asunto seguía abierto.",
            "Volvió {season}, y nada se había cerrado.",
        ],
        "year_later": "Pasó un año. Cuando llegó {season}, el asunto volvía a estar ahí.",
        "years_later": "{n} años después, al llegar {season}, la aldea lo seguía cargando.",
        "repeat_quarrel_one": "Volvieron a pelearse, como si la primera vez hubiera sido un ensayo.",
        "repeat_quarrel_many": "Volvieron a pelearse {n} veces. Nunca llegaba a arreglarse nada.",
        "repeat_quarrel_endless": "Y así siguió la pelea, estación tras estación; hay cosas que necesitan un testigo más que una solución.",
        "repeat_refusal_one": "La puerta volvió a quedarse cerrada.",
        "repeat_refusal_many": "La puerta se quedó cerrada {n} veces más. La aldea las fue contando.",
        "repeat_gift_one": "El pan volvió a llegar, sin decir nada.",
        "repeat_gift_many": "El pan llegó {n} veces más, sin ceremonia; eso es lo que lo hace pan.",
        "close_relapse": "La paz que se hizo no se sostuvo; hay grietas que quieren seguir abiertas.",
        "close_broken": "Nadie lo arregló. Al final pasaban el uno junto al otro sin mediar palabra.",
        "close_uneasy": "Quedó entre ellos una paz incómoda, fina como el hielo de marzo.",
        "close_mended": "Lo que se había roto, lo remendaron mejor que nuevo.",
        "close_warm": "Tuvieron suerte el uno con el otro, y lo sabían.",
        "close_widowed": "Habían tenido suerte el uno con el otro. El final fue triste, pero era una tristeza que la aldea reconocía.",
        "close_departed": "Antes de que cerrara el registro, {a} se había ido — empujado por un frío que la aldea nunca terminó de ponerle nombre.",
        "close_departed_bonded": "Lo que {a} y su pareja habían construido no sobrevivió al frío de la aldea. {a} se fue; el vínculo no sobrevivió a la marcha.",
        "title_reconciliation": "{a} y {b}: una reconciliación",
        "title_estrangement": "{a} y {b}: un distanciamiento",
        "title_feud": "{a} y {b}: una enemistad",
        "title_bond": "{a} y {b}: una amistad",
        "title_love": "{a} y {b}: un amor",
        "title_open": "{a} y {b}: un asunto sin cerrar",
        "title_debt": "{a} y {b}: una deuda impagada",
        "chronicle_title": ["Crónica de {village}",
                            "Registro de {village}",
                            "Lo que pasó en {village}"],
        "arrivals_note_1_named": "{name} llegó a {village} sin historia que la aldea conociera. Nunca sabe bien qué hacer con eso.",
        "prologue": [("En {village} vivían {n} almas al abrir este registro, "
                      "y abarca {days} de sus días. "
                      "Nada de lo que sigue es inventado; solo se miró, y se contó."),
                     ("Este es el registro de {village}, que tenía {n} almas cuando se abrió. "
                      "Cubre {days} de sus días. "
                      "Nada está inventado."),
                    ],
        "epilogue": [("Cuando el registro se cierra, {a} y {b} eran lo más parecido a inseparables que hay en {village}; "
                      "{c} y {d} seguían sin hablarse."),
                     ("Al final, {a} y {b} seguían encontrando razones para cruzarse en {village}. "
                      "{c} y {d} seguían encontrando razones para no hacerlo."),
                    ],
        "pride_note": "{count} veces alguien en {village} pasó hambre antes que pedir ayuda. El orgullo es otra clase de hambruna.",
        "debt_note": "Al cerrarse el registro quedaban en {village} {count} favores sin devolver. Esas cuentas no las llevaba la aldea en libro alguno, y por eso no se perdió ninguna.",
        "deaths_note_1": "Una persona de {village} no sobrevivió a estos años. Una aldea lleva a sus muertos en silencio, que es la manera en que los muertos acaban cargando con la aldea.",
        "deaths_note_n": "{count} personas de {village} no sobrevivieron a estos años. Una aldea lleva a sus muertos en silencio, que es la manera en que los muertos acaban cargando con la aldea.",
        "arrivals_note_1": "Un forastero llegó a {village} en este tiempo. La aldea nunca sabe bien qué hacer con alguien que no tiene historia.",
        "arrivals_note_n": "{count} forasteros llegaron a {village} en este tiempo. La aldea nunca sabe bien qué hacer con alguien que no tiene historia.",
        "bonds_note_1": "Un vínculo se forjó en {village} en este tiempo. La mayoría de las cosas duraderas empiezan sin que nadie señale el momento.",
        "bonds_note_n": "{count} vínculos se forjaron en {village} en este tiempo. La mayoría de las cosas duraderas empiezan sin que nadie señale el momento.",
        "births_note_1": "Un niño nació en {village} en este tiempo.",
        "births_note_n": "{count} niños nacieron en {village} en este tiempo.",
        "growth_note": "Al cerrar el registro, {village} contaba más almas que al abrirse.",
        "famine_note": "El año {year} fue un año de hambre en {village}.",
        "birth_intro": ["{name}, {nacido} en {village}, era {adjs}.",
                        "{name} se había criado en {village} y era {adjs}."],
        "birth_intro_m": ["{name}, nacido en {village}, era {adjs}.",
                          "{name} se había criado en {village} y era {adjs}."],
        "refusal_pride": [
            "El orgullo es su propio tipo de hambruna.",
            "Hay gente que prefiere sufrir antes que ser vista sufriendo.",
        ],
        "gift_unexpected": [
            "La generosidad no es siempre una cuestión de carácter.",
            "Hasta las manos cerradas se abren a veces.",
        ],
        "MEDIATION_elder": [
            "Fue {c}, {anciano} de la aldea, quien los hizo sentarse. Hay cosas que solo ceden a la paciencia de los años.",
            "A {c}, que había visto lo suficiente como para saber cómo acaban los rencores, le tocó sentarlos. Algo se aflojó.",
        ],
        "died_starvation": "{a} no sobrevivió a esta crónica. Un invierno largo puso fin a sus días antes de que el relato cerrara.",
        "died_misfortune": "{a} no sobrevivió a esta crónica; un golpe repentino, cuando ya no quedaba nada con que resistirlo.",
        "died_old_age": [
            "{a} no sobrevivió a esta crónica. Había vivido en {village} el tiempo suficiente para ser parte de su memoria; después pasó a serlo solo.",
            "{a} tuvo una vida larga en {village}, y la aldea cambió varias veces a su alrededor. Un final distinto al de los demás.",
        ],
        "died_leaving": "Dejó atrás a {names}.",
        "BIRTH": [
            "Llegó {c}. Hay cosas que llegan sin que nadie las pida y que la aldea guarda para siempre.",
            "Nació {c}, y la aldea supo de inmediato que era de los suyos.",
        ],
        "COMING_OF_AGE": "{c} creció. La aldea tuvo así un adulto más, y más manos en las que confiar.",
        "elder_intro": [
            "A {name}, que llevaba aquí más tiempo que nadie y recordaba lo que otros habían olvidado, {lo} conocía todo el mundo. Era {adjs}.",
            "{name}, {anciano} de la aldea, era {adjs}.",
        ],
        "elder_intro_m": [
            "A {name}, que llevaba aquí más tiempo que nadie y recordaba lo que otros habían olvidado, lo conocía todo el mundo. Era {adjs}.",
            "{name}, {anciano} de la aldea, era {adjs}.",
        ],
        "QUARREL_private": [
            "{a} y {b} lo resolvieron sin testigos. Para la mañana la aldea ya lo sabía de todos modos.",
            "Lo que pasó entre {a} y {b} pasó sin que nadie lo viera. Las peleas privadas suelen durar más.",
        ],
        "winter_later": [
            "Volvió el invierno, y con él volvió el asunto sin resolver.",
            "Llegó otro invierno. La versión más fría de todo regresó con él.",
        ],
        "dead_section": "## Después",
        "legacy_generous": [
            "{name} fue el alma más desprendida que conoció {village}. La aldea notó el frío que dejó.",
            "{name} nunca despachó a nadie con las manos vacías. Esa clase de persona no se sustituye; se echa de menos.",
        ],
        "legacy_proud": [
            "{name} se marchó con las cuentas saldadas. Hay gente que no tolera dejar deudas.",
            "{name} lo había mantenido todo en equilibrio hasta el final. Una pérdida complicada.",
        ],
        "legacy_diligent": [
            "{name} había trabajado más que nadie. Lo que {name} mantenía en pie pasaba invisible hasta que se detuvo.",
            "Los campos que labraba {name} eran los mejor cuidados de {village}. Ese saber no se escribe.",
        ],
        "legacy_mediator": [
            "{name} había sentado a la misma mesa a más vecinos enfrentados que nadie. La aldea sintió la falta como se siente la de quien sabe callar las peleas.",
            "La gente acudía a {name} con cosas que no podía decir en otra parte. Después no quedó nadie igual.",
        ],
        "legacy_bonded": [
            "{name} había construido una vida con {partner} en {village}. Ese vínculo quedó en la memoria de la aldea.",
            "Lo que {name} levantó aquí — los años, lo compartido con {partner} — lo sobrevivió. Suele ocurrir.",
        ],
        "legacy_newcomer": [
            "{name} llegó a {village} sin historia y se marchó con una. Así es como se ve el pertenecer.",
            "{name} vino de fuera y acabó siendo parte del lugar. La aldea carga ese tipo de presencia en silencio.",
        ],
        "legacy_quiet": [
            "{name} no dejó una huella ruidosa. Los silenciosos rara vez la dejan, pero el lugar cambia cuando se van.",
            "{name} era parte del ruido de fondo que hace que un lugar parezca habitado. El silencio que dejó fue preciso.",
        ],
        "legacy_long_life": [
            "{name} había vivido en {village} el tiempo suficiente para recordar lo que nadie más podía. Ese tipo de testigo no se sustituye; se pierde.",
            "Los años que {name} pasó en {village} sobrevivieron a varias versiones del lugar. Cuando se fue, se fue con él algo que la aldea sabía de sí misma.",
        ],
        "arrival_arc_title": "{name}: una llegada",
        "arrival_intro": [
            "{name} llegó en {season}. {village} no esperaba a nadie.",
            "{name} llegó a {village} en {season}, sin historia que nadie aquí conociera.",
        ],
        "arrival_settled": [
            "Al cerrarse el registro, {name} era parte de {village} como una piedra es parte de un muro: sin ruido, pero con peso.",
            "{name} había llegado sin conocer a nadie y se fue siendo parte de {village}. La aldea se hace así.",
        ],
        "arrival_cold": [
            "Al cerrarse el registro, {village} y {name} aún no habían llegado a entenderse del todo.",
            "Hubo entre {name} y la aldea una distancia que no llegó a cerrarse.",
        ],
        "arrival_died": [
            "{name} no llegó a ser conocido del todo. La aldea anotó la pérdida como anota todas las cosas breves.",
            "{name} llegó y no sobrevivió estos años. Hay historias que empiezan y terminan antes de que el relato las encuentre.",
        ],
        "village_section": "## La aldea",
        "LEAN_SEASON": [
            "En {season} hubo hambre en {village}. Más de la mitad de las casas tenían la despensa escasa, y nadie fingía lo contrario.",
            "La escasez llegó a {village} durante {season} de golpe, a todas las casas a la vez. Ese tipo de hambre es distinto.",
            "Durante {season}, la mayor parte de {village} contaba sus reservas día a día. Los hornos ardían con cuidado y los niños se quedaban con lo mejor.",
        ],
        "LEAN_SEASON_solidarity": [
            " Los que aún tenían algo de sobra lo dieron sin que nadie se lo pidiera. Así es la aldea en sus mejores momentos.",
            " Algunos vaciaron parte de sus propias alacenas en las de sus vecinos. Nadie lo mencionó después.",
        ],
        "BOUNTY": [
            "En {season} hubo abundancia en {village}. La mayor parte de las casas tenía más que suficiente, y el sobrante siempre encuentra la puerta.",
            "{village} llegó a {season} con las despensas llenas. Los que recuerdan los años de hambre nunca lo dan por seguro.",
            "Durante {season} la aldea estaba bien alimentada, y se notaba: noches más largas, más visitas, peleas que no llegaban a empezar.",
        ],
        "DEPARTURE": [
            "{a} se fue de {village}. Sin anuncio, sin despedida — una mañana la ausencia estaba simplemente ahí.",
            "La noticia de que {a} había dejado {village} llegó como siempre llegan las noticias: alguien notó la falta, y alguien se lo contó a alguien.",
        ],
        "departed_note": [
            "{a} dejó {village} antes de que cerrara este registro. La aldea se había enfriado con {a}, o {a} con ella — al final, el orden ya no importaba.",
            "{a} se fue antes del final. Hay personas que no esperan a que una aldea decida qué piensa de ellas.",
        ],
        "departure_arc_title": "{name}: una partida",
        "departure_section": "## Los que se fueron",
        "departures_note_1": "Una persona dejó {village} en este tiempo, antes de que cerrara el registro.",
        "departures_note_n": "{count} personas dejaron {village} en este tiempo, antes de que cerrara el registro.",
        "colophon": "*(semilla del mundo: {seed} — vuelve a ejecutarla y pasarán las mismas cosas, en el mismo orden, a la misma gente)*",
    },
    "fr": {
        "seasons": ("le printemps", "l'été", "l'automne", "l'hiver"),
        "seasons_in": ("au printemps", "en été", "en automne", "en hiver"),
        "traits": {
            "diligence": (("infatigable", "infatigable"), ("fainéant", "fainéante")),
            "generosity": (("généreux", "généreuse"), ("avare", "avare")),
            "pride": (("fier", "fière"), ("humble", "humble")),
            "openness": (("bavard", "bavarde"), ("taciturne", "taciturne")),
        },
        "intro": ["{name} était {adjs}.",
                  "Tout le monde connaissait {name}, {adjs}."],
        "and": "et",
        "opening": ["Tout commença {season}.",
                    "On en entendit parler pour la première fois {season}."],
        "later_season": ["{season} arriva.", "C'était déjà {season}."],
        "soon_after": ["Les jours qui suivirent furent courts.", "Peu après."],
        "GIFT": ["Quand les réserves de {b} vinrent à manquer, {a} remplit le panier sans qu'on le lui demande.",
                 "{a} partagea son pain avec {b} dans les mauvais temps, et {b} ne l'oublia pas."],
        "REFUSAL": ["{a} frappa à la porte de {b} le ventre creux et repartit les mains vides.",
                    "{b} renvoya {a} sans rien, et tout le village en fut refroidi."],
        "OFFENSE": ["Il parvint aux oreilles de {a} que {b} parlait de l'affaire derrière des portes closes.",
                    "Quelqu'un se chargea de rapporter à {a} ce que {b} allait disant."],
        "QUARREL": ["{a} et {b} se disputèrent là où tout le monde pouvait entendre, et le village fit semblant de ne pas écouter.",
                    "Il y eut des mots durs entre {a} et {b}, en pleine rue."],
        "MEDIATION": ["{c} les fit asseoir à la même table et ne laissa ni l'un ni l'autre repartir en colère. Quelque chose se dénoua.",
                      "Il fallut {c}, en qui ils avaient tous deux confiance, pour qu'ils se parlent de nouveau."],
        "REPAYMENT": ["{a} n'avait pas oublié l'ancienne gentillesse, et quand le besoin frappa chez {b}, il la rendit sans un mot.",
                      "Le pain que {b} avait donné revint à sa propre porte, porté par {a}."],
        "INGRATITUDE": ["{a} avait rempli le panier de {b} ; quand le sien se vida, la porte de {b} resta close. Le village tient des comptes qu'aucun registre ne voit, et celui-là fut inscrit dans toutes les mémoires.",
                        "{b} devait à {a} le genre de dette que personne n'écrit, et la solda par une porte fermée. Personne ne dit rien. Tout le monde compta."],
        "RESENTMENT": ["La faveur pesait à {a}. C'est chose difficile que de devoir, et {a} se mit à éviter le regard de {b}.",
                       "{a} n'avait jamais rendu ce que {b} lui avait donné, et la dette s'aigrit, comme la gratitude s'aigrit quand on la porte trop longtemps."],
        "BOND": ["{a} et {b} se choisirent avant que la saison ne tourne. Le village le sut avant qu'ils en disent un mot.",
                 "Ce qui avait grandi entre {a} et {b} devint quelque chose d'assumé. Ils partagèrent pain et foyer après cela."],
        "WIDOWING": ["{a} survécut à {b}. Le village ne laissa pas {a} {seul} avec cela, c'est ainsi qu'on porte le deuil en pareil endroit.",
                     "Quand {b} mourut, {a} perdit quelque chose que l'on ne perd pas de la même façon que le reste."],
        "carried_by": " C'est {c} qui porta le récit.",
        "grown": " Le récit avait grossi en chemin.",
        "repeat_one": "Cela se reproduisit une fois encore.",
        "repeat_many": "Cela se reproduisit {n} fois encore, comme si les rancœurs tenaient leur propre calendrier.",
        "repeat_good_one": "Et cela se reproduisit, discrètement, quand il le fallut.",
        "repeat_good_many": "Et cela se reproduisit {n} fois encore, sans que personne en fasse grand cas ; la bonté aussi tient son calendrier.",
        "repeat_endless": "Et ainsi de suite, saison après saison, jusqu'à ce que compter perde son sens.",
        "repeat_good_endless": "Et ainsi de suite, saison après saison ; certaines choses n'ont pas besoin d'être remarquées pour continuer.",
        "seasons_later": [
            "Plusieurs saisons s'écoulèrent. Quand {season} arriva, l'affaire n'était pas close.",
            "Quand {season} revint, rien n'avait été réglé.",
        ],
        "year_later": "Un an s'écoula ; quand {season} arriva, l'affaire n'était pas close.",
        "years_later": "{n} ans passèrent ; quand {season} arriva, le village portait encore cela.",
        "repeat_quarrel_one": "Ils se battirent de nouveau, comme si la première fois avait été une répétition.",
        "repeat_quarrel_many": "Ils se battirent {n} fois encore. Cela ne réglait jamais rien.",
        "repeat_quarrel_endless": "Et la dispute continua, saison après saison ; certaines choses ont besoin d'un témoin plus que d'une résolution.",
        "repeat_refusal_one": "La porte resta close une fois de plus.",
        "repeat_refusal_many": "La porte resta close {n} fois encore. Le village compta chacune.",
        "repeat_gift_one": "Le pain revint, sans un mot.",
        "repeat_gift_many": "Le pain revint {n} fois encore, sans cérémonie ; c'est ce qui en fait du pain.",
        "close_relapse": "La paix qui fut faite ne tint pas ; certaines fissures veulent rester ouvertes.",
        "close_broken": "Personne ne raccommoda rien. À la fin, ils se croisaient sans un mot.",
        "close_uneasy": "Une paix précaire s'installa entre eux, mince comme la glace de mars.",
        "close_mended": "Ce qui s'était brisé, ils le recoussirent mieux qu'avant.",
        "close_warm": "Ils eurent de la chance l'un envers l'autre, et ils le savaient.",
        "close_widowed": "Ils avaient eu de la chance l'un envers l'autre. La fin fut triste, mais c'était une tristesse que le village reconnut.",
        "close_departed": "Avant la fin du récit, {a} était parti — poussé dehors par une froideur que le village n'a jamais su nommer.",
        "close_departed_bonded": "Ce que {a} et son partenaire avaient construit ne survécut pas à la froideur du village. {a} partit ; le lien ne survécut pas au départ.",
        "title_reconciliation": "{a} et {b} : une réconciliation",
        "title_estrangement": "{a} et {b} : un éloignement",
        "title_feud": "{a} et {b} : une inimitié",
        "title_bond": "{a} et {b} : une amitié",
        "title_love": "{a} et {b} : une histoire",
        "title_open": "{a} et {b} : une affaire non réglée",
        "title_debt": "{a} et {b} : une dette impayée",
        "chronicle_title": ["Chronique de {village}",
                            "Registre de {village}",
                            "Ce qui s'est passé à {village}"],
        "arrivals_note_1_named": "{name} arriva à {village} sans passé que le village connaisse. On ne sait jamais quoi faire de quelqu'un sans histoire.",
        "prologue": [("{village} comptait {n} âmes à l'ouverture de ce récit, "
                      "et il couvre {days} jours de leur vie. "
                      "Rien n'y est inventé ; on a seulement regardé, et raconté."),
                     ("Voici le registre de {village}, qui comptait {n} personnes à son ouverture. "
                      "Il couvre {days} de leurs jours. "
                      "Rien n'est inventé."),
                    ],
        "epilogue": [("Quand le récit se ferme, {a} et {b} étaient aussi proches que deux personnes peuvent l'être à {village} ; "
                      "{c} et {d} ne se parlaient toujours pas."),
                     ("À la fin, {a} et {b} trouvaient encore des raisons de se croiser à {village}. "
                      "{c} et {d} trouvaient encore des raisons de ne pas le faire."),
                    ],
        "pride_note": "{count} fois, quelqu'un à {village} préféra souffrir de la faim plutôt que de demander de l'aide. L'orgueil est une autre forme de famine.",
        "debt_note": "Quand le récit se ferme, {count} faveurs à {village} n'avaient pas encore été rendues. Le village ne les consignait dans aucun registre, c'est pourquoi aucune ne fut jamais perdue.",
        "deaths_note_1": "Une âme à {village} ne survécut pas à ces années. Un village porte ses morts en silence, c'est ainsi que les morts finissent par porter le village.",
        "deaths_note_n": "{count} âmes à {village} ne survécurent pas à ces années. Un village porte ses morts en silence, c'est ainsi que les morts finissent par porter le village.",
        "arrivals_note_1": "Un étranger arriva à {village} en ce temps. Le village ne sait jamais trop quoi faire de quelqu'un qui n'a pas d'histoire.",
        "arrivals_note_n": "{count} étrangers arrivèrent à {village} en ce temps. Le village ne sait jamais trop quoi faire de quelqu'un qui n'a pas d'histoire.",
        "bonds_note_1": "Un lien se noua à {village} en ce temps. La plupart des choses durables commencent sans que le moment soit marqué.",
        "bonds_note_n": "{count} liens se nouèrent à {village} en ce temps. La plupart des choses durables commencent sans que le moment soit marqué.",
        "births_note_1": "Un enfant naquit à {village} en ce temps.",
        "births_note_n": "{count} enfants naquirent à {village} en ce temps.",
        "growth_note": "À la clôture de ce récit, {village} comptait plus d'âmes qu'à son ouverture.",
        "famine_note": "L'an {year} fut une année de famine à {village}.",
        "birth_intro": ["{name}, {ne} à {village}, était {adjs}.",
                        "Tout le monde à {village} connaissait {name}, {adjs}, depuis l'enfance."],
        "refusal_pride": [
            "L'orgueil est sa propre sorte de famine.",
            "Certains préfèrent souffrir plutôt que d'être vus souffrir.",
        ],
        "gift_unexpected": [
            "La générosité n'est pas toujours une question de caractère.",
            "Même les poings fermés s'ouvrent parfois.",
        ],
        "MEDIATION_elder": [
            "Ce fut {c}, {ancien}, qui les fit s'asseoir à la même table. Il y a des choses qui ne cèdent qu'à la patience des années.",
            "{c}, qui avait vu assez d'hivers pour savoir comment les rancœurs se terminent, les fit parler. Quelque chose se dénoua.",
        ],
        "died_starvation": "{a} ne survécut pas à cette chronique. Un long hiver l'emporta avant la clôture du récit.",
        "died_misfortune": "{a} ne survécut pas à cette chronique ; un coup soudain, quand il ne restait plus rien pour l'absorber.",
        "died_old_age": [
            "{a} ne survécut pas à cette chronique. Assez d'années à {village} pour en faire partie de la mémoire ; pour n'en devenir que cela.",
            "{a} avait mené une longue vie à {village}, et le village avait changé plusieurs fois autour d'elle. Une fin différente des autres.",
        ],
        "died_leaving": "{su} laissa {names} derrière {lu}.",
        "BIRTH": [
            "Un enfant — {c} — arriva. Il y a des choses qui arrivent sans cérémonie et qui se font sentir pendant des années.",
            "{c} naquit. Le village {lo} reçut comme il reçoit toujours ce qui arrive sans demander.",
        ],
        "COMING_OF_AGE": "{c} grandit. Le village compta un habitant de plus parmi les siens.",
        "elder_intro": [
            "{name}, qui était là depuis le plus longtemps et se souvenait de ce que d'autres avaient oublié, était {adjs}.",
            "Tout le monde était venu trouver {name} au moins une fois. {name} était {adjs}.",
        ],
        "QUARREL_private": [
            "{a} et {b} réglèrent leur compte sans témoin. Le lendemain, tout le village était au courant.",
            "Ce qui se passa entre {a} et {b} se passa sans que personne ne le voie. Les disputes privées ont tendance à durer plus longtemps.",
        ],
        "winter_later": [
            "L'hiver revint, et l'ancienne affaire revint avec lui.",
            "Un autre hiver s'installa. La version froide de toutes choses revint aussi.",
        ],
        "dead_section": "## Après",
        "legacy_generous": [
            "{name} fut l'âme la plus généreuse que {village} ait connue. Le village se trouva plus froid après.",
            "{name} n'avait jamais renvoyé personne les mains vides. Ce genre de personne ne se remplace pas ; on la remarque surtout par son absence.",
        ],
        "legacy_proud": [
            "{name} repartit les comptes soldés. Les fiers ne supportent pas de laisser des dettes.",
            "{name} avait tout maintenu en équilibre jusqu'au bout. Une perte compliquée.",
        ],
        "legacy_diligent": [
            "{name} avait travaillé plus dur que n'importe qui. Ce que {name} faisait tourner passait inaperçu jusqu'à ce que ça s'arrête.",
            "Les champs que {name} entretenait étaient les mieux tenus de {village}. Ce genre de savoir ne s'écrit pas.",
        ],
        "legacy_mediator": [
            "{name} avait assis plus de voisins en dispute à la même table que n'importe qui. Le village ressentit l'absence comme on ressent celle d'un pacificateur.",
            "Les gens venaient trouver {name} avec des choses qu'ils ne pouvaient pas dire ailleurs. Après, il n'y avait plus personne tout à fait comme ça.",
        ],
        "legacy_bonded": [
            "{name} avait construit une vie avec {partner} à {village}. Ce lien devint une partie de l'histoire du village.",
            "Ce que {name} avait bâti ici — les années, le lien avec {partner} — lui survécut. C'est souvent ainsi.",
        ],
        "legacy_newcomer": [
            "{name} était arrivé à {village} sans passé et en repartit avec un. C'est à cela que ressemble l'appartenance.",
            "{name} vint d'ailleurs et devint partie du lieu quand même. Le village porte ce genre de personne discrètement.",
        ],
        "legacy_quiet": [
            "{name} ne laissa pas une empreinte bruyante. Les discrets le font rarement, mais le lieu change quand ils partent.",
            "{name} faisait partie du fond sonore qui rend un endroit habité. Le silence qui suivit fut précis.",
        ],
        "legacy_long_life": [
            "{name} avait vécu à {village} assez longtemps pour se souvenir de ce que personne d'autre ne pouvait. Ce genre de témoin ne se remplace pas ; il se perd.",
            "Les années que {name} passa à {village} survécurent à plusieurs versions du lieu. Quand {name} s'en alla, quelque chose que le village savait de lui-même s'en alla aussi.",
        ],
        "arrival_arc_title": "{name}: une arrivée",
        "arrival_intro": [
            "{name} arriva {season_in}. {village} n'attendait personne.",
            "{name} vint à {village} {season_in}, sans passé que quiconque ici connaisse.",
        ],
        "arrival_settled": [
            "À la clôture de ce récit, {name} faisait partie de {village} comme une pierre fait partie d'un mur — sans bruit, mais là.",
            "Sans passé au départ, {name} en avait un à la fin. C'est ainsi que les villages absorbent les étrangers.",
        ],
        "arrival_cold": [
            "{name} restait quelque chose que le village n'avait pas tout à fait résolu à la clôture de ce récit.",
            "Il y eut entre {name} et le village une distance qui ne se ferma pas vraiment.",
        ],
        "arrival_died": [
            "{name} ne resta pas assez longtemps pour être pleinement connu. Le village nota la perte comme il note toutes les choses brèves.",
            "{name} arriva et ne survécut pas à ces années. Certaines histoires commencent et se terminent avant que le récit les trouve.",
        ],
        "village_section": "## Le village",
        "LEAN_SEASON": [
            "{village} traversa {season} dans la faim. Plus de la moitié des maisons avaient les garde-manger vides, et personne ne faisait semblant du contraire.",
            "La disette frappa {village} {season_in} — pas maison par maison, mais d'un coup. Ce genre de faim est différent.",
            "{season_in}, la plupart de {village} comptait ses réserves au jour le jour. Les fours étaient prudents et les enfants recevaient le meilleur de ce qui restait.",
        ],
        "LEAN_SEASON_solidarity": [
            " Ceux qui avaient encore quelque chose donnèrent sans qu'on le leur demande. Le village à son meilleur ressemble à cela.",
            " Quelques âmes généreuses vidèrent une partie de leurs étagères dans celles de leurs voisins. Personne n'en parla ensuite.",
        ],
        "BOUNTY": [
            "{village} traversa {season} dans l'abondance. La plupart des maisons avaient plus que suffisant, et le surplus trouve toujours la porte.",
            "{village} passa {season} sans manquer de rien. Ceux qui se souviennent des années de disette ne s'y habituent jamais.",
            "{season_in}, le village était bien nourri et cela se voyait — des soirées plus longues, plus de visites, des querelles qui ne commençaient pas vraiment.",
        ],
        "DEPARTURE": [
            "{a} quitta {village}. Sans annoncer, sans vrai adieu — un matin l'absence était là, c'est tout.",
            "La nouvelle que {a} avait quitté {village} se répandit comme toutes les nouvelles : quelqu'un nota l'absence, quelqu'un en parla.",
        ],
        "departed_note": [
            "{a} quitta {village} avant la fin de ce récit. Le village s'était refroidi à l'égard de {a}, ou l'inverse — à la fin, l'ordre n'avait plus d'importance.",
            "{a} était parti avant la fin. Certaines personnes n'attendent pas qu'un village se décide.",
        ],
        "departure_arc_title": "{name} : un départ",
        "departure_section": "## Ceux qui sont partis",
        "departures_note_1": "Une personne quitta {village} durant cette période, avant que le récit ne se ferme.",
        "departures_note_n": "{count} personnes quittèrent {village} durant cette période, avant que le récit ne se ferme.",
        "colophon": "*(graine du monde : {seed} — lancez-la de nouveau et les mêmes choses arriveront, dans le même ordre, aux mêmes gens)*",
    },
    "pt": {
        "seasons": ("a primavera", "o verão", "o outono", "o inverno"),
        "seasons_in": ("na primavera", "no verão", "no outono", "no inverno"),
        "traits": {
            "diligence": (("incansável", "incansável"), ("preguiçoso", "preguiçosa")),
            "generosity": (("generoso", "generosa"), ("avarento", "avarenta")),
            "pride": (("orgulhoso", "orgulhosa"), ("humilde", "humilde")),
            "openness": (("falador", "faladora"), ("reservado", "reservada")),
        },
        "intro": ["{name} era {adjs}.",
                  "Toda a aldeia conhecia {name}, {adjs}."],
        "and": "e",
        "opening": ["Tudo começou {season}.",
                    "A primeira notícia foi {season}."],
        "later_season": ["{season} chegou.", "Já era {season}."],
        "soon_after": ["Não passaram muitos dias.", "Pouco depois."],
        "GIFT": ["Quando as reservas de {b} escassearam, {a} encheu o cesto sem que ninguém pedisse.",
                 "{a} partilhou o pão com {b} numa fase difícil, e não foi esquecido."],
        "REFUSAL": ["{a} foi à porta de {b} com fome e voltou de mãos vazias.",
                    "{b} mandou {a} embora sem nada, e toda a aldeia ficou mais fria por isso."],
        "OFFENSE": ["Chegou aos ouvidos de {a} que {b} andava a falar do assunto a portas fechadas.",
                    "Alguém tratou de contar a {a} o que {b} ia dizendo."],
        "QUARREL": ["{a} e {b} discutiram onde todos podiam ouvir, e a aldeia fingiu não escutar.",
                    "Entre {a} e {b} houve palavras graves, em plena rua."],
        "MEDIATION": ["{c} sentou-os à mesma mesa e não deixou nenhum sair zangado. Algo se desatou.",
                      "Precisou de {c}, em quem ambos confiavam, para que voltassem a falar-se."],
        "REPAYMENT": ["{a} não tinha esquecido o favor antigo, e quando a necessidade bateu à porta de {b}, devolveu-o sem dizer uma palavra.",
                      "O pão que {b} uma vez deu voltou à sua própria porta, e foi {a} quem o trouxe."],
        "INGRATITUDE": ["{a} enchera o cesto de {b} uma vez; quando o seu ficou vazio, a porta de {b} não se abriu. A aldeia guarda contas que nenhum livro vê, e essa ficou registada em todas as cabeças.",
                        "{b} devia a {a} o tipo de dívida que ninguém escreve, e saldou-a com uma porta fechada. Ninguém disse nada. Toda a gente contou."],
        "RESENTMENT": ["O favor pesava a {a}. É coisa difícil dever, e {a} começou a evitar o olhar de {b}.",
                       "{a} nunca tinha devolvido o que {b} lhe dera, e a dívida azedou, como a gratidão azeda quando se carrega demasiado tempo."],
        "BOND": ["{a} e {b} escolheram-se um ao outro antes que a estação mudasse. A aldeia soube antes de qualquer um deles dizer uma palavra.",
                 "O que crescera entre {a} e {b} tornou-se algo assumido. Partilharam pão e lar a partir daí."],
        "WIDOWING": ["{a} sobreviveu a {b}. A aldeia não deixou {a} {sozinho} com isso, que é assim que o luto se carrega num lugar como este.",
                     "Quando {b} morreu, {a} perdeu algo que não se perde da mesma forma que o resto."],
        "carried_by": " Foi {c} quem trouxe a história.",
        "grown": " A história cresceu pelo caminho.",
        "repeat_one": "Voltou a acontecer uma vez.",
        "repeat_many": "Voltou a acontecer {n} vezes, como se os rancores tivessem o seu próprio calendário.",
        "repeat_good_one": "E voltou a acontecer, em silêncio, quando foi preciso.",
        "repeat_good_many": "E voltou a acontecer {n} vezes, sem alarde; a bondade também tem o seu calendário.",
        "repeat_endless": "E assim continuou, estação após estação, até o contar perder sentido.",
        "repeat_good_endless": "E assim continuou, estação após estação; há coisas que não precisam de ser assinaladas para continuar.",
        "seasons_later": [
            "Várias estações passaram. Quando chegou {season}, o assunto não estava resolvido.",
            "Quando {season} voltou, nada se resolvera.",
        ],
        "year_later": "Passou um ano; quando chegou {season}, o assunto voltou.",
        "years_later": "{n} anos depois, quando {season} chegou, a aldeia ainda carregava isso.",
        "repeat_quarrel_one": "Voltaram a lutar, como se a primeira vez tivesse sido um ensaio.",
        "repeat_quarrel_many": "Voltaram a lutar {n} vezes. Nunca chegava a resolver-se nada.",
        "repeat_quarrel_endless": "E assim continuou a luta, estação após estação; há coisas que precisam de uma testemunha mais do que de uma resolução.",
        "repeat_refusal_one": "A porta voltou a fechar-se.",
        "repeat_refusal_many": "A porta fechou-se {n} vezes mais. A aldeia contou cada uma.",
        "repeat_gift_one": "O pão voltou a chegar, sem uma palavra.",
        "repeat_gift_many": "O pão chegou {n} vezes mais, sem cerimónia; é isso que o faz pão.",
        "close_relapse": "A paz que se fez não durou; há fissuras que querem ficar abertas.",
        "close_broken": "Ninguém arranjou nada. No fim, cruzavam-se sem uma palavra.",
        "close_uneasy": "Ficou entre eles uma paz incómoda, fina como o gelo de março.",
        "close_mended": "O que se quebrara, consertaram-no melhor do que era.",
        "close_warm": "Tiveram sorte um com o outro, e sabiam-no.",
        "close_widowed": "Tinham tido sorte um com o outro. O fim foi triste, mas era uma tristeza que a aldeia reconhecia.",
        "close_departed": "Antes de fechar o registo, {a} tinha ido embora — empurrado por uma frieza que a aldeia nunca soube nomear.",
        "close_departed_bonded": "O que {a} e o seu companheiro tinham construído não sobreviveu à frieza da aldeia. {a} partiu; o laço não sobreviveu à partida.",
        "title_reconciliation": "{a} e {b}: uma reconciliação",
        "title_estrangement": "{a} e {b}: um afastamento",
        "title_feud": "{a} e {b}: uma rivalidade",
        "title_bond": "{a} e {b}: uma amizade",
        "title_love": "{a} e {b}: um amor",
        "title_open": "{a} e {b}: um assunto por resolver",
        "title_debt": "{a} e {b}: uma dívida por saldar",
        "chronicle_title": ["Crónica de {village}",
                            "Registo de {village}",
                            "O que aconteceu em {village}"],
        "arrivals_note_1_named": "{name} chegou a {village} sem história que a aldeia conhecesse. A aldeia nunca sabe bem o que fazer com isso.",
        "prologue": [("{village} tinha {n} almas quando este registo se abriu, "
                      "e abrange {days} dos seus dias. "
                      "Nada do que aqui está foi inventado; apenas se olhou, e contou."),
                     ("Este é o registo de {village}, que tinha {n} pessoas quando se abriu. "
                      "Abrange {days} dos seus dias. "
                      "Nada foi inventado."),
                    ],
        "epilogue": [("Quando o registo fecha, {a} e {b} eram tão próximos quanto duas pessoas podem ser em {village}; "
                      "{c} e {d} ainda não se falavam."),
                     ("No fim, {a} e {b} ainda encontravam razões para se cruzar em {village}. "
                      "{c} e {d} ainda encontravam razões para não o fazer."),
                    ],
        "pride_note": "{count} vezes alguém em {village} passou fome antes de pedir ajuda. O orgulho é outra forma de fome.",
        "debt_note": "Quando o registo fecha, {count} favores em {village} ainda não tinham sido devolvidos. A aldeia não guardava essas contas em livro algum, por isso nenhuma se perdeu.",
        "deaths_note_1": "Uma alma em {village} não sobreviveu a estes anos. Uma aldeia carrega os seus mortos em silêncio, que é como os mortos acabam por carregar a aldeia.",
        "deaths_note_n": "{count} almas em {village} não sobreviveram a estes anos. Uma aldeia carrega os seus mortos em silêncio, que é como os mortos acabam por carregar a aldeia.",
        "arrivals_note_1": "Um estranho chegou a {village} neste tempo. A aldeia nunca sabe bem o que fazer com alguém que não tem história.",
        "arrivals_note_n": "{count} estranhos chegaram a {village} neste tempo. A aldeia nunca sabe bem o que fazer com alguém que não tem história.",
        "bonds_note_1": "Um laço formou-se em {village} neste tempo. A maioria das coisas duradouras começa sem que o momento seja assinalado.",
        "bonds_note_n": "{count} laços formaram-se em {village} neste tempo. A maioria das coisas duradouras começa sem que o momento seja assinalado.",
        "births_note_1": "Uma criança nasceu em {village} neste tempo.",
        "births_note_n": "{count} crianças nasceram em {village} neste tempo.",
        "growth_note": "Quando o registo fechou, {village} tinha mais almas do que quando se abriu.",
        "famine_note": "O ano {year} foi um ano de fome em {village}.",
        "birth_intro": ["{name}, {nascido} em {village}, era {adjs}.",
                        "{name} tinha crescido em {village} e era {adjs}."],
        "refusal_pride": [
            "O orgulho tem a sua própria forma de fome.",
            "Há quem prefira sofrer a ser visto a sofrer.",
        ],
        "gift_unexpected": [
            "A generosidade nem sempre é uma questão de caráter.",
            "Até os punhos fechados se abrem às vezes.",
        ],
        "MEDIATION_elder": [
            "Foi {c}, que já tinha visto o suficiente para saber como os rancores acabam, quem os fez sentar à mesma mesa. Algo se desatou.",
            "{c}, que havia vivido na aldeia tempo suficiente para recordar a última vez que isto acontecera, fê-los falar. Algo se desatou.",
        ],
        "died_starvation": "{a} não sobreviveu a esta crónica. Um longo inverno levou-{lo} antes que o relato fechasse.",
        "died_misfortune": "{a} não sobreviveu a esta crónica; um golpe súbito, quando já não havia nada com que resistir.",
        "died_old_age": [
            "{a} não sobreviveu a esta crónica. Tinha vivido em {village} tempo suficiente para fazer parte da sua memória; depois passou a ser apenas isso.",
            "{a} teve uma vida longa em {village}, e a aldeia mudou várias vezes à sua volta. Um fim diferente dos outros.",
        ],
        "died_leaving": "Deixou {names} para trás.",
        "BIRTH": [
            "Uma criança — {c} — chegou a eles. Há coisas que chegam sem cerimónia e que se fazem sentir por anos.",
            "{c} nasceu. A aldeia recebeu-{lo} como recebe sempre o que chega sem pedir.",
        ],
        "COMING_OF_AGE": "{c} cresceu. A aldeia contou mais um dos seus.",
        "elder_intro": [
            "{name}, que estava aqui há mais tempo do que ninguém e se lembrava do que outros tinham esquecido, era {adjs}.",
            "Toda a aldeia tinha ido ter com {name} pelo menos uma vez. {name} era {adjs}.",
        ],
        "QUARREL_private": [
            "{a} e {b} resolveram o assunto sem testemunhas. De manhã, a aldeia já sabia de qualquer modo.",
            "O que se passou entre {a} e {b} aconteceu sem que ninguém visse. As brigas privadas tendem a durar mais.",
        ],
        "winter_later": [
            "O inverno voltou, e com ele voltou o assunto por resolver.",
            "Chegou outro inverno. A versão fria de tudo o resto voltou também.",
        ],
        "dead_section": "## Depois",
        "legacy_generous": [
            "{name} foi a alma mais generosa que {village} conheceu. A aldeia ficou mais fria com a ausência.",
            "{name} nunca dispensou ninguém de mãos vazias. Esse tipo de pessoa não se substitui; nota-se a falta.",
        ],
        "legacy_proud": [
            "{name} partiu com as contas saldadas. Há quem não tolere deixar dívidas para trás.",
            "{name} manteve tudo equilibrado até ao fim. Uma perda complicada.",
        ],
        "legacy_diligent": [
            "{name} trabalhou mais do que ninguém. O que {name} mantinha a funcionar passava despercebido até parar.",
            "Os campos que {name} cuidava eram os mais bem tratados de {village}. Esse saber não se escreve.",
        ],
        "legacy_mediator": [
            "{name} tinha sentado mais vizinhos em conflito à mesma mesa do que ninguém. A aldeia sentiu a falta como se sente a falta de quem sabe acabar com as discussões.",
            "As pessoas iam ter com {name} com coisas que não podiam dizer em mais lado nenhum. Depois não ficou ninguém igual.",
        ],
        "legacy_bonded": [
            "{name} tinha construído uma vida com {partner} em {village}. Esse laço tornou-se parte da história da aldeia.",
            "O que {name} construiu aqui — os anos, o laço com {partner} — sobreviveu-lhe. Costuma acontecer.",
        ],
        "legacy_newcomer": [
            "{name} chegou a {village} sem história e foi-se com uma. É assim que o pertencer tem aspeto.",
            "{name} veio de fora e tornou-se parte do lugar mesmo assim. A aldeia carrega esse tipo de presença em silêncio.",
        ],
        "legacy_quiet": [
            "{name} não deixou uma marca ruidosa. Os silenciosos raramente a deixam, mas o lugar muda quando partem.",
            "{name} fazia parte do ruído de fundo que faz um lugar parecer habitado. O silêncio que ficou foi preciso.",
        ],
        "legacy_long_life": [
            "{name} tinha vivido em {village} tempo suficiente para lembrar o que mais ninguém podia. Esse tipo de testemunha não se substitui; perde-se.",
            "Os anos que {name} passou em {village} sobreviviram a várias versões do lugar. Quando partiu, foi com ela algo que a aldeia sabia de si mesma.",
        ],
        "arrival_arc_title": "{name}: uma chegada",
        "arrival_intro": [
            "{name} chegou {season_in}. {village} não estava à espera de ninguém.",
            "{name} chegou a {village} {season_in}, sem história que alguém aqui conhecesse.",
        ],
        "arrival_settled": [
            "Quando o registo fecha, {name} fazia parte de {village} como uma pedra faz parte de um muro — sem ruído, mas presente.",
            "Chegou sem conhecer ninguém e acabou fazendo parte de {village}. É assim que as aldeias absorvem quem chega.",
        ],
        "arrival_cold": [
            "Quando o registo fecha, {village} e {name} ainda não tinham chegado a entender-se de todo.",
            "Ficou entre {name} e a aldeia uma distância que não chegou a fechar.",
        ],
        "arrival_died": [
            "{name} não ficou tempo suficiente para ser plenamente conhecido. A aldeia anotou a perda como anota todas as coisas breves.",
            "{name} chegou e não sobreviveu a estes anos. Há histórias que começam e acabam antes de o relato as encontrar.",
        ],
        "village_section": "## A aldeia",
        "LEAN_SEASON": [
            "{village} atravessou {season} na fome. Mais de metade das casas tinham as despensas vazias, e ninguém fingia o contrário.",
            "A escassez chegou a {village} {season_in} de uma vez — não casa por casa, mas a todas ao mesmo tempo. Esse tipo de privação é diferente.",
            "{season_in}, a maior parte de {village} contava as reservas dia a dia. Os fornos eram cuidadosos e as crianças ficavam com o melhor do que havia.",
        ],
        "LEAN_SEASON_solidarity": [
            " Os que ainda tinham algo a dar deram sem que ninguém pedisse. A aldeia no seu melhor tem esse aspeto.",
            " Alguns esvaziaram parte das suas prateleiras nas dos vizinhos. Ninguém falou nisso depois.",
        ],
        "BOUNTY": [
            "{village} atravessou {season} na abundância. A maior parte das casas tinha mais do que suficiente, e o excedente sempre encontra a porta.",
            "{village} passou {season} com as despensas cheias. Os que se lembram dos anos de fome nunca dão isso por garantido.",
            "{season_in}, a aldeia estava bem alimentada e notava-se — noites mais longas, mais visitas, brigas que não chegavam a começar.",
        ],
        "DEPARTURE": [
            "{a} foi-se embora de {village}. Sem anúncio, sem despedida formal — uma manhã a ausência estava simplesmente lá.",
            "A notícia de que {a} tinha deixado {village} chegou como chegam sempre: alguém notou a falta, alguém o contou a alguém.",
        ],
        "departed_note": [
            "{a} deixou {village} antes de este registo fechar. A aldeia esfriara para com {a}, ou {a} para com ela — no fim, a ordem já não importava.",
            "{a} foi-se antes do final. Há pessoas que não esperam que uma aldeia decida o que pensa delas.",
        ],
        "departure_arc_title": "{name}: uma partida",
        "departure_section": "## Os que partiram",
        "departures_note_1": "Uma pessoa deixou {village} durante este tempo, antes de o registo fechar.",
        "departures_note_n": "{count} pessoas deixaram {village} durante este tempo, antes de o registo fechar.",
        "colophon": "*(semente do mundo: {seed} — corre-a de novo e as mesmas coisas acontecerão, na mesma ordem, às mesmas pessoas)*",
    },
    "it": {
        "seasons": ("la primavera", "l'estate", "l'autunno", "l'inverno"),
        "seasons_in": ("in primavera", "in estate", "in autunno", "in inverno"),
        "traits": {
            "diligence": (("instancabile", "instancabile"), ("pigro", "pigra")),
            "generosity": (("generoso", "generosa"), ("avaro", "avara")),
            "pride": (("orgoglioso", "orgogliosa"), ("umile", "umile")),
            "openness": (("loquace", "loquace"), ("riservato", "riservata")),
        },
        "intro": ["{name} era {adjs}.",
                  "Tutti conoscevano {name}, {adjs}."],
        "and": "e",
        "opening": ["Tutto iniziò {season}.",
                    "I primi segni si videro {season}."],
        "later_season": ["Arrivò {season}.", "Era già {season}."],
        "soon_after": ["Non passarono molti giorni.", "Poco dopo."],
        "GIFT": ["Quando le provviste di {b} si svuotarono, {a} riempì il cesto senza che nessuno glielo chiedesse.",
                 "{a} condivise il pane con {b} in un momento difficile, e non fu dimenticato."],
        "REFUSAL": ["{a} andò affamato alla porta di {b} e tornò a mani vuote.",
                    "{b} mandò via {a} senza nulla, e tutto il villaggio ne sentì il freddo."],
        "OFFENSE": ["La voce arrivò a {a} che {b} stava parlando della faccenda a porte chiuse.",
                    "Qualcuno si incaricò di far sapere a {a} quello che {b} andava dicendo."],
        "QUARREL": ["{a} e {b} litigarono dove tutti potevano sentirli, e il villaggio finse di non ascoltare.",
                    "Tra {a} e {b} ci furono parole grosse, in piena strada."],
        "MEDIATION": ["{c} li sedette allo stesso tavolo e non lasciò andare nessuno dei due in collera. Qualcosa si allentò.",
                      "Ci volle {c}, di cui si fidavano entrambi, perché si parlassero di nuovo."],
        "REPAYMENT": ["{a} non aveva dimenticato il vecchio favore, e quando il bisogno bussò a casa di {b}, lo restituì senza dire una parola.",
                      "Il pane che {b} aveva dato tornò alla sua stessa porta, e fu {a} a portarlo."],
        "INGRATITUDE": ["{a} aveva riempito il cesto di {b} una volta; quando il suo rimase vuoto, la porta di {b} non si aprì. Il villaggio tiene conti che nessun registro vede, e quello fu annotato in ogni testa.",
                        "{b} doveva a {a} il tipo di debito che nessuno scrive, e lo pagò con la porta chiusa. Nessuno disse nulla. Tutti contarono."],
        "RESENTMENT": ["Il favore pesava a {a}. È dura dover qualcosa, e {a} cominciò ad evitare lo sguardo di {b}.",
                       "{a} non aveva mai restituito quel che {b} gli aveva dato un giorno, e il debito inasprì, come inasprisce la gratitudine quando si porta troppo a lungo."],
        "BOND": ["{a} e {b} si scelsero prima che cambiasse la stagione. Il villaggio lo sapeva già prima che uno dei due dicesse una parola.",
                 "Quello che era cresciuto tra {a} e {b} divenne qualcosa di dichiarato. Condivisero pane e focolare da allora in poi."],
        "WIDOWING": ["{a} sopravvisse a {b}. Il villaggio non lasciò {a} {solo} con il dolore, che è il modo in cui si porta il lutto in un posto così.",
                     "Quando {b} morì, {a} perse qualcosa che non si perde allo stesso modo del resto."],
        "carried_by": " Fu {c} a portare la storia.",
        "grown": " La storia si era ingrandita per strada.",
        "repeat_one": "Accadde ancora una volta.",
        "repeat_many": "Accadde ancora {n} volte, come se i rancori tenessero un loro calendario.",
        "repeat_good_one": "E accadde di nuovo, in silenzio, quando ce n'era bisogno.",
        "repeat_good_many": "E accadde ancora {n} volte, senza che nessuno ne facesse caso; anche la bontà ha il suo calendario.",
        "repeat_endless": "E così continuò, stagione dopo stagione, finché contare perse di senso.",
        "repeat_good_endless": "E così continuò, stagione dopo stagione; ci sono cose che non hanno bisogno di essere notate per andare avanti.",
        "seasons_later": [
            "Passarono alcune stagioni. Quando arrivò {season}, la faccenda era ancora aperta.",
            "Tornò {season}, e nulla era stato risolto.",
        ],
        "year_later": "Passò un anno; quando arrivò {season}, la faccenda era ancora lì.",
        "years_later": "{n} anni dopo, quando arrivò {season}, il villaggio la portava ancora.",
        "repeat_quarrel_one": "Litigarono di nuovo, come se la prima volta fosse stata una prova.",
        "repeat_quarrel_many": "Litigarono ancora {n} volte. Non si risolveva mai nulla.",
        "repeat_quarrel_endless": "E così continuò la lite, stagione dopo stagione; ci sono cose che hanno bisogno di un testimone più che di una soluzione.",
        "repeat_refusal_one": "La porta rimase chiusa ancora una volta.",
        "repeat_refusal_many": "La porta rimase chiusa ancora {n} volte. Il villaggio le contò tutte.",
        "repeat_gift_one": "Il pane arrivò di nuovo, senza dire nulla.",
        "repeat_gift_many": "Il pane arrivò ancora {n} volte, senza cerimonie; è quello che lo fa essere pane.",
        "close_relapse": "La pace che fu fatta non tenne; ci sono crepe che vogliono restare aperte.",
        "close_broken": "Nessuno la rattoppò. Alla fine si incrociavano senza dire una parola.",
        "close_uneasy": "Rimase tra loro una pace precaria, sottile come il ghiaccio di marzo.",
        "close_mended": "Quello che si era rotto, lo rattopparono meglio di prima.",
        "close_warm": "Furono fortunati l'uno con l'altro, e lo sapevano.",
        "close_widowed": "Erano stati fortunati l'uno con l'altro. Il finale fu triste, ma era una tristezza che il villaggio riconosceva.",
        "close_departed": "Prima che il registro si chiudesse, {a} era andato via — spinto da una freddezza che il villaggio non seppe mai nominare.",
        "close_departed_bonded": "Ciò che {a} e il suo compagno avevano costruito non sopravvisse alla freddezza del villaggio. {a} partì; il legame non sopravvisse alla partenza.",
        "title_reconciliation": "{a} e {b}: una riconciliazione",
        "title_estrangement": "{a} e {b}: un allontanamento",
        "title_feud": "{a} e {b}: una rivalità",
        "title_bond": "{a} e {b}: un'amicizia",
        "title_love": "{a} e {b}: un amore",
        "title_open": "{a} e {b}: una faccenda in sospeso",
        "title_debt": "{a} e {b}: un debito non saldato",
        "chronicle_title": ["Cronaca di {village}",
                            "Registro di {village}",
                            "Quel che accadde a {village}"],
        "arrivals_note_1_named": "{name} arrivò a {village} senza una storia che il villaggio conoscesse. Non si sa mai bene cosa fare con qualcuno che non ha storia.",
        "prologue": [("{village} contava {n} anime all'apertura di questo registro, "
                      "e abbraccia {days} dei loro giorni. "
                      "Nulla di ciò che segue è inventato; è stato solo osservato, e raccontato."),
                     ("{village} aveva {n} persone quando questo registro fu aperto. "
                      "Abbraccia {days} dei loro giorni. "
                      "Nulla è inventato."),
                    ],
        "epilogue": [("Quando il registro si chiude, {a} e {b} erano quanto di più vicino ci sia a inseparabili a {village}; "
                      "{c} e {d} ancora non si parlavano."),
                     ("Alla fine, {a} e {b} trovavano ancora ragioni per incontrarsi a {village}. "
                      "{c} e {d} trovavano ancora ragioni per non farlo."),
                    ],
        "pride_note": "{count} volte qualcuno a {village} patì la fame piuttosto che chiedere aiuto. L'orgoglio è la sua stessa forma di carestia.",
        "debt_note": "Alla chiusura del registro, a {village} c'erano ancora {count} favori non restituiti. Il villaggio non li teneva in nessun libro, ed è per questo che nessuno andò perduto.",
        "deaths_note_1": "Un'anima di {village} non sopravvisse a questi anni. Un villaggio porta i suoi morti in silenzio, ed è così che i morti finiscono per portare il villaggio.",
        "deaths_note_n": "{count} anime di {village} non sopravvissero a questi anni. Un villaggio porta i suoi morti in silenzio, ed è così che i morti finiscono per portare il villaggio.",
        "arrivals_note_1": "Uno straniero arrivò a {village} in questo tempo. Il villaggio non sa mai bene cosa fare con qualcuno che non ha storia.",
        "arrivals_note_n": "{count} stranieri arrivarono a {village} in questo tempo. Il villaggio non sa mai bene cosa fare con qualcuno che non ha storia.",
        "bonds_note_1": "Un legame si formò a {village} in questo tempo. La maggior parte delle cose durature inizia senza che nessuno segni il momento.",
        "bonds_note_n": "{count} legami si formarono a {village} in questo tempo. La maggior parte delle cose durature inizia senza che nessuno segni il momento.",
        "births_note_1": "Un bambino nacque a {village} in questo tempo.",
        "births_note_n": "{count} bambini nacquero a {village} in questo tempo.",
        "growth_note": "Alla chiusura del registro, {village} contava più anime di quante ne avesse all'apertura.",
        "famine_note": "L'anno {year} fu un anno di fame a {village}.",
        "birth_intro": ["{name}, {nato} a {village}, era {adjs}.",
                        "Tutti a {village} conoscevano {name}, {adjs}, fin dall'infanzia."],
        "refusal_pride": [
            "L'orgoglio è la sua stessa forma di carestia.",
            "C'è chi preferisce soffrire piuttosto che essere visto soffrire.",
        ],
        "gift_unexpected": [
            "La generosità non è sempre una questione di carattere.",
            "Anche i pugni chiusi si aprono, a volte.",
        ],
        "MEDIATION_elder": [
            "Fu {c}, {anziano}, a farli sedere allo stesso tavolo. Ci sono cose che cedono solo alla pazienza degli anni.",
            "{c}, che aveva visto abbastanza inverni da sapere come finiscono i rancori, li fece parlare. Qualcosa si allentò.",
        ],
        "died_starvation": "{a} non sopravvisse a questa cronaca. Un lungo inverno pose fine ai suoi giorni prima che il resoconto si chiudesse.",
        "died_misfortune": "{a} non sopravvisse a questa cronaca; un colpo improvviso, quando non restava più nulla con cui resistere.",
        "died_old_age": [
            "{a} non sopravvisse a questa cronaca. Aveva vissuto a {village} abbastanza a lungo da essere parte della sua memoria; poi ne divenne soltanto questo.",
            "{a} ebbe una vita lunga a {village}, e il villaggio cambiò più volte attorno a {a}. Un finale diverso dagli altri.",
        ],
        "died_leaving": "Lasciò {names} dietro di sé.",
        "BIRTH": [
            "Un bambino — {c} — arrivò a loro. Ci sono cose che arrivano senza cerimonie e si fanno sentire per anni.",
            "Nacque {c}, e il villaggio {lo} accolse come accoglie sempre ciò che arriva senza chiedere.",
        ],
        "COMING_OF_AGE": "{c} crebbe. Il villaggio contò un adulto in più tra i propri.",
        "elder_intro": [
            "{name}, che era qui da più tempo di chiunque altro e ricordava quello che gli altri avevano dimenticato, era {adjs}.",
            "Tutti erano andati da {name} almeno una volta. {name} era {adjs}.",
        ],
        "QUARREL_private": [
            "{a} e {b} la risolsero senza testimoni. La mattina dopo il villaggio lo sapeva comunque.",
            "Quel che passò tra {a} e {b} passò senza che nessuno lo vedesse. Le liti private tendono a durare di più.",
        ],
        "winter_later": [
            "Tornò l'inverno, e con lui tornò la vecchia faccenda irrisolta.",
            "Arrivò un altro inverno. La versione fredda di tutto il resto tornò con lui.",
        ],
        "dead_section": "## Dopo",
        "legacy_generous": [
            "{name} fu l'anima più generosa che {village} avesse conosciuto. Il villaggio sentì il freddo della sua assenza.",
            "{name} non aveva mai rimandato nessuno a mani vuote. Quel tipo di persona non si sostituisce; si nota quando manca.",
        ],
        "legacy_proud": [
            "{name} se ne andò con i conti in pareggio. C'è chi non sopporta di lasciare debiti.",
            "{name} aveva tenuto tutto in equilibrio fino alla fine. Una perdita complicata.",
        ],
        "legacy_diligent": [
            "{name} aveva lavorato più di chiunque altro. Quello che {name} teneva in piedi passava inosservato finché non si fermò.",
            "I campi che {name} curava erano i meglio tenuti di {village}. Quel sapere non si scrive.",
        ],
        "legacy_mediator": [
            "{name} aveva fatto sedere allo stesso tavolo più vicini in lite di chiunque altro. Il villaggio sentì la mancanza come si sente quella di chi sa fare tacere le liti.",
            "La gente andava da {name} con cose che non poteva dire altrove. Poi non rimase nessuno così.",
        ],
        "legacy_bonded": [
            "{name} aveva costruito una vita con {partner} a {village}. Quel legame divenne parte della storia del villaggio.",
            "Quello che {name} aveva costruito qui — gli anni, il legame con {partner} — lo sopravvisse. Di solito è così.",
        ],
        "legacy_newcomer": [
            "{name} arrivò a {village} senza una storia e se ne andò con una. È così che si vede l'appartenenza.",
            "{name} venne da fuori e diventò parte del posto comunque. Il villaggio porta quel tipo di presenza in silenzio.",
        ],
        "legacy_quiet": [
            "{name} non lasciò un'impronta rumorosa. I silenziosi raramente lo fanno, ma il posto cambia quando se ne vanno.",
            "{name} faceva parte del rumore di fondo che rende un posto abitato. Il silenzio che rimase fu preciso.",
        ],
        "legacy_long_life": [
            "{name} aveva vissuto a {village} abbastanza a lungo da ricordare quello che nessun altro poteva. Quel tipo di testimone non si sostituisce; si perde.",
            "Gli anni che {name} trascorse a {village} sopravvissero a diverse versioni del posto. Quando {name} se ne andò, se ne andò qualcosa che il villaggio sapeva di sé.",
        ],
        "arrival_arc_title": "{name}: un arrivo",
        "arrival_intro": [
            "{name} arrivò {season_in}. {village} non aspettava nessuno.",
            "{name} giunse a {village} {season_in}, senza una storia che qualcuno qui conoscesse.",
        ],
        "arrival_settled": [
            "Alla chiusura del registro, {name} faceva parte di {village} come una pietra fa parte di un muro — senza rumore, ma presente.",
            "{name} era arrivato senza conoscere nessuno e se ne andò come parte di {village}. I villaggi si fanno così.",
        ],
        "arrival_cold": [
            "Alla chiusura del registro, {village} e {name} non si erano ancora capiti del tutto.",
            "Rimase tra {name} e il villaggio una distanza che non si chiuse mai del tutto.",
        ],
        "arrival_died": [
            "{name} non restò abbastanza a lungo per essere pienamente conosciuto. Il villaggio annotò la perdita come annota tutte le cose brevi.",
            "{name} arrivò e non sopravvisse a questi anni. Ci sono storie che iniziano e finiscono prima che il racconto le trovi.",
        ],
        "village_section": "## Il villaggio",
        "LEAN_SEASON": [
            "{village} attraversò {season} nella fame. Più della metà delle case aveva le dispense vuote, e nessuno fingeva il contrario.",
            "La scarsità colpì {village} {season_in} tutta in una volta — non una casa alla volta, ma tutte insieme. Quel tipo di fame è diverso.",
            "{season_in}, la maggior parte di {village} contava le riserve giorno per giorno. I forni erano prudenti e i bambini ricevevano il meglio di quel che restava.",
        ],
        "LEAN_SEASON_solidarity": [
            " Chi aveva ancora qualcosa da dare lo diede senza che nessuno lo chiedesse. Il villaggio nel suo meglio ha quell'aspetto.",
            " Alcuni svuotarono parte dei propri scaffali in quelli dei vicini. Nessuno ne parlò dopo.",
        ],
        "BOUNTY": [
            "{village} attraversò {season} nell'abbondanza. La maggior parte delle case aveva più del necessario, e il surplus trova sempre la porta.",
            "{village} passò {season} con le dispense piene. Chi ricorda gli anni di fame non lo dà mai per scontato.",
            "{season_in}, il villaggio era ben nutrito e si vedeva — serate più lunghe, più visite, liti che non iniziavano mai del tutto.",
        ],
        "DEPARTURE": [
            "{a} lasciò {village}. Senza annuncio, senza vero commiato — un mattino l'assenza era semplicemente lì.",
            "La notizia che {a} aveva lasciato {village} si sparse come si spargono sempre: qualcuno notò l'assenza, qualcuno ne parlò.",
        ],
        "departed_note": [
            "{a} lasciò {village} prima che questo registro si chiudesse. Il villaggio si era raffreddato verso {a}, o viceversa — alla fine, l'ordine non contava più.",
            "{a} se ne andò prima della fine. Alcune persone non aspettano che un villaggio decida cosa pensa di loro.",
        ],
        "departure_arc_title": "{name}: una partenza",
        "departure_section": "## Chi se ne andò",
        "departures_note_1": "Una persona lasciò {village} durante questo periodo, prima che il registro si chiudesse.",
        "departures_note_n": "{count} persone lasciarono {village} durante questo periodo, prima che il registro si chiudesse.",
        "colophon": "*(seme del mondo: {seed} — eseguilo di nuovo e le stesse cose accadranno, nello stesso ordine, alle stesse persone)*",
    },
}


class Narrator:
    def __init__(self, world, lang: str = "en", seed: int = 0, narrator_seed: int | None = None):
        self.world = world
        self.lang = lang
        self.t = TEXT[lang]
        nseed = narrator_seed if narrator_seed is not None else (seed ^ 0xFAB)
        self.rng = random.Random(nseed)
        self.village = self.rng.choice(VILLAGE_NAMES[lang])
        self._introduced: set = set()

    def _gform(self, cid: int, m: str, f: str) -> str:
        """Return the masculine or feminine form of a word for this character."""
        return m if self.world.char(cid).gender == "m" else f

    # ------------------------------------------------------------------
    # picking what deserves telling

    def arcs(self):
        pairs: dict = {}
        for ev in self.world.events:
            if ev.kind in ARC_KINDS:
                key = frozenset(ev.actors[:2])
                pairs.setdefault(key, []).append(ev)
        # Attach birth and coming-of-age to bonded pairs so family arcs feel complete.
        bond_pairs = {key for key, evs in pairs.items() if any(e.kind == "BOND" for e in evs)}
        for ev in self.world.events:
            if ev.kind == "BIRTH":
                pair_key = frozenset(ev.actors[1:3])
                if pair_key in bond_pairs:
                    pairs[pair_key].append(ev)
            elif ev.kind == "COMING_OF_AGE":
                child = self.world.char(ev.actors[0])
                if child.parent_ids:
                    pair_key = frozenset(child.parent_ids)
                    if pair_key in bond_pairs:
                        pairs[pair_key].append(ev)
        # Re-sort each arc by tick after adding family events.
        for key in pairs:
            pairs[key].sort(key=lambda e: e.tick)
        scored = []
        for key, events in pairs.items():
            if len(events) < 2:
                continue
            scored.append((self.drama(events), key, events))
        scored.sort(key=lambda item: -item[0])
        max_arcs = max(3, self.world.tick // 96)
        chosen, appearances = [], {}
        for score, key, events in scored:
            if score < 1.0 or len(chosen) == max_arcs:
                break
            if any(appearances.get(cid, 0) >= 2 for cid in key):
                continue  # no one gets to star in every story
            for cid in key:
                appearances[cid] = appearances.get(cid, 0) + 1
            chosen.append((key, events))
        return chosen

    def drama(self, events):
        score = sum(abs(ev.valence) for ev in events)
        means = [sum(ev.data["affinity"]) / 2 for ev in events if "affinity" in ev.data]
        poles = [1 if m > 0.1 else -1 for m in means if abs(m) > 0.1]
        flips = sum(1 for x, y in zip(poles, poles[1:]) if x != y)
        score += 2.0 * flips
        kinds = {ev.kind for ev in events}
        score += 0.75 * len(kinds)  # varied arcs read better than one scene on repeat
        if "MEDIATION" in kinds:
            score += 1.5
        if "GIFT" in kinds and ("QUARREL" in kinds or "OFFENSE" in kinds):
            score += 1.0
        if "INGRATITUDE" in kinds:
            score += 1.5  # a kindness betrayed is the oldest story there is
        if "RESENTMENT" in kinds or "REPAYMENT" in kinds:
            score += 1.0  # what a debt does to people, either way it goes
        if "BOND" in kinds:
            score += 2.5  # a bond formed is inherently dramatic
        if "WIDOWING" in kinds:
            score += 3.0  # love and loss: the oldest arc
        if "BIRTH" in kinds or "COMING_OF_AGE" in kinds:
            score += 1.5  # family arcs feel complete
        if any(season_index(ev.tick) == 3 for ev in events):
            score += 0.3  # winter gives weight to a story
        return score

    # ------------------------------------------------------------------
    # rendering helpers

    def pick(self, key, **fields):
        return self.rng.choice(self.t[key]).format(**fields)

    def season_name(self, tick):
        return self.t["seasons"][season_index(tick)]

    def name(self, cid):
        return self.world.char(cid).name

    def adjectives(self, char):
        traits = {
            "diligence": char.diligence, "generosity": char.generosity,
            "pride": char.pride, "openness": char.openness,
        }
        chosen = sorted(traits, key=lambda k: -abs(traits[k] - 0.5))[:2]
        out = []
        for key in chosen:
            pair = self.t["traits"][key]
            adj = pair[0] if traits[key] >= 0.5 else pair[1]
            if isinstance(adj, tuple):  # gendered language
                adj = adj[0] if char.gender == "m" else adj[1]
            out.append(adj)
        return out

    def introduce(self, char):
        if char.id in self._introduced:
            return None
        self._introduced.add(char.id)
        adj1, adj2 = self.adjectives(char)
        conj = self.t["and"]
        # Spanish/Portuguese vowel harmony: "e" before e/i/hi
        if self.lang in ("es", "pt") and (adj2[:1] in ("e", "i") or adj2[:2] == "hi"):
            conj = "e"
        adjs = f"{adj1} {conj} {adj2}"
        if char.elder and char.parent_ids is None and "elder_intro" in self.t:
            fields: dict = {"name": char.name, "adjs": adjs}
            if self.lang == "es":
                fields["lo"] = self._gform(char.id, "lo", "la")
                fields["anciano"] = self._gform(char.id, "anciano", "anciana")
                key = ("elder_intro_m" if char.gender == "m" and "elder_intro_m" in self.t
                       else "elder_intro")
            else:
                key = "elder_intro"
            return self.rng.choice(self.t[key]).format(**fields)
        if char.parent_ids is not None and "birth_intro" in self.t:
            fields: dict = {"name": char.name, "adjs": adjs, "village": self.village}
            if self.lang == "es":
                fields["nacido"] = self._gform(char.id, "nacido", "nacida")
                key = ("birth_intro_m" if char.gender == "m" and "birth_intro_m" in self.t
                       else "birth_intro")
            elif self.lang == "fr":
                fields["ne"] = self._gform(char.id, "né", "née")
                key = "birth_intro"
            elif self.lang == "pt":
                fields["nascido"] = self._gform(char.id, "nascido", "nascida")
                key = "birth_intro"
            elif self.lang == "it":
                fields["nato"] = self._gform(char.id, "nato", "nata")
                key = "birth_intro"
            else:
                key = "birth_intro"
            return self.rng.choice(self.t[key]).format(**fields)
        key = "intro_m" if (self.lang == "es" and char.gender == "m"
                            and "intro_m" in self.t) else "intro"
        return self.pick(key, name=char.name, adjs=adjs)

    def connector(self, prev, ev):
        if prev is None:
            bare = self.t.get("seasons_in", self.t["seasons"])
            return self.pick("opening", season=bare[season_index(ev.tick)])
        gap = ev.tick // TICKS_PER_SEASON - prev.tick // TICKS_PER_SEASON
        if gap == 0:
            return self.pick("soon_after")
        sname = self.season_name(ev.tick)
        # Family events don't carry conflict framing regardless of how much time passed.
        if ev.kind in ("BIRTH", "COMING_OF_AGE"):
            text = self.pick("later_season", season=sname)
            return text[0].upper() + text[1:]
        if gap >= 8 and "years_later" in self.t:
            return self.t["years_later"].format(n=gap // 4, season=sname)
        if gap >= 4 and "year_later" in self.t:
            return self.t["year_later"].format(season=sname)
        if gap >= 2 and season_index(ev.tick) == 3 and "winter_later" in self.t:
            if ev.kind not in ("BIRTH", "COMING_OF_AGE"):
                return self.rng.choice(self.t["winter_later"])
        if gap >= 2 and "seasons_later" in self.t:
            return self.pick("seasons_later", season=sname)
        text = self.pick("later_season", season=sname)
        return text[0].upper() + text[1:]

    def beat(self, ev):
        if ev.kind == "BIRTH":
            child_id = ev.actors[0]
            fields = {"c": self.name(child_id),
                      "a": self.name(ev.actors[1]), "b": self.name(ev.actors[2])}
            if self.lang in ("fr", "pt", "it"):
                _m = {"fr": "le", "pt": "o", "it": "lo"}
                _f = {"fr": "la", "pt": "a", "it": "la"}
                fields["lo"] = self._gform(child_id, _m[self.lang], _f[self.lang])
            return self.rng.choice(self.t["BIRTH"]).format(**fields)
        if ev.kind == "COMING_OF_AGE":
            return self.t["COMING_OF_AGE"].format(c=self.name(ev.actors[0]))
        a, b = ev.actors[0], ev.actors[1]
        fields = {"a": self.name(a), "b": self.name(b)}
        if ev.kind == "MEDIATION":
            mid = ev.data["mediator"]
            mediator = self.world.char(mid)
            fields["c"] = self.name(mid)
            if mediator.elder and "MEDIATION_elder" in self.t:
                if self.lang == "es":
                    fields["anciano"] = self._gform(mid, "anciano", "anciana")
                elif self.lang == "fr":
                    fields["ancien"] = self._gform(mid, "l'ancien", "l'ancienne")
                elif self.lang == "it":
                    fields["anziano"] = self._gform(mid, "l'anziano", "l'anziana")
                return self.rng.choice(self.t["MEDIATION_elder"]).format(**fields)
        if ev.kind == "WIDOWING":
            # gender-agreeing words for the survivor ({a})
            if self.lang == "es":
                fields["solo"] = self._gform(a, "solo", "sola")
            elif self.lang == "fr":
                fields["seul"] = self._gform(a, "seul", "seule")
            elif self.lang == "pt":
                fields["sozinho"] = self._gform(a, "sozinho", "sozinha")
            elif self.lang == "it":
                fields["solo"] = self._gform(a, "solo", "sola")
        if ev.kind == "QUARREL" and not ev.data.get("witnesses") and "QUARREL_private" in self.t:
            text = self.pick("QUARREL_private", **fields)
        else:
            text = self.pick(ev.kind, **fields)
        if ev.kind == "OFFENSE":
            if ev.data.get("via") is not None:
                text += self.t["carried_by"].format(c=self.name(ev.data["via"]))
            if ev.data.get("distorted"):
                text += self.t["grown"]
        elif ev.kind == "REFUSAL":
            refuser = self.world.char(a)
            if refuser.pride > 0.62 and self.rng.random() < 0.30 and "refusal_pride" in self.t:
                text += " " + self.rng.choice(self.t["refusal_pride"])
        elif ev.kind == "GIFT":
            donor = self.world.char(a)
            if donor.generosity < 0.35 and self.rng.random() < 0.25 and "gift_unexpected" in self.t:
                text += " " + self.rng.choice(self.t["gift_unexpected"])
        return text

    def death_cause(self, cid: int) -> str | None:
        """Return the cause of death for a character, or None if still living."""
        for ev in self.world.events:
            if ev.kind == "DEATH" and cid in ev.actors:
                return ev.data.get("cause", "starvation")
        return None

    def _survivors_of(self, cid: int) -> dict | None:
        """Return a {names: ...} dict for the survivors of the deceased, or None."""
        survivor_id = None
        for ev in self.world.events:
            if ev.kind == "WIDOWING" and ev.actors[1] == cid:
                survivor_id = ev.actors[0]
                break
        children = [ch for ch in self.world.chars
                    if ch.parent_ids and cid in ch.parent_ids and ch.alive]
        names = []
        if survivor_id is not None and self.world.char(survivor_id).alive:
            names.append(self.name(survivor_id))
        names += [ch.name for ch in children]
        if not names:
            return None
        conj = self.t["and"]
        if len(names) == 1:
            combined = names[0]
        elif len(names) == 2:
            combined = f"{names[0]} {conj} {names[1]}"
        else:
            combined = ", ".join(names[:-1]) + f" {conj} {names[-1]}"
        return {"names": combined}

    def death_note(self, cid: int) -> str | None:
        """Render the death postscript for a character, or None if still living."""
        cause = self.death_cause(cid)
        if cause is None:
            return None
        dead = self.world.char(cid)
        fields: dict = {"a": self.name(cid), "village": self.village}
        if self.lang == "pt":
            fields["lo"] = self._gform(cid, "o", "a")
        tmpl = self.t[f"died_{cause}"]
        note = (self.rng.choice(tmpl) if isinstance(tmpl, list) else tmpl).format(**fields)
        survivors = self._survivors_of(cid)
        if survivors and "died_leaving" in self.t:
            if self.lang == "fr":
                leaving = {"su": "Il" if dead.gender == "m" else "Elle",
                           "lu": "lui" if dead.gender == "m" else "elle",
                           **survivors}
            else:
                leaving = survivors
            note += " " + self.t["died_leaving"].format(**leaving)
        return note

    def departure_note(self, cid: int) -> str | None:
        """Postscript for a character who left the village, or None if they stayed/died."""
        char = self.world.char(cid)
        if char.alive or not char.departed:
            return None
        if "departed_note" not in self.t:
            return None
        tmpl = self.t["departed_note"]
        return (self.rng.choice(tmpl) if isinstance(tmpl, list) else tmpl).format(
            a=self.name(cid), village=self.village)

    # ------------------------------------------------------------------
    # assembling the chronicle

    def death_legacy(self, cid: int) -> str | None:
        """One evocative sentence about how the village remembers a dead character."""
        char = self.world.char(cid)
        if char.alive:
            return None
        mediations = sum(1 for ev in self.world.events
                         if ev.kind == "MEDIATION" and ev.data.get("mediator") == cid)
        was_bonded = any(ev.kind == "BOND" and cid in ev.actors for ev in self.world.events)
        fields: dict = {"name": char.name, "village": self.village}
        if mediations >= 2 and "legacy_mediator" in self.t:
            return self.rng.choice(self.t["legacy_mediator"]).format(**fields)
        if char.generosity > 0.72 and "legacy_generous" in self.t:
            return self.rng.choice(self.t["legacy_generous"]).format(**fields)
        if char.pride > 0.72 and "legacy_proud" in self.t:
            return self.rng.choice(self.t["legacy_proud"]).format(**fields)
        if char.diligence > 0.72 and "legacy_diligent" in self.t:
            return self.rng.choice(self.t["legacy_diligent"]).format(**fields)
        if was_bonded and "legacy_bonded" in self.t:
            bond_ev = next((ev for ev in self.world.events if ev.kind == "BOND" and cid in ev.actors), None)
            if bond_ev:
                partner_id = next(x for x in bond_ev.actors if x != cid)
                fields["partner"] = self.name(partner_id)
            return self.rng.choice(self.t["legacy_bonded"]).format(**fields)
        if char.joined_at > 0 and "legacy_newcomer" in self.t:
            return self.rng.choice(self.t["legacy_newcomer"]).format(**fields)
        if (self.death_cause(cid) == "old_age" and "legacy_long_life" in self.t):
            return self.rng.choice(self.t["legacy_long_life"]).format(**fields)
        if "legacy_quiet" in self.t:
            return self.rng.choice(self.t["legacy_quiet"]).format(**fields)
        return None

    def tell_dead(self) -> list[str]:
        """Legacy notes for dead characters as a section (excludes those who departed)."""
        w = self.world
        dead = [c for c in w.chars if not c.alive and not c.departed]
        if not dead or "dead_section" not in self.t:
            return []
        legacies = [(c, self.death_legacy(c.id)) for c in dead]
        legacies = [(c, leg) for c, leg in legacies if leg]
        if not legacies:
            return []
        parts: list[str] = [self.t["dead_section"], ""]
        for _, leg in legacies:
            parts.append(leg)
            parts.append("")
        return parts

    def departure_arcs(self, pair_arcs: list) -> list:
        """Departed characters with enough unclaimed history for their own arc."""
        w = self.world
        claimed_ids = {ev.data["id"] for _, evs in pair_arcs for ev in evs}
        departed = [c for c in w.chars if not c.alive and c.departed]
        result = []
        for c in departed:
            events = [ev for ev in w.events
                      if ev.kind in ARC_KINDS and c.id in ev.actors[:2]
                      and ev.data["id"] not in claimed_ids]
            if len(events) < 2:
                continue
            result.append((c.id, events))
        return result

    def tell_departure_arc(self, cid: int, events: list) -> str | None:
        """An arc about how someone came to be pushed out of the village."""
        if "departure_arc_title" not in self.t:
            return None
        char = self.world.char(cid)
        title = self.t["departure_arc_title"].format(name=char.name)
        lines = ["## " + title, ""]
        intro = self.introduce(char)
        if intro:
            lines.append(intro)
            lines.append("")
        body_events = sorted(events, key=lambda e: e.tick)[:4]
        body, prev = [], None
        for ev in body_events:
            body.append(self.connector(prev, ev) + " " + self.beat(ev))
            prev = ev
        if body:
            lines.append(" ".join(body))
            lines.append("")
        note = self.departure_note(cid)
        if note:
            lines.append(note)
        return "\n".join(lines)

    def tell_departures(self, exclude: set | None = None) -> list[str]:
        """Short notes for departed characters not covered by a departure arc."""
        w = self.world
        exclude = exclude or set()
        departed = [c for c in w.chars if not c.alive and c.departed and c.id not in exclude]
        if not departed or "departed_note" not in self.t:
            return []
        parts: list[str] = []
        if "departure_section" in self.t:
            parts.append(self.t["departure_section"])
            parts.append("")
        for c in departed:
            note = self.departure_note(c.id)
            if note:
                parts.append(note)
                parts.append("")
        return parts

    def arrival_arcs(self, pair_arcs: list) -> list:
        """Return arrival arcs for newcomers with enough history outside the pair arcs."""
        w = self.world
        claimed_ids = {ev.data["id"] for _, evs in pair_arcs for ev in evs}
        newcomers = [c for c in w.chars if c.joined_at > 0]
        result = []
        for c in newcomers:
            if w.tick - c.joined_at < TICKS_PER_SEASON * 2:
                continue
            events = [ev for ev in w.events
                      if ev.kind in ARC_KINDS and c.id in ev.actors[:2]
                      and ev.tick > c.joined_at
                      and ev.data["id"] not in claimed_ids]
            if len(events) < 2:
                continue
            result.append((c.id, events))
        result.sort(key=lambda x: -len(x[1]))
        return result[:1]

    def tell_arrival_arc(self, cid: int, events: list) -> str | None:
        """A short arc about a newcomer's integration into the village."""
        if "arrival_arc_title" not in self.t:
            return None
        char = self.world.char(cid)
        title = self.t["arrival_arc_title"].format(name=char.name)
        lines = ["## " + title, ""]
        intro_sentence = self.introduce(char)
        if intro_sentence:
            lines.append(intro_sentence)
            lines.append("")
        arrival_ev = next(
            (ev for ev in self.world.events if ev.kind == "ARRIVAL" and ev.actors[0] == cid), None)
        ref_tick = arrival_ev.tick if arrival_ev else events[0].tick
        sname = self.season_name(ref_tick)
        seasons_in_list = self.t.get("seasons_in", self.t["seasons"])
        sname_in = seasons_in_list[season_index(ref_tick)]
        arrival_text = self.rng.choice(self.t["arrival_intro"]).format(
            name=char.name, season=sname, season_in=sname_in, village=self.village)
        body_events = sorted(events, key=lambda e: e.tick)[:3]
        body, prev = [arrival_text], arrival_ev
        for ev in body_events:
            body.append(self.connector(prev, ev) + " " + self.beat(ev))
            prev = ev
        lines.append(" ".join(body))
        lines.append("")
        others = [c for c in self.world.living if c.id != cid]
        avg_aff = sum(c.feel(cid) for c in others) / len(others) if others else 0.0
        if not char.alive and "arrival_died" in self.t:
            closing_key = "arrival_died"
        elif avg_aff > 0.2 and "arrival_settled" in self.t:
            closing_key = "arrival_settled"
        elif "arrival_cold" in self.t:
            closing_key = "arrival_cold"
        else:
            closing_key = None
        if closing_key:
            lines.append(self.rng.choice(self.t[closing_key]).format(
                name=char.name, village=self.village))
        return "\n".join(lines)

    def tell_village_moments(self) -> list[str]:
        """Village-wide lean or abundant seasons rendered as a section."""
        w = self.world
        lean_events = [ev for ev in w.events if ev.kind == "LEAN_SEASON"]
        bounty_events = [ev for ev in w.events if ev.kind == "BOUNTY"]
        if not lean_events and not bounty_events:
            return []
        if "LEAN_SEASON" not in self.t and "BOUNTY" not in self.t:
            return []
        parts: list[str] = []
        if "village_section" in self.t:
            parts.append(self.t["village_section"].format(village=self.village))
            parts.append("")
        # Most severe lean season and, separately, the first bounty (at most one each)
        selected = []
        if lean_events and "LEAN_SEASON" in self.t:
            worst = max(lean_events, key=lambda e: e.data.get("hungry_count", 0))
            selected.append(worst)
        if bounty_events and "BOUNTY" in self.t:
            selected.append(bounty_events[0])
        seasons_in_list = self.t.get("seasons_in", self.t["seasons"])
        for ev in selected:
            sname = self.season_name(ev.tick)
            sname_in = seasons_in_list[season_index(ev.tick)]
            if ev.kind == "LEAN_SEASON":
                para = self.rng.choice(self.t["LEAN_SEASON"]).format(
                    season=sname, season_in=sname_in, village=self.village)
                if ev.data.get("had_solidarity") and "LEAN_SEASON_solidarity" in self.t:
                    para += self.rng.choice(self.t["LEAN_SEASON_solidarity"])
            else:
                para = self.rng.choice(self.t["BOUNTY"]).format(
                    season=sname, season_in=sname_in, village=self.village)
            parts.append(para[0].upper() + para[1:] if para else para)
            parts.append("")
        return parts

    def arc_title(self, key, events):
        a_id, b_id = sorted(key)
        a, b = self.world.char(a_id), self.world.char(b_id)
        first = sum(events[0].data.get("affinity", (0, 0))) / 2
        final = (a.feel(b.id) + b.feel(a.id)) / 2
        kinds = {ev.kind for ev in events}
        if "BOND" in kinds:
            shape = "love"
        elif final > 0.2 and (first < -0.05 or "MEDIATION" in kinds or "QUARREL" in kinds):
            shape = "reconciliation"
        elif final < -0.1 and kinds & {"INGRATITUDE", "RESENTMENT"} and "REPAYMENT" not in kinds:
            shape = "debt"
        elif final < -0.3 and first > 0.05:
            shape = "estrangement"
        elif final < -0.3:
            shape = "feud"
        elif final > 0.2:
            shape = "bond"
        else:
            shape = "open"
        return self.t["title_" + shape].format(a=a.name, b=b.name), final, kinds

    def closing(self, final, kinds, departed_cid=None):
        if "BOND" in kinds and "WIDOWING" in kinds:
            return self.t["close_widowed"]
        if "BOND" in kinds and departed_cid is not None:
            name = self.name(departed_cid)
            if "close_departed_bonded" in self.t:
                return self.t["close_departed_bonded"].format(a=name, village=self.village)
            return self.t["close_widowed"]   # structural parallel: bond ended
        if "BOND" in kinds:
            return self.t["close_warm"]
        if departed_cid is not None and final < -0.2 and "close_departed" in self.t:
            return self.t["close_departed"].format(
                a=self.name(departed_cid), village=self.village)
        if final < -0.35:
            if "MEDIATION" in kinds:
                return self.t["close_relapse"]
            return self.t["close_broken"]
        if final < 0.2:
            return self.t["close_uneasy"]
        if kinds & {"QUARREL", "OFFENSE", "REFUSAL", "MEDIATION"}:
            return self.t["close_mended"]
        return self.t["close_warm"]

    def _skipped_note(self, skipped: list) -> str:
        dominant_kind = max(
            set(ev.kind for ev in skipped),
            key=lambda k: sum(1 for e in skipped if e.kind == k))
        suffix = "_one" if len(skipped) == 1 else ("_many" if len(skipped) <= 6 else "_endless")
        n = len(skipped)
        if dominant_kind == "QUARREL" and f"repeat_quarrel{suffix}" in self.t:
            return self.t[f"repeat_quarrel{suffix}"].format(n=n)
        if dominant_kind == "REFUSAL" and f"repeat_refusal{suffix}" in self.t:
            return self.t[f"repeat_refusal{suffix}"].format(n=n)
        if dominant_kind in ("GIFT", "REPAYMENT") and f"repeat_gift{suffix}" in self.t and suffix != "_endless":
            return self.t[f"repeat_gift{suffix}"].format(n=n)
        tone = "repeat_good" if sum(ev.valence for ev in skipped) > 0 else "repeat"
        return self.t[tone + suffix].format(n=n)

    def tell_arc(self, key, events):
        title, final, kinds = self.arc_title(key, events)
        lines = ["## " + title, ""]
        intro = []
        for cid in sorted(key):
            sentence = self.introduce(self.world.char(cid))
            if sentence:
                intro.append(sentence)
        if intro:
            lines.append(" ".join(intro))
            lines.append("")
        body, prev, told_kinds, skipped = [], None, {}, []
        for ev in events:
            # each kind of scene is told once; repeats become a single note
            if ev.kind in told_kinds and ev.kind != "MEDIATION":
                skipped.append(ev)
                continue
            told_kinds[ev.kind] = True
            if ev.kind == "WIDOWING" and skipped:
                body.append(self._skipped_note(skipped))
                skipped = []
            body.append(self.connector(prev, ev) + " " + self.beat(ev))
            prev = ev
        if skipped:
            body.append(self._skipped_note(skipped))
        lines.append(" ".join(body))
        lines.append("")
        departed_in_arc = next(
            (cid for cid in key if not self.world.char(cid).alive
             and self.world.char(cid).departed), None)
        lines.append(self.closing(final, kinds, departed_cid=departed_in_arc))
        # If one of the pair died, note it quietly after the closing.
        # Departures are covered separately by tell_departures().
        for cid in sorted(key):
            note = self.death_note(cid)
            if note is not None:
                lines.append("")
                lines.append(note)
        return "\n".join(lines)

    def chronicle(self):
        w = self.world
        title_tmpl = self.t["chronicle_title"]
        title = (self.rng.choice(title_tmpl) if isinstance(title_tmpl, list) else title_tmpl)
        parts = ["# " + title.format(village=self.village), ""]
        prologue_tmpl = self.t["prologue"]
        parts.append((self.rng.choice(prologue_tmpl) if isinstance(prologue_tmpl, list) else prologue_tmpl
                       ).format(village=self.village, n=self.world.initial_people, days=w.tick))

        pride_count = sum(1 for ev in w.events
                          if ev.kind == "HARDSHIP" and ev.data.get("pride"))
        if pride_count >= 3:
            parts.append("")
            parts.append(self.t["pride_note"].format(count=pride_count, village=self.village))

        debt_count = sum(len(c.debts) for c in w.chars)
        if debt_count >= 3:
            parts.append("")
            parts.append(self.t["debt_note"].format(count=debt_count, village=self.village))

        death_count = sum(1 for ev in w.events if ev.kind == "DEATH")
        if death_count >= 1:
            parts.append("")
            key = "deaths_note_1" if death_count == 1 else "deaths_note_n"
            parts.append(self.t[key].format(count=death_count, village=self.village))

        departure_count = sum(1 for ev in w.events if ev.kind == "DEPARTURE")
        if departure_count >= 1 and "departures_note_1" in self.t:
            parts.append("")
            dep_key = "departures_note_1" if departure_count == 1 else "departures_note_n"
            parts.append(self.t[dep_key].format(count=departure_count, village=self.village))

        arrival_evs = [ev for ev in w.events if ev.kind == "ARRIVAL"]
        arrival_count = len(arrival_evs)
        if arrival_count == 1 and "arrivals_note_1_named" in self.t:
            newcomer = w.char(arrival_evs[0].actors[0])
            parts.append("")
            parts.append(self.t["arrivals_note_1_named"].format(
                name=newcomer.name, village=self.village))
        elif arrival_count >= 2:
            parts.append("")
            parts.append(self.t["arrivals_note_n"].format(count=arrival_count, village=self.village))

        bond_count = sum(1 for ev in w.events if ev.kind == "BOND")
        if bond_count >= 1:
            parts.append("")
            key = "bonds_note_1" if bond_count == 1 else "bonds_note_n"
            parts.append(self.t[key].format(count=bond_count, village=self.village))

        birth_count = sum(1 for ev in w.events if ev.kind == "BIRTH")
        if birth_count >= 1:
            parts.append("")
            key = "births_note_1" if birth_count == 1 else "births_note_n"
            parts.append(self.t[key].format(count=birth_count, village=self.village))

        if birth_count >= 1 and len(w.living) > w.initial_people and "growth_note" in self.t:
            parts.append("")
            parts.append(self.t["growth_note"].format(village=self.village))

        if "famine_note" in self.t:
            from collections import Counter
            year_stress: Counter = Counter()
            for ev in w.events:
                if ev.kind == "HARDSHIP":
                    year_stress[year_of(ev.tick)] += 1
                elif ev.kind == "DEATH" and ev.data.get("cause") == "starvation":
                    year_stress[year_of(ev.tick)] += 3
            if len(year_stress) >= 2:
                worst_year, worst_count = year_stress.most_common(1)[0]
                avg = sum(year_stress.values()) / len(year_stress)
                if worst_count >= 4 and worst_count > avg * 1.8:
                    parts.append("")
                    parts.append(self.t["famine_note"].format(
                        year=worst_year, village=self.village))

        parts.append("")
        village_moments = self.tell_village_moments()
        if village_moments:
            parts.extend(village_moments)
        pair_arcs = self.arcs()
        arr_arcs = self.arrival_arcs(pair_arcs)
        dep_arcs = self.departure_arcs(pair_arcs)
        dep_arc_ids = {cid for cid, _ in dep_arcs}
        for cid, events in arr_arcs:
            section = self.tell_arrival_arc(cid, events)
            if section:
                parts.append(section)
                parts.append("")
        for cid, events in dep_arcs:
            section = self.tell_departure_arc(cid, events)
            if section:
                parts.append(section)
                parts.append("")
        for key, events in pair_arcs:
            parts.append(self.tell_arc(key, events))
            parts.append("")
        dead_section = self.tell_dead()
        if dead_section:
            parts.extend(dead_section)

        departure_section = self.tell_departures(exclude=dep_arc_ids)
        if departure_section:
            parts.extend(departure_section)

        best, worst = self.extremes()
        if best and worst:
            epilogue_tmpl = self.t["epilogue"]
            epilogue = (self.rng.choice(epilogue_tmpl) if isinstance(epilogue_tmpl, list) else epilogue_tmpl)
            parts.append(epilogue.format(
                a=self.name(best[0]), b=self.name(best[1]),
                c=self.name(worst[0]), d=self.name(worst[1]),
                village=self.village))
            parts.append("")

        parts.append(self.t["colophon"].format(seed=w.seed))
        parts.append("")
        return "\n".join(parts)

    def extremes(self):
        best = worst = None
        best_v, worst_v = -10.0, 10.0
        for a in self.world.living:
            for b in self.world.living:
                if b.id <= a.id:
                    continue
                mutual = a.feel(b.id) + b.feel(a.id)
                if mutual > best_v:
                    best, best_v = (a.id, b.id), mutual
                if mutual < worst_v:
                    worst, worst_v = (a.id, b.id), mutual
        return best, worst
