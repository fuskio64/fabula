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
             "REPAYMENT", "INGRATITUDE", "RESENTMENT", "BOND", "WIDOWING",
             "ESTRANGEMENT", "RECONCILIATION"}

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
        "ESTRANGEMENT": [
            "Whatever the original quarrel had been, what {a} and {b} had between them had passed from bitter into permanent.",
            "By that season it was clear: neither {a} nor {b} expected it to change. The hostility had stopped being about any one thing.",
        ],
        "inherited_cold": [
            "{a} had come of age in a house where {b} was not spoken of warmly. There is a kind of dislike that is inherited rather than earned, and {a} arrived already carrying some of the older quarrel.",
            "From the start, {a} seemed to hold opinions about {b} formed before any word passed between them. The household had kept its accounting.",
        ],
        "inherited_warm": [
            "{a} had grown up hearing good things said about {b}. There was already something between them, put there by the generation before.",
            "From the start, {a} came to {b} without suspicion — the family had thought well of them, and it showed.",
        ],
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
        "close_grudge": "One of them had not let go. The other may not have known it was still there.",
        "close_debt": "The debt was never returned. Some obligations become permanent simply by going too long unaddressed.",
        "title_reconciliation": "{a} and {b}: a reconciliation",
        "title_estrangement": "{a} and {b}: an estrangement",
        "title_feud": "{a} and {b}: a feud",
        "title_grudge": "{a} and {b}: an old wound",
        "title_bond": "{a} and {b}: a friendship",
        "title_love": "{a} and {b}: a love",
        "title_open": "{a} and {b}: an unfinished business",
        "title_debt": "{a} and {b}: a debt unpaid",
        "chronicle_title": ["The Chronicle of {village}",
                            "A Record of {village}",
                            "What Happened in {village}"],
        "arrivals_note_1_named": "{name} came to {village} as someone the village did not know yet. The village is always uncertain what to make of someone with no history here.",
        "prologue": [("{village} held {n} souls at the opening of this record, "
                      "and it covers {duration} of them. "
                      "Nothing in it was invented; it was only watched, and told."),
                     ("This is the record of {village}, which held {n} people at its opening. "
                      "It covers {duration}. "
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
        "mass_death": "In that {season}, year {year}, {names} all died within the same days.",
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
        "gift_lean": [
            "The stores were already short; the gift cost more than it looked.",
            "In a lean season, bread given away is bread genuinely given.",
        ],
        "refusal_lean": [
            "The season had not been good to anyone — which made the closed door harder to carry.",
            "It was a hungry time. The refusal meant more because of it.",
        ],
        "MEDIATION_elder": [
            "It fell to {c} — who had seen enough winters to know how grudges end — to sit them at one table. Something mended.",
            "{c}, who had been in the village long enough to remember the last time this had happened, made them speak. Something loosened.",
        ],
        "RECONCILIATION": [
            "{a} and {b} found themselves on speaking terms again — not declared, just there one morning.",
            "Whatever the old quarrel had been, it wore itself out. {a} and {b} were civil again, then warmer than civil.",
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
        "birth_arc_title": "{name}: born in {village}",
        "birth_intro": [
            "{name} was born in {village} to {pa} and {pb}. They grew up knowing everyone before anyone had decided what to make of them.",
            "{name} came of age in {village} having grown up inside all the old stories — the settled affections, the grudges carried quietly, the debts that never found their way back.",
        ],
        "birth_orphan": [
            "By the time {name} came of age, {dead} was already gone. They grew up toward an absence.",
            "{name} came of age in {village} without {dead} still living. The village was what family remained.",
        ],
        "adoption_note": [
            "When {child}'s parents died, {pa} and {pb} took the child in. The village counted three in their home after that.",
            "After both of {child}'s parents were gone, {pa} and {pb} opened their door. That is one of the things a village can do.",
        ],
        "tell_adoption": [
            "When {child} lost both parents, {pa} and {pb} took them in. {village} is the kind of place where that happened.",
            "The record notes one adoption in {village}: {pa} and {pb} took in {child} after both parents were gone.",
        ],
        "birth_settled": [
            "By the end of this record, {name} had taken their place in {village} as if it had always been waiting for them.",
            "{name} had grown up here and, when the record closes, was as much a part of it as anyone.",
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
        "BLIGHT": [
            "A blight came to {village} that {season}. It struck without warning — {n} households found their stores halved overnight, and the hunger that followed was sharp and sudden.",
            "Something moved through the fields of {village} that {season}. Not weather, not neglect — just a sudden failure. {n} households came up short at once.",
            "The {season} blight was not anyone's fault. The crop failed for {n} households without warning, and the village had no answer for it.",
        ],
        "drought_note": [
            "The drought of year {year} was the kind that a village does not forget. Two full seasons of thin harvests — not one household escaped it. The village found out, in that stretch, who it was.",
            "There was a drought in year {year}. It lasted through {season} and into the next season, and it did not ask permission. {village} came through it, or most of {village} did.",
            "In year {year}, the wells held and the sky did not. Two seasons of half-harvests. The village grew quieter and more careful in ways that did not entirely go away afterward.",
        ],
        "drought_end_note": [
            "The drought of year {year} broke in {end_season}. {village} did not make a ceremony of it. The harvest simply returned to what it had been, and that was the whole of it.",
            "By {end_season} the two thin seasons were over. {village} did not go back entirely to what it had been in year {year} — but the fields came back, and the village resumed.",
            "What {village} had become during the drought of year {year}, some of it stayed. Certain economies do not unlearn quickly. The harvest in {end_season} was ordinary; that was enough.",
        ],
        "celebration_note": [
            "When {newborn} was born, {parent1} and {parent2} opened what they had. It was one of those times {village} remembered what it was.",
            "There was a celebration when {newborn} arrived — the kind that needed no organizing. {village} simply gathered.",
            "{newborn}'s birth came in a good season. The village marked it the way it marked the things that mattered: together, without ceremony.",
        ],
        "pact_note": [
            "What {a} and {b} had was not the arrangement that {village} had words for. It was something older and less examined — and it held.",
            "{a} and {b} had never needed to name it. After a certain season, though, they did — quietly, without witnesses. That was enough.",
            "The village had a word for partners and a word for neighbors. What {a} and {b} were to each other required neither.",
        ],
        "tribute_note": [
            "When {name} died, the people who had loved them brought bread to the ones left behind. There is a word for that, though {village} would not have used it.",
            "In the days after {name}'s death, the village answered in the only way it knew — bread at the door, unannounced. That is its own kind of eulogy.",
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
        "lean_recurring": "That was not the only lean season. {village} counted {n} in the course of these years — hunger was a recurring visitor, not a single hard winter.",
        "social_hub": "At the close of this record, {name} was the person most others in {village} kept near — the village's center, in whatever way villages have centers.",
        "social_edge": "{name} was present in {village} through all of this, but not truly woven into it. There, but at the village's edge.",
        "founders_gone": "Of the {original} who opened this record, only {remaining} were still in {village} at its close.",
        "founders_all_gone": "None of the {original} who opened this record were still in {village} at its close. The village that remained was an entirely different one.",
        "theme_pride": [
            "This was a village that ran on pride. Not cruelty — just pride. The kind that would rather go hungry than ask, and sometimes did.",
            "What shaped {village}, in the end, was not generosity or its absence. It was pride: the silent kind, that mistakes suffering for dignity.",
        ],
        "theme_debt": [
            "The accounting never closed in {village}. Favors given and not returned accumulated across the years; the village kept them in heads, not books, and some are still kept there.",
            "Debts were the grammar of {village}. Every act of giving made a record in someone, and those records outlasted the givers.",
        ],
        "theme_quarrel": [
            "{village} was a village that quarreled. Not viciously — they still shared bread — but disagreement was the way it took its temperature, and the thermometer was always reading.",
            "The argument was how {village} was alive. Not a sign of breakdown; just the sound of people who cared about the same small patch of world.",
        ],
        "theme_generous": [
            "What passed between people in {village} was mostly bread — given freely, and mostly returned. The economy here was not obligation; it was care, and it held.",
            "{village} was fed by its own generosity. Not everyone gave, and not every gift came back; but the direction of things was toward the open hand.",
        ],
        "theme_cold": [
            "There was coldness in {village}. Not malice — a narrowness to the giving, a tendency to count stores. The village survived on that narrowness, too; it just cost something.",
            "The door in {village} did not always open. Not out of cruelty — but the village had learned to hold what it had, and the learning had stayed in the walls.",
        ],
        "mediator_note": [
            "{name} brought people back to speaking terms in {village} more than once. That kind of work belongs to the village's quiet infrastructure — never remarked on, but noticed when it stops.",
            "More than once, {name} sat two people down at the same table and would not let either leave angry. These things are easy to overlook, until you notice they always came to the same person.",
        ],
        "resentment_note": [
            "There is something in the record harder to name: what {debtor} had owed {creditor} for {seasons} seasons, and what happened to it in the carrying. The village did not know. {creditor} did not know. The record keeps it anyway.",
            "What {debtor} owed {creditor} had been a kindness at the start. After long enough it became something else — not the debt, but the weight of owing it to that particular person, and the pride that would not put it down.",
            "The giving and the receiving between {debtor} and {creditor} had gone on long enough to become a private injury. {village} would not have seen it. Only the record has it.",
        ],
        "offense_note": [
            "The day the wrong story reached {name} — about {source}, or about something between them — was the kind of day that closes a gap and opens another. {village} did not always see it happening.",
            "There are things that travel faster than the truth in {village}. What {name} heard about {source} was one of them. Whether the version that arrived was accurate, the record does not say — only that it changed things.",
            "Word of what had passed between them reached {name} — not directly, not precisely. That is how it is with stories in a small place. They arrive having already changed.",
        ],
        "most_generous": [
            "More bread left {name}'s house than any other in {village}. The village noticed — they always do.",
            "{name} gave more than their share. It is not always a comfortable thing to be, but they were it.",
        ],
        "most_quarrelsome": [
            "{name} was at one end of more arguments than anyone in {village}. Not always wrong, but never quiet about it.",
            "The village learned to expect {name} in the middle of things. There is always one person like this.",
        ],
        "landmark_year": [
            "Year {year} was the one {village} keeps coming back to. More was decided in that stretch than in any other.",
            "More happened in year {year} than the record can easily hold. It shaped everything that came after.",
            "If there is a year that explains what {village} became, it is year {year}.",
        ],
        "trajectory_warming": [
            "{village} ended warmer than it started. Whatever quarrels passed in between, the final direction was toward each other.",
            "The record opens on careful distances and closes with less of them. Not warmth exactly — but less distance.",
        ],
        "trajectory_cooling": [
            "{village} ended colder than it opened. Not broken — but weathered in a way that shows.",
            "Whatever had built between people in the early years, by the close there was less of it. Not lost — just spent.",
        ],
        "crisis_season": [
            "There was a {season} when {village} felt it all at once — lean stores and hard words in the same breath. That kind of season tests a village.",
            "In {village}, there was one {season} that asked more than the rest. The stores were low and the quarrels were many. The village came through it.",
        ],
        "crisis_season_death": [
            "There was a {season} when {village} bore too much at once — lean stores, many quarrels, and a death. The village came through it, but not unchanged.",
            "One {season} in {village} was harder than it should have been. Someone died while the stores were low and neighbors were not speaking. That kind of convergence leaves a mark.",
        ],
        "first_gift": [
            "The first thing that passed between people in {village} was a gift — {a} to {b}. Every village has to begin somewhere.",
            "{a} gave {b} bread before anything else was recorded. {village} opened in generosity.",
        ],
        "first_refusal": [
            "The record of {village} opens on a refusal. {a} went to {b}'s door and came back empty-handed.",
            "Before anything else was written down, {b} turned {a} away. {village} did not open warmly.",
        ],
        "first_quarrel": [
            "In {village}, the first thing worth writing down was a quarrel — {a} and {b} at hard words before much else had happened.",
            "The first notable event in {village} was a quarrel between {a} and {b}. Some villages begin that way.",
        ],
        "first_bond": [
            "The first thing this record notes about {village} is a bond — {a} and {b} chose each other before the village had much history.",
            "{a} and {b} bonded early, before the village had learned what it was. That kind of thing sets a tone.",
        ],
        "last_gift": [
            "The last thing recorded in {village} was a gift — {a} to {b}.",
            "What closed the record in {village} was a gift. {a} gave {b} bread, and the telling stopped.",
        ],
        "last_refusal": [
            "The last thing this record notes in {village} is a closed door — {a} turned {b} away.",
            "What the record ends on in {village} is a refusal. {a} went to {b}'s door and came back empty-handed.",
        ],
        "last_quarrel": [
            "The record of {village} closes on a quarrel — {a} and {b}, still at hard words at the end.",
            "The last thing worth writing down in {village} was a quarrel. {a} and {b}. It was not resolved before the telling stopped.",
        ],
        "last_bond": [
            "What the record closes on in {village} is a bond — {a} and {b}, choosing each other near the end.",
            "The last notable thing in {village} was a bond. {a} and {b}, late in the telling.",
        ],
        "lingering_debt": [
            "At the close of this record, {debtor} still owed {creditor}. The favor had been given {duration} before, and it had simply gone unanswered.",
            "One debt in {village} outlasted everything: {creditor} had given {debtor} bread, and it was never brought back. These things happen.",
        ],
        "notable_rumor": [
            "The tale had grown in the telling. Of all that was spoken of in {village}, what happened between {a} and {b} was what changed most — by the time it reached most ears, it was not quite the story it began as.",
            "What passed between {a} and {b} traveled the farthest of any story in {village}. It did not travel intact.",
        ],
        "decisive_season": [
            "The season this record turns on is {season}, year {year}. More was decided in those weeks than in any other stretch of this chronicle.",
            "If {village} has a pivot, it is {season} of year {year}. Everything before it was prelude; everything after was consequence.",
        ],
        "hard_year": [
            "Year {year} was the worst on record for {village}. {n} people died in that stretch. The village was smaller after it and knew it.",
            "{n} deaths in year {year}. More than any other year in this record. {village} was changed by that, even if it kept moving.",
        ],
        "good_year": [
            "Year {year} was the most alive {village} ever was. More bonds, more births, more repair than any other stretch of the record.",
            "If there was a good year in {village}, it was year {year}. Things opened up then in a way they did not elsewhere in the record.",
        ],
        "memorial_note": [
            "When {name} died, the village gathered. That is what a village does for someone it needed without knowing it.",
            "{name} was the kind of person whose absence changes the shape of the room. When they died, those left behind drew closer — the way people do when they realize something is gone.",
            "The record shows a gathering after {name}'s death. Not a ceremony. Just people who had cared for the same person finding themselves in the same place.",
        ],
        "illness_note": [
            "{name} fell ill during this record. They recovered, though they were not quite what they had been.",
            "There was a stretch when {name} was too sick to work. The village did what villages do — it noticed, and it helped what it could.",
        ],
        "illness_note_death": [
            "{name} fell ill. They did not recover.",
            "The illness took {name} — not quickly, but steadily, the way these things go in small places.",
        ],
        "vigil_note": [
            "When {name} had been ill long enough that the village stopped pretending it wasn't serious, the people who had been carrying it inwardly made it outward.",
            "There came a point in {name}'s illness when the village gathered without being asked. Not to help — there was nothing to do. To be there.",
            "The vigil for {name} was quiet. No one said they were keeping one. But the same people kept appearing at the same threshold.",
        ],
        "population_arc": [
            "The village reached its peak of {peak} souls in year {peak_year}, then came down to {close} by the close of this record.",
            "At its fullest, {village} held {peak} people. By the end, {close} remained. That is where the count settled.",
        ],
        "population_arc_stable": [
            "{village} stayed roughly the same size across this record. It began with {start} and ended with {close}. Some villages hold.",
        ],
        "estrangement_note": [
            "{a} and {b} had not spoken in {duration}. The village had learned to work around it — the way a village always learns to work around what will not be fixed.",
            "The cold between {a} and {b} was {duration} old and showed no sign of thawing. Some silences outlast the reasons for them.",
        ],
        "feud_note": [
            "{a} and {b} were at war. Not the open kind — the kind that makes you choose before you know you are choosing. The village organized itself around their hatred.",
            "The feud between {a} and {b} was the kind that gives a village its shape. Everyone knew which side they were on, even those who would have rather stayed out of it.",
            "There was no pretending that {a} and {b} could be in the same room. The record has a feud in it, and a feud changes what kind of place a village is.",
        ],
        "debt_culture_giving": [
            "{village} ran on credit. More bread left hands than came back — not through carelessness, but because giving was the way of it here.",
            "The ledger in {village} was always in deficit: gifts outnumbered repayments. The village ran on trust, and most of the time the trust held.",
        ],
        "debt_culture_hoarding": [
            "{village} was careful with its bread. Refusals outnumbered gifts in the count — not cruelty, but caution. The kind of place where you know whose door not to knock on.",
            "The bread did not move freely in {village}. People counted their stores and thought twice. Most of them thought twice too many times.",
        ],
        "debt_culture_balanced": [
            "{village} kept its accounts. Bread went out; bread came back. The village neither gave recklessly nor held too tight.",
        ],
        "most_bereaved": [
            "{name} outlived more people they loved than anyone else in {village}. That kind of loss does something to a person.",
            "More of {name}'s close connections were gone by the close than any other person's. {village} owed them a kind of recognition it never quite gave.",
        ],
        "oldest_resident": [
            "{name} had been in {village} since the first season recorded here — the only one still present at the close who had seen all of it.",
            "Of everyone who was there at the start, only {name} remained at the end. That is a particular kind of witness.",
        ],
        "village_character_generous": [
            "{village} was, at its heart, a village that gave. The bread moved more freely here than most places could sustain.",
            "More bread left hands in {village} than was ever asked for. That kind of place is rare.",
        ],
        "village_character_proud": [
            "What defined {village} above all was its reluctance to ask. People here suffered quietly before they would knock on a neighbor's door.",
            "{village} ran on silent pride. The hungry went without asking, and the overfull held onto what they had.",
        ],
        "village_character_healing": [
            "{village} was a village that chose repair. When things broke between people, there was usually someone willing to sit them down.",
            "Quarrels happened here, but they did not usually last. Someone always knew whose door to knock on first.",
        ],
        "village_character_bitter": [
            "The bitterness in {village} was its own kind of weather — chronic, low-grade, and mostly unaddressed.",
            "Debts curdled here more often than not. The village accumulated resentments the way other places accumulated snow.",
        ],
        "village_character_estranged": [
            "{village} specialized in silences. When things went wrong between people, the usual resolution was distance.",
            "The estrangements in {village} outlasted their causes. People learned to work around the silences rather than break them.",
        ],
        "season_rhythm_lean": [
            "{village} learned to dread {season}. More hungry seasons fell then than any other time of year.",
            "If hard times were coming to {village}, they usually came in {season}. The village grew to expect it.",
        ],
        "season_rhythm_quarrel": [
            "The quarrels in {village} had a season — {season}, almost always. Something about that time of year made patience thin.",
            "{season} was when things broke down in {village}. The village knew it and still could not seem to prevent it.",
        ],
        "birth_cohort": [
            "Around {season} of year {year}, {n} children were born close enough together to become a generation — the kind that grows up knowing each other before they know anything else.",
            "{village} had a small wave of births around {season}, year {year}. {n} children came of age alongside each other, and what they shared growing up shaped them all.",
        ],
        "second_gen_1": [
            "{name} was the first child raised in {village} to become fully one of its own. The village was beginning to have a past it could remember from both sides.",
            "By the time {name} came of age, {village} already felt like something that had a history. That is a different thing from being new.",
        ],
        "second_gen_n": [
            "By the close of this record, {n} children who had grown up in {village} were adults in it. The village was becoming a place that could remember things that predated its youngest members.",
            "{n} of the souls counted in {village} at the close had been born and raised there. The village was starting to pass things down.",
        ],
        "large_family": [
            "{pa} and {pb} raised {n} children in {village}. That is enough for a lineage.",
            "Three children came from {pa} and {pb} in {village}. The village had not expected that kind of continuity.",
        ],
        "mentor_note": [
            "{elder} took {young} under their wing when {young} came of age. Something passed between them — the kind of thing that cannot be taught directly, only witnessed.",
            "When {young} came of age in {village}, {elder} was the one who made the difference. There is always one person like that, in the right place at the right time.",
        ],
        "legacy_note": [
            "What {teacher} taught {student} did not die with the teacher. Something of that patience stayed in the way {student} moved through a season.",
            "{teacher} had passed something to {student} that outlasted the passing. You could see it in the way {student} worked — careful, deliberate, exactly as the old one had been.",
            "The teaching between {teacher} and {student} turned out to be the kind that keeps. {student} worked the same way long after {teacher} was gone.",
        ],
        "jealousy_note": [
            "When {loved_one} and {rival} made their arrangement, not everyone was glad. {name} had carried something for {loved_one} — quietly, without ever saying so — and the bonding landed like a door closing.",
            "{name} had known, without ever stating it, that there was something between them and {loved_one}. The bond with {rival} changed that. The village did not need to be told; it noticed the coldness.",
            "There are feelings a village does not discuss. What {name} had felt toward {loved_one} was one of them. When {loved_one} and {rival} joined households, {name}'s mood shifted in a way everyone registered and no one named.",
        ],
        "reconciliation_1": [
            "Only once in the record of {village} did two people who had truly broken find their way back to each other. It was {a} and {b}. The record does not say what shifted. But it did.",
            "The repair between {a} and {b} was the only one in {village}'s record. It happened once. The village was quieter for it.",
        ],
        "reconciliation_n": [
            "{village} had {n} repairs in its record. Each time, two people who had broken found their way back. That is unusual for a place this size.",
            "{n} reconciliations in {village}. Something here inclined toward repair — or at least, more often than not, toward trying.",
        ],
        "widowing_note": [
            "This village knew widowing. {n} people here outlived their partners. That shapes a place in ways that don't show up in any count.",
            "{village} had {n} people who outlived the person they had bound themselves to. The village kept moving around that fact the way villages do.",
        ],
        "colophon": "*(world seed {seed} — run it again and the same things will happen, in the same order, to the same people)*",
        "era_opening": "The Opening Years",
        "era_middle": "The Middle Seasons",
        "era_closing": "The Later Record",
        "era_hungry": "The Hungry Seasons",
        "era_loss": "The Years of Loss",
        "era_bitter": "The Bitter Years",
        "era_quarrelsome": "The Quarrelsome Seasons",
        "era_warm": "The Warm Years",
        "witness_alive": [
            "More of this record passed through {name} than through anyone else. They were present for quarrels and gifts, for debts and reconciliations — and they are still in {village} at the close.",
            "{name} stood closer to more of what happened here than any other single person. That may be accident, or it may be something about them. They are still alive.",
        ],
        "witness_dead": [
            "More of this record passed through {name} than through anyone else. They did not survive to see its close.",
            "{name} was near enough to more of what happened here that the record carries their shape, whether or not they knew it. They are gone now.",
        ],
        "witness_departed": [
            "More of this record passed through {name} than through anyone else. They left {village} before the close.",
        ],
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
        "ESTRANGEMENT": [
            "Fuera cual fuera la disputa original, lo que había entre {a} y {b} había pasado de amargo a permanente.",
            "Para esa estación estaba claro: ni {a} ni {b} esperaban que cambiara. La hostilidad había dejado de ser por algo en concreto.",
        ],
        "inherited_cold": [
            "{a} había crecido en una casa donde {b} no era bien recordado. Hay rencores que se heredan en lugar de ganarse, y {a} llegó cargando ya parte del más viejo.",
            "Desde el principio, {a} parecía tener opiniones sobre {b} formadas antes de que mediara una sola palabra entre ellos.",
        ],
        "inherited_warm": [
            "{a} había crecido oyendo cosas buenas de {b}. Ya había algo entre ellos, puesto ahí por la generación anterior.",
            "Desde el principio, {a} se acercó a {b} sin recelo — la familia lo había tenido en buena estima, y se notaba.",
        ],
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
        "close_grudge": "Uno de los dos no lo había soltado. El otro puede que no supiera que seguía ahí.",
        "close_debt": "La deuda nunca se devolvió. Algunas obligaciones se vuelven permanentes simplemente por haber pasado demasiado tiempo sin resolverse.",
        "title_reconciliation": "{a} y {b}: una reconciliación",
        "title_estrangement": "{a} y {b}: un distanciamiento",
        "title_feud": "{a} y {b}: una enemistad",
        "title_grudge": "{a} y {b}: una herida vieja",
        "title_bond": "{a} y {b}: una amistad",
        "title_love": "{a} y {b}: un amor",
        "title_open": "{a} y {b}: un asunto sin cerrar",
        "title_debt": "{a} y {b}: una deuda impagada",
        "chronicle_title": ["Crónica de {village}",
                            "Registro de {village}",
                            "Lo que pasó en {village}"],
        "arrivals_note_1_named": "{name} llegó a {village} sin historia que la aldea conociera. Nunca sabe bien qué hacer con eso.",
        "prologue": [("En {village} vivían {n} almas al abrir este registro, "
                      "y abarca {duration}. "
                      "Nada de lo que sigue es inventado; solo se miró, y se contó."),
                     ("Este es el registro de {village}, que tenía {n} almas cuando se abrió. "
                      "Cubre {duration}. "
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
        "mass_death": "En {season} del año {year}, {names} murieron todos en los mismos días.",
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
        "gift_lean": [
            "Las reservas ya estaban bajas; el regalo costó más de lo que parecía.",
            "En una temporada mala, el pan que se regala es pan de verdad.",
        ],
        "refusal_lean": [
            "La temporada no había sido buena para nadie — lo que hacía la puerta cerrada más difícil de cargar.",
            "Era un tiempo de hambre. La negativa pesaba más por eso.",
        ],
        "MEDIATION_elder": [
            "Fue {c}, {anciano} de la aldea, quien los hizo sentarse. Hay cosas que solo ceden a la paciencia de los años.",
            "A {c}, que había visto lo suficiente como para saber cómo acaban los rencores, le tocó sentarlos. Algo se aflojó.",
        ],
        "RECONCILIATION": [
            "{a} y {b} se encontraron hablándose otra vez — sin anunciarlo, simplemente un día estaba ahí.",
            "La vieja disputa se fue gastando sola. {a} y {b} volvieron a cruzarse la mirada, y con ella algo más.",
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
        "birth_arc_title": "{name}: nacido en {village}",
        "birth_intro": [
            "{name} nació en {village}, hijo de {pa} y {pb}. Creció conociéndolo todo antes de que nadie hubiera decidido qué hacer con él.",
            "{name} llegó a la edad adulta en {village} habiendo crecido dentro de todas las viejas historias — las afecciones establecidas, los rencores llevados en silencio, las deudas que nunca encontraron su camino de vuelta.",
        ],
        "birth_orphan": [
            "Cuando {name} llegó a la edad adulta, {dead} ya se había ido. Creció hacia una ausencia.",
            "{name} llegó a la edad adulta en {village} sin que {dead} siguiera viviendo. La aldea era la familia que quedaba.",
        ],
        "adoption_note": [
            "Cuando los padres de {child} murieron, {pa} y {pb} acogieron al niño/a. A partir de entonces el pueblo los contó como tres en su hogar.",
            "Después de que ambos padres de {child} se fueran, {pa} y {pb} abrieron su puerta. Eso es una de las cosas que puede hacer una aldea.",
        ],
        "tell_adoption": [
            "Cuando {child} perdió a sus dos padres, {pa} y {pb} lo/la acogieron. {village} es el tipo de lugar donde eso ocurrió.",
            "El registro anota una adopción en {village}: {pa} y {pb} acogieron a {child} después de que sus dos padres se fueran.",
        ],
        "birth_settled": [
            "Al cerrar este registro, {name} había ocupado su lugar en {village} como si siempre hubiera estado esperándolo.",
            "{name} había crecido aquí y, cuando el registro se cierra, formaba parte de la aldea tanto como cualquier otro.",
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
        "BLIGHT": [
            "Una plaga llegó a {village} durante {season}. Golpeó sin aviso — {n} hogares vieron sus reservas reducidas a la mitad de la noche a la mañana, y el hambre que siguió fue aguda y repentina.",
            "Algo se movió por los campos de {village} ese {season}. No fue el clima, no fue el descuido — fue un fracaso súbito. {n} hogares se quedaron sin nada a la vez.",
            "La plaga de {season} no fue culpa de nadie. La cosecha falló en {n} hogares sin aviso, y la aldea no tenía respuesta.",
        ],
        "drought_note": [
            "La sequía del año {year} fue del tipo que una aldea no olvida. Dos estaciones completas de cosechas escasas — ningún hogar se libró. La aldea descubrió, en ese tiempo, quién era.",
            "Hubo una sequía en el año {year}. Duró durante {season} y hasta la siguiente estación, y no pidió permiso. {village} sobrevivió, o casi todo {village}.",
            "En el año {year}, los pozos aguantaron y el cielo no. Dos estaciones de media cosecha. La aldea se volvió más silenciosa y más cuidadosa de maneras que no desaparecieron del todo después.",
        ],
        "drought_end_note": [
            "La sequía del año {year} se rompió en {end_season}. {village} no hizo una ceremonia de ello. La cosecha simplemente volvió a lo que había sido, y eso fue todo.",
            "Para el {end_season} las dos estaciones escasas habían terminado. {village} no volvió del todo a lo que había sido en el año {year} — pero los campos regresaron, y la aldea continuó.",
            "Lo que {village} había llegado a ser durante la sequía del año {year}, algo de ello se quedó. Ciertas economías no se desaprenden rápidamente. La cosecha en {end_season} fue ordinaria; con eso bastó.",
        ],
        "celebration_note": [
            "Cuando nació {newborn}, {parent1} y {parent2} abrieron lo que tenían. Fue una de esas veces en que {village} recordó lo que era.",
            "Hubo una celebración cuando llegó {newborn} — del tipo que no necesita organización. {village} simplemente se reunió.",
            "El nacimiento de {newborn} llegó en una buena estación. La aldea lo marcó como marcaba las cosas que importaban: juntos, sin ceremonia.",
        ],
        "pact_note": [
            "Lo que {a} y {b} tenían no era el tipo de acuerdo para el que {village} tenía palabras. Era algo más antiguo y menos examinado — y duró.",
            "{a} y {b} nunca habían necesitado ponerle nombre. Después de cierta estación, lo hicieron — en silencio, sin testigos. Con eso bastó.",
            "La aldea tenía una palabra para los compañeros y una para los vecinos. Lo que {a} y {b} eran el uno para el otro no requería ninguna de las dos.",
        ],
        "tribute_note": [
            "Cuando {name} murió, los que lo habían querido llevaron pan a los que quedaron atrás. Hay una palabra para eso, aunque {village} no la hubiera usado.",
            "En los días después de la muerte de {name}, la aldea respondió de la única manera que sabía — pan a la puerta, sin anunciarse. Eso es su propia clase de elegía.",
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
        "lean_recurring": "No fue la única estación de escasez. {village} vivió {n} a lo largo de estos años — el hambre fue un visitante que volvió, no un único invierno difícil.",
        "social_hub": "Al cierre de este registro, {name} era la persona de quien los demás en {village} se mantenían más cerca — el centro de la aldea, en la medida en que las aldeas tienen un centro.",
        "social_edge": "{name} estuvo presente en {village} durante todo esto, pero sin llegar a tejerse del todo en ella. Allí, pero en el margen.",
        "founders_gone": "De los {original} que abrieron este registro, solo {remaining} seguían en {village} al cerrarse.",
        "founders_all_gone": "Ninguno de los {original} que abrieron este registro seguía en {village} al cerrarse. La aldea que quedó era una completamente distinta.",
        "theme_pride": [
            "Esta aldea funcionaba con orgullo. No con crueldad — solo orgullo. El tipo que prefiere pasar hambre antes que pedir, y a veces lo hacía.",
            "Lo que dio forma a {village}, al final, no fue la generosidad ni su ausencia. Fue el orgullo: el silencioso, que confunde el sufrimiento con la dignidad.",
        ],
        "theme_debt": [
            "Las cuentas nunca se cerraron en {village}. Los favores dados y no devueltos se acumularon con los años; la aldea los guardaba en cabezas, no en libros, y algunos siguen ahí.",
            "Las deudas eran la gramática de {village}. Cada acto de dar dejaba un registro en alguien, y esos registros sobrevivían a quienes los hacían.",
        ],
        "theme_quarrel": [
            "{village} era una aldea que discutía. No con maldad — seguían compartiendo el pan —, pero la disputa era la forma en que tomaba su temperatura, y el termómetro siempre marcaba.",
            "La discusión era cómo {village} estaba viva. No una señal de quiebre; solo el sonido de gente a la que le importaba el mismo pequeño trozo de mundo.",
        ],
        "theme_generous": [
            "Lo que pasaba entre la gente de {village} era principalmente pan — dado libremente, y en su mayoría devuelto. La economía aquí no era obligación; era cuidado, y aguantó.",
            "{village} se alimentaba de su propia generosidad. No todos daban, y no todo regalo volvía; pero la dirección de las cosas era hacia la mano abierta.",
        ],
        "theme_cold": [
            "Había frialdad en {village}. No malicia — una estrechez en el dar, la tendencia a contar las provisiones. La aldea también sobrevivió con esa estrechez; solo que tuvo un coste.",
            "La puerta en {village} no siempre se abría. No por crueldad — pero la aldea había aprendido a guardar lo suyo, y el aprendizaje se había quedado en las paredes.",
        ],
        "mediator_note": [
            "{name} devolvió a la gente las palabras en {village} más de una vez. Ese tipo de trabajo pertenece a la infraestructura silenciosa de la aldea — nunca se menciona, pero se nota cuando falta.",
            "Más de una vez, {name} sentó a dos personas en la misma mesa y no dejó que ninguna se fuera enojada. Es fácil no verlo, hasta que uno se da cuenta de que siempre iban al mismo lugar.",
        ],
        "resentment_note": [
            "Hay algo en el registro más difícil de nombrar: lo que {debtor} le debía a {creditor} durante {seasons} estaciones, y lo que le pasó en el camino. La aldea no lo sabía. {creditor} no lo sabía. El registro lo guarda de todas formas.",
            "Lo que {debtor} le debía a {creditor} había sido una bondad al principio. Después de bastante tiempo se convirtió en otra cosa — no la deuda en sí, sino el peso de debérsela a esa persona en particular, y el orgullo que no la dejaba ir.",
            "El dar y recibir entre {debtor} y {creditor} había durado lo suficiente para convertirse en una herida privada. {village} no lo habría visto. Solo el registro lo tiene.",
        ],
        "offense_note": [
            "El día en que la historia equivocada llegó a {name} — sobre {source}, o sobre algo que había pasado entre ellos — fue el tipo de día que cierra una distancia y abre otra. {village} no siempre lo vio pasar.",
            "Hay cosas que viajan más rápido que la verdad en {village}. Lo que {name} escuchó sobre {source} era una de ellas. Si la versión que llegó era precisa, el registro no lo dice — solo que cambió las cosas.",
            "Lo que había pasado entre ellos y {source} le llegó a {name} — no directamente, no con precisión. Así es con las historias en un lugar pequeño. Llegan habiendo cambiado ya.",
        ],
        "most_generous": [
            "De ninguna casa salió más pan que de la de {name}. La aldea lo notó — siempre lo notan.",
            "{name} dio más de lo que le correspondía. No es siempre cómodo ser así, pero lo era.",
        ],
        "most_quarrelsome": [
            "{name} estuvo en más disputas que nadie en {village}. No siempre equivocado, pero nunca callado.",
            "La aldea aprendió a esperar a {name} en el medio de todo. Siempre hay uno así.",
        ],
        "landmark_year": [
            "El año {year} es al que {village} vuelve una y otra vez. Más se decidió en ese tiempo que en ningún otro.",
            "En el año {year} ocurrió más de lo que el registro puede contener fácilmente. Marcó todo lo que vino después.",
            "Si hay un año que explica en qué se convirtió {village}, es el año {year}.",
        ],
        "trajectory_warming": [
            "{village} terminó más cálida de lo que empezó. Fuera cual fuera la disputa intermedia, la dirección final era hacia los demás.",
            "El registro se abre en distancias cuidadosas y se cierra con menos de ellas. No exactamente calidez — pero sí menos distancia.",
        ],
        "trajectory_cooling": [
            "{village} terminó más fría de lo que abrió. No rota — pero desgastada de una manera que se nota.",
            "Lo que se había construido entre la gente en los primeros años, al cerrar el registro era menos. No perdido — solo gastado.",
        ],
        "crisis_season": [
            "Hubo una {season} en que {village} lo vivió todo a la vez — despensas vacías y palabras duras en el mismo aliento. Ese tipo de estación pone a prueba a un pueblo.",
            "En {village} hubo una {season} que exigió más que las demás. Las reservas eran escasas y las disputas, muchas. El pueblo lo superó.",
        ],
        "crisis_season_death": [
            "Hubo una {season} en que {village} cargó con demasiado a la vez — despensas vacías, muchas disputas y una muerte. El pueblo lo superó, pero no sin cambiar.",
            "Una {season} en {village} fue más dura de lo que debía ser. Alguien murió mientras las despensas estaban bajas y los vecinos no se hablaban. Ese tipo de confluencia deja huella.",
        ],
        "first_gift": [
            "Lo primero que pasó entre la gente de {village} fue un regalo — {a} a {b}. Todo pueblo tiene que empezar por algo.",
            "{a} le dio pan a {b} antes de que se anotara cualquier otra cosa. {village} se abrió en generosidad.",
        ],
        "first_refusal": [
            "El registro de {village} se abre con un rechazo. {a} fue a la puerta de {b} y volvió con las manos vacías.",
            "Antes de que se anotara nada más, {b} le cerró la puerta a {a}. {village} no empezó con calidez.",
        ],
        "first_quarrel": [
            "En {village}, lo primero que mereció escribirse fue una disputa — {a} y {b} a malas palabras antes de que pasara mucho más.",
            "El primer acontecimiento notable en {village} fue una disputa entre {a} y {b}. Algunos pueblos empiezan así.",
        ],
        "first_bond": [
            "Lo primero que este registro anota sobre {village} es un vínculo — {a} y {b} se eligieron el uno al otro antes de que el pueblo tuviera mucha historia.",
            "{a} y {b} se vincularon pronto, antes de que el pueblo supiera lo que era. Ese tipo de cosa marca el tono.",
        ],
        "last_gift": [
            "Lo último registrado en {village} fue un regalo — {a} a {b}.",
            "Lo que cierra el registro de {village} es un regalo. {a} le dio pan a {b}, y el relato se detuvo.",
        ],
        "last_refusal": [
            "Lo último que anota este registro en {village} es una puerta cerrada — {a} echó a {b}.",
            "En lo que acaba el registro de {village} es un rechazo. {a} fue a la puerta de {b} y volvió con las manos vacías.",
        ],
        "last_quarrel": [
            "El registro de {village} cierra con una pelea — {a} y {b}, aún con palabras duras al final.",
            "Lo último que valió la pena anotar en {village} fue una pelea. {a} y {b}. No se resolvió antes de que se detuviera el relato.",
        ],
        "last_bond": [
            "Con lo que cierra el registro de {village} es con un vínculo — {a} y {b}, eligiéndose cerca del final.",
            "Lo último notable en {village} fue un vínculo. {a} y {b}, tarde en el relato.",
        ],
        "lingering_debt": [
            "Al cerrar este registro, {debtor} todavía le debía a {creditor}. El favor se había dado {duration} antes, y simplemente nunca fue devuelto.",
            "Una deuda en {village} lo sobrevivió todo: {creditor} le había dado pan a {debtor}, y nunca se lo devolvió. Estas cosas pasan.",
        ],
        "notable_rumor": [
            "El relato había crecido con cada boca. De todo lo que se habló en {village}, lo que pasó entre {a} y {b} fue lo que más cambió — cuando llegó a la mayoría, ya no era exactamente la historia que había empezado.",
            "Lo que ocurrió entre {a} y {b} fue la historia que más lejos viajó en {village}. No viajó intacta.",
        ],
        "decisive_season": [
            "La estación en que este registro gira es el {season} del año {year}. Más se decidió en esas semanas que en ningún otro tramo de esta crónica.",
            "Si {village} tiene un pivote, es el {season} del año {year}. Todo lo anterior fue preludio; todo lo que vino después, consecuencia.",
        ],
        "hard_year": [
            "El año {year} fue el peor que registra {village}. {n} personas murieron en ese tramo. La aldea fue más pequeña después y lo sabía.",
            "{n} muertes en el año {year}. Más que en ningún otro año del registro. {village} quedó marcada por eso, aunque siguió adelante.",
        ],
        "good_year": [
            "El año {year} fue el más vivo que {village} conoció. Más lazos, más nacimientos, más reparaciones que en cualquier otro tramo del registro.",
            "Si hubo un buen año en {village}, fue el año {year}. Las cosas se abrieron entonces de una manera que no lo hicieron en ningún otro momento.",
        ],
        "memorial_note": [
            "Cuando {name} murió, la aldea se reunió. Eso es lo que hace una aldea por alguien que necesitaba sin saberlo.",
            "{name} era el tipo de persona cuya ausencia cambia la forma del lugar. Cuando murió, los que quedaron se acercaron los unos a los otros, como la gente hace cuando se da cuenta de que algo se ha ido.",
            "El registro muestra una reunión tras la muerte de {name}. No una ceremonia. Solo gente que había querido a la misma persona encontrándose en el mismo lugar.",
        ],
        "illness_note": [
            "{name} cayó enfermo durante este registro. Se recuperó, aunque no era del todo lo que había sido.",
            "Hubo un período en que {name} estaba demasiado enfermo para trabajar. La aldea hizo lo que hacen las aldeas — se dio cuenta y ayudó en lo que pudo.",
        ],
        "illness_note_death": [
            "{name} cayó enfermo. No se recuperó.",
            "La enfermedad se llevó a {name} — no rápidamente, sino de forma constante, como suceden estas cosas en los lugares pequeños.",
        ],
        "vigil_note": [
            "Cuando {name} había estado enfermo el tiempo suficiente como para que la aldea dejara de fingir que no era grave, los que lo habían cargado en silencio lo hicieron visible.",
            "Llegó un momento en la enfermedad de {name} en que la aldea se reunió sin que nadie lo pidiera. No para ayudar — no había nada que hacer. Para estar.",
            "La vigilia por {name} fue silenciosa. Nadie dijo que la estaban haciendo. Pero las mismas personas seguían apareciendo en el mismo umbral.",
        ],
        "population_arc": [
            "La aldea alcanzó su punto máximo de {peak} almas en el año {peak_year}, luego bajó a {close} al cierre de este registro.",
            "En su momento de mayor auge, {village} albergó {peak} personas. Al final, quedaron {close}. Ahí se asentó el recuento.",
        ],
        "population_arc_stable": [
            "{village} se mantuvo más o menos del mismo tamaño durante este registro. Empezó con {start} y terminó con {close}. Algunas aldeas aguantan.",
        ],
        "estrangement_note": [
            "{a} y {b} no se habían hablado en {duration}. La aldea había aprendido a trabajar alrededor de eso — como siempre aprende a trabajar alrededor de lo que no se arreglará.",
            "El frío entre {a} y {b} tenía {duration} y no mostraba señales de deshielo. Algunos silencios sobreviven a sus razones.",
        ],
        "feud_note": [
            "{a} y {b} estaban en guerra. No del tipo abierto — del tipo que te hace elegir antes de que sepas que estás eligiendo. La aldea se organizó alrededor de su odio.",
            "La enemistad entre {a} y {b} era del tipo que da forma a una aldea. Todo el mundo sabía de qué lado estaba, incluso los que habrían preferido no involucrarse.",
            "No había manera de pretender que {a} y {b} podían estar en la misma habitación. El registro tiene una enemistad, y una enemistad cambia el tipo de lugar que es una aldea.",
        ],
        "debt_culture_giving": [
            "{village} funcionaba a crédito. Salía más pan del que volvía — no por descuido, sino porque dar era la manera de ser aquí.",
            "El libro de cuentas de {village} siempre estaba en déficit: los regalos superaban los pagos. La aldea vivía de la confianza, y la mayor parte del tiempo la confianza aguantaba.",
        ],
        "debt_culture_hoarding": [
            "{village} era cuidadosa con su pan. Las negativas superaban a los regalos — no crueldad, sino precaución. El tipo de lugar donde se sabe a qué puerta no llamar.",
            "El pan no circulaba libremente en {village}. La gente contaba sus provisiones y lo pensaba dos veces. La mayoría lo pensó demasiadas veces.",
        ],
        "debt_culture_balanced": [
            "{village} llevaba sus cuentas. El pan salía; el pan volvía. La aldea no daba con imprudencia ni apretaba demasiado.",
        ],
        "most_bereaved": [
            "{name} sobrevivió a más personas queridas que nadie en {village}. Ese tipo de pérdida hace algo con una persona.",
            "Más de las conexiones cercanas de {name} se habían ido al cerrar el registro que las de cualquier otro. {village} le debía un reconocimiento que nunca llegó a darle.",
        ],
        "oldest_resident": [
            "{name} había estado en {village} desde la primera estación registrada — el único que seguía presente al final y que lo había visto todo.",
            "De todos los que estaban al principio, solo {name} quedaba al final. Es una clase de testigo muy particular.",
        ],
        "village_character_generous": [
            "{village} era, en el fondo, una aldea que daba. El pan circulaba aquí más libremente de lo que la mayoría de lugares podría sostener.",
            "Más pan salió de las manos en {village} del que alguien pidió. Ese tipo de lugar es raro.",
        ],
        "village_character_proud": [
            "Lo que definía a {village} por encima de todo era su renuncia a pedir. La gente aquí sufría en silencio antes de llamar a la puerta del vecino.",
            "{village} funcionaba con orgullo silencioso. Los hambrientos se quedaban sin pedir, y los que tenían de sobra guardaban lo que tenían.",
        ],
        "village_character_healing": [
            "{village} era una aldea que elegía la reparación. Cuando las cosas se rompían entre la gente, siempre había alguien dispuesto a sentarles juntos.",
            "Las peleas pasaban aquí, pero solían no durar. Alguien siempre sabía a qué puerta llamar primero.",
        ],
        "village_character_bitter": [
            "El rencor en {village} era su propio tipo de clima — crónico, de baja intensidad, y mayormente sin resolver.",
            "Las deudas se agriaban aquí más a menudo que no. La aldea acumulaba resentimientos como otros lugares acumulan nieve.",
        ],
        "village_character_estranged": [
            "{village} se especializó en silencios. Cuando las cosas salían mal entre la gente, la resolución habitual era la distancia.",
            "Los distanciamientos en {village} sobrevivían a sus causas. La gente aprendió a trabajar alrededor de los silencios en lugar de romperlos.",
        ],
        "season_rhythm_lean": [
            "{village} aprendió a temer {season}. Más temporadas de hambre caían entonces que en ningún otro momento del año.",
            "Si llegaban tiempos difíciles a {village}, solían llegar en {season}. La aldea llegó a esperarlo.",
        ],
        "season_rhythm_quarrel": [
            "Las peleas en {village} tenían una estación — {season}, casi siempre. Algo en esa época del año hacía que la paciencia escaseara.",
            "{season} era cuando las cosas se rompían en {village}. La aldea lo sabía y aún así no parecía poder prevenirlo.",
        ],
        "birth_cohort": [
            "Alrededor de {season} del año {year}, {n} niños nacieron con suficiente cercanía como para convertirse en una generación — el tipo que crece sabiéndose mutuamente antes de saber cualquier otra cosa.",
            "{village} tuvo una pequeña oleada de nacimientos alrededor de {season}, año {year}. {n} niños crecieron juntos, y lo que compartieron al crecer los marcó a todos.",
        ],
        "second_gen_1": [
            "{name} fue el primer hijo criado en {village} en convertirse plenamente en uno de los suyos. La aldea empezaba a tener un pasado del que recordar ambas orillas.",
            "Cuando {name} llegó a la madurez, {village} ya parecía algo con historia. Eso es distinto de ser nuevo.",
        ],
        "second_gen_n": [
            "Al cerrar el registro, {n} niños que habían crecido en {village} eran ya adultos en ella. La aldea se estaba convirtiendo en un lugar que recordaba cosas anteriores a sus miembros más jóvenes.",
            "{n} de las almas contadas en {village} al cierre habían nacido y crecido allí. La aldea empezaba a transmitir cosas.",
        ],
        "large_family": [
            "{pa} y {pb} criaron {n} hijos en {village}. Eso ya es suficiente para un linaje.",
            "Tres hijos vinieron de {pa} y {pb} en {village}. La aldea no esperaba ese tipo de continuidad.",
        ],
        "mentor_note": [
            "{elder} tomó a {young} bajo su ala cuando llegó a la edad adulta. Algo pasó entre ellos — el tipo de cosa que no puede enseñarse directamente, solo presenciarse.",
            "Cuando {young} llegó a la edad adulta en {village}, {elder} fue quien marcó la diferencia. Siempre hay una persona así, en el lugar correcto en el momento preciso.",
        ],
        "legacy_note": [
            "Lo que {teacher} enseñó a {student} no murió con él. Algo de esa paciencia quedó en la manera en que {student} trabajaba.",
            "{teacher} había transmitido algo a {student} que sobrevivió a su muerte. Se veía en cómo {student} trabajaba — con cuidado, con deliberación, exactamente como el viejo.",
            "La enseñanza entre {teacher} y {student} resultó ser del tipo que perdura. {student} trabajaba de la misma manera mucho después de que {teacher} se fuera.",
        ],
        "jealousy_note": [
            "Cuando {loved_one} y {rival} hicieron su arreglo, no todos se alegraron. {name} había llevado algo por {loved_one} — en silencio, sin decirlo nunca — y la unión llegó como una puerta que se cierra.",
            "{name} había sabido, sin decirlo nunca, que había algo entre ellos y {loved_one}. El vínculo con {rival} cambió eso. El pueblo no necesitó que se lo dijeran; notó la frialdad.",
            "Hay sentimientos que un pueblo no discute. Lo que {name} había sentido por {loved_one} era uno de ellos. Cuando {loved_one} y {rival} formaron hogar, el estado de ánimo de {name} cambió de una manera que todos registraron y nadie nombró.",
        ],
        "reconciliation_1": [
            "Solo una vez en el registro de {village} dos personas que se habían roto de verdad encontraron el camino de vuelta. Fueron {a} y {b}. El registro no dice qué cambió. Pero cambió.",
            "La reconciliación entre {a} y {b} fue la única en el registro de {village}. Ocurrió una vez. El pueblo fue más silencioso por ello.",
        ],
        "reconciliation_n": [
            "{village} tuvo {n} reconciliaciones en su registro. Cada vez, dos personas que se habían roto encontraron el camino de vuelta. Eso es inusual para un lugar de este tamaño.",
            "{n} reconciliaciones en {village}. Algo aquí inclinaba hacia la reparación — o al menos, hacia el intento.",
        ],
        "widowing_note": [
            "Este pueblo conoció la viudedad. {n} personas aquí sobrevivieron a sus parejas. Eso le da forma a un lugar de maneras que no aparecen en ningún recuento.",
            "{village} tuvo {n} personas que sobrevivieron a quien se habían ligado. El pueblo seguía moviéndose alrededor de ese hecho como los pueblos se mueven.",
        ],
        "colophon": "*(semilla del mundo: {seed} — vuelve a ejecutarla y pasarán las mismas cosas, en el mismo orden, a la misma gente)*",
        "era_opening": "Los Primeros Años",
        "era_middle": "Las Estaciones Intermedias",
        "era_closing": "El Registro Final",
        "era_hungry": "Los Años de Hambre",
        "era_loss": "Los Años de Pérdida",
        "era_bitter": "Los Años Amargos",
        "era_quarrelsome": "Las Estaciones Pendencieras",
        "era_warm": "Los Años Cálidos",
        "witness_alive": [
            "Más de este registro pasó cerca de {name} que de nadie más. Estuvo presente en peleas y dones, en deudas y reconciliaciones — y sigue en {village} al cierre.",
            "{name} estuvo más cerca de lo que ocurrió aquí que cualquier otra persona. Puede ser casualidad, o puede ser algo de él. Sigue con vida.",
        ],
        "witness_dead": [
            "Más de este registro pasó cerca de {name} que de nadie más. No sobrevivió para ver su cierre.",
            "{name} estuvo tan cerca de lo que ocurrió aquí que el registro lleva su sello, lo supiera o no. Ya no está.",
        ],
        "witness_departed": [
            "Más de este registro pasó cerca de {name} que de nadie más. Se fue de {village} antes del cierre.",
        ],
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
        "ESTRANGEMENT": [
            "Quelle qu'ait été la dispute d'origine, ce qui existait entre {a} et {b} avait passé de l'amer au définitif.",
            "Cette saison-là, c'était clair : ni {a} ni {b} n'attendait que cela change. L'hostilité avait cessé d'être liée à quoi que ce soit de précis.",
        ],
        "inherited_cold": [
            "{a} avait grandi dans une maison où l'on ne parlait pas en bien de {b}. Il y a des rancœurs qu'on hérite plus qu'on ne gagne, et {a} en portait déjà une part.",
            "Dès le début, {a} semblait avoir sur {b} des opinions formées avant qu'un seul mot soit échangé entre eux.",
        ],
        "inherited_warm": [
            "{a} avait grandi en entendant du bien de {b}. Il y avait déjà quelque chose entre eux, mis là par la génération précédente.",
            "Dès le début, {a} abordait {b} sans méfiance — la famille en avait gardé une bonne opinion, et cela se voyait.",
        ],
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
        "close_grudge": "L'un des deux n'avait pas lâché prise. L'autre ne savait peut-être pas que c'était encore là.",
        "close_debt": "La dette ne fut jamais rendue. Certaines obligations deviennent permanentes simplement parce qu'elles restent trop longtemps sans réponse.",
        "title_reconciliation": "{a} et {b} : une réconciliation",
        "title_estrangement": "{a} et {b} : un éloignement",
        "title_feud": "{a} et {b} : une inimitié",
        "title_grudge": "{a} et {b} : une vieille blessure",
        "title_bond": "{a} et {b} : une amitié",
        "title_love": "{a} et {b} : une histoire",
        "title_open": "{a} et {b} : une affaire non réglée",
        "title_debt": "{a} et {b} : une dette impayée",
        "chronicle_title": ["Chronique de {village}",
                            "Registre de {village}",
                            "Ce qui s'est passé à {village}"],
        "arrivals_note_1_named": "{name} arriva à {village} sans passé que le village connaisse. On ne sait jamais quoi faire de quelqu'un sans histoire.",
        "prologue": [("{village} comptait {n} âmes à l'ouverture de ce récit, "
                      "et il couvre {duration}. "
                      "Rien n'y est inventé ; on a seulement regardé, et raconté."),
                     ("Voici le registre de {village}, qui comptait {n} personnes à son ouverture. "
                      "Il couvre {duration}. "
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
        "mass_death": "Ce {season}-là, en l'an {year}, {names} moururent tous dans les mêmes jours.",
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
        "gift_lean": [
            "Les réserves étaient déjà basses ; le don avait coûté plus qu'il n'y paraissait.",
            "En une saison de vaches maigres, le pain donné est du pain vraiment donné.",
        ],
        "refusal_lean": [
            "La saison n'avait pas été bonne pour personne — ce qui rendait la porte fermée plus difficile à porter.",
            "C'était une époque de faim. Le refus pesait davantage à cause de cela.",
        ],
        "MEDIATION_elder": [
            "Ce fut {c}, {ancien}, qui les fit s'asseoir à la même table. Il y a des choses qui ne cèdent qu'à la patience des années.",
            "{c}, qui avait vu assez d'hivers pour savoir comment les rancœurs se terminent, les fit parler. Quelque chose se dénoua.",
        ],
        "RECONCILIATION": [
            "{a} et {b} se retrouvèrent à se parler de nouveau — sans l'annoncer, un matin c'était là.",
            "La vieille querelle finit par s'user. {a} et {b} échangèrent un regard, puis davantage.",
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
        "birth_arc_title": "{name} : né à {village}",
        "birth_intro": [
            "{name} est né à {village}, de {pa} et {pb}. Il grandit en connaissant tout le monde avant que quiconque ait décidé quoi faire de lui.",
            "{name} atteignit l'âge adulte à {village} ayant grandi dans toutes les vieilles histoires — les affections établies, les rancœurs portées en silence, les dettes qui ne trouvèrent jamais leur chemin de retour.",
        ],
        "birth_orphan": [
            "Quand {name} atteignit l'âge adulte, {dead} était déjà parti. Il grandit vers une absence.",
            "{name} atteignit l'âge adulte à {village} sans que {dead} soit encore en vie. Le village était la famille qui restait.",
        ],
        "adoption_note": [
            "Quand les parents de {child} moururent, {pa} et {pb} prirent l'enfant chez eux. Le village les compta trois dans leur foyer après cela.",
            "Après la mort des deux parents de {child}, {pa} et {pb} ouvrirent leur porte. C'est l'une des choses qu'un village peut faire.",
        ],
        "tell_adoption": [
            "Quand {child} perdit ses deux parents, {pa} et {pb} l'accueillirent. {village} est le genre d'endroit où cela s'est produit.",
            "Le registre note une adoption à {village} : {pa} et {pb} ont recueilli {child} après la mort de ses deux parents.",
        ],
        "birth_settled": [
            "À la clôture de ce registre, {name} avait pris sa place à {village} comme si elle l'avait toujours attendu.",
            "{name} avait grandi ici et, quand le registre se clôt, faisait partie du village autant que n'importe qui d'autre.",
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
        "BLIGHT": [
            "Un fléau frappa {village} {season_in}. Il arriva sans avertissement — {n} foyers virent leurs réserves réduites de moitié en une nuit, et la faim qui suivit fut vive et soudaine.",
            "Quelque chose traversa les champs de {village} {season_in}. Pas le temps, pas la négligence — juste un échec brutal. {n} foyers se retrouvèrent à court d'un coup.",
            "Le fléau {season_in} n'était la faute de personne. La récolte échoua pour {n} foyers sans prévenir, et le village n'avait pas de réponse.",
        ],
        "drought_note": [
            "La sécheresse de l'an {year} était du genre qu'un village n'oublie pas. Deux saisons complètes de maigres récoltes — pas un foyer n'y échappa. Le village découvrit, dans cet intervalle, ce qu'il était.",
            "Il y eut une sécheresse en l'an {year}. Elle dura {season} et au-delà, sans demander la permission. {village} s'en sortit, ou presque.",
            "En l'an {year}, les puits tinrent et le ciel non. Deux saisons de demi-récoltes. Le village devint plus silencieux et plus prudent d'une façon qui ne disparut pas tout à fait ensuite.",
        ],
        "drought_end_note": [
            "La sécheresse de l'an {year} prit fin en {end_season}. {village} n'en fit pas une cérémonie. La récolte revint simplement à ce qu'elle était, et ce fut tout.",
            "Au {end_season} les deux maigres saisons étaient terminées. {village} ne revint pas tout à fait à ce qu'il était en l'an {year} — mais les champs revinrent, et le village reprit.",
            "Ce que {village} était devenu pendant la sécheresse de l'an {year}, une part en demeura. Certaines économies ne se désapprennent pas vite. La récolte en {end_season} fut ordinaire ; cela suffit.",
        ],
        "celebration_note": [
            "Quand {newborn} naquit, {parent1} et {parent2} ouvrirent ce qu'ils avaient. Ce fut une de ces fois où {village} se souvint de ce qu'il était.",
            "Il y eut une célébration quand {newborn} arriva — le genre qui n'a pas besoin d'être organisé. {village} se rassembla simplement.",
            "La naissance de {newborn} tomba en bonne saison. Le village la marqua comme il marquait les choses importantes : ensemble, sans cérémonie.",
        ],
        "pact_note": [
            "Ce que {a} et {b} avaient n'était pas le genre d'accord pour lequel {village} avait des mots. C'était quelque chose de plus ancien et de moins examiné — et cela tint.",
            "{a} et {b} n'avaient jamais eu besoin de lui donner un nom. Après une certaine saison, ils le firent — en silence, sans témoins. Cela suffit.",
            "Le village avait un mot pour les partenaires et un mot pour les voisins. Ce que {a} et {b} étaient l'un pour l'autre n'en nécessitait aucun.",
        ],
        "tribute_note": [
            "Quand {name} mourut, ceux qui l'avaient aimé apportèrent du pain à ceux qui restaient. Il y a un mot pour cela, même si {village} ne l'aurait pas employé.",
            "Dans les jours qui suivirent la mort de {name}, le village répondit de la seule façon qu'il connaissait — du pain à la porte, sans prévenir. C'est sa propre façon de faire un éloge.",
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
        "lean_recurring": "Ce ne fut pas la seule saison de disette. {village} en connut {n} au fil de ces années — la faim fut une visiteuse régulière, non un seul hiver difficile.",
        "social_hub": "À la clôture de ce récit, {name} était la personne dont les autres à {village} restaient le plus proches — le centre du village, dans la mesure où les villages en ont un.",
        "social_edge": "{name} fut là pendant tout cela, à {village}, sans jamais vraiment y trouver de place. Là pendant toutes ces années, mais en retrait du reste.",
        "founders_gone": "Au terme de ce récit, {remaining} seulement, sur les {original} qui l'avaient ouvert, étaient encore à {village}.",
        "founders_all_gone": "Aucun des {original} qui ouvrirent ce récit n'était encore à {village} à sa clôture. Le village qui restait était entièrement différent.",
        "theme_pride": [
            "Ce village fonctionnait à la fierté. Pas à la cruauté — à la fierté. Celle qui préfère avoir faim plutôt que de demander, et qui le faisait parfois.",
            "Ce qui a façonné {village}, en fin de compte, n'était ni la générosité ni son absence. C'était la fierté : le genre silencieux, qui confond la souffrance avec la dignité.",
        ],
        "theme_debt": [
            "Les comptes ne se sont jamais soldés à {village}. Les faveurs accordées et non rendues s'accumulèrent au fil des années ; le village les gardait dans les têtes, pas dans les livres, et certains y sont encore.",
            "Les dettes étaient la grammaire de {village}. Chaque acte de donner laissait une trace en quelqu'un, et ces traces survivaient à ceux qui les avaient faites.",
        ],
        "theme_quarrel": [
            "{village} était un village qui se disputait. Pas avec méchanceté — on partageait encore le pain —, mais la dispute était la façon dont il prenait sa température, et le thermomètre affichait toujours quelque chose.",
            "La dispute était la façon dont {village} était vivant. Pas un signe d'effondrement ; juste le son de gens qui se souciaient du même petit bout de monde.",
        ],
        "theme_generous": [
            "Ce qui circulait entre les gens de {village} était surtout du pain — donné librement, et le plus souvent rendu. L'économie ici n'était pas l'obligation ; c'était le soin, et ça tenait.",
            "{village} était nourri par sa propre générosité. Tout le monde ne donnait pas, et tous les dons ne revenaient pas ; mais la direction des choses allait vers la main ouverte.",
        ],
        "theme_cold": [
            "Il y avait de la froideur à {village}. Pas de la malveillance — une étroitesse dans le donner, une tendance à compter les provisions. Le village a aussi survécu grâce à cette étroitesse ; mais elle avait un prix.",
            "La porte à {village} ne s'ouvrait pas toujours. Pas par cruauté — mais le village avait appris à garder ce qu'il avait, et l'apprentissage était resté dans les murs.",
        ],
        "mediator_note": [
            "{name} avait raccommodé les gens à {village} plus d'une fois. Ce genre de travail appartient à l'infrastructure silencieuse du village — jamais remarqué, mais perceptible quand il s'arrête.",
            "Plus d'une fois, {name} avait assis deux personnes à la même table sans les laisser partir en colère. On ne le voit pas, jusqu'au jour où l'on remarque que c'était toujours la même personne.",
        ],
        "resentment_note": [
            "Il y a quelque chose dans le registre de plus difficile à nommer : ce que {debtor} devait à {creditor} depuis {seasons} saisons, et ce qui lui arriva dans le portage. Le village ne le savait pas. {creditor} ne le savait pas. Le registre le garde quand même.",
            "Ce que {debtor} devait à {creditor} avait été une gentillesse au départ. Après assez longtemps, c'était devenu autre chose — pas la dette elle-même, mais le poids de la devoir à cette personne en particulier, et l'orgueil qui ne la posait pas.",
            "Le donner et recevoir entre {debtor} et {creditor} avait duré assez longtemps pour devenir une blessure privée. {village} ne l'aurait pas vu. Seul le registre l'a.",
        ],
        "offense_note": [
            "Le jour où la mauvaise histoire parvint à {name} — sur {source}, ou sur ce qui s'était passé entre eux — fut le genre de jour qui ferme une distance et en ouvre une autre. {village} ne le voyait pas toujours.",
            "Il y a des choses qui voyagent plus vite que la vérité à {village}. Ce que {name} entendit sur {source} en était une. Si la version arrivée était exacte, le registre ne le dit pas — seulement que cela changea les choses.",
            "Ce qui s'était passé entre eux et {source} parvint à {name} — pas directement, pas avec précision. C'est ainsi avec les histoires dans un petit endroit. Elles arrivent ayant déjà changé.",
        ],
        "most_generous": [
            "Plus de pain sortit de chez {name} que de toute autre maison à {village}. Le village le remarqua — on remarque toujours ce genre de choses.",
            "{name} donna plus que sa part. Ce n'est pas toujours une position confortable, mais c'était la sienne.",
        ],
        "most_quarrelsome": [
            "{name} se trouva au bout de plus de disputes que n'importe qui à {village}. Pas toujours dans son tort, mais jamais silencieux.",
            "Le village apprit à attendre {name} au centre des choses. Il y en a toujours un comme ça.",
        ],
        "landmark_year": [
            "L'an {year} est celui auquel {village} revient sans cesse. Plus fut décidé dans cet intervalle que dans tout autre.",
            "Il s'est passé plus de choses en l'an {year} que le registre ne peut aisément contenir. Cela a façonné tout ce qui suivit.",
            "S'il est une année qui explique ce que {village} est devenu, c'est l'an {year}.",
        ],
        "trajectory_warming": [
            "{village} s'est terminé plus chaud qu'il n'avait commencé. Quelles que soient les disputes intermédiaires, la direction finale était l'un vers l'autre.",
            "Le récit s'ouvre sur des distances prudentes et se clôt avec moins d'entre elles. Pas vraiment de la chaleur — mais moins de distance.",
        ],
        "trajectory_cooling": [
            "{village} s'est terminé plus froid qu'il n'avait ouvert. Pas brisé — mais éprouvé d'une façon qui se voit.",
            "Ce qui s'était construit entre les gens les premières années, à la clôture il en restait moins. Pas perdu — juste dépensé.",
        ],
        "crisis_season": [
            "Il y eut une {season} où {village} ressentit tout en même temps — des réserves vides et des mots durs dans le même souffle. Ce genre de saison met un village à l'épreuve.",
            "Dans {village}, il y eut une {season} qui demanda plus que les autres. Les réserves étaient basses et les querelles, nombreuses. Le village s'en sortit.",
        ],
        "crisis_season_death": [
            "Il y eut une {season} où {village} porta trop à la fois — des réserves vides, de nombreuses querelles et une mort. Le village s'en sortit, mais pas sans changement.",
            "Une {season} à {village} fut plus dure qu'elle n'aurait dû l'être. Quelqu'un mourut tandis que les réserves étaient basses et les voisins ne se parlaient plus. Ce genre de convergence laisse une trace.",
        ],
        "first_gift": [
            "La première chose qui circula entre les gens de {village} fut un don — de {a} à {b}. Tout village doit bien commencer quelque part.",
            "{a} donna du pain à {b} avant que quoi que ce soit d'autre soit noté. {village} s'ouvrit dans la générosité.",
        ],
        "first_refusal": [
            "Le registre de {village} s'ouvre sur un refus. {a} alla à la porte de {b} et repartit les mains vides.",
            "Avant que quoi que ce soit d'autre soit noté, {b} ferma la porte à {a}. {village} ne s'ouvrit pas chaleureusement.",
        ],
        "first_quarrel": [
            "À {village}, la première chose qui mérita d'être écrite fut une querelle — {a} et {b} aux prises avant que beaucoup d'autres choses se passent.",
            "Le premier événement notable à {village} fut une querelle entre {a} et {b}. Certains villages commencent ainsi.",
        ],
        "first_bond": [
            "La première chose que ce registre note sur {village} est un lien — {a} et {b} se choisirent l'un l'autre avant que le village ait beaucoup d'histoire.",
            "{a} et {b} se lièrent tôt, avant que le village sache ce qu'il était. Ce genre de chose donne le ton.",
        ],
        "last_gift": [
            "La dernière chose enregistrée à {village} fut un don — {a} à {b}.",
            "Ce qui clôt le registre de {village}, c'est un don. {a} donna du pain à {b}, et le récit s'arrêta.",
        ],
        "last_refusal": [
            "La dernière chose que ce registre note à {village} est une porte fermée — {a} renvoya {b}.",
            "Ce sur quoi le registre de {village} se termine est un refus. {a} alla à la porte de {b} et repartit les mains vides.",
        ],
        "last_quarrel": [
            "Le registre de {village} se clôt sur une querelle — {a} et {b}, encore aux mots durs à la fin.",
            "La dernière chose qui valait la peine d'être notée à {village} fut une querelle. {a} et {b}. Elle ne fut pas résolue avant que le récit s'arrête.",
        ],
        "last_bond": [
            "Ce sur quoi le registre de {village} se ferme, c'est un lien — {a} et {b}, se choisissant près de la fin.",
            "La dernière chose notable à {village} fut un lien. {a} et {b}, tard dans le récit.",
        ],
        "lingering_debt": [
            "À la clôture de ce registre, {debtor} devait encore à {creditor}. La faveur avait été accordée {duration} auparavant, et elle était simplement restée sans réponse.",
            "Une dette à {village} survécut à tout : {creditor} avait donné du pain à {debtor}, et cela ne fut jamais rendu. Ces choses arrivent.",
        ],
        "notable_rumor": [
            "Le récit avait grandi dans la transmission. De tout ce qui se dit à {village}, ce qui s'était passé entre {a} et {b} était ce qui avait le plus changé — au moment d'atteindre la plupart des oreilles, ce n'était plus tout à fait l'histoire telle qu'elle avait commencé.",
            "Ce qui s'était passé entre {a} et {b} fut l'histoire qui voyagea le plus loin à {village}. Elle ne voyagea pas intacte.",
        ],
        "decisive_season": [
            "La saison sur laquelle ce registre bascule est le {season} de l'an {year}. Plus fut décidé en ces semaines que dans toute autre partie de cette chronique.",
            "Si {village} a un pivot, c'est le {season} de l'an {year}. Tout ce qui précéda fut un prélude ; tout ce qui suivit, une conséquence.",
        ],
        "hard_year": [
            "L'an {year} fut le pire que ce registre note pour {village}. {n} personnes moururent cette année-là. Le village fut plus petit après et le savait.",
            "{n} morts en l'an {year}. Plus que toute autre année dans ce registre. {village} en fut changée, même si elle continua d'avancer.",
        ],
        "good_year": [
            "L'an {year} fut le plus vivant qu'ait connu {village}. Plus de liens, plus de naissances, plus de réparations que dans toute autre partie du registre.",
            "S'il y eut une bonne année à {village}, ce fut l'an {year}. Les choses s'ouvrirent alors d'une façon qu'elles ne firent nulle part ailleurs dans le registre.",
        ],
        "memorial_note": [
            "Quand {name} mourut, le village se rassembla. C'est ce que fait un village pour quelqu'un dont il avait besoin sans le savoir.",
            "{name} était le genre de personne dont l'absence change la forme du lieu. Quand ils moururent, ceux qui restèrent se rapprochèrent — comme les gens le font quand ils réalisent que quelque chose est parti.",
            "Le registre montre un rassemblement après la mort de {name}. Pas une cérémonie. Juste des gens qui avaient aimé la même personne se retrouvant au même endroit.",
        ],
        "illness_note": [
            "{name} tomba malade durant ce registre. Il se remit, bien qu'il ne fut plus tout à fait ce qu'il avait été.",
            "Il y eut une période où {name} était trop malade pour travailler. Le village fit ce que font les villages — il remarqua, et aida du mieux qu'il put.",
        ],
        "illness_note_death": [
            "{name} tomba malade. Il ne se remit pas.",
            "La maladie emporta {name} — pas rapidement, mais régulièrement, comme ces choses se passent dans les petits endroits.",
        ],
        "vigil_note": [
            "Quand {name} fut malade assez longtemps pour que le village cessât de prétendre que ce n'était pas grave, ceux qui le portaient en silence le montrèrent.",
            "Il arriva un moment dans la maladie de {name} où le village se rassembla sans y être invité. Non pour aider — il n'y avait rien à faire. Pour être là.",
            "La veille auprès de {name} fut silencieuse. Personne ne dit qu'il en tenait une. Mais les mêmes personnes continuaient d'apparaître au même seuil.",
        ],
        "population_arc": [
            "Le village atteignit son sommet de {peak} âmes en l'an {peak_year}, puis redescendit à {close} à la clôture de ce registre.",
            "À son apogée, {village} comptait {peak} personnes. À la fin, {close} restèrent. C'est là que le compte s'arrêta.",
        ],
        "population_arc_stable": [
            "{village} resta à peu près de la même taille tout au long de ce registre. Il commença avec {start} et finit avec {close}. Certains villages tiennent.",
        ],
        "estrangement_note": [
            "{a} et {b} ne s'étaient plus parlé depuis {duration}. Le village avait appris à composer avec cela — comme un village apprend toujours à composer avec ce qui ne sera pas réparé.",
            "Le froid entre {a} et {b} durait depuis {duration} et ne montrait aucun signe de dégel. Certains silences survivent à leurs raisons.",
        ],
        "feud_note": [
            "{a} et {b} étaient en guerre. Pas du genre ouvert — du genre qui vous force à choisir avant que vous sachiez que vous choisissez. Le village s'est organisé autour de leur haine.",
            "La querelle entre {a} et {b} était du genre qui donne sa forme à un village. Tout le monde savait de quel côté il était, même ceux qui auraient préféré rester à l'écart.",
            "Il n'y avait pas moyen de prétendre que {a} et {b} pouvaient être dans la même pièce. Le registre a une querelle, et une querelle change ce qu'est un village.",
        ],
        "debt_culture_giving": [
            "{village} fonctionnait à crédit. Plus de pain sortait qu'il n'en revenait — non par négligence, mais parce que donner était la manière d'être ici.",
            "Le grand livre de {village} était toujours déficitaire : les dons dépassaient les remboursements. Le village vivait de confiance, et la plupart du temps la confiance tenait.",
        ],
        "debt_culture_hoarding": [
            "{village} était prudente avec son pain. Les refus dépassaient les dons en nombre — non par cruauté, mais par précaution. Le genre d'endroit où l'on sait à quelle porte ne pas frapper.",
            "Le pain ne circulait pas librement à {village}. Les gens comptaient leurs réserves et y réfléchissaient à deux fois. La plupart y réfléchirent trop souvent.",
        ],
        "debt_culture_balanced": [
            "{village} tenait ses comptes. Le pain sortait ; le pain revenait. Le village ne donnait ni avec imprudence ni ne serrait trop.",
        ],
        "most_bereaved": [
            "{name} avait survécu à plus de gens qu'il aimait que quiconque à {village}. Ce genre de perte fait quelque chose à une personne.",
            "Plus des liens proches de {name} avaient disparu à la clôture du registre que ceux de toute autre personne. {village} lui devait une reconnaissance qu'elle ne lui donna jamais tout à fait.",
        ],
        "oldest_resident": [
            "{name} était à {village} depuis la première saison enregistrée ici — le seul encore présent à la clôture qui avait tout vu.",
            "De tous ceux qui étaient là au début, seul {name} restait à la fin. C'est une façon particulière d'être témoin.",
        ],
        "village_character_generous": [
            "{village} était, au fond, un village qui donnait. Le pain circulait ici plus librement que la plupart des endroits ne pourraient le soutenir.",
            "Plus de pain quittait les mains à {village} qu'on ne l'avait demandé. Ce genre d'endroit est rare.",
        ],
        "village_character_proud": [
            "Ce qui définissait {village} par-dessus tout était sa réticence à demander. Les gens souffraient ici en silence avant de frapper à la porte d'un voisin.",
            "{village} fonctionnait à l'orgueil silencieux. Les affamés se passaient de demander, et ceux qui avaient du surplus gardaient ce qu'ils avaient.",
        ],
        "village_character_healing": [
            "{village} était un village qui choisissait la réparation. Quand les choses se brisaient entre les gens, il y avait toujours quelqu'un pour les asseoir ensemble.",
            "Les querelles arrivaient ici, mais ne duraient généralement pas. Quelqu'un savait toujours à quelle porte frapper en premier.",
        ],
        "village_character_bitter": [
            "L'amertume à {village} avait son propre temps — chronique, de faible intensité, et largement sans réponse.",
            "Les dettes tournaient ici plus souvent qu'autrement. Le village accumulait les rancœurs comme d'autres endroits accumulent la neige.",
        ],
        "village_character_estranged": [
            "{village} se spécialisait dans les silences. Quand les choses tournaient mal entre les gens, la résolution habituelle était la distance.",
            "Les brouilles à {village} survivaient à leurs causes. Les gens apprenaient à contourner les silences plutôt qu'à les briser.",
        ],
        "season_rhythm_lean": [
            "{village} apprit à redouter {season}. Plus de saisons difficiles tombaient à ce moment-là qu'à tout autre moment de l'année.",
            "Si des temps difficiles venaient à {village}, ils arrivaient généralement {season}. Le village en vint à s'y attendre.",
        ],
        "season_rhythm_quarrel": [
            "Les querelles à {village} avaient une saison — {season}, presque toujours. Quelque chose dans cette période de l'année amincissait la patience.",
            "C'était {season} que les choses se brisaient à {village}. Le village le savait et ne semblait pourtant pas pouvoir l'empêcher.",
        ],
        "birth_cohort": [
            "Vers {season} de l'an {year}, {n} enfants naquirent assez proches pour former une génération — le genre qui grandit en se connaissant avant de connaître quoi que ce soit d'autre.",
            "{village} connut une petite vague de naissances autour de {season}, an {year}. {n} enfants grandirent côte à côte, et ce qu'ils partagèrent en grandissant les marqua tous.",
        ],
        "second_gen_1": [
            "{name} fut le premier enfant élevé à {village} à en devenir pleinement l'un des siens. Le village commençait à avoir un passé dont il pouvait se souvenir des deux côtés.",
            "Quand {name} atteignit l'âge adulte, {village} avait déjà l'air d'avoir une histoire. C'est autre chose que d'être nouveau.",
        ],
        "second_gen_n": [
            "À la clôture de ce récit, {n} enfants élevés à {village} en étaient devenus les adultes. Le village commençait à être un endroit qui se souvenait de choses antérieures à ses membres les plus jeunes.",
            "{n} des âmes comptées à {village} à la clôture y étaient nées et avaient grandi. Le village commençait à transmettre.",
        ],
        "large_family": [
            "{pa} et {pb} élevèrent {n} enfants à {village}. C'est suffisant pour une lignée.",
            "Trois enfants vinrent de {pa} et {pb} à {village}. Le village n'avait pas attendu ce genre de continuité.",
        ],
        "mentor_note": [
            "{elder} prit {young} sous son aile quand {young} atteignit l'âge adulte. Quelque chose passa entre eux — le genre de chose qui ne peut pas s'enseigner directement, seulement se témoigner.",
            "Quand {young} atteignit l'âge adulte à {village}, {elder} fut celui qui fit la différence. Il y a toujours une personne comme ça, au bon endroit au bon moment.",
        ],
        "legacy_note": [
            "Ce que {teacher} avait enseigné à {student} ne mourut pas avec lui. Quelque chose de cette patience resta dans la façon dont {student} travaillait.",
            "{teacher} avait transmis quelque chose à {student} qui survécut à sa mort. On le voyait dans la façon dont {student} travaillait — soigneuse, délibérée, exactement comme l'avait fait l'ancien.",
            "L'enseignement entre {teacher} et {student} s'avéra être du genre qui dure. {student} travaillait de la même façon longtemps après que {teacher} fut parti.",
        ],
        "jealousy_note": [
            "Quand {loved_one} et {rival} firent leur arrangement, tout le monde n'en fut pas heureux. {name} avait porté quelque chose pour {loved_one} — en silence, sans jamais le dire — et le lien arriva comme une porte qui se ferme.",
            "{name} avait su, sans jamais l'exprimer, qu'il y avait quelque chose entre eux et {loved_one}. Le lien avec {rival} changea cela. Le village n'eut pas besoin qu'on lui dise ; il remarqua la froideur.",
            "Il y a des sentiments qu'un village ne discute pas. Ce que {name} avait ressenti pour {loved_one} en était un. Quand {loved_one} et {rival} unirent leurs foyers, l'humeur de {name} changea d'une façon que tout le monde remarqua sans jamais la nommer.",
        ],
        "reconciliation_1": [
            "Une seule fois dans le registre de {village}, deux personnes qui s'étaient vraiment brisées trouvèrent le chemin du retour. C'étaient {a} et {b}. Le registre ne dit pas ce qui changea. Mais quelque chose changea.",
            "La réconciliation entre {a} et {b} fut la seule dans le registre de {village}. Elle arriva une fois. Le village en fut plus silencieux.",
        ],
        "reconciliation_n": [
            "{village} eut {n} réconciliations dans son registre. Chaque fois, deux personnes qui s'étaient brisées trouvèrent le chemin du retour. C'est inhabituel pour un endroit de cette taille.",
            "{n} réconciliations à {village}. Quelque chose ici inclinait vers la réparation — ou du moins vers l'effort.",
        ],
        "widowing_note": [
            "Ce village connut le veuvage. {n} personnes ici survécurent à leurs partenaires. Cela façonne un endroit de façons qui n'apparaissent dans aucun compte.",
            "{village} eut {n} personnes qui survécurent à ceux à qui elles s'étaient liées. Le village continuait à se mouvoir autour de ce fait comme les villages se meuvent.",
        ],
        "colophon": "*(graine du monde : {seed} — lancez-la de nouveau et les mêmes choses arriveront, dans le même ordre, aux mêmes gens)*",
        "era_opening": "Les Premières Années",
        "era_middle": "Les Saisons du Milieu",
        "era_closing": "La Fin du Registre",
        "era_hungry": "Les Années de Disette",
        "era_loss": "Les Années de Deuil",
        "era_bitter": "Les Années Amères",
        "era_quarrelsome": "Les Saisons des Querelles",
        "era_warm": "Les Années Douces",
        "witness_alive": [
            "Plus d'événements de ce registre ont traversé {name} que quiconque d'autre. Il était là pour les querelles et les dons, les dettes et les réconciliations — et il est encore à {village} à la clôture.",
            "{name} s'est trouvé plus près de ce qui s'est passé ici que toute autre personne. C'est peut-être le hasard, ou quelque chose en lui. Il est encore en vie.",
        ],
        "witness_dead": [
            "Plus d'événements de ce registre ont traversé {name} que quiconque d'autre. Il n'a pas survécu pour en voir la clôture.",
            "{name} était si près de ce qui s'est passé ici que le registre porte son empreinte, qu'il le sache ou non. Il est parti maintenant.",
        ],
        "witness_departed": [
            "Plus d'événements de ce registre ont traversé {name} que quiconque d'autre. Il a quitté {village} avant la clôture.",
        ],
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
        "ESTRANGEMENT": [
            "Qualquer que fosse a disputa original, o que havia entre {a} e {b} tinha passado de amargo a permanente.",
            "Nessa estação ficou claro: nem {a} nem {b} esperavam que mudasse. A hostilidade tinha deixado de ser por algo específico.",
        ],
        "inherited_cold": [
            "{a} crescera numa casa onde {b} não era falado com apreço. Há rancores que se herdam em vez de se ganhar, e {a} chegou já carregando parte do mais antigo.",
            "Desde o início, {a} parecia ter opiniões sobre {b} formadas antes de qualquer palavra entre eles.",
        ],
        "inherited_warm": [
            "{a} crescera a ouvir coisas boas de {b}. Já havia algo entre eles, posto ali pela geração anterior.",
            "Desde o início, {a} aproximou-se de {b} sem desconfiança — a família tinha-o em boa estima, e notava-se.",
        ],
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
        "close_grudge": "Um deles não tinha largado. O outro pode não ter sabido que ainda estava lá.",
        "close_debt": "A dívida nunca foi devolvida. Algumas obrigações tornam-se permanentes simplesmente por terem passado demasiado tempo sem resposta.",
        "title_reconciliation": "{a} e {b}: uma reconciliação",
        "title_estrangement": "{a} e {b}: um afastamento",
        "title_feud": "{a} e {b}: uma rivalidade",
        "title_grudge": "{a} e {b}: uma velha ferida",
        "title_bond": "{a} e {b}: uma amizade",
        "title_love": "{a} e {b}: um amor",
        "title_open": "{a} e {b}: um assunto por resolver",
        "title_debt": "{a} e {b}: uma dívida por saldar",
        "chronicle_title": ["Crónica de {village}",
                            "Registo de {village}",
                            "O que aconteceu em {village}"],
        "arrivals_note_1_named": "{name} chegou a {village} sem história que a aldeia conhecesse. A aldeia nunca sabe bem o que fazer com isso.",
        "prologue": [("{village} tinha {n} almas quando este registo se abriu, "
                      "e abrange {duration}. "
                      "Nada do que aqui está foi inventado; apenas se olhou, e contou."),
                     ("Este é o registo de {village}, que tinha {n} pessoas quando se abriu. "
                      "Abrange {duration}. "
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
        "mass_death": "Nessa {season}, ano {year}, {names} morreram todos nos mesmos dias.",
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
        "gift_lean": [
            "As reservas já estavam baixas; a dádiva custou mais do que parecia.",
            "Numa estação má, o pão dado é pão verdadeiramente dado.",
        ],
        "refusal_lean": [
            "A estação não tinha sido boa para ninguém — o que tornava a porta fechada mais difícil de suportar.",
            "Era um tempo de fome. A recusa pesava mais por causa disso.",
        ],
        "MEDIATION_elder": [
            "Foi {c}, que já tinha visto o suficiente para saber como os rancores acabam, quem os fez sentar à mesma mesa. Algo se desatou.",
            "{c}, que havia vivido na aldeia tempo suficiente para recordar a última vez que isto acontecera, fê-los falar. Algo se desatou.",
        ],
        "RECONCILIATION": [
            "{a} e {b} voltaram a falar-se — sem declarar nada, simplesmente uma manhã estava lá.",
            "A velha disputa foi-se gastando sozinha. {a} e {b} voltaram a cruzar-se os olhares, e com eles algo mais.",
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
        "birth_arc_title": "{name}: nascido em {village}",
        "birth_intro": [
            "{name} nasceu em {village}, filho de {pa} e {pb}. Cresceu a conhecer toda a gente antes de alguém ter decidido o que fazer com ele.",
            "{name} chegou à maioridade em {village} tendo crescido dentro de todas as velhas histórias — as afeições estabelecidas, os rancores carregados em silêncio, as dívidas que nunca encontraram o caminho de volta.",
        ],
        "birth_orphan": [
            "Quando {name} chegou à maioridade, {dead} já havia partido. Cresceu em direção a uma ausência.",
            "{name} chegou à maioridade em {village} sem {dead} ainda a viver. A aldeia era a família que restava.",
        ],
        "adoption_note": [
            "Quando os pais de {child} morreram, {pa} e {pb} acolheram a criança. A partir daí a aldeia contou três na sua casa.",
            "Depois de ambos os pais de {child} terem partido, {pa} e {pb} abriram a porta. É uma das coisas que uma aldeia pode fazer.",
        ],
        "tell_adoption": [
            "Quando {child} perdeu os dois pais, {pa} e {pb} acolheram-no/na. {village} é o tipo de lugar onde isso aconteceu.",
            "O registo nota uma adoção em {village}: {pa} e {pb} acolheram {child} depois de os dois pais terem partido.",
        ],
        "birth_settled": [
            "Ao encerrar este registo, {name} havia ocupado o seu lugar em {village} como se sempre o tivesse esperado.",
            "{name} havia crescido aqui e, quando o registo se fecha, fazia parte da aldeia tanto como qualquer outro.",
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
        "BLIGHT": [
            "Uma praga chegou a {village} {season_in}. Chegou sem aviso — {n} lares viram as suas reservas reduzidas a metade de um dia para o outro, e a fome que se seguiu foi aguda e repentina.",
            "Algo atravessou os campos de {village} {season_in}. Não foi o tempo, não foi o descuido — foi uma falha súbita. {n} lares ficaram sem nada de uma vez.",
            "A praga {season_in} não foi culpa de ninguém. A colheita falhou em {n} lares sem aviso, e a aldeia não tinha resposta.",
        ],
        "drought_note": [
            "A seca do ano {year} foi do tipo que uma aldeia não esquece. Duas estações completas de colheitas magras — nenhum lar escapou. A aldeia descobriu, nesse período, o que era.",
            "Houve uma seca no ano {year}. Durou o {season} e a estação seguinte, sem pedir licença. {village} sobreviveu, ou quase.",
            "No ano {year}, os poços aguentaram e o céu não. Duas estações de meia colheita. A aldeia tornou-se mais silenciosa e mais cuidadosa de formas que não desapareceram completamente depois.",
        ],
        "drought_end_note": [
            "A seca do ano {year} terminou no {end_season}. {village} não fez uma cerimónia disso. A colheita simplesmente voltou ao que tinha sido, e foi tudo.",
            "No {end_season} as duas estações magras tinham acabado. {village} não voltou inteiramente ao que era no ano {year} — mas os campos voltaram, e a aldeia continuou.",
            "O que {village} se tinha tornado durante a seca do ano {year}, algo disso ficou. Certas economias não se desaprendem rapidamente. A colheita no {end_season} foi ordinária; isso chegou.",
        ],
        "celebration_note": [
            "Quando {newborn} nasceu, {parent1} e {parent2} abriram o que tinham. Foi uma dessas vezes em que {village} se lembrou do que era.",
            "Houve uma celebração quando {newborn} chegou — o tipo que não precisa de organização. {village} simplesmente se reuniu.",
            "O nascimento de {newborn} veio numa boa estação. A aldeia marcou-o como marcava as coisas que importavam: juntos, sem cerimónia.",
        ],
        "pact_note": [
            "O que {a} e {b} tinham não era o tipo de acordo para o qual {village} tinha palavras. Era algo mais antigo e menos examinado — e durou.",
            "{a} e {b} nunca tinham precisado de lhe dar um nome. Depois de certa estação, fizeram-no — em silêncio, sem testemunhas. Bastou isso.",
            "A aldeia tinha uma palavra para os companheiros e uma para os vizinhos. O que {a} e {b} eram um para o outro não requeria nenhuma das duas.",
        ],
        "tribute_note": [
            "Quando {name} morreu, os que o tinham amado trouxeram pão aos que ficaram. Há uma palavra para isso, embora {village} não a usasse.",
            "Nos dias após a morte de {name}, a aldeia respondeu da única forma que sabia — pão à porta, sem avisar. É a sua própria espécie de elegia.",
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
        "lean_recurring": "Não foi a única estação de escassez. {village} conheceu {n} ao longo destes anos — a fome foi uma visita que se repetiu, não um único inverno difícil.",
        "social_hub": "No encerramento deste registo, {name} era a pessoa de quem os outros em {village} mais se mantinham próximos — o centro da aldeia, na medida em que as aldeias têm um centro.",
        "social_edge": "{name} esteve presente em {village} durante tudo isto, mas sem nunca se tecer de todo na aldeia. Ali, mas à margem.",
        "founders_gone": "Dos {original} que abriram este registo, apenas {remaining} estavam ainda em {village} ao seu encerramento.",
        "founders_all_gone": "Nenhum dos {original} que abriram este registo estava ainda em {village} ao seu encerramento. A aldeia que ficou era uma completamente diferente.",
        "theme_pride": [
            "Esta aldeia funcionava com orgulho. Não com crueldade — apenas orgulho. O tipo que prefere passar fome a pedir, e às vezes passava.",
            "O que moldou {village}, no fim, não foi a generosidade nem a sua ausência. Foi o orgulho: o silencioso, que confunde o sofrimento com dignidade.",
        ],
        "theme_debt": [
            "As contas nunca fecharam em {village}. Os favores dados e não devolvidos acumularam-se ao longo dos anos; a aldeia guardava-os nas cabeças, não nos livros, e alguns ainda lá estão.",
            "As dívidas eram a gramática de {village}. Cada ato de dar deixava um registo em alguém, e esses registos sobreviviam a quem os fazia.",
        ],
        "theme_quarrel": [
            "{village} era uma aldeia que discutia. Não viciosamente — continuavam a partilhar o pão —, mas a disputa era a forma como tomava a sua temperatura, e o termómetro marcava sempre.",
            "A discussão era como {village} estava viva. Não um sinal de rutura; apenas o som de pessoas que se preocupavam com o mesmo pequeno pedaço de mundo.",
        ],
        "theme_generous": [
            "O que circulava entre as pessoas de {village} era sobretudo pão — dado livremente, e na maior parte devolvido. A economia aqui não era obrigação; era cuidado, e aguentou.",
            "{village} alimentava-se da sua própria generosidade. Nem todos davam, e nem todas as dádivas voltavam; mas a direção das coisas era para a mão aberta.",
        ],
        "theme_cold": [
            "Havia frieza em {village}. Não malícia — uma estreiteza no dar, a tendência para contar as reservas. A aldeia também sobreviveu com essa estreiteza; apenas teve um custo.",
            "A porta em {village} nem sempre se abria. Não por crueldade — mas a aldeia aprendera a guardar o que tinha, e o aprendizado ficara nas paredes.",
        ],
        "mediator_note": [
            "{name} trouxe as pessoas de volta ao diálogo em {village} mais de uma vez. Esse tipo de trabalho pertence à infraestrutura silenciosa da aldeia — nunca mencionado, mas notado quando falta.",
            "Mais de uma vez, {name} sentou duas pessoas à mesma mesa e não deixou nenhuma partir zangada. É fácil não notar, até se perceber que era sempre a mesma pessoa.",
        ],
        "resentment_note": [
            "Há algo no registo mais difícil de nomear: o que {debtor} devia a {creditor} durante {seasons} estações, e o que lhe aconteceu no carregamento. A aldeia não sabia. {creditor} não sabia. O registo guarda-o de qualquer maneira.",
            "O que {debtor} devia a {creditor} tinha sido uma gentileza no início. Depois de tempo suficiente tornou-se outra coisa — não a dívida em si, mas o peso de a dever a essa pessoa em particular, e o orgulho que não a largava.",
            "O dar e receber entre {debtor} e {creditor} tinha durado tempo suficiente para se tornar uma ferida privada. {village} não teria visto. Só o registo o tem.",
        ],
        "offense_note": [
            "O dia em que a história errada chegou a {name} — sobre {source}, ou sobre algo que tinha acontecido entre eles — foi o tipo de dia que fecha uma distância e abre outra. {village} nem sempre o via acontecer.",
            "Há coisas que viajam mais depressa do que a verdade em {village}. O que {name} ouviu sobre {source} era uma delas. Se a versão que chegou era exacta, o registo não o diz — apenas que mudou as coisas.",
            "O que tinha passado entre eles e {source} chegou a {name} — não directamente, não com precisão. É assim com as histórias num lugar pequeno. Chegam já tendo mudado.",
        ],
        "most_generous": [
            "De nenhuma casa saiu mais pão do que da de {name}. A aldeia reparou nisso — repara sempre.",
            "{name} deu mais do que lhe cabia. Não é sempre uma posição confortável, mas era a dele.",
        ],
        "most_quarrelsome": [
            "{name} esteve numa ponta de mais disputas do que qualquer outro em {village}. Nem sempre errado, mas nunca calado.",
            "A aldeia aprendeu a esperar por {name} no meio de tudo. Há sempre um assim.",
        ],
        "landmark_year": [
            "O ano {year} é aquele a que {village} continua a voltar. Mais foi decidido nesse período do que em qualquer outro.",
            "Aconteceu mais no ano {year} do que o registo consegue facilmente conter. Moldou tudo o que veio depois.",
            "Se há um ano que explica o que {village} se tornou, é o ano {year}.",
        ],
        "trajectory_warming": [
            "{village} terminou mais quente do que começou. Quaisquer que fossem as disputas no meio, a direção final era um para o outro.",
            "O registo abre em distâncias cautelosas e fecha com menos delas. Não exatamente calor — mas menos distância.",
        ],
        "trajectory_cooling": [
            "{village} terminou mais fria do que abriu. Não destruída — mas desgastada de uma forma que se nota.",
            "O que se construíra entre as pessoas nos primeiros anos, ao encerrar o registo era menos. Não perdido — apenas gasto.",
        ],
        "crisis_season": [
            "Houve uma {season} em que {village} sentiu tudo ao mesmo tempo — despensas vazias e palavras duras no mesmo fôlego. Esse tipo de estação põe à prova uma aldeia.",
            "Em {village}, houve uma {season} que exigiu mais do que as outras. As reservas eram escassas e as disputas, muitas. A aldeia sobreviveu.",
        ],
        "crisis_season_death": [
            "Houve uma {season} em que {village} carregou demasiado ao mesmo tempo — despensas vazias, muitas disputas e uma morte. A aldeia sobreviveu, mas não saiu ilesa.",
            "Uma {season} em {village} foi mais dura do que devia ser. Alguém morreu enquanto as reservas estavam baixas e os vizinhos não se falavam. Esse tipo de convergência deixa marca.",
        ],
        "first_gift": [
            "A primeira coisa que circulou entre as pessoas de {village} foi um presente — de {a} para {b}. Toda aldeia tem de começar de algum lugar.",
            "{a} deu pão a {b} antes de qualquer outra coisa ser registada. {village} abriu em generosidade.",
        ],
        "first_refusal": [
            "O registo de {village} abre-se com uma recusa. {a} foi à porta de {b} e voltou de mãos vazias.",
            "Antes de qualquer outra coisa ser anotada, {b} fechou a porta a {a}. {village} não abriu com calor.",
        ],
        "first_quarrel": [
            "Em {village}, a primeira coisa que mereceu ser escrita foi uma disputa — {a} e {b} em palavras duras antes que muito mais tivesse acontecido.",
            "O primeiro acontecimento notável em {village} foi uma disputa entre {a} e {b}. Algumas aldeias começam assim.",
        ],
        "first_bond": [
            "A primeira coisa que este registo anota sobre {village} é um vínculo — {a} e {b} escolheram-se um ao outro antes de a aldeia ter muita história.",
            "{a} e {b} vincularam-se cedo, antes de a aldeia saber o que era. Esse tipo de coisa dá o tom.",
        ],
        "last_gift": [
            "A última coisa registada em {village} foi um presente — {a} a {b}.",
            "O que fecha o registo de {village} é um presente. {a} deu pão a {b}, e o relato parou.",
        ],
        "last_refusal": [
            "A última coisa que este registo nota em {village} é uma porta fechada — {a} mandou {b} embora.",
            "O que termina o registo de {village} é uma recusa. {a} foi à porta de {b} e voltou de mãos vazias.",
        ],
        "last_quarrel": [
            "O registo de {village} fecha numa disputa — {a} e {b}, ainda com palavras duras no final.",
            "A última coisa que valeu a pena anotar em {village} foi uma disputa. {a} e {b}. Não foi resolvida antes de o relato parar.",
        ],
        "last_bond": [
            "O que fecha o registo de {village} é um vínculo — {a} e {b}, escolhendo-se perto do fim.",
            "A última coisa notável em {village} foi um vínculo. {a} e {b}, tarde no relato.",
        ],
        "lingering_debt": [
            "Ao encerrar este registo, {debtor} ainda devia a {creditor}. O favor tinha sido dado {duration} antes, e simplesmente ficou sem resposta.",
            "Uma dívida em {village} sobreviveu a tudo: {creditor} tinha dado pão a {debtor}, e nunca foi devolvido. Estas coisas acontecem.",
        ],
        "notable_rumor": [
            "O relato tinha crescido com cada boca. De tudo o que se falou em {village}, o que aconteceu entre {a} e {b} foi o que mais mudou — quando chegou à maioria dos ouvidos, já não era bem a história que tinha começado.",
            "O que se passou entre {a} e {b} foi a história que mais longe viajou em {village}. Não viajou intacta.",
        ],
        "decisive_season": [
            "A estação em que este registo muda de rumo é o {season} do ano {year}. Mais foi decidido nessas semanas do que em qualquer outra parte desta crónica.",
            "Se {village} tem um ponto de viragem, é o {season} do ano {year}. Tudo o que veio antes foi prelúdio; tudo o que veio depois, consequência.",
        ],
        "hard_year": [
            "O ano {year} foi o pior que este registo anota para {village}. {n} pessoas morreram nesse período. A aldeia ficou mais pequena depois e sabia disso.",
            "{n} mortes no ano {year}. Mais do que qualquer outro ano neste registo. {village} ficou mudada por isso, mesmo que continuasse a avançar.",
        ],
        "good_year": [
            "O ano {year} foi o mais vivo que {village} já conheceu. Mais laços, mais nascimentos, mais reparações do que em qualquer outra parte do registo.",
            "Se houve um bom ano em {village}, foi o ano {year}. As coisas abriram-se então de uma forma que não aconteceu em mais nenhum momento.",
        ],
        "memorial_note": [
            "Quando {name} morreu, a aldeia reuniu-se. É o que uma aldeia faz por alguém de que precisava sem o saber.",
            "{name} era o tipo de pessoa cuja ausência muda a forma do lugar. Quando morreu, os que ficaram aproximaram-se uns dos outros — como as pessoas fazem quando percebem que algo se foi.",
            "O registo mostra uma reunião após a morte de {name}. Não uma cerimónia. Apenas pessoas que tinham amado a mesma pessoa encontrando-se no mesmo lugar.",
        ],
        "illness_note": [
            "{name} adoeceu durante este registo. Recuperou, embora não fosse bem o que tinha sido.",
            "Houve um período em que {name} estava demasiado doente para trabalhar. A aldeia fez o que as aldeias fazem — reparou, e ajudou no que pôde.",
        ],
        "illness_note_death": [
            "{name} adoeceu. Não recuperou.",
            "A doença levou {name} — não rapidamente, mas de forma constante, como estas coisas acontecem nos lugares pequenos.",
        ],
        "vigil_note": [
            "Quando {name} tinha estado doente tempo suficiente para a aldeia deixar de fingir que não era grave, os que o tinham carregado em silêncio tornaram-no visível.",
            "Chegou um momento na doença de {name} em que a aldeia se reuniu sem ser pedido. Não para ajudar — não havia nada a fazer. Para estar.",
            "A vigília por {name} foi silenciosa. Ninguém disse que a estava a fazer. Mas as mesmas pessoas continuavam a aparecer no mesmo limiar.",
        ],
        "population_arc": [
            "A aldeia atingiu o seu pico de {peak} almas no ano {peak_year}, depois desceu para {close} ao fecho deste registo.",
            "No seu auge, {village} tinha {peak} pessoas. No final, ficaram {close}. Foi aí que a contagem se fixou.",
        ],
        "population_arc_stable": [
            "{village} manteve-se aproximadamente do mesmo tamanho ao longo deste registo. Começou com {start} e terminou com {close}. Algumas aldeias aguentam.",
        ],
        "estrangement_note": [
            "{a} e {b} não se tinham falado em {duration}. A aldeia aprendera a trabalhar em volta disso — como uma aldeia aprende sempre a trabalhar em volta do que não vai ser consertado.",
            "O frio entre {a} e {b} tinha {duration} e não mostrava sinais de degelo. Alguns silêncios sobrevivem às suas razões.",
        ],
        "feud_note": [
            "{a} e {b} estavam em guerra. Não do tipo aberto — do tipo que te faz escolher antes de saberes que estás a escolher. A aldeia organizou-se à volta do seu ódio.",
            "A inimizade entre {a} e {b} era do tipo que dá forma a uma aldeia. Toda a gente sabia de que lado estava, mesmo os que teriam preferido ficar de fora.",
            "Não havia como fingir que {a} e {b} podiam estar na mesma sala. O registo tem uma inimizade, e uma inimizade muda o tipo de lugar que é uma aldeia.",
        ],
        "debt_culture_giving": [
            "{village} funcionava a crédito. Saía mais pão do que voltava — não por descuido, mas porque dar era a maneira de ser aqui.",
            "O livro de contas de {village} estava sempre em défice: os presentes superavam os pagamentos. A aldeia vivia de confiança, e na maior parte das vezes a confiança aguentava.",
        ],
        "debt_culture_hoarding": [
            "{village} era cuidadosa com o seu pão. As recusas superavam os presentes — não crueldade, mas cautela. O tipo de sítio onde se sabe a que porta não bater.",
            "O pão não circulava livremente em {village}. As pessoas contavam as suas reservas e pensavam duas vezes. A maioria pensou demasiadas vezes.",
        ],
        "debt_culture_balanced": [
            "{village} mantinha as suas contas. O pão saía; o pão voltava. A aldeia não dava com imprudência nem segurava demasiado.",
        ],
        "most_bereaved": [
            "{name} sobreviveu a mais pessoas que amava do que qualquer outra em {village}. Esse tipo de perda faz algo a uma pessoa.",
            "Mais das ligações próximas de {name} tinham desaparecido ao fechar o registo do que as de qualquer outra pessoa. {village} devia-lhe um reconhecimento que nunca lhe deu bem.",
        ],
        "oldest_resident": [
            "{name} estava em {village} desde a primeira estação aqui registada — o único ainda presente no final que tinha visto tudo.",
            "De todos os que estavam no início, só {name} ficou no fim. É uma forma particular de ser testemunha.",
        ],
        "village_character_generous": [
            "{village} era, no fundo, uma aldeia que dava. O pão circulava aqui mais livremente do que a maioria dos sítios conseguiria sustentar.",
            "Saiu mais pão das mãos em {village} do que alguém alguma vez pediu. Esse tipo de sítio é raro.",
        ],
        "village_character_proud": [
            "O que definia {village} acima de tudo era a sua relutância em pedir. As pessoas aqui sofriam em silêncio antes de bater à porta do vizinho.",
            "{village} funcionava com orgulho silencioso. Os famintos ficavam sem pedir, e os que tinham de sobra guardavam o que tinham.",
        ],
        "village_character_healing": [
            "{village} era uma aldeia que escolhia a reparação. Quando as coisas se partiam entre as pessoas, havia sempre alguém disposto a sentá-las juntas.",
            "As brigas aconteciam aqui, mas normalmente não duravam. Alguém sabia sempre a que porta bater primeiro.",
        ],
        "village_character_bitter": [
            "O rancor em {village} era o seu próprio tipo de clima — crónico, de baixa intensidade, e maioritariamente sem resposta.",
            "As dívidas azedavam aqui mais vezes do que não. A aldeia acumulava ressentimentos como outros sítios acumulam neve.",
        ],
        "village_character_estranged": [
            "{village} especializou-se em silêncios. Quando as coisas corriam mal entre as pessoas, a resolução habitual era a distância.",
            "Os afastamentos em {village} sobreviviam às suas causas. As pessoas aprendiam a trabalhar em volta dos silêncios em vez de os romper.",
        ],
        "season_rhythm_lean": [
            "{village} aprendeu a temer {season}. Mais estações difíceis caíam então do que em qualquer outra altura do ano.",
            "Se tempos difíceis chegavam a {village}, chegavam geralmente {season}. A aldeia chegou a esperá-los.",
        ],
        "season_rhythm_quarrel": [
            "As brigas em {village} tinham uma estação — {season}, quase sempre. Algo nessa época do ano fazia a paciência escassear.",
            "{season} era quando as coisas se partiam em {village}. A aldeia sabia-o e ainda assim não parecia conseguir preveni-lo.",
        ],
        "birth_cohort": [
            "Por volta de {season} do ano {year}, {n} crianças nasceram próximas o suficiente para se tornarem uma geração — o tipo que cresce a conhecer-se antes de conhecer qualquer outra coisa.",
            "{village} teve uma pequena vaga de nascimentos por volta de {season}, ano {year}. {n} crianças cresceram lado a lado, e o que partilharam ao crescer marcou-as a todas.",
        ],
        "second_gen_1": [
            "{name} foi a primeira criança criada em {village} a tornar-se plenamente uma das suas. A aldeia começava a ter um passado de que se podia lembrar dos dois lados.",
            "Quando {name} chegou à maioridade, {village} já parecia algo com história. Isso é diferente de ser novo.",
        ],
        "second_gen_n": [
            "Ao fechar o registo, {n} crianças que tinham crescido em {village} eram já adultos nela. A aldeia estava a tornar-se um lugar que se lembrava de coisas anteriores aos seus membros mais jovens.",
            "{n} das almas contadas em {village} ao fecho tinham nascido e crescido lá. A aldeia começava a transmitir.",
        ],
        "large_family": [
            "{pa} e {pb} criaram {n} filhos em {village}. É suficiente para uma linhagem.",
            "Três filhos vieram de {pa} e {pb} em {village}. A aldeia não esperava esse tipo de continuidade.",
        ],
        "mentor_note": [
            "{elder} tomou {young} sob a sua asa quando {young} chegou à maioridade. Algo passou entre eles — o tipo de coisa que não pode ser ensinada diretamente, apenas testemunhada.",
            "Quando {young} chegou à maioridade em {village}, {elder} foi quem fez a diferença. Há sempre uma pessoa assim, no lugar certo no momento certo.",
        ],
        "legacy_note": [
            "O que {teacher} ensinou a {student} não morreu com o professor. Algo daquela paciência ficou na forma como {student} trabalhava.",
            "{teacher} havia transmitido algo a {student} que sobreviveu à sua morte. Via-se na forma como {student} trabalhava — cuidadosa, deliberada, exatamente como o velho.",
            "O ensinamento entre {teacher} e {student} revelou-se do tipo que perdura. {student} trabalhava da mesma forma muito depois de {teacher} ter partido.",
        ],
        "jealousy_note": [
            "Quando {loved_one} e {rival} fizeram o seu arranjo, nem todos ficaram contentes. {name} tinha carregado algo por {loved_one} — em silêncio, sem nunca o dizer — e a ligação chegou como uma porta a fechar.",
            "{name} sabia, sem nunca o afirmar, que havia algo entre eles e {loved_one}. O vínculo com {rival} mudou isso. A aldeia não precisou de ser informada; notou a frieza.",
            "Há sentimentos que uma aldeia não discute. O que {name} sentia por {loved_one} era um deles. Quando {loved_one} e {rival} formaram lar, o humor de {name} mudou de uma forma que todos registaram e ninguém nomeou.",
        ],
        "reconciliation_1": [
            "Apenas uma vez no registo de {village} duas pessoas que se tinham verdadeiramente rompido encontraram o caminho de volta. Foram {a} e {b}. O registo não diz o que mudou. Mas mudou.",
            "A reconciliação entre {a} e {b} foi a única no registo de {village}. Aconteceu uma vez. A aldeia ficou mais silenciosa por isso.",
        ],
        "reconciliation_n": [
            "{village} teve {n} reconciliações no seu registo. Cada vez, duas pessoas que se tinham rompido encontraram o caminho de volta. É invulgar para um lugar deste tamanho.",
            "{n} reconciliações em {village}. Algo aqui inclinava para a reparação — ou pelo menos para a tentativa.",
        ],
        "widowing_note": [
            "Esta aldeia conheceu a viuvez. {n} pessoas aqui sobreviveram aos seus parceiros. Isso molda um lugar de formas que não aparecem em nenhuma contagem.",
            "{village} teve {n} pessoas que sobreviveram àqueles a quem se tinham ligado. A aldeia continuava a mover-se em torno desse facto como as aldeias se movem.",
        ],
        "colophon": "*(semente do mundo: {seed} — corre-a de novo e as mesmas coisas acontecerão, na mesma ordem, às mesmas pessoas)*",
        "era_opening": "Os Primeiros Anos",
        "era_middle": "As Estações do Meio",
        "era_closing": "O Registo Final",
        "era_hungry": "Os Anos de Fome",
        "era_loss": "Os Anos de Perda",
        "era_bitter": "Os Anos Amargos",
        "era_quarrelsome": "As Estações das Querelas",
        "era_warm": "Os Anos Quentes",
        "witness_alive": [
            "Mais deste registo passou perto de {name} do que de qualquer outra pessoa. Estava presente em disputas e dádivas, em dívidas e reconciliações — e ainda está em {village} no encerramento.",
            "{name} esteve mais perto do que aconteceu aqui do que qualquer outra pessoa. Pode ser acaso, ou pode ser algo nele. Ainda está vivo.",
        ],
        "witness_dead": [
            "Mais deste registo passou perto de {name} do que de qualquer outra pessoa. Não sobreviveu para ver o seu encerramento.",
            "{name} estava tão perto do que aconteceu aqui que o registo carrega a sua marca, soubesse ele ou não. Já não está.",
        ],
        "witness_departed": [
            "Mais deste registo passou perto de {name} do que de qualquer outra pessoa. Saiu de {village} antes do encerramento.",
        ],
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
        "ESTRANGEMENT": [
            "Qualunque fosse stata la disputa originale, quello che c'era tra {a} e {b} era passato dall'amaro al definitivo.",
            "Quella stagione era chiaro: né {a} né {b} si aspettava che cambiasse. L'ostilità aveva smesso di riguardare qualcosa di preciso.",
        ],
        "inherited_cold": [
            "{a} era cresciuto in una casa dove {b} non era tenuto in buon conto. Certi rancori si ereditano più che si guadagnano, e {a} era arrivato già portandone una parte.",
            "Fin dall'inizio, {a} sembrava avere su {b} opinioni formate prima che tra loro passasse una parola.",
        ],
        "inherited_warm": [
            "{a} era cresciuto sentendo cose buone di {b}. C'era già qualcosa tra loro, messo lì dalla generazione precedente.",
            "Fin dall'inizio, {a} si avvicinò a {b} senza diffidenza — la famiglia lo aveva sempre stimato, e si vedeva.",
        ],
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
        "close_grudge": "Uno dei due non aveva lasciato andare. L'altro forse non sapeva che fosse ancora lì.",
        "close_debt": "Il debito non fu mai restituito. Certe obbligazioni diventano permanenti semplicemente perché rimangono troppo a lungo senza risposta.",
        "title_grudge": "{a} e {b}: una vecchia ferita",
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
                      "e abbraccia {duration}. "
                      "Nulla di ciò che segue è inventato; è stato solo osservato, e raccontato."),
                     ("{village} aveva {n} persone quando questo registro fu aperto. "
                      "Abbraccia {duration}. "
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
        "mass_death": "In quell'{season} dell'anno {year}, {names} morirono tutti nello stesso giro di giorni.",
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
        "gift_lean": [
            "Le riserve erano già scarse; il dono era costato più di quanto sembrasse.",
            "In una stagione di magra, il pane dato è pane davvero dato.",
        ],
        "refusal_lean": [
            "La stagione non era stata buona per nessuno — il che rendeva la porta chiusa più difficile da portare.",
            "Era un tempo di fame. Il rifiuto pesava di più per questo.",
        ],
        "MEDIATION_elder": [
            "Fu {c}, {anziano}, a farli sedere allo stesso tavolo. Ci sono cose che cedono solo alla pazienza degli anni.",
            "{c}, che aveva visto abbastanza inverni da sapere come finiscono i rancori, li fece parlare. Qualcosa si allentò.",
        ],
        "RECONCILIATION": [
            "{a} e {b} si ritrovarono a parlarsi di nuovo — senza dichiararlo, una mattina era lì.",
            "La vecchia lite si consumò da sola. {a} e {b} si scambiarono uno sguardo, poi qualcosa di più.",
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
        "birth_arc_title": "{name}: nato a {village}",
        "birth_intro": [
            "{name} nacque a {village}, figlio di {pa} e {pb}. Crebbe conoscendo tutti prima che qualcuno avesse deciso cosa farne.",
            "{name} raggiunse l'età adulta a {village} essendo cresciuto dentro tutte le vecchie storie — le affezioni consolidate, i rancori portati in silenzio, i debiti che non trovarono mai la via del ritorno.",
        ],
        "birth_orphan": [
            "Quando {name} raggiunse l'età adulta, {dead} era già andato. Crebbe verso un'assenza.",
            "{name} raggiunse l'età adulta a {village} senza che {dead} fosse ancora in vita. Il villaggio era la famiglia che restava.",
        ],
        "adoption_note": [
            "Quando i genitori di {child} morirono, {pa} e {pb} accolsero il bambino. Il villaggio li contò in tre nella loro casa da allora.",
            "Dopo che entrambi i genitori di {child} erano partiti, {pa} e {pb} aprirono la porta. È una delle cose che un villaggio può fare.",
        ],
        "tell_adoption": [
            "Quando {child} perse entrambi i genitori, {pa} e {pb} li accolsero. {village} è il tipo di posto dove successe.",
            "Il registro nota un'adozione a {village}: {pa} e {pb} accolsero {child} dopo la morte di entrambi i genitori.",
        ],
        "birth_settled": [
            "Alla chiusura di questo registro, {name} aveva preso il suo posto a {village} come se lo avesse sempre aspettato.",
            "{name} era cresciuto qui e, quando il registro si chiude, faceva parte del villaggio quanto chiunque altro.",
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
        "BLIGHT": [
            "Un flagello colpì {village} {season_in}. Arrivò senza preavviso — {n} famiglie videro le proprie riserve dimezzate da un giorno all'altro, e la fame che ne seguì fu acuta e improvvisa.",
            "Qualcosa attraversò i campi di {village} {season_in}. Non fu il tempo, non fu la trascuratezza — solo un fallimento improvviso. {n} famiglie si ritrovarono a corto tutte insieme.",
            "Il flagello {season_in} non fu colpa di nessuno. Il raccolto fallì per {n} famiglie senza preavviso, e il villaggio non aveva risposta.",
        ],
        "drought_note": [
            "La siccità dell'anno {year} fu del tipo che un villaggio non dimentica. Due stagioni intere di magri raccolti — nessuna famiglia ne fu risparmiata. Il villaggio scoprì, in quel periodo, chi era.",
            "Ci fu una siccità nell'anno {year}. Durò attraverso {season} e nella stagione successiva, senza chiedere il permesso. {village} se la cavò, o quasi.",
            "Nell'anno {year}, i pozzi ressero e il cielo no. Due stagioni di mezzo raccolto. Il villaggio divenne più silenzioso e più cauto in modi che non scomparvero del tutto dopo.",
        ],
        "drought_end_note": [
            "La siccità dell'anno {year} si spezzò in {end_season}. {village} non ne fece una cerimonia. Il raccolto tornò semplicemente a com'era, e fu tutto.",
            "Nell'{end_season} le due stagioni magre erano finite. {village} non tornò del tutto a com'era nell'anno {year} — ma i campi tornarono, e il villaggio riprese.",
            "Quello che {village} era diventato durante la siccità dell'anno {year}, qualcosa rimase. Certe economie non si disimparano in fretta. Il raccolto in {end_season} fu ordinario; bastò.",
        ],
        "celebration_note": [
            "Quando nacque {newborn}, {parent1} e {parent2} aprirono quel che avevano. Fu una di quelle volte in cui {village} si ricordò di cosa era.",
            "Ci fu una celebrazione quando arrivò {newborn} — il tipo che non ha bisogno di essere organizzato. {village} si radunò semplicemente.",
            "La nascita di {newborn} arrivò in una buona stagione. Il villaggio la segnò come segnava le cose che contavano: insieme, senza cerimonie.",
        ],
        "pact_note": [
            "Quello che {a} e {b} avevano non era il tipo di accordo per cui {village} aveva parole. Era qualcosa di più antico e meno esaminato — e resse.",
            "{a} e {b} non avevano mai avuto bisogno di dargli un nome. Dopo una certa stagione, lo fecero — in silenzio, senza testimoni. Bastò.",
            "Il villaggio aveva una parola per i compagni e una per i vicini. Quello che {a} e {b} erano l'uno per l'altro non ne richiedeva nessuna delle due.",
        ],
        "tribute_note": [
            "Quando {name} morì, coloro che lo avevano amato portarono pane a chi era rimasto. C'è una parola per questo, anche se {village} non l'avrebbe usata.",
            "Nei giorni dopo la morte di {name}, il villaggio rispose nell'unico modo che conosceva — pane alla porta, senza annunciarsi. È la sua propria forma di elogio funebre.",
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
        "lean_recurring": "Non fu la sola stagione di carestia. {village} ne contò {n} nel corso di questi anni — la fame fu una visitatrice ricorrente, non un singolo inverno difficile.",
        "social_hub": "Alla chiusura del registro, {name} era la persona di cui gli altri a {village} si tenevano più vicini — il centro del villaggio, nella misura in cui i villaggi ne hanno uno.",
        "social_edge": "{name} fu lì per tutto questo, a {village}, senza mai trovare davvero posto nel tessuto comune. Presente, ma ai margini.",
        "founders_gone": "Dei {original} che aprirono questo registro, solo {remaining} erano ancora a {village} alla sua chiusura.",
        "founders_all_gone": "Nessuno dei {original} che aprirono questo registro era ancora a {village} alla sua chiusura. Il villaggio che restò era completamente diverso.",
        "theme_pride": [
            "Questo villaggio funzionava con l'orgoglio. Non con la crudeltà — solo l'orgoglio. Il tipo che preferisce avere fame piuttosto che chiedere, e a volte lo faceva.",
            "Ciò che ha dato forma a {village}, alla fine, non era la generosità né la sua assenza. Era l'orgoglio: quello silenzioso, che scambia la sofferenza per dignità.",
        ],
        "theme_debt": [
            "I conti non si sono mai chiusi a {village}. I favori dati e non restituiti si accumularono nel corso degli anni; il villaggio li conservava nelle teste, non nei libri, e alcuni ci sono ancora.",
            "I debiti erano la grammatica di {village}. Ogni atto di dare lasciava una traccia in qualcuno, e quelle tracce sopravvivevano a chi le aveva create.",
        ],
        "theme_quarrel": [
            "{village} era un villaggio che litigava. Non in modo vizioso — condividevano ancora il pane —, ma la disputa era il modo in cui prendeva la sua temperatura, e il termometro segnava sempre qualcosa.",
            "Il litigio era il modo in cui {village} era vivo. Non un segno di crollo; solo il suono di persone che si preoccupavano dello stesso piccolo pezzo di mondo.",
        ],
        "theme_generous": [
            "Quello che circolava tra le persone di {village} era soprattutto pane — dato liberamente, e perlopiù restituito. L'economia qui non era obbligo; era cura, e reggeva.",
            "{village} si nutriva della propria generosità. Non tutti davano, e non tutti i doni tornavano; ma la direzione delle cose era verso la mano aperta.",
        ],
        "theme_cold": [
            "C'era freddezza a {village}. Non malvagità — una strettezza nel dare, la tendenza a contare le riserve. Il villaggio sopravvisse anche grazie a quella strettezza; ma aveva un costo.",
            "La porta a {village} non si apriva sempre. Non per crudeltà — ma il villaggio aveva imparato a tenere ciò che aveva, e l'apprendimento era rimasto nelle mura.",
        ],
        "mediator_note": [
            "{name} aveva riconciliato le persone a {village} più di una volta. Quel tipo di lavoro fa parte dell'infrastruttura silenziosa del villaggio — mai citato, ma percepibile quando manca.",
            "Più di una volta, {name} aveva messo due persone allo stesso tavolo senza lasciar partire nessuna arrabbiata. È facile non vederlo, finché non ci si accorge che era sempre la stessa persona.",
        ],
        "resentment_note": [
            "C'è qualcosa nel registro più difficile da nominare: quello che {debtor} doveva a {creditor} per {seasons} stagioni, e cosa gli accadde nel portarlo. Il villaggio non lo sapeva. {creditor} non lo sapeva. Il registro lo conserva comunque.",
            "Quello che {debtor} doveva a {creditor} era stata una gentilezza all'inizio. Dopo abbastanza tempo era diventato qualcos'altro — non il debito in sé, ma il peso di doverlo a quella persona in particolare, e l'orgoglio che non lo mollava.",
            "Il dare e ricevere tra {debtor} e {creditor} era andato avanti abbastanza a lungo da diventare una ferita privata. {village} non lo avrebbe visto. Solo il registro ce l'ha.",
        ],
        "offense_note": [
            "Il giorno in cui la storia sbagliata raggiunse {name} — su {source}, o su quello che era successo tra loro — fu il tipo di giorno che chiude una distanza e ne apre un'altra. {village} non lo vedeva sempre accadere.",
            "Ci sono cose che viaggiano più veloci della verità a {village}. Quello che {name} sentì su {source} era una di quelle. Se la versione arrivata fosse accurata, il registro non lo dice — solo che cambiò le cose.",
            "Quello che era successo tra loro e {source} raggiunse {name} — non direttamente, non con precisione. È così con le storie in un posto piccolo. Arrivano già cambiate.",
        ],
        "most_generous": [
            "Da nessun'altra casa uscì più pane che da quella di {name}. Il villaggio se ne accorse — se ne accorgono sempre.",
            "{name} diede più della sua parte. Non è sempre una posizione comoda da ricoprire, ma era la sua.",
        ],
        "most_quarrelsome": [
            "{name} si trovò da un capo di più dispute di chiunque altro a {village}. Non sempre nel torto, ma mai in silenzio.",
            "Il villaggio imparò ad aspettarsi {name} in mezzo a tutto. C'è sempre qualcuno così.",
        ],
        "landmark_year": [
            "L'anno {year} è quello a cui {village} continua a tornare. Più fu deciso in quel periodo che in qualunque altro.",
            "In quell'anno {year} accadde più di quanto il registro riesca a contenere agevolmente. Plasmò tutto ciò che venne dopo.",
            "Se c'è un anno che spiega cosa è diventato {village}, è l'anno {year}.",
        ],
        "trajectory_warming": [
            "{village} si è chiuso più caldo di com'era cominciato. Quali che fossero le dispute nel mezzo, la direzione finale era l'uno verso l'altro.",
            "Il registro si apre su distanze prudenti e si chiude con meno di esse. Non proprio calore — ma meno distanza.",
        ],
        "trajectory_cooling": [
            "{village} si è chiuso più freddo di com'era aperto. Non spezzato — ma logorato in un modo che si vede.",
            "Quello che si era costruito tra le persone nei primi anni, alla chiusura del registro era meno. Non perso — solo consumato.",
        ],
        "crisis_season": [
            "Ci fu una {season} in cui {village} sentì tutto in una volta — dispense vuote e parole dure nello stesso respiro. Quel tipo di stagione mette alla prova un villaggio.",
            "A {village} ci fu una {season} che chiese più delle altre. Le riserve erano scarse e le liti, molte. Il villaggio resse.",
        ],
        "crisis_season_death": [
            "Ci fu una {season} in cui {village} portò troppo allo stesso tempo — dispense vuote, molte liti e una morte. Il villaggio resse, ma non rimase uguale a prima.",
            "Una {season} a {village} fu più dura di quanto avrebbe dovuto essere. Qualcuno morì mentre le riserve erano scarse e i vicini non si rivolgevano la parola. Quel tipo di convergenza lascia un segno.",
        ],
        "first_gift": [
            "La prima cosa che circolò tra le persone di {village} fu un dono — da {a} a {b}. Ogni villaggio deve cominciare da qualche parte.",
            "{a} diede pane a {b} prima che qualsiasi altra cosa fosse registrata. {village} si aprì nella generosità.",
        ],
        "first_refusal": [
            "Il registro di {village} si apre con un rifiuto. {a} andò alla porta di {b} e tornò a mani vuote.",
            "Prima che qualsiasi altra cosa venisse annotata, {b} chiuse la porta a {a}. {village} non si aprì con calore.",
        ],
        "first_quarrel": [
            "A {village}, la prima cosa che meritò di essere scritta fu una lite — {a} e {b} a dure parole prima che accadesse molto altro.",
            "Il primo evento degno di nota a {village} fu una lite tra {a} e {b}. Alcuni villaggi cominciano così.",
        ],
        "first_bond": [
            "La prima cosa che questo registro annota su {village} è un legame — {a} e {b} si scelsero prima che il villaggio avesse molta storia.",
            "{a} e {b} si legarono presto, prima che il villaggio sapesse cosa fosse. Questo tipo di cosa dà il tono.",
        ],
        "last_gift": [
            "L'ultima cosa registrata a {village} fu un dono — {a} a {b}.",
            "Ciò che chiude il registro di {village} è un dono. {a} diede pane a {b}, e il racconto si fermò.",
        ],
        "last_refusal": [
            "L'ultima cosa che questo registro nota a {village} è una porta chiusa — {a} mandò via {b}.",
            "Con ciò che termina il registro di {village} è un rifiuto. {a} andò alla porta di {b} e tornò a mani vuote.",
        ],
        "last_quarrel": [
            "Il registro di {village} si chiude su una lite — {a} e {b}, ancora a parole dure alla fine.",
            "L'ultima cosa degna di nota a {village} fu una lite. {a} e {b}. Non fu risolta prima che il racconto si fermasse.",
        ],
        "last_bond": [
            "Con ciò che si chiude il registro di {village} è un legame — {a} e {b}, scegliendosi verso la fine.",
            "L'ultima cosa notevole a {village} fu un legame. {a} e {b}, tardi nel racconto.",
        ],
        "lingering_debt": [
            "Alla chiusura di questo registro, {debtor} doveva ancora a {creditor}. Il favore era stato fatto {duration} prima, ed era semplicemente rimasto senza risposta.",
            "Un debito a {village} sopravvisse a tutto: {creditor} aveva dato pane a {debtor}, e non fu mai restituito. Queste cose accadono.",
        ],
        "notable_rumor": [
            "Il racconto era cresciuto nella trasmissione. Di tutto ciò che si disse a {village}, ciò che accadde tra {a} e {b} fu quello che cambiò di più — quando raggiunse la maggior parte delle orecchie, non era più del tutto la storia com'era cominciata.",
            "Ciò che accadde tra {a} e {b} fu la storia che viaggiò più lontano a {village}. Non viaggiò intatta.",
        ],
        "decisive_season": [
            "La stagione su cui questo registro fa perno è il {season} dell'anno {year}. Più fu deciso in quelle settimane che in qualunque altra parte di questa cronaca.",
            "Se {village} ha un punto di svolta, è il {season} dell'anno {year}. Tutto ciò che venne prima fu preludio; tutto ciò che seguì, conseguenza.",
        ],
        "hard_year": [
            "L'anno {year} fu il peggiore che questo registro annoti per {village}. {n} persone morirono in quel tratto. Il villaggio fu più piccolo dopo e lo sapeva.",
            "{n} morti nell'anno {year}. Più di qualunque altro anno in questo registro. {village} ne fu cambiata, anche se continuò ad andare avanti.",
        ],
        "good_year": [
            "L'anno {year} fu il più vivo che {village} abbia mai conosciuto. Più legami, più nascite, più riparazioni che in qualunque altra parte del registro.",
            "Se ci fu un buon anno a {village}, fu l'anno {year}. Le cose si aprirono allora in un modo che non fecero altrove nel registro.",
        ],
        "memorial_note": [
            "Quando {name} morì, il villaggio si riunì. È quello che fa un villaggio per qualcuno di cui aveva bisogno senza saperlo.",
            "{name} era il tipo di persona la cui assenza cambia la forma del posto. Quando morì, quelli che rimasero si avvicinarono — come fanno le persone quando capiscono che qualcosa è andato.",
            "Il registro mostra un raduno dopo la morte di {name}. Non una cerimonia. Solo persone che avevano amato la stessa persona ritrovandosi nello stesso posto.",
        ],
        "illness_note": [
            "{name} si ammalò durante questo registro. Si riprese, anche se non era del tutto quel che era stato.",
            "Ci fu un periodo in cui {name} era troppo malato per lavorare. Il villaggio fece quello che fanno i villaggi — notò, e aiutò quel che poté.",
        ],
        "illness_note_death": [
            "{name} si ammalò. Non si riprese.",
            "La malattia portò via {name} — non rapidamente, ma costantemente, come queste cose succedono nei posti piccoli.",
        ],
        "vigil_note": [
            "Quando {name} era stato abbastanza malato a lungo da far smettere al villaggio di fingere che non fosse serio, quelli che lo portavano in silenzio lo resero visibile.",
            "Arrivò un momento nella malattia di {name} in cui il villaggio si radunò senza essere chiamato. Non per aiutare — non c'era nulla da fare. Per esserci.",
            "La veglia per {name} fu silenziosa. Nessuno disse che la stava facendo. Ma le stesse persone continuavano ad apparire alla stessa soglia.",
        ],
        "population_arc": [
            "Il villaggio raggiunse il suo apice di {peak} anime nell'anno {peak_year}, poi scese a {close} alla chiusura di questo registro.",
            "Al suo massimo, {village} contava {peak} persone. Alla fine, ne rimasero {close}. È lì che il conto si fermò.",
        ],
        "population_arc_stable": [
            "{village} rimase grossomodo della stessa dimensione per tutto il registro. Iniziò con {start} e finì con {close}. Certi villaggi reggono.",
        ],
        "estrangement_note": [
            "{a} e {b} non si parlavano da {duration}. Il villaggio aveva imparato a lavorarci intorno — come un villaggio impara sempre a lavorare intorno a ciò che non verrà riparato.",
            "Il freddo tra {a} e {b} durava da {duration} e non mostrava segni di disgelo. Certi silenzi sopravvivono alle loro ragioni.",
        ],
        "feud_note": [
            "{a} e {b} erano in guerra. Non del tipo aperto — del tipo che ti costringe a scegliere prima che tu sappia di stare scegliendo. Il villaggio si organizzò attorno al loro odio.",
            "La faida tra {a} e {b} era del tipo che dà forma a un villaggio. Tutti sapevano da che parte stavano, anche quelli che avrebbero preferito restare fuori.",
            "Non c'era modo di fingere che {a} e {b} potessero stare nella stessa stanza. Il registro ha una faida, e una faida cambia il tipo di posto che è un villaggio.",
        ],
        "debt_culture_giving": [
            "{village} funzionava a credito. Usciva più pane di quanto ne tornasse — non per negligenza, ma perché dare era il modo di essere qui.",
            "Il libro contabile di {village} era sempre in deficit: i doni superavano i rimborsi. Il villaggio viveva di fiducia, e per lo più la fiducia reggeva.",
        ],
        "debt_culture_hoarding": [
            "{village} era prudente con il suo pane. I rifiuti superavano i doni — non crudeltà, ma cautela. Il tipo di posto dove si sa a quale porta non bussare.",
            "Il pane non circolava liberamente a {village}. La gente contava le proprie riserve e ci pensava due volte. La maggior parte ci pensò troppe volte.",
        ],
        "debt_culture_balanced": [
            "{village} teneva i suoi conti. Il pane usciva; il pane tornava. Il villaggio non dava con imprudenza né stringeva troppo.",
        ],
        "most_bereaved": [
            "{name} sopravvisse a più persone che amava di chiunque altro a {village}. Quel tipo di perdita fa qualcosa a una persona.",
            "Più dei legami stretti di {name} erano spariti alla chiusura del registro che quelli di chiunque altro. {village} gli doveva un riconoscimento che non gli diede mai del tutto.",
        ],
        "oldest_resident": [
            "{name} era a {village} dalla prima stagione qui registrata — l'unico ancora presente alla chiusura che aveva visto tutto.",
            "Di tutti quelli che c'erano all'inizio, solo {name} rimase alla fine. È un modo particolare di essere testimone.",
        ],
        "village_character_generous": [
            "{village} era, nel profondo, un villaggio che dava. Il pane circolava qui più liberamente di quanto la maggior parte dei posti potesse sostenere.",
            "Da {village} uscì più pane di quanto qualcuno avesse mai chiesto. Quel tipo di posto è raro.",
        ],
        "village_character_proud": [
            "Ciò che definiva {village} sopra ogni cosa era la sua riluttanza a chiedere. Le persone qui soffrivano in silenzio prima di bussare alla porta di un vicino.",
            "{village} andava avanti con orgoglio silenzioso. Gli affamati facevano a meno di chiedere, e chi aveva del surplus teneva quel che aveva.",
        ],
        "village_character_healing": [
            "{village} era un villaggio che sceglieva la riparazione. Quando le cose si rompevano tra la gente, c'era sempre qualcuno disposto a sederli insieme.",
            "I litigi accadevano qui, ma di solito non duravano. Qualcuno sapeva sempre a quale porta bussare per primo.",
        ],
        "village_character_bitter": [
            "L'amarezza a {village} era il suo tipo di clima — cronica, di bassa intensità, e per lo più senza risposta.",
            "I debiti qui marcivano più spesso che no. Il villaggio accumulava risentimenti come altri posti accumulano neve.",
        ],
        "village_character_estranged": [
            "{village} si specializzò nei silenzi. Quando le cose andavano male tra le persone, la soluzione abituale era la distanza.",
            "I distacchi a {village} sopravvivevano alle loro cause. La gente imparò a lavorarci intorno piuttosto che a romperli.",
        ],
        "season_rhythm_lean": [
            "{village} imparò a temere {season}. Più stagioni difficili cadevano allora che in qualsiasi altro momento dell'anno.",
            "Se tempi difficili arrivavano a {village}, arrivavano di solito {season}. Il villaggio arrivò ad aspettarselo.",
        ],
        "season_rhythm_quarrel": [
            "I litigi a {village} avevano una stagione — {season}, quasi sempre. Qualcosa in quel periodo dell'anno assottigliava la pazienza.",
            "{season} era quando le cose si rompevano a {village}. Il villaggio lo sapeva e tuttavia non sembrava riuscire a prevenirlo.",
        ],
        "birth_cohort": [
            "Intorno a {season} dell'anno {year}, {n} bambini nacquero abbastanza vicini da formare una generazione — il tipo che cresce conoscendosi prima di conoscere qualsiasi altra cosa.",
            "{village} ebbe una piccola ondata di nascite intorno a {season}, anno {year}. {n} bambini crebbero fianco a fianco, e ciò che condivisero crescendo li segnò tutti.",
        ],
        "second_gen_1": [
            "{name} fu il primo figlio cresciuto a {village} a diventarne pienamente uno dei suoi. Il villaggio stava cominciando ad avere un passato di cui ricordarsi da entrambe le parti.",
            "Quando {name} raggiunse l'età adulta, {village} sembrava già qualcosa con una storia. Questo è diverso dall'essere nuovo.",
        ],
        "second_gen_n": [
            "Alla chiusura del registro, {n} bambini cresciuti a {village} ne erano già diventati gli adulti. Il villaggio stava diventando un posto che ricordava cose precedenti ai suoi membri più giovani.",
            "{n} delle anime conteggiate a {village} alla chiusura erano nate e cresciute lì. Il villaggio stava cominciando a trasmettere.",
        ],
        "large_family": [
            "{pa} e {pb} cresciarono {n} figli a {village}. È abbastanza per una stirpe.",
            "Tre figli vennero da {pa} e {pb} a {village}. Il villaggio non si aspettava quel tipo di continuità.",
        ],
        "mentor_note": [
            "{elder} prese {young} sotto la propria ala quando {young} raggiunse la maggiore età. Qualcosa passò tra loro — il tipo di cosa che non può essere insegnata direttamente, solo testimoniata.",
            "Quando {young} raggiunse la maggiore età a {village}, {elder} fu colui che fece la differenza. C'è sempre una persona così, nel posto giusto al momento giusto.",
        ],
        "legacy_note": [
            "Ciò che {teacher} aveva insegnato a {student} non morì con lui. Qualcosa di quella pazienza rimase nel modo in cui {student} lavorava.",
            "{teacher} aveva trasmesso qualcosa a {student} che sopravvisse alla sua morte. Lo si vedeva nel modo in cui {student} lavorava — attento, deliberato, esattamente come il vecchio.",
            "L'insegnamento tra {teacher} e {student} si rivelò essere del tipo che dura. {student} lavorava allo stesso modo molto dopo che {teacher} se ne era andato.",
        ],
        "jealousy_note": [
            "Quando {loved_one} e {rival} fecero il loro accordo, non tutti ne furono contenti. {name} aveva portato qualcosa per {loved_one} — in silenzio, senza mai dirlo — e il legame arrivò come una porta che si chiude.",
            "{name} sapeva, senza mai affermarlo, che c'era qualcosa tra loro e {loved_one}. Il legame con {rival} cambiò questo. Il villaggio non aveva bisogno che glielo dicessero; notò la freddezza.",
            "Ci sono sentimenti che un villaggio non discute. Quello che {name} aveva provato per {loved_one} era uno di quelli. Quando {loved_one} e {rival} unirono le loro case, l'umore di {name} cambiò in un modo che tutti registrarono e nessuno nominò.",
        ],
        "reconciliation_1": [
            "Una sola volta nel registro di {village} due persone che si erano davvero spezzate trovarono la strada del ritorno. Furono {a} e {b}. Il registro non dice cosa cambiò. Ma qualcosa cambiò.",
            "La riconciliazione tra {a} e {b} fu l'unica nel registro di {village}. Avvenne una volta. Il villaggio ne fu più silenzioso.",
        ],
        "reconciliation_n": [
            "{village} ebbe {n} riconciliazioni nel suo registro. Ogni volta, due persone che si erano spezzate trovarono la strada del ritorno. È insolito per un posto di queste dimensioni.",
            "{n} riconciliazioni a {village}. Qualcosa qui inclinava verso la riparazione — o almeno verso il tentativo.",
        ],
        "widowing_note": [
            "Questo villaggio conobbe la vedovanza. {n} persone qui sopravvissero ai loro compagni. Questo plasma un luogo in modi che non appaiono in nessun conto.",
            "{village} ebbe {n} persone che sopravvissero a coloro ai quali si erano legate. Il villaggio continuava a muoversi attorno a questo fatto come i villaggi si muovono.",
        ],
        "colophon": "*(seme del mondo: {seed} — eseguilo di nuovo e le stesse cose accadranno, nello stesso ordine, alle stesse persone)*",
        "era_opening": "I Primi Anni",
        "era_middle": "Le Stagioni di Mezzo",
        "era_closing": "Il Registro Finale",
        "era_hungry": "Gli Anni della Fame",
        "era_loss": "Gli Anni della Perdita",
        "era_bitter": "Gli Anni Amari",
        "era_quarrelsome": "Le Stagioni delle Liti",
        "era_warm": "Gli Anni Caldi",
        "witness_alive": [
            "Più di questo registro è passato vicino a {name} che a chiunque altro. Era presente nelle liti e nei doni, nei debiti e nelle riconciliazioni — ed è ancora a {village} alla chiusura.",
            "{name} era più vicino a ciò che è successo qui di qualsiasi altra persona. Potrebbe essere un caso, o qualcosa in lui. È ancora vivo.",
        ],
        "witness_dead": [
            "Più di questo registro è passato vicino a {name} che a chiunque altro. Non è sopravvissuto per vederne la chiusura.",
            "{name} era così vicino a ciò che è successo qui che il registro porta la sua impronta, che lo sapesse o meno. È andato ora.",
        ],
        "witness_departed": [
            "Più di questo registro è passato vicino a {name} che a chiunque altro. Ha lasciato {village} prima della chiusura.",
        ],
    },
}

_DURATION_NUMS = {
    "en": ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"],
    "es": ["uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez"],
    "fr": ["un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix"],
    "pt": ["um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez"],
    "it": ["uno", "due", "tre", "quattro", "cinque", "sei", "sette", "otto", "nove", "dieci"],
}
_DURATION_ONE = {
    "en": {"year": "one",  "season": "one"},
    "es": {"year": "un",   "season": "una"},
    "fr": {"year": "un",   "season": "une"},
    "pt": {"year": "um",   "season": "uma"},
    "it": {"year": "un",   "season": "una"},
}
_DURATION_YEAR = {
    "en": ("year",    "years"),
    "es": ("año",     "años"),
    "fr": ("an",      "ans"),
    "pt": ("ano",     "anos"),
    "it": ("anno",    "anni"),
}
_DURATION_SEASON = {
    "en": ("season",   "seasons"),
    "es": ("estación", "estaciones"),
    "fr": ("saison",   "saisons"),
    "pt": ("estação",  "estações"),
    "it": ("stagione", "stagioni"),
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

    def _inherited_note(self, cid_a: int, cid_b: int) -> str | None:
        """Return a sentence if cid_a came of age with strong inherited feelings toward cid_b."""
        if "inherited_cold" not in self.t:
            return None
        for ev in self.world.events:
            if ev.kind == "COMING_OF_AGE" and ev.actors[0] == cid_a:
                inherited = ev.data.get("inherited")
                if not inherited:
                    return None
                for other_id, avg_feeling in inherited:
                    if other_id == cid_b:
                        a = self.world.char(cid_a).name
                        b = self.world.char(cid_b).name
                        if avg_feeling < 0:
                            return self.rng.choice(self.t["inherited_cold"]).format(a=a, b=b)
                        else:
                            return self.rng.choice(self.t["inherited_warm"]).format(a=a, b=b)
                return None
        return None

    def _duration_text(self) -> str:
        """Convert world.tick to a human-readable duration like 'four years' or 'two years and three seasons'."""
        total_seasons = self.world.tick // TICKS_PER_SEASON
        years = total_seasons // 4
        rem = total_seasons % 4
        lang = self.lang

        def word(n, kind):
            if n == 1:
                return _DURATION_ONE[lang][kind]
            nums = _DURATION_NUMS[lang]
            return nums[n - 1] if 1 < n <= len(nums) else str(n)

        y_sing, y_plur = _DURATION_YEAR[lang]
        s_sing, s_plur = _DURATION_SEASON[lang]
        conj = self.t["and"]

        if years == 0:
            noun = s_sing if total_seasons == 1 else s_plur
            return f"{word(total_seasons, 'season')} {noun}"
        elif rem == 0:
            noun = y_sing if years == 1 else y_plur
            return f"{word(years, 'year')} {noun}"
        else:
            y_noun = y_sing if years == 1 else y_plur
            s_noun = s_sing if rem == 1 else s_plur
            return f"{word(years, 'year')} {y_noun} {conj} {word(rem, 'season')} {s_noun}"

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
        tick = max(1, self.world.tick)
        quarter = tick / 4

        def w(ev):
            # Gently favour recent events so long runs surface current stories.
            # Range: 0.8x (very early) to 1.1x (most recent quarter).
            if ev.tick < quarter:
                return 0.8
            elif ev.tick < 2 * quarter:
                return 0.9
            elif ev.tick < 3 * quarter:
                return 1.0
            return 1.1

        score = sum(abs(ev.valence) * w(ev) for ev in events)
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
        if "ESTRANGEMENT" in kinds:
            score += 1.2  # a silence that became permanent
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
            parents = [self.world.char(pid) for pid in char.parent_ids
                       if pid < len(self.world.chars)]
            pa = parents[0].name if len(parents) >= 1 else "?"
            pb = parents[1].name if len(parents) >= 2 else pa
            fields: dict = {"name": char.name, "adjs": adjs, "village": self.village,
                            "pa": pa, "pb": pb}
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

    def _in_lean_season(self, tick: int) -> bool:
        """Return True if the given tick falls within a lean or blighted season."""
        season_start = (tick // TICKS_PER_SEASON) * TICKS_PER_SEASON
        season_end = season_start + TICKS_PER_SEASON
        return any(
            ev.kind in ("LEAN_SEASON", "BLIGHT") and season_start <= ev.tick < season_end
            for ev in self.world.events
        )

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
            elif self._in_lean_season(ev.tick) and self.rng.random() < 0.35 and "refusal_lean" in self.t:
                text += " " + self.rng.choice(self.t["refusal_lean"])
        elif ev.kind == "GIFT":
            donor = self.world.char(a)
            if donor.generosity < 0.35 and self.rng.random() < 0.25 and "gift_unexpected" in self.t:
                text += " " + self.rng.choice(self.t["gift_unexpected"])
            elif self._in_lean_season(ev.tick) and self.rng.random() < 0.22 and "gift_lean" in self.t:
                text += " " + self.rng.choice(self.t["gift_lean"])
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

    def birth_arcs(self, pair_arcs: list) -> list:
        """Return birth arcs for village-born characters with enough post-childhood history."""
        w = self.world
        if "birth_arc_title" not in self.t:
            return []
        claimed_ids = {ev.data["id"] for _, evs in pair_arcs for ev in evs}
        born_here = [c for c in w.chars if c.parent_ids is not None and not c.childhood]
        result = []
        for c in born_here:
            coa_ev = next(
                (ev for ev in w.events if ev.kind == "COMING_OF_AGE" and ev.actors[0] == c.id), None)
            if coa_ev is None:
                continue
            events = [ev for ev in w.events
                      if ev.kind in ARC_KINDS and c.id in ev.actors[:2]
                      and ev.tick > coa_ev.tick
                      and ev.data["id"] not in claimed_ids]
            if not events:
                continue
            result.append((c.id, events))
        result.sort(key=lambda x: -len(x[1]))
        return result[:1]

    def tell_birth_arc(self, cid: int, events: list) -> str | None:
        """A short arc about a village-born character coming of age."""
        if "birth_arc_title" not in self.t:
            return None
        char = self.world.char(cid)
        title = self.t["birth_arc_title"].format(name=char.name, village=self.village)
        lines = ["## " + title, ""]

        # Find parent names from BIRTH event
        birth_ev = next(
            (ev for ev in self.world.events if ev.kind == "BIRTH" and ev.actors[0] == cid), None)
        pa_name = self.world.char(birth_ev.actors[1]).name if birth_ev else "?"
        pb_name = self.world.char(birth_ev.actors[2]).name if birth_ev else "?"

        intro = self.rng.choice(self.t["birth_intro"]).format(
            name=char.name, pa=pa_name, pb=pb_name, village=self.village)
        lines.append(intro)
        lines.append("")

        # Note if a parent died before they came of age
        if char.parent_ids and "birth_orphan" in self.t:
            coa_ev = next(
                (ev for ev in self.world.events
                 if ev.kind == "COMING_OF_AGE" and ev.actors[0] == cid), None)
            coa_tick = coa_ev.tick if coa_ev else self.world.tick
            dead_parents = [
                self.world.char(pid).name for pid in char.parent_ids
                if pid < len(self.world.chars)
                and not self.world.chars[pid].alive
                and any(ev.kind == "DEATH" and ev.actors[0] == pid and ev.tick < coa_tick
                        for ev in self.world.events)
            ]
            if dead_parents:
                orphan_note = self.rng.choice(self.t["birth_orphan"]).format(
                    name=char.name, dead=dead_parents[0], village=self.village)
                lines.append(orphan_note)
                lines.append("")

        # A few events from their post-childhood life
        body_events = sorted(events, key=lambda e: e.tick)[:3]
        coa_ev = next(
            (ev for ev in self.world.events if ev.kind == "COMING_OF_AGE" and ev.actors[0] == cid), None)
        prev = coa_ev
        body = []
        for ev in body_events:
            body.append(self.connector(prev, ev) + " " + self.beat(ev))
            prev = ev
        if body:
            lines.append(" ".join(body))
            lines.append("")

        # Closing sentence
        others = [c for c in self.world.living if c.id != cid]
        avg_aff = sum(c.feel(cid) for c in others) / len(others) if others else 0.0
        if avg_aff > 0.15 and "birth_settled" in self.t:
            lines.append(self.rng.choice(self.t["birth_settled"]).format(
                name=char.name, village=self.village))
        return "\n".join(lines)

    def tell_village_moments(self) -> list[str]:
        """Village-wide lean or abundant seasons, and blights, rendered as a section."""
        w = self.world
        lean_events = [ev for ev in w.events if ev.kind == "LEAN_SEASON"]
        bounty_events = [ev for ev in w.events if ev.kind == "BOUNTY"]
        blight_events = [ev for ev in w.events if ev.kind == "BLIGHT"]
        if not lean_events and not bounty_events and not blight_events:
            return []
        parts: list[str] = []
        if "village_section" in self.t:
            parts.append(self.t["village_section"].format(village=self.village))
            parts.append("")
        seasons_in_list = self.t.get("seasons_in", self.t["seasons"])

        # Most severe blight (if any) — rendered first as cause, lean season as effect
        if blight_events and "BLIGHT" in self.t:
            worst_blight = max(blight_events, key=lambda e: e.data.get("affected_count", 0))
            sname = self.season_name(worst_blight.tick)
            sname_in = seasons_in_list[season_index(worst_blight.tick)]
            n = worst_blight.data.get("affected_count", 3)
            para = self.rng.choice(self.t["BLIGHT"]).format(
                season=sname, season_in=sname_in, village=self.village, n=n)
            parts.append(para[0].upper() + para[1:])
            parts.append("")

        # Most severe lean season and, separately, the first bounty (at most one each)
        selected = []
        if lean_events and "LEAN_SEASON" in self.t:
            worst = max(lean_events, key=lambda e: e.data.get("hungry_count", 0))
            selected.append(worst)
        if bounty_events and "BOUNTY" in self.t:
            selected.append(bounty_events[0])
        for ev in selected:
            sname = self.season_name(ev.tick)
            sname_in = seasons_in_list[season_index(ev.tick)]
            if ev.kind == "LEAN_SEASON":
                para = self.rng.choice(self.t["LEAN_SEASON"]).format(
                    season=sname, season_in=sname_in, village=self.village)
                if ev.data.get("had_solidarity") and "LEAN_SEASON_solidarity" in self.t:
                    para += self.rng.choice(self.t["LEAN_SEASON_solidarity"])
                parts.append(para[0].upper() + para[1:] if para else para)
                parts.append("")
                if len(lean_events) > 1 and "lean_recurring" in self.t:
                    parts.append(self.t["lean_recurring"].format(
                        n=len(lean_events), village=self.village))
                    parts.append("")
            else:
                para = self.rng.choice(self.t["BOUNTY"]).format(
                    season=sname, season_in=sname_in, village=self.village)
                parts.append(para[0].upper() + para[1:] if para else para)
                parts.append("")
        return parts

    def tell_founding_persistence(self) -> str | None:
        """Note when a significant fraction of the founding population is gone."""
        if "founders_gone" not in self.t:
            return None
        w = self.world
        founders = [c for c in w.chars if c.joined_at == 0 and c.parent_ids is None]
        original = len(founders)
        if original < 6:
            return None
        remaining = sum(1 for c in founders if c.alive)
        if remaining >= original * 0.6:
            return None
        if remaining == 0 and "founders_all_gone" in self.t:
            return self.t["founders_all_gone"].format(
                original=original, village=self.village)
        return self.t["founders_gone"].format(
            original=original, remaining=remaining, village=self.village)

    def tell_social_close(self) -> str | None:
        """One or two sentences about the village's social hub and most isolated person."""
        living = self.world.living
        if len(living) < 4:
            return None
        if "social_hub" not in self.t:
            return None

        def mutual_avg(c):
            others = [o for o in living if o.id != c.id]
            if not others:
                return 0.0
            return sum((c.feel(o.id) + o.feel(c.id)) / 2 for o in others) / len(others)

        scores = [(c, mutual_avg(c)) for c in living]
        village_mean = sum(s for _, s in scores) / len(scores)
        hub_char, hub_score = max(scores, key=lambda x: x[1])
        edge_char, edge_score = min(scores, key=lambda x: x[1])

        sentences = []
        if hub_score >= 0.2 and hub_score >= village_mean + 0.1:
            sentences.append(self.t["social_hub"].format(
                name=hub_char.name, village=self.village))
        if (edge_score <= -0.1 and edge_score <= village_mean - 0.1
                and edge_char.id != hub_char.id):
            sentences.append(self.t["social_edge"].format(
                name=edge_char.name, village=self.village))
        return " ".join(sentences) if sentences else None

    def tell_village_theme(self) -> str | None:
        """One or two sentences naming the dominant character of the village's history."""
        w = self.world
        if w.tick < 96 or "theme_pride" not in self.t:
            return None
        scale = max(1.0, w.tick / 192)
        evs = w.events

        gifts = sum(1 for ev in evs if ev.kind == "GIFT")
        refusals = sum(1 for ev in evs if ev.kind == "REFUSAL")
        repays = sum(1 for ev in evs if ev.kind == "REPAYMENT")
        quarrels = sum(1 for ev in evs if ev.kind == "QUARREL")
        mediations = sum(1 for ev in evs if ev.kind == "MEDIATION")
        bonds = sum(1 for ev in evs if ev.kind == "BOND")
        open_debts = sum(len(c.debts) for c in w.chars)
        pride_hardships = sum(1 for ev in evs
                              if ev.kind == "HARDSHIP" and ev.data.get("pride"))
        departures = sum(1 for ev in evs if ev.kind == "DEPARTURE")

        repay_rate = repays / gifts if gifts > 0 else 0.0
        mediation_rate = mediations / quarrels if quarrels > 0 else 0.0
        refusal_rate = refusals / (gifts + refusals) if (gifts + refusals) > 0 else 0.0

        candidates: list = []
        if pride_hardships >= 3 * scale:
            candidates.append(("pride", pride_hardships / scale))
        if open_debts >= 4 * scale and repay_rate < 0.30:
            candidates.append(("debt", (open_debts / scale) * (1 - repay_rate)))
        if quarrels >= 5 * scale and mediation_rate < 0.25:
            candidates.append(("quarrel", (quarrels / scale) * (1 - mediation_rate)))
        if gifts >= 7 * scale and bonds >= 2 and repay_rate >= 0.40:
            candidates.append(("generous", (gifts / scale) * repay_rate))
        if refusal_rate >= 0.30 or (departures >= 2 and refusal_rate >= 0.20):
            candidates.append(("cold", refusal_rate * 10 + departures))

        if not candidates:
            return None
        best_theme = max(candidates, key=lambda x: x[1])[0]
        return self.rng.choice(self.t[f"theme_{best_theme}"]).format(village=self.village)

    def tell_village_trajectory(self) -> str | None:
        """Note whether the village ended warmer or colder than it started."""
        w = self.world
        if w.tick < 192 or "trajectory_warming" not in self.t:
            return None
        midpoint = w.tick // 2
        skip_kinds = {"HARVEST", "LEAN_SEASON", "BOUNTY", "HARDSHIP", "FESTIVAL",
                      "ARRIVAL", "DEPARTURE", "DEATH", "BIRTH", "COMING_OF_AGE",
                      "MISFORTUNE", "RUMOR"}

        def avg_valence(evs):
            pair_evs = [ev for ev in evs if len(ev.actors) == 2
                        and ev.kind not in skip_kinds]
            if len(pair_evs) < 4:
                return 0.0
            return sum(ev.valence for ev in pair_evs) / len(pair_evs)

        v_early = avg_valence([ev for ev in w.events if ev.tick < midpoint])
        v_late = avg_valence([ev for ev in w.events if ev.tick >= midpoint])

        if v_early == 0.0 or v_late == 0.0:
            return None
        diff = v_late - v_early

        if diff > 0.15:
            return self.rng.choice(self.t["trajectory_warming"]).format(village=self.village)
        elif diff < -0.20:
            return self.rng.choice(self.t["trajectory_cooling"]).format(village=self.village)
        return None

    def tell_most_generous(self) -> str | None:
        """Name the person who gave the most bread."""
        if "most_generous" not in self.t:
            return None
        from collections import Counter
        donors: Counter = Counter()
        for ev in self.world.events:
            if ev.kind == "GIFT":
                donors[ev.actors[0]] += 1
        if not donors or sum(donors.values()) < 5:
            return None
        top_id, top_count = donors.most_common(1)[0]
        total = sum(donors.values())
        if top_count < total * 0.25:
            return None
        return self.rng.choice(self.t["most_generous"]).format(
            name=self.world.char(top_id).name, village=self.village)

    def tell_most_quarrelsome(self) -> str | None:
        """Name the person who was in the most quarrels."""
        if "most_quarrelsome" not in self.t:
            return None
        from collections import Counter
        fighters: Counter = Counter()
        for ev in self.world.events:
            if ev.kind == "QUARREL":
                fighters[ev.actors[0]] += 1
                fighters[ev.actors[1]] += 1
        if not fighters or sum(fighters.values()) < 8:
            return None
        top_id, top_count = fighters.most_common(1)[0]
        total = sum(fighters.values())
        if top_count < total * 0.25:
            return None
        char = self.world.char(top_id)
        if not char.alive:
            return None
        return self.rng.choice(self.t["most_quarrelsome"]).format(
            name=char.name, village=self.village)

    def tell_drought(self) -> str | None:
        """Note a drought — a 2-season village-wide crop failure."""
        if "drought_note" not in self.t:
            return None
        drought_evs = [ev for ev in self.world.events if ev.kind == "DROUGHT"]
        if not drought_evs:
            return None
        from .model import year_of, season_index
        ev = drought_evs[0]
        year = year_of(ev.tick)
        sname = self.t["seasons"][season_index(ev.tick)]
        return self.rng.choice(self.t["drought_note"]).format(
            year=year, season=sname, village=self.village)

    def tell_drought_end(self) -> str | None:
        """Note the season when a drought finally broke."""
        if "drought_end_note" not in self.t:
            return None
        drought_end_evs = [ev for ev in self.world.events if ev.kind == "DROUGHT_END"]
        if not drought_end_evs:
            return None
        drought_evs = [ev for ev in self.world.events if ev.kind == "DROUGHT"]
        if not drought_evs:
            return None
        from .model import year_of, season_index
        start_year = year_of(drought_evs[0].tick)
        end_ev = drought_end_evs[0]
        end_sname = self.t["seasons"][season_index(end_ev.tick)]
        return self.rng.choice(self.t["drought_end_note"]).format(
            year=start_year, end_season=end_sname, village=self.village)

    def tell_celebration(self) -> str | None:
        """Note a birth that brought the village together in a good season."""
        if "celebration_note" not in self.t:
            return None
        celeb_evs = [ev for ev in self.world.events if ev.kind == "CELEBRATION"]
        if not celeb_evs:
            return None
        ev = celeb_evs[0]
        newborn_id = ev.data.get("newborn")
        if newborn_id is None or newborn_id >= len(self.world.chars):
            return None
        newborn = self.world.chars[newborn_id]
        pids = newborn.parent_ids
        parent1 = self.world.chars[pids[0]].name if pids and pids[0] < len(self.world.chars) else "?"
        parent2 = self.world.chars[pids[1]].name if pids and len(pids) > 1 and pids[1] < len(self.world.chars) else "?"
        return self.rng.choice(self.t["celebration_note"]).format(
            newborn=newborn.name, parent1=parent1, parent2=parent2, village=self.village)

    def tell_pact(self) -> str | None:
        """Note a close friendship between two characters who named what they had."""
        if "pact_note" not in self.t:
            return None
        pact_evs = [ev for ev in self.world.events if ev.kind == "PACT"]
        if not pact_evs:
            return None
        ev = pact_evs[0]
        if len(ev.actors) < 2:
            return None
        a = self.world.chars[ev.actors[0]].name
        b = self.world.chars[ev.actors[1]].name
        return self.rng.choice(self.t["pact_note"]).format(a=a, b=b, village=self.village)

    def tell_tribute_note(self) -> str | None:
        """Name the most notable person whose death prompted tribute gifts."""
        if "tribute_note" not in self.t:
            return None
        tribute_evs = [ev for ev in self.world.events if ev.kind == "TRIBUTE"]
        if not tribute_evs:
            return None
        from collections import Counter
        deceased_counts: Counter = Counter(
            ev.data.get("deceased") for ev in tribute_evs
            if ev.data.get("deceased") is not None
        )
        if not deceased_counts:
            return None
        deceased_id, _ = deceased_counts.most_common(1)[0]
        deceased = self.world.chars[deceased_id] if deceased_id < len(self.world.chars) else None
        if deceased is None:
            return None
        return self.rng.choice(self.t["tribute_note"]).format(
            name=deceased.name, village=self.village)

    def tell_decisive_season(self) -> str | None:
        """Name the single most event-dense season as the chronicle's pivot."""
        if "decisive_season" not in self.t:
            return None
        seasons_run = self.world.tick // TICKS_PER_SEASON
        if seasons_run < 4:
            return None
        _DECISIVE_KINDS = {
            "QUARREL", "BOND", "INGRATITUDE", "RESENTMENT", "ESTRANGEMENT",
            "RECONCILIATION", "MEDIATION", "DEATH", "BIRTH", "REPAYMENT",
            "BLIGHT", "LEAN_SEASON",
        }
        from collections import defaultdict
        by_season: dict = defaultdict(int)
        for ev in self.world.events:
            if ev.kind in _DECISIVE_KINDS:
                by_season[ev.tick // TICKS_PER_SEASON] += 1
        if not by_season:
            return None
        completed = {s: c for s, c in by_season.items() if s < seasons_run - 1}
        if not completed:
            return None
        best_s = max(completed, key=lambda s: completed[s])
        best_count = completed[best_s]
        avg = sum(completed.values()) / len(completed)
        if best_count < avg * 1.8 or best_count < 3:
            return None
        sname = self.t["seasons"][best_s % 4]
        year = (best_s // 4) + 1
        return self.rng.choice(self.t["decisive_season"]).format(
            season=sname, year=year, village=self.village)

    def tell_estrangement_note(self) -> str | None:
        """Note the longest-standing active estrangement at close of record."""
        if "estrangement_note" not in self.t:
            return None
        w = self.world
        living = w.living
        estranged_evs = [ev for ev in w.events if ev.kind == "ESTRANGEMENT"]
        if not estranged_evs:
            return None
        # Find pairs still estranged (not reconciled, both living)
        reconciled = {frozenset(ev.actors[:2]) for ev in w.events if ev.kind == "RECONCILIATION"}
        best_ev = None
        for ev in estranged_evs:
            pair = frozenset(ev.actors[:2])
            if pair in reconciled:
                continue
            a_id, b_id = ev.actors[0], ev.actors[1]
            if a_id >= len(w.chars) or b_id >= len(w.chars):
                continue
            if not w.chars[a_id].alive or not w.chars[b_id].alive:
                continue
            if best_ev is None or ev.tick < best_ev.tick:
                best_ev = ev
        if best_ev is None:
            return None
        age = w.tick - best_ev.tick
        duration = self._duration_text_for(age)
        a = w.char(best_ev.actors[0]).name
        b = w.char(best_ev.actors[1]).name
        return self.rng.choice(self.t["estrangement_note"]).format(
            a=a, b=b, duration=duration, village=self.village)

    def tell_feud(self) -> str | None:
        """Note an active feud — a declared mutual hostility that shaped the village."""
        if "feud_note" not in self.t:
            return None
        feud_evs = [ev for ev in self.world.events if ev.kind == "FEUD"]
        if not feud_evs:
            return None
        ev = feud_evs[0]
        a = self.world.char(ev.actors[0]).name
        b = self.world.char(ev.actors[1]).name
        return self.rng.choice(self.t["feud_note"]).format(a=a, b=b, village=self.village)

    def tell_jealousy(self) -> str | None:
        """Note a JEALOUSY event — unrequited feelings made bitter by a bond."""
        if "jealousy_note" not in self.t:
            return None
        jealousy_evs = [ev for ev in self.world.events if ev.kind == "JEALOUSY"]
        if not jealousy_evs:
            return None
        ev = jealousy_evs[0]
        name = self.world.char(ev.actors[0]).name
        loved_one = self.world.char(ev.actors[1]).name
        rival = self.world.char(ev.actors[2]).name
        return self.rng.choice(self.t["jealousy_note"]).format(
            name=name, loved_one=loved_one, rival=rival, village=self.village)

    def tell_debt_culture(self) -> str | None:
        """Characterize whether this village was giving, hoarding, or balanced."""
        gifts = sum(1 for ev in self.world.events if ev.kind == "GIFT")
        refusals = sum(1 for ev in self.world.events if ev.kind == "REFUSAL")
        total = gifts + refusals
        if total < 6:
            return None
        ratio = gifts / total
        if ratio >= 0.72 and "debt_culture_giving" in self.t:
            return self.rng.choice(self.t["debt_culture_giving"]).format(village=self.village)
        if ratio <= 0.40 and "debt_culture_hoarding" in self.t:
            return self.rng.choice(self.t["debt_culture_hoarding"]).format(village=self.village)
        if 0.45 <= ratio <= 0.65 and "debt_culture_balanced" in self.t:
            return self.rng.choice(self.t["debt_culture_balanced"]).format(village=self.village)
        return None

    def tell_most_bereaved(self) -> str | None:
        """Name the person who lost the most close connections."""
        if "most_bereaved" not in self.t:
            return None
        w = self.world
        total_gone = sum(1 for c in w.chars if not c.alive or c.departed)
        if total_gone < 3:
            return None
        losses: dict = {}
        for c in w.chars:
            if not c.alive:
                continue
            gone = 0
            for ev in w.events:
                if ev.kind not in ("DEATH", "DEPARTURE"):
                    continue
                departed_id = ev.actors[0]
                if departed_id == c.id or departed_id >= len(w.chars):
                    continue
                departed = w.chars[departed_id]
                if abs(c.feel(departed_id)) > 0.3 or abs(departed.feel(c.id)) > 0.3:
                    gone += 1
            losses[c.id] = gone
        if not losses:
            return None
        top_id = max(losses, key=lambda i: losses[i])
        top_count = losses[top_id]
        avg = sum(losses.values()) / len(losses)
        # Only fire if this person lost significantly more than average
        if top_count < 3 or top_count < avg * 1.8:
            return None
        return self.rng.choice(self.t["most_bereaved"]).format(
            name=w.char(top_id).name, village=self.village)

    def tell_oldest_resident(self) -> str | None:
        """Name the last surviving founder when most others are gone."""
        if "oldest_resident" not in self.t:
            return None
        w = self.world
        seasons_run = w.tick // TICKS_PER_SEASON
        if seasons_run < 8:
            return None
        all_founders = [c for c in w.chars if c.joined_at == 0 and c.parent_ids is None]
        if len(all_founders) < 5:
            return None
        surviving = [c for c in all_founders if c.alive]
        if len(surviving) != 1:
            return None
        gone_count = len(all_founders) - 1
        if gone_count < len(all_founders) * 0.6:
            return None
        return self.rng.choice(self.t["oldest_resident"]).format(
            name=surviving[0].name, village=self.village)

    def tell_hard_year(self) -> str | None:
        """Name the year with the most deaths, if it stands out."""
        if "hard_year" not in self.t:
            return None
        from collections import Counter
        by_year: Counter = Counter()
        for ev in self.world.events:
            if ev.kind == "DEATH":
                by_year[year_of(ev.tick)] += 1
        if not by_year:
            return None
        worst_year, worst_n = by_year.most_common(1)[0]
        if worst_n < 3:
            return None
        # skip if already covered by tell_mass_death (same season)
        return self.rng.choice(self.t["hard_year"]).format(
            year=worst_year, n=worst_n, village=self.village)

    def tell_good_year(self) -> str | None:
        """Name the year with the most positive events."""
        if "good_year" not in self.t:
            return None
        from collections import Counter
        _POSITIVE = {"BOND", "BIRTH", "RECONCILIATION", "TRIBUTE", "REPAYMENT", "BOUNTY"}
        by_year: Counter = Counter()
        for ev in self.world.events:
            if ev.kind in _POSITIVE:
                by_year[year_of(ev.tick)] += 1
        if not by_year:
            return None
        n_years = year_of(self.world.tick - 1)
        if n_years < 3:
            return None
        best_year, best_n = by_year.most_common(1)[0]
        avg = sum(by_year.values()) / len(by_year)
        if best_n < avg * 1.6 or best_n < 4:
            return None
        return self.rng.choice(self.t["good_year"]).format(
            year=best_year, village=self.village)

    def tell_population_arc(self) -> str | None:
        """Note the population arc: peak and close, or stability."""
        w = self.world
        if "population_arc" not in self.t:
            return None
        n_years = year_of(w.tick - 1) if w.tick > 0 else 1
        if n_years < 2:
            return None
        # track living count at start of each year
        start_count = w.initial_people
        close_count = sum(1 for c in w.chars if c.alive)
        # find peak: count living chars at each tick by scanning join/death events
        # approximate: use chars' lifespan overlap by year
        by_tick_count: dict = {}
        for yr in range(1, n_years + 2):
            tick_start = (yr - 1) * 96
            alive_at = sum(
                1 for c in w.chars
                if (c.born_at if c.born_at is not None else c.joined_at) <= tick_start
                and (c.died_at if c.died_at is not None else w.tick) > tick_start
            )
            by_tick_count[yr] = alive_at
        peak_year = max(by_tick_count, key=lambda y: by_tick_count[y])
        peak = by_tick_count[peak_year]
        swing = peak - close_count
        if swing <= 1 and abs(close_count - start_count) <= 2:
            if "population_arc_stable" in self.t:
                return self.rng.choice(self.t["population_arc_stable"]).format(
                    start=start_count, close=close_count, village=self.village)
            return None
        if swing < 3:
            return None
        return self.rng.choice(self.t["population_arc"]).format(
            peak=peak, peak_year=peak_year, close=close_count, village=self.village)

    def tell_memorial(self) -> str | None:
        """Note a MEMORIAL event — the village gathered after someone beloved died."""
        if "memorial_note" not in self.t:
            return None
        memorial_evs = [ev for ev in self.world.events if ev.kind == "MEMORIAL"]
        if not memorial_evs:
            return None
        # pick the memorial with the most mourners (most significant death)
        ev = max(memorial_evs, key=lambda e: len(e.actors))
        deceased = self.world.char(ev.actors[0]).name
        return self.rng.choice(self.t["memorial_note"]).format(
            name=deceased, village=self.village)

    def tell_illness(self) -> str | None:
        """Note an illness episode — a character fell ill and either recovered or died."""
        if "illness_note" not in self.t:
            return None
        illness_evs = [ev for ev in self.world.events if ev.kind == "ILLNESS" and ev.actors]
        if not illness_evs:
            return None
        recovery_ids = {ev.actors[0] for ev in self.world.events
                        if ev.kind == "RECOVERY" and ev.actors}
        # prefer illness-then-death (more dramatic) over recovery
        for ev in illness_evs:
            cid = ev.actors[0]
            if cid >= len(self.world.chars):
                continue
            c = self.world.chars[cid]
            if not c.alive and not c.departed and cid not in recovery_ids:
                if "illness_note_death" in self.t:
                    return self.rng.choice(self.t["illness_note_death"]).format(
                        name=c.name, village=self.village)
        # fall back to a recovery story
        for ev in illness_evs:
            cid = ev.actors[0]
            if cid in recovery_ids and cid < len(self.world.chars):
                c = self.world.chars[cid]
                return self.rng.choice(self.t["illness_note"]).format(
                    name=c.name, village=self.village)
        return None

    def tell_vigil(self) -> str | None:
        """Note when the village gathered silently around a gravely ill person."""
        if "vigil_note" not in self.t:
            return None
        vigil_evs = [ev for ev in self.world.events if ev.kind == "VIGIL" and ev.actors]
        if not vigil_evs:
            return None
        ev = vigil_evs[0]
        if ev.actors[0] >= len(self.world.chars):
            return None
        name = self.world.chars[ev.actors[0]].name
        return self.rng.choice(self.t["vigil_note"]).format(name=name, village=self.village)

    def tell_village_character(self) -> str | None:
        """Characterize the village's dominant social pattern."""
        w = self.world
        gifts = sum(1 for ev in w.events if ev.kind == "GIFT")
        refusals = sum(1 for ev in w.events if ev.kind == "REFUSAL")
        quarrels = sum(1 for ev in w.events if ev.kind == "QUARREL")
        mediations = sum(1 for ev in w.events if ev.kind == "MEDIATION")
        resentments = sum(1 for ev in w.events if ev.kind == "RESENTMENT")
        estrangements = sum(1 for ev in w.events if ev.kind == "ESTRANGEMENT")
        pride_events = sum(1 for ev in w.events
                           if ev.kind == "HARDSHIP" and ev.data.get("pride"))
        total_give = gifts + refusals
        total_q = quarrels + mediations

        living_count = max(1, len(w.living))
        seasons_run = max(1, w.tick // TICKS_PER_SEASON)

        # Check each character type in exclusivity order — only the first match fires.
        # "Generous" and "proud" are already covered by tell_debt_culture / tell_village_moments;
        # this method focuses on social-repair and bitterness patterns.
        if mediations >= 5 and total_q >= 8:
            med_ratio = mediations / total_q
            if med_ratio >= 0.13:
                key = "village_character_healing"
                if key in self.t:
                    return self.rng.choice(self.t[key]).format(village=self.village)

        if resentments >= 5 and resentments >= seasons_run * 0.3:
            key = "village_character_bitter"
            if key in self.t:
                return self.rng.choice(self.t[key]).format(village=self.village)

        if estrangements >= 3 and estrangements >= living_count * 0.3:
            key = "village_character_estranged"
            if key in self.t:
                return self.rng.choice(self.t[key]).format(village=self.village)

        return None

    def tell_season_rhythm(self) -> str | None:
        """Note if one season type consistently has more hardship or quarrels."""
        w = self.world
        seasons_run = w.tick // TICKS_PER_SEASON
        if seasons_run < 8:
            return None
        seasons_label = self.t.get("seasons", ("spring", "summer", "autumn", "winter"))

        lean_by_season = [0, 0, 0, 0]
        quarrel_by_season = [0, 0, 0, 0]
        count_by_season = [0, 0, 0, 0]

        for ev in w.events:
            s = season_index(ev.tick)
            count_by_season[s] += 1
            if ev.kind == "LEAN_SEASON":
                lean_by_season[s] += 1
            elif ev.kind == "QUARREL":
                quarrel_by_season[s] += 1

        seasons_per_type = [seasons_run // 4] * 4
        for i in range(seasons_run % 4):
            seasons_per_type[i] += 1

        # Quarrel rhythm: one season type has a markedly higher quarrel rate than the others.
        # (Lean seasons are excluded — they always cluster in winter, which is trivial.)
        total_quarrels = sum(quarrel_by_season)
        if total_quarrels >= 10:
            rates = [
                quarrel_by_season[i] / max(1, seasons_per_type[i])
                for i in range(4)
            ]
            best_s = max(range(4), key=lambda i: rates[i])
            others_avg = sum(rates[j] for j in range(4) if j != best_s) / 3
            if (quarrel_by_season[best_s] >= 5
                    and (others_avg == 0 or rates[best_s] >= others_avg * 2.5)):
                key = "season_rhythm_quarrel"
                if key not in self.t:
                    return None
                return self.rng.choice(self.t[key]).format(
                    season=seasons_label[best_s], village=self.village)
        return None

    def tell_large_family(self) -> str | None:
        """Note if any couple raised 3+ children in the village."""
        if "large_family" not in self.t:
            return None
        w = self.world
        from collections import Counter
        parent_pair: Counter = Counter()
        for c in w.chars:
            if c.parent_ids:
                key = tuple(sorted(c.parent_ids))
                parent_pair[key] += 1
        if not parent_pair:
            return None
        (pa_id, pb_id), n = parent_pair.most_common(1)[0]
        if n < 3:
            return None
        pa = w.chars[pa_id].name if pa_id < len(w.chars) else "?"
        pb = w.chars[pb_id].name if pb_id < len(w.chars) else "?"
        return self.rng.choice(self.t["large_family"]).format(
            pa=pa, pb=pb, n=n, village=self.village)

    def tell_second_generation(self) -> str | None:
        """Note if any born-in-village characters came of age in this record."""
        if "second_gen_1" not in self.t:
            return None
        w = self.world
        came_of_age = [ev for ev in w.events if ev.kind == "COMING_OF_AGE"]
        if not came_of_age:
            return None
        n = len(came_of_age)
        if n == 1:
            char = w.chars[came_of_age[0].actors[0]]
            return self.rng.choice(self.t["second_gen_1"]).format(
                name=char.name, village=self.village)
        return self.rng.choice(self.t["second_gen_n"]).format(
            n=n, village=self.village)

    def tell_birth_cohort(self) -> str | None:
        """Note if several children were born within a short window."""
        if "birth_cohort" not in self.t:
            return None
        w = self.world
        births = [ev for ev in w.events if ev.kind == "BIRTH"]
        if len(births) < 3:
            return None
        seasons_label = self.t.get("seasons", ("spring", "summer", "autumn", "winter"))

        # Slide a 6-season window and find the densest cluster
        birth_ticks = sorted(ev.tick for ev in births)
        best_count = 0
        best_start = birth_ticks[0]
        window = TICKS_PER_SEASON * 6
        for start in birth_ticks:
            count = sum(1 for t in birth_ticks if start <= t < start + window)
            if count > best_count:
                best_count = count
                best_start = start

        if best_count < 3:
            return None

        # Require the cohort to be significantly larger than the base birth rate
        total_seasons = max(1, w.tick // TICKS_PER_SEASON)
        avg_per_6seasons = len(births) * 6 / total_seasons
        if best_count < avg_per_6seasons * 1.8 and best_count < 4:
            return None

        s = season_index(best_start)
        y = year_of(best_start)
        return self.rng.choice(self.t["birth_cohort"]).format(
            n=best_count, season=seasons_label[s], year=y, village=self.village)

    def tell_witness(self) -> str | None:
        """Name the character who was most central to the arc events — by raw event count."""
        if "witness_alive" not in self.t:
            return None
        w = self.world
        counts: dict = {}
        for ev in w.events:
            if ev.kind in ARC_KINDS and len(ev.actors) >= 2:
                for cid in ev.actors[:2]:
                    counts[cid] = counts.get(cid, 0) + 1
        if not counts:
            return None
        vals = sorted(counts.values(), reverse=True)
        top_id = max(counts, key=lambda cid: counts[cid])
        top_count = vals[0]
        second = vals[1] if len(vals) > 1 else 0
        mean = sum(vals) / len(vals)
        if top_count < 15:
            return None
        if top_count < mean * 2.5 or top_count < second * 2.0:
            return None
        char = w.chars[top_id] if top_id < len(w.chars) else None
        if char is None:
            return None
        if char.alive:
            key = "witness_alive"
        elif char.departed:
            key = "witness_departed"
        else:
            key = "witness_dead"
        templates = self.t[key]
        return self.rng.choice(templates).format(name=char.name, village=self.village)

    def tell_mass_death(self) -> str | None:
        """Note the worst single season if 3+ people died in it."""
        if "mass_death" not in self.t:
            return None
        w = self.world
        from collections import defaultdict
        season_deaths: dict = defaultdict(list)
        for ev in w.events:
            if ev.kind == "DEATH":
                sn = ev.tick // TICKS_PER_SEASON
                season_deaths[sn].append(ev)
        if not season_deaths:
            return None
        worst_sn = max(season_deaths, key=lambda sn: len(season_deaths[sn]))
        worst = season_deaths[worst_sn]
        if len(worst) < 3:
            return None
        seasons = self.t["seasons"]
        si = season_index(worst_sn * TICKS_PER_SEASON)
        yr = year_of(worst_sn * TICKS_PER_SEASON)
        names_list = [w.chars[ev.actors[0]].name for ev in worst if ev.actors[0] < len(w.chars)]
        and_word = self.t.get("and", "and")
        if len(names_list) > 2:
            names_str = ", ".join(names_list[:-1]) + f", {and_word} " + names_list[-1]
        else:
            names_str = f" {and_word} ".join(names_list)
        return self.t["mass_death"].format(season=seasons[si], year=yr, names=names_str)

    def tell_landmark_year(self) -> str | None:
        """Name the single most eventful year if it stands clearly above the rest."""
        if "landmark_year" not in self.t:
            return None
        seasons_run = self.world.tick // TICKS_PER_SEASON
        years_run = seasons_run // 4
        if years_run < 2:
            return None
        _LANDMARK_KINDS = {
            "GIFT", "REFUSAL", "QUARREL", "BOND", "INGRATITUDE",
            "RESENTMENT", "ESTRANGEMENT", "RECONCILIATION", "MEDIATION",
            "DEATH", "BIRTH", "REPAYMENT",
        }
        from collections import defaultdict
        by_year: dict = defaultdict(int)
        for ev in self.world.events:
            if ev.kind in _LANDMARK_KINDS:
                by_year[year_of(ev.tick)] += 1
        if not by_year:
            return None
        # Only count completed years
        completed = {y: c for y, c in by_year.items() if y < years_run}
        if not completed:
            return None
        best_year = max(completed, key=lambda y: completed[y])
        best_count = completed[best_year]
        avg = sum(completed.values()) / len(completed)
        if best_count < avg * 1.5 or best_count < 4:
            return None
        return self.rng.choice(self.t["landmark_year"]).format(
            year=best_year + 1, village=self.village)

    def tell_first_moment(self) -> str | None:
        """Note the first notable event in the village's record."""
        wanted = {"GIFT", "REFUSAL", "QUARREL", "BOND"}
        for ev in self.world.events:
            if ev.kind not in wanted or len(ev.actors) < 2:
                continue
            a = self.world.char(ev.actors[0]).name
            b = self.world.char(ev.actors[1]).name
            key = f"first_{ev.kind.lower()}"
            if key not in self.t:
                return None
            return self.rng.choice(self.t[key]).format(
                a=a, b=b, village=self.village)
        return None

    def tell_last_moment(self) -> str | None:
        """Note the last notable event in the village's record — a closing observation."""
        wanted = {"GIFT", "REFUSAL", "QUARREL", "BOND"}
        for ev in reversed(self.world.events):
            if ev.kind not in wanted or len(ev.actors) < 2:
                continue
            a = self.world.char(ev.actors[0]).name
            b = self.world.char(ev.actors[1]).name
            key = f"last_{ev.kind.lower()}"
            if key not in self.t:
                return None
            return self.rng.choice(self.t[key]).format(
                a=a, b=b, village=self.village)
        return None

    def tell_reconciliation(self) -> str | None:
        """Note reconciliation events — rare acts of repair between estranged pairs."""
        rec_evs = [ev for ev in self.world.events
                   if ev.kind == "RECONCILIATION" and len(ev.actors) >= 2]
        n = len(rec_evs)
        if n == 0:
            return None
        if n == 1:
            if "reconciliation_1" not in self.t:
                return None
            a = self.world.char(rec_evs[0].actors[0]).name
            b = self.world.char(rec_evs[0].actors[1]).name
            return self.rng.choice(self.t["reconciliation_1"]).format(
                a=a, b=b, village=self.village)
        if "reconciliation_n" not in self.t:
            return None
        return self.rng.choice(self.t["reconciliation_n"]).format(
            n=n, village=self.village)

    def tell_widowing(self) -> str | None:
        """Note the count of widowing events — people who outlived their partners."""
        if "widowing_note" not in self.t:
            return None
        n = sum(1 for ev in self.world.events if ev.kind == "WIDOWING")
        if n < 1:
            return None
        return self.rng.choice(self.t["widowing_note"]).format(
            n=n, village=self.village)

    def tell_adoption(self) -> str | None:
        """Note an adoption event — a couple who took in an orphaned child."""
        if "tell_adoption" not in self.t:
            return None
        adoption_evs = [ev for ev in self.world.events
                        if ev.kind == "ADOPTION" and len(ev.actors) >= 3]
        if not adoption_evs:
            return None
        ev = adoption_evs[0]
        child = self.world.char(ev.actors[0]).name
        pa = self.world.char(ev.actors[1]).name
        pb = self.world.char(ev.actors[2]).name
        return self.rng.choice(self.t["tell_adoption"]).format(
            child=child, pa=pa, pb=pb, village=self.village)

    def tell_mentor(self) -> str | None:
        """Note a TEACHING event — an elder who mentored a young person."""
        if "mentor_note" not in self.t:
            return None
        teaching_evs = [ev for ev in self.world.events
                        if ev.kind == "TEACHING" and len(ev.actors) >= 2]
        if not teaching_evs:
            return None
        ev = teaching_evs[0]
        elder = self.world.char(ev.actors[0]).name
        young = self.world.char(ev.actors[1]).name
        return self.rng.choice(self.t["mentor_note"]).format(
            elder=elder, young=young, village=self.village)

    def tell_legacy(self) -> str | None:
        """Note a LEGACY event — a teacher's influence that outlasted their death."""
        if "legacy_note" not in self.t:
            return None
        legacy_evs = [ev for ev in self.world.events if ev.kind == "LEGACY"]
        if not legacy_evs:
            return None
        ev = legacy_evs[0]
        if len(ev.actors) < 2:
            return None
        teacher = self.world.char(ev.actors[0]).name
        student = self.world.char(ev.actors[1]).name
        return self.rng.choice(self.t["legacy_note"]).format(
            teacher=teacher, student=student, village=self.village)

    def tell_notable_rumor(self) -> str | None:
        """Note the most widely-shared and distorted story in the village's gossip network."""
        if "notable_rumor" not in self.t:
            return None
        from collections import defaultdict
        _NOTABLE_KINDS = {"GIFT", "REFUSAL", "QUARREL", "INGRATITUDE", "RESENTMENT", "BOND"}
        ev_by_id = {ev.data.get("id", -1): ev for ev in self.world.events
                    if ev.data.get("id", -1) >= 0}
        ev_memories: dict = defaultdict(list)
        for c in self.world.chars:
            for m in c.memories:
                if m.event_id >= 0:
                    ev_memories[m.event_id].append(m)
        best_score = 0.0
        best_eid = None
        for eid, mems in ev_memories.items():
            ev = ev_by_id.get(eid)
            if ev is None or ev.kind not in _NOTABLE_KINDS or len(ev.actors) < 2:
                continue
            fh = [m for m in mems if m.firsthand]
            sh = [m for m in mems if not m.firsthand]
            if not fh or len(sh) < 3:
                continue
            avg_drift = sum(abs(m.valence - fh[0].valence) for m in sh) / len(sh)
            score = len(sh) * avg_drift
            if score > best_score:
                best_score = score
                best_eid = eid
        if best_eid is None or best_score < 4.0:
            return None
        ev = ev_by_id[best_eid]
        a = self.world.char(ev.actors[0]).name
        b = self.world.char(ev.actors[1]).name
        return self.rng.choice(self.t["notable_rumor"]).format(
            a=a, b=b, village=self.village)

    def tell_lingering_debt(self) -> str | None:
        """Note the oldest unpaid debt if it dates from the first half of the run."""
        if "lingering_debt" not in self.t:
            return None
        w = self.world
        threshold = w.tick // 3
        oldest_tick = threshold  # only debts from the first third of the run qualify
        oldest_debtor = oldest_creditor = None
        for c in w.chars:
            if not c.alive:
                continue
            for creditor_id, debt in c.debts.items():
                if debt.since < oldest_tick:
                    oldest_tick = debt.since
                    oldest_debtor = c
                    oldest_creditor = w.char(creditor_id)
        if oldest_debtor is None:
            return None
        if not oldest_creditor.alive:
            return None
        age_ticks = w.tick - oldest_tick
        duration = self._duration_text_for(age_ticks)
        return self.rng.choice(self.t["lingering_debt"]).format(
            debtor=oldest_debtor.name,
            creditor=oldest_creditor.name,
            village=self.village,
            duration=duration)

    def _duration_text_for(self, ticks: int) -> str:
        """Return a natural-language duration string for a given number of ticks."""
        total_seasons = ticks // TICKS_PER_SEASON
        if total_seasons == 0:
            total_seasons = 1
        years = total_seasons // 4
        rem = total_seasons % 4
        lang = self.lang
        def word(n, kind):
            if n == 1:
                return _DURATION_ONE[lang][kind]
            nums = _DURATION_NUMS[lang]
            return nums[n - 1] if 1 < n <= len(nums) else str(n)
        y_sing, y_plur = _DURATION_YEAR[lang]
        s_sing, s_plur = _DURATION_SEASON[lang]
        conj = self.t["and"]
        if years == 0:
            noun = s_sing if total_seasons == 1 else s_plur
            return f"{word(total_seasons, 'season')} {noun}"
        elif rem == 0:
            noun = y_sing if years == 1 else y_plur
            return f"{word(years, 'year')} {noun}"
        else:
            y_noun = y_sing if years == 1 else y_plur
            s_noun = s_sing if rem == 1 else s_plur
            return f"{word(years, 'year')} {y_noun} {conj} {word(rem, 'season')} {s_noun}"

    def tell_crisis_season(self) -> str | None:
        """Note when a lean season coincided with multiple quarrels or a death in the same season."""
        if "crisis_season" not in self.t:
            return None
        from collections import defaultdict
        by_season: dict = defaultdict(list)
        for ev in self.world.events:
            sn = ev.tick // TICKS_PER_SEASON
            by_season[sn].append(ev)
        for sn in sorted(by_season):
            evs = by_season[sn]
            kinds = {ev.kind for ev in evs}
            if "LEAN_SEASON" not in kinds:
                continue
            quarrel_count = sum(1 for ev in evs if ev.kind == "QUARREL")
            has_death = "DEATH" in kinds
            if quarrel_count >= 3 or (quarrel_count >= 2 and has_death):
                sname = self.season_name(sn * TICKS_PER_SEASON)
                tmpl_key = "crisis_season_death" if has_death else "crisis_season"
                if tmpl_key not in self.t:
                    tmpl_key = "crisis_season"
                return self.rng.choice(self.t[tmpl_key]).format(
                    season=sname, village=self.village)
        return None

    def tell_mediator_note(self) -> str | None:
        """Note if one character served as the village's peacekeeper more than others."""
        if "mediator_note" not in self.t:
            return None
        from collections import Counter
        mediator_counts: Counter = Counter()
        total = 0
        for ev in self.world.events:
            if ev.kind == "MEDIATION":
                total += 1
                mid = ev.data.get("mediator")
                if mid is not None:
                    mediator_counts[mid] += 1
        if total < 3:
            return None
        top_id, top_count = mediator_counts.most_common(1)[0] if mediator_counts else (None, 0)
        if top_id is None or top_count < 3:
            return None
        if top_count < total * 0.35:
            return None
        name = self.world.char(top_id).name
        return self.rng.choice(self.t["mediator_note"]).format(name=name, village=self.village)

    def tell_resentment_note(self) -> str | None:
        """Note the private moment when a debt became bitterness — only the debtor knows."""
        if "resentment_note" not in self.t:
            return None
        from .model import TICKS_PER_SEASON
        for ev in self.world.events:
            if ev.kind == "RESENTMENT" and len(ev.actors) >= 2:
                debtor_id, creditor_id = ev.actors[0], ev.actors[1]
                if debtor_id >= len(self.world.chars) or creditor_id >= len(self.world.chars):
                    continue
                debtor = self.world.chars[debtor_id].name
                creditor = self.world.chars[creditor_id].name
                carried = ev.data.get("carried", 0)
                seasons = max(1, carried // TICKS_PER_SEASON)
                return self.rng.choice(self.t["resentment_note"]).format(
                    debtor=debtor, creditor=creditor, seasons=seasons, village=self.village)
        return None

    def tell_offense_note(self) -> str | None:
        """Note the day a story arrived having already changed — gossip that offended the subject."""
        if "offense_note" not in self.t:
            return None
        for ev in self.world.events:
            if ev.kind == "OFFENSE" and len(ev.actors) >= 2:
                listener_id, source_id = ev.actors[0], ev.actors[1]
                if listener_id >= len(self.world.chars) or source_id >= len(self.world.chars):
                    continue
                listener_name = self.world.chars[listener_id].name
                source_name = self.world.chars[source_id].name
                return self.rng.choice(self.t["offense_note"]).format(
                    name=listener_name, source=source_name, village=self.village)
        return None

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
            # Detect one-sided grudge: one person's affinity very negative, the other neutral-ish
            af = a.feel(b.id)
            bf = b.feel(a.id)
            if "title_grudge" in self.t and (
                    (af < -0.55 and bf > -0.2) or (bf < -0.55 and af > -0.2)):
                shape = "grudge"
            else:
                shape = "feud"
        elif final > 0.2:
            shape = "bond"
        else:
            shape = "open"
        return self.t["title_" + shape].format(a=a.name, b=b.name), final, kinds, shape

    def closing(self, final, kinds, departed_cid=None, shape=None):
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
        if shape == "grudge" and "close_grudge" in self.t:
            return self.t["close_grudge"]
        if shape == "debt" and "close_debt" in self.t:
            return self.t["close_debt"]
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
        title, final, kinds, shape = self.arc_title(key, events)
        lines = ["## " + title, ""]
        intro = []
        for cid in sorted(key):
            sentence = self.introduce(self.world.char(cid))
            if sentence:
                intro.append(sentence)
        if intro:
            lines.append(" ".join(intro))
            lines.append("")
        # inherited-feeling note: only for arcs where one person came of age here
        pair = sorted(key)
        if len(pair) == 2:
            inherit_note = (self._inherited_note(pair[0], pair[1]) or
                            self._inherited_note(pair[1], pair[0]))
            if inherit_note:
                lines.append(inherit_note)
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
        lines.append(self.closing(final, kinds, departed_cid=departed_in_arc, shape=shape))
        # If one of the pair died, note it quietly after the closing.
        # Departures are covered separately by tell_departures().
        for cid in sorted(key):
            note = self.death_note(cid)
            if note is not None:
                lines.append("")
                lines.append(note)
        return "\n".join(lines)

    def _era_label(self, era_idx: int, n_eras: int,
                   start_tick: int, end_tick: int,
                   avoid: set | None = None) -> str:
        """Return a short evocative label for a time period based on its dominant events."""
        avoid = avoid or set()
        era_evs = [ev for ev in self.world.events if start_tick <= ev.tick < end_tick]
        era_seasons = max(1, (end_tick - start_tick) // TICKS_PER_SEASON)
        lean = sum(1 for ev in era_evs if ev.kind in ("LEAN_SEASON", "BLIGHT"))
        deaths = sum(1 for ev in era_evs if ev.kind == "DEATH")
        bonds = sum(1 for ev in era_evs if ev.kind in ("BOND", "RECONCILIATION"))
        quarrels = sum(1 for ev in era_evs if ev.kind == "QUARREL")
        resentments = sum(1 for ev in era_evs if ev.kind == "RESENTMENT")

        # Candidates ordered by strength of signal
        candidates = []
        if lean / era_seasons >= 0.35:
            candidates.append("era_hungry")
        if deaths >= 2:
            candidates.append("era_loss")
        if resentments >= 2:
            candidates.append("era_bitter")
        if quarrels >= 5:
            candidates.append("era_quarrelsome")
        if bonds >= 2:
            candidates.append("era_warm")

        # Pick first candidate not already used; fall back to positional generics
        for key in candidates:
            label = self.t.get(key, "")
            if label and label not in avoid:
                return label

        # Generic by position, avoiding repeats
        generics = ["era_opening", "era_middle", "era_closing"]
        for generic_key in [generics[min(era_idx, 2)], generics[-1], generics[0]]:
            label = self.t.get(generic_key, "")
            if label and label not in avoid:
                return label
        return f"Part {era_idx + 1}"

    def chronicle(self):
        w = self.world
        title_tmpl = self.t["chronicle_title"]
        title = (self.rng.choice(title_tmpl) if isinstance(title_tmpl, list) else title_tmpl)
        parts = ["# " + title.format(village=self.village), ""]
        prologue_tmpl = self.t["prologue"]
        parts.append((self.rng.choice(prologue_tmpl) if isinstance(prologue_tmpl, list) else prologue_tmpl
                       ).format(village=self.village, n=self.world.initial_people, days=w.tick,
                                duration=self._duration_text()))

        first_moment = self.tell_first_moment()
        if first_moment:
            parts.append("")
            parts.append(first_moment)

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

        persistence_note = self.tell_founding_persistence()
        if persistence_note:
            parts.append("")
            parts.append(persistence_note)

        hard_year_note = self.tell_hard_year()
        if hard_year_note:
            parts.append("")
            parts.append(hard_year_note)

        drought_note = self.tell_drought()
        if drought_note:
            parts.append("")
            parts.append(drought_note)

        drought_end_note = self.tell_drought_end()
        if drought_end_note:
            parts.append("")
            parts.append(drought_end_note)

        celebration_note = self.tell_celebration()
        if celebration_note:
            parts.append("")
            parts.append(celebration_note)

        pact_note = self.tell_pact()
        if pact_note:
            parts.append("")
            parts.append(pact_note)

        memorial_note = self.tell_memorial()
        if memorial_note:
            parts.append("")
            parts.append(memorial_note)

        illness_note = self.tell_illness()
        if illness_note:
            parts.append("")
            parts.append(illness_note)

        vigil_note = self.tell_vigil()
        if vigil_note:
            parts.append("")
            parts.append(vigil_note)

        population_arc_note = self.tell_population_arc()
        if population_arc_note:
            parts.append("")
            parts.append(population_arc_note)

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

        mass_death_note = self.tell_mass_death()
        if mass_death_note:
            parts.append("")
            parts.append(mass_death_note)

        parts.append("")
        village_moments = self.tell_village_moments()
        if village_moments:
            parts.extend(village_moments)
        crisis_note = self.tell_crisis_season()
        if crisis_note:
            parts.append(crisis_note)
            parts.append("")
        pair_arcs = self.arcs()
        arr_arcs = self.arrival_arcs(pair_arcs)
        brth_arcs = self.birth_arcs(pair_arcs)
        dep_arcs = self.departure_arcs(pair_arcs)
        dep_arc_ids = {cid for cid, _ in dep_arcs}
        for cid, events in arr_arcs:
            section = self.tell_arrival_arc(cid, events)
            if section:
                parts.append(section)
                parts.append("")
        for cid, events in brth_arcs:
            section = self.tell_birth_arc(cid, events)
            if section:
                parts.append(section)
                parts.append("")
        for cid, events in dep_arcs:
            section = self.tell_departure_arc(cid, events)
            if section:
                parts.append(section)
                parts.append("")
        seasons_run = w.tick // TICKS_PER_SEASON
        use_eras = seasons_run >= 16 and "era_opening" in self.t
        if use_eras:
            n_eras = 3 if seasons_run >= 32 else 2
            boundaries = [w.tick * i // n_eras for i in range(n_eras + 1)]
            # Sort arcs chronologically by first event; within each era, preserve drama order
            era_arcs: list = [[] for _ in range(n_eras)]
            for key, events in pair_arcs:
                arc_start = events[0].tick if events else 0
                era_idx = min(n_eras - 1, next(
                    (i for i, b in enumerate(boundaries[1:]) if arc_start < b), n_eras - 1))
                era_arcs[era_idx].append((key, events))
            used_era_labels: set = set()
            for era_idx in range(n_eras):
                if not era_arcs[era_idx]:
                    continue
                label = self._era_label(era_idx, n_eras,
                                        boundaries[era_idx], boundaries[era_idx + 1],
                                        avoid=used_era_labels)
                used_era_labels.add(label)
                parts.append("---")
                parts.append("")
                parts.append(f"*{label}*")
                parts.append("")
                for key, events in era_arcs[era_idx]:
                    parts.append(self.tell_arc(key, events))
                    parts.append("")
        else:
            for key, events in pair_arcs:
                parts.append(self.tell_arc(key, events))
                parts.append("")
        dead_section = self.tell_dead()
        if dead_section:
            parts.extend(dead_section)

        departure_section = self.tell_departures(exclude=dep_arc_ids)
        if departure_section:
            parts.extend(departure_section)

        social_note = self.tell_social_close()
        if social_note:
            parts.append(social_note)
            parts.append("")

        rumor_note = self.tell_notable_rumor()
        if rumor_note:
            parts.append(rumor_note)
            parts.append("")

        decisive_note = self.tell_decisive_season()
        if decisive_note:
            parts.append(decisive_note)
            parts.append("")

        mediator_note = self.tell_mediator_note()
        if mediator_note:
            parts.append(mediator_note)
            parts.append("")

        resentment_note = self.tell_resentment_note()
        if resentment_note:
            parts.append(resentment_note)
            parts.append("")

        offense_note = self.tell_offense_note()
        if offense_note:
            parts.append(offense_note)
            parts.append("")

        theme_note = self.tell_village_theme()
        if theme_note:
            parts.append(theme_note)
            parts.append("")

        trajectory_note = self.tell_village_trajectory()
        if trajectory_note:
            parts.append(trajectory_note)
            parts.append("")

        generous_note = self.tell_most_generous()
        if generous_note:
            parts.append(generous_note)
            parts.append("")

        quarrelsome_note = self.tell_most_quarrelsome()
        if quarrelsome_note:
            parts.append(quarrelsome_note)
            parts.append("")

        landmark_note = self.tell_landmark_year()
        if landmark_note:
            parts.append(landmark_note)
            parts.append("")

        lingering_debt = self.tell_lingering_debt()
        if lingering_debt:
            parts.append(lingering_debt)
            parts.append("")

        tribute_note = self.tell_tribute_note()
        if tribute_note:
            parts.append(tribute_note)
            parts.append("")

        estrangement_note = self.tell_estrangement_note()
        if estrangement_note:
            parts.append(estrangement_note)
            parts.append("")

        feud_note = self.tell_feud()
        if feud_note:
            parts.append(feud_note)
            parts.append("")

        jealousy_note = self.tell_jealousy()
        if jealousy_note:
            parts.append(jealousy_note)
            parts.append("")

        debt_culture_note = self.tell_debt_culture()
        if debt_culture_note:
            parts.append(debt_culture_note)
            parts.append("")

        bereaved_note = self.tell_most_bereaved()
        if bereaved_note:
            parts.append(bereaved_note)
            parts.append("")

        oldest_note = self.tell_oldest_resident()
        if oldest_note:
            parts.append(oldest_note)
            parts.append("")

        birth_cohort_note = self.tell_birth_cohort()
        if birth_cohort_note:
            parts.append(birth_cohort_note)
            parts.append("")

        second_gen_note = self.tell_second_generation()
        if second_gen_note:
            parts.append(second_gen_note)
            parts.append("")

        large_family_note = self.tell_large_family()
        if large_family_note:
            parts.append(large_family_note)
            parts.append("")

        adoption_note = self.tell_adoption()
        if adoption_note:
            parts.append(adoption_note)
            parts.append("")

        mentor_note = self.tell_mentor()
        if mentor_note:
            parts.append(mentor_note)
            parts.append("")

        legacy_note = self.tell_legacy()
        if legacy_note:
            parts.append(legacy_note)
            parts.append("")

        season_note = self.tell_season_rhythm()
        if season_note:
            parts.append(season_note)
            parts.append("")

        character_note = self.tell_village_character()
        if character_note:
            parts.append(character_note)
            parts.append("")

        good_year_note = self.tell_good_year()
        if good_year_note:
            parts.append(good_year_note)
            parts.append("")

        reconciliation_note = self.tell_reconciliation()
        if reconciliation_note:
            parts.append(reconciliation_note)
            parts.append("")

        widowing_note = self.tell_widowing()
        if widowing_note:
            parts.append(widowing_note)
            parts.append("")

        witness_note = self.tell_witness()
        if witness_note:
            parts.append(witness_note)
            parts.append("")

        best, worst = self.extremes()
        if best and worst:
            epilogue_tmpl = self.t["epilogue"]
            epilogue = (self.rng.choice(epilogue_tmpl) if isinstance(epilogue_tmpl, list) else epilogue_tmpl)
            parts.append(epilogue.format(
                a=self.name(best[0]), b=self.name(best[1]),
                c=self.name(worst[0]), d=self.name(worst[1]),
                village=self.village))
            parts.append("")

        last_moment = self.tell_last_moment()
        if last_moment:
            parts.append(last_moment)
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
