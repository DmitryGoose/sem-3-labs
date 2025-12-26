"""
Telegram бот - Помощник по подбору героя в Dota 2
Лабораторная работа №6
Конечный автомат из 3 состояний
"""

import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота (получить у @BotFather)
BOT_TOKEN = "8573641738:AAFafgHH7u9ysU_-mv2YUTq7m2XbpcCjY_U"


# ============================================
# БАЗА ДАННЫХ ГЕРОЕВ DOTA 2
# ============================================

HEROES_DATABASE = {
    # ============================================
    # CARRY ГЕРОИ
    # ============================================
    ("Carry", "Melee", "Легкая"): [
        {"name": "Wraith King", "emoji": "👑", "tip": "Фармь лес с Vampiric Aura, в лейте ты неубиваем с Aegis + ульт."},
        {"name": "Juggernaut", "emoji": "⚔️", "tip": "Blade Fury для ранних килов, Omnislash - твой главный damage."},
        {"name": "Lifestealer", "emoji": "🧟", "tip": "Feast позволяет фармить без регена, Rage спасает от магии."},
        {"name": "Ursa", "emoji": "🐻", "tip": "Рошан на 10-15 минуте, Fury Swipes стакаются быстро."},
        {"name": "Chaos Knight", "emoji": "🐴", "tip": "Phantasm создаёт армию, с Armlet иллюзии не теряют HP."},
    ],
    ("Carry", "Melee", "Средняя"): [
        {"name": "Phantom Assassin", "emoji": "🗡️", "tip": "BKB обязателен, криты решают драки. Dagger для фарма."},
        {"name": "Faceless Void", "emoji": "⏰", "tip": "Chrono только когда команда рядом, Time Walk отменяет урон."},
        {"name": "Slark", "emoji": "🐟", "tip": "Играй агрессивно, Shadow Dance восстанавливает HP быстро."},
        {"name": "Monkey King", "emoji": "🐵", "tip": "Накопи Jingu стаки, потом прыгай в драку с ультом."},
        {"name": "Troll Warlord", "emoji": "🏹", "tip": "Melee форма для лайфстила, Ranged для харасса и кайта."},
        {"name": "Bloodseeker", "emoji": "🩸", "tip": "Rupture на мобильных героев, Thirst даёт vision на раненых."},
        {"name": "Riki", "emoji": "🥷", "tip": "Diffusal Blade core, Tricks of the Trade уклоняется от спеллов."},
        {"name": "Sven", "emoji": "⚔️", "tip": "God's Strength + Cleave = рампага, Storm Hammer для инициации."},
    ],
    ("Carry", "Melee", "Сложная"): [
        {"name": "Anti-Mage", "emoji": "🔮", "tip": "Фарми 25 минут, Blink каждые 4 сек, сжигай ману танкам."},
        {"name": "Ember Spirit", "emoji": "🔥", "tip": "Оставляй Remnant на фонтане, Sleight + Chains комбо."},
        {"name": "Void Spirit", "emoji": "💜", "tip": "Dissimilate для уклонения, играй как assassin."},
        {"name": "Phantom Lancer", "emoji": "🔱", "tip": "Doppelganger для escape, иллюзии сжигают ману с Diffusal."},
        {"name": "Spectre", "emoji": "👻", "tip": "Фарми до Radiance, Haunt в каждую драку даже издалека."},
        {"name": "Terrorblade", "emoji": "😈", "tip": "Sunder на низком HP, Metamorphosis для командных драк."},
        {"name": "Naga Siren", "emoji": "🧜‍♀️", "tip": "Иллюзии фармят всю карту, Song спасает или сетапит."},
        {"name": "Meepo", "emoji": "🐭", "tip": "Poof для быстрого фарма и burst урона, все Meepo должны жить."},
    ],
    ("Carry", "Ranged", "Легкая"): [
        {"name": "Drow Ranger", "emoji": "🏹", "tip": "Держи дистанцию! Marksmanship отключается вблизи."},
        {"name": "Viper", "emoji": "🐍", "tip": "Доминируй на линии, Nethertoxin ломает пассивки."},
        {"name": "Sniper", "emoji": "🔫", "tip": "Positioning is key! Headshot + Take Aim = безопасный DPS."},
        {"name": "Huskar", "emoji": "🔥", "tip": "Чем меньше HP, тем больше урона. Armlet toggle мастхэв."},
    ],
    ("Carry", "Ranged", "Средняя"): [
        {"name": "Luna", "emoji": "🌙", "tip": "Moon Glaives для быстрого фарма, Eclipse в ночь сильнее."},
        {"name": "Gyrocopter", "emoji": "🚁", "tip": "Flak Cannon в драках, Rocket Barrage для ранних килов."},
        {"name": "Medusa", "emoji": "🐍", "tip": "Фармь до поздней игры, Stone Gaze против инициаторов."},
        {"name": "Weaver", "emoji": "🪲", "tip": "Shukuchi для harass и escape, Time Lapse спасает жизни."},
        {"name": "Muerta", "emoji": "💀", "tip": "Pierce the Veil = неуязвимость к физ. урону."},
        {"name": "Clinkz", "emoji": "🏹", "tip": "Skeleton Walk для ганков, Burning Barrage огромный burst."},
        {"name": "Templar Assassin", "emoji": "🗡️", "tip": "Refraction блокирует урон, Meld + Desolator combo."},
    ],
    ("Carry", "Ranged", "Сложная"): [
        {"name": "Morphling", "emoji": "💧", "tip": "Attribute Shift в STR когда фокусят, AGI для урона."},
        {"name": "Arc Warden", "emoji": "⚡", "tip": "Tempest Double удваивает предметы, сплитпуш машина."},
        {"name": "Lone Druid", "emoji": "🐻", "tip": "Bear - твой main damage, держи его живым!"},
        {"name": "Invoker", "emoji": "🌟", "tip": "Exort build для урона: Forge Spirits + Cold Snap + Sun Strike."},
    ],

    # ============================================
    # SUPPORT ГЕРОИ
    # ============================================
    ("Support", "Melee", "Легкая"): [
        {"name": "Ogre Magi", "emoji": "👹", "tip": "Bloodlust на керри, Fireblast спам, ты очень танковый."},
        {"name": "Treant Protector", "emoji": "🌳", "tip": "Living Armor глобально хилит башни и союзников."},
        {"name": "Undying", "emoji": "💀", "tip": "Decay в драках крадёт силу, Tombstone ставь в центр боя."},
        {"name": "Abaddon", "emoji": "🏇", "tip": "Aphotic Shield снимает станы с союзников, спасай керри."},
        {"name": "Omniknight", "emoji": "⚔️", "tip": "Heavenly Grace даёт иммунитет к дебаффам."},
        {"name": "Wraith King", "emoji": "👑", "tip": "Vampiric Aura помогает команде, стан надёжный."},
    ],
    ("Support", "Melee", "Средняя"): [
        {"name": "Earth Spirit", "emoji": "🪨", "tip": "Boulder Smash + Rolling Boulder = длинный стан."},
        {"name": "Tusk", "emoji": "🦣", "tip": "Snowball спасает союзников от ультов, Sigil замедляет."},
        {"name": "Clockwerk", "emoji": "⚙️", "tip": "Hookshot издалека, Cogs изолируют цель от команды."},
        {"name": "Spirit Breaker", "emoji": "🐂", "tip": "Charge на вражеского саппорта, глобальное присутствие."},
        {"name": "Marci", "emoji": "👧", "tip": "Dispose спасает союзников, Rebound для инициации."},
        {"name": "Tiny", "emoji": "🪨", "tip": "Toss союзника к врагу или врага к команде."},
        {"name": "Night Stalker", "emoji": "🦇", "tip": "Void через BKB, ночью даёшь vision команде."},
        {"name": "Slardar", "emoji": "🐊", "tip": "Corrosive Haze снимает весь армор, Guardian Sprint для ward."},
    ],
    ("Support", "Melee", "Сложная"): [
        {"name": "Earthshaker", "emoji": "🔨", "tip": "Echo Slam жди толпу, Fissure блокирует пути отхода."},
        {"name": "Pangolier", "emoji": "🦔", "tip": "Rolling Thunder для инициации, Shield Crash stack resist."},
        {"name": "Sand King", "emoji": "🦂", "tip": "Blink + Epicenter, Burrowstrike через несколько врагов."},
        {"name": "Nyx Assassin", "emoji": "🪲", "tip": "Carapace отражает урон, Vendetta для scout и pick-off."},
        {"name": "Bounty Hunter", "emoji": "🥷", "tip": "Track даёт золото всей команде, следи за курьерами."},
    ],
    ("Support", "Ranged", "Легкая"): [
        {"name": "Crystal Maiden", "emoji": "❄️", "tip": "Arcane Aura с уровня 1, Frostbite на 3 сек рутает."},
        {"name": "Lich", "emoji": "🥶", "tip": "Frost Shield на керри, Chain Frost в кучу врагов."},
        {"name": "Warlock", "emoji": "📖", "tip": "Fatal Bonds перед ультом, Golem станит при призыве."},
        {"name": "Vengeful Spirit", "emoji": "👼", "tip": "Swap спасает керри, Wave of Terror для vision."},
        {"name": "Witch Doctor", "emoji": "🎭", "tip": "Maledict до нюков команды, Cask отскакивает долго."},
        {"name": "Jakiro", "emoji": "🐉", "tip": "Liquid Fire на башни, Ice Path + Macropyre combo."},
        {"name": "Silencer", "emoji": "🤫", "tip": "Global Silence прерывает инициацию врага."},
        {"name": "Venomancer", "emoji": "🐛", "tip": "Wards для vision и пуша, Gale замедляет сильно."},
    ],
    ("Support", "Ranged", "Средняя"): [
        {"name": "Shadow Shaman", "emoji": "🐸", "tip": "Hex + Shackles = 7 сек контроля, Wards сносят башни."},
        {"name": "Disruptor", "emoji": "🌩️", "tip": "Glimpse возвращает TP-шников, Static Storm AoE silence."},
        {"name": "Lion", "emoji": "🦁", "tip": "Hex + Earth Spike = мгновенный kill potential."},
        {"name": "Dazzle", "emoji": "💜", "tip": "Shallow Grave в последний момент, Weave в драку."},
        {"name": "Io", "emoji": "💫", "tip": "Tether к керри и хиль его, Relocate для ганков."},
        {"name": "Shadow Demon", "emoji": "👿", "tip": "Disruption спасает и сетапит, иллюзии для damage."},
        {"name": "Bane", "emoji": "😱", "tip": "Nightmare на инициатора, Fiend's Grip на главную цель."},
        {"name": "Skywrath Mage", "emoji": "🦅", "tip": "Ancient Seal + Mystic Flare combo убивает мгновенно."},
        {"name": "Pugna", "emoji": "💀", "tip": "Nether Ward наказывает кастеров, Decrepify для save."},
        {"name": "Grimstroke", "emoji": "🖌️", "tip": "Soulbind связывает двух врагов, ульты бьют обоих."},
        {"name": "Hoodwink", "emoji": "🐿️", "tip": "Bushwhack станит у деревьев, Scurry даёт evasion."},
    ],
    ("Support", "Ranged", "Сложная"): [
        {"name": "Rubick", "emoji": "🧙", "tip": "Кради ульты: Ravage, Black Hole, RP. Позиционируйся сзади."},
        {"name": "Winter Wyvern", "emoji": "🐉", "tip": "Cold Embrace хилит но замораживает, Curse на толпу."},
        {"name": "Mirana", "emoji": "🐱", "tip": "Arrow через деревья, Moonlight Shadow для smoke ganks."},
        {"name": "Oracle", "emoji": "🔮", "tip": "False Promise + Purifying Flames = огромный хил."},
        {"name": "Chen", "emoji": "⛪", "tip": "Большие крипы со станом, Hand of God глобальный хил."},
        {"name": "Enchantress", "emoji": "🦌", "tip": "Enchant вражеских крипов, Impetus больше урона от дистанции."},
        {"name": "Keeper of the Light", "emoji": "🧙‍♂️", "tip": "Chakra Magic на керри, Illuminate через fog."},
        {"name": "Visage", "emoji": "👻", "tip": "Familiars для стана и урона, micro обязателен."},
        {"name": "Dark Willow", "emoji": "🧚", "tip": "Terrorize отталкивает, Bedlam огромный урон вблизи."},
        {"name": "Phoenix", "emoji": "🔥", "tip": "Supernova перерождает, но яйцо уязвимо."},
    ],

    # ============================================
    # OFFLANE ГЕРОИ
    # ============================================
    ("Offlane", "Melee", "Легкая"): [
        {"name": "Bristleback", "emoji": "🦔", "tip": "Стой спиной к врагам, Quill Spray стакается бесконечно."},
        {"name": "Axe", "emoji": "🪓", "tip": "Прыгай в толпу, Call + Blade Mail отражает урон."},
        {"name": "Tidehunter", "emoji": "🐙", "tip": "Kraken Shell снимает дебаффы, жди идеальный Ravage."},
        {"name": "Centaur Warrunner", "emoji": "🐴", "tip": "Stampede спасает команду глобально, Double Edge burst."},
        {"name": "Slardar", "emoji": "🐊", "tip": "Blink + Crush инициация, Haze на керри врага."},
        {"name": "Underlord", "emoji": "👹", "tip": "Atrophy Aura снижает урон врагов, Firestorm на волну."},
        {"name": "Wraith King", "emoji": "👑", "tip": "Стан, танк и две жизни. Radiance build для teamfight."},
    ],
    ("Offlane", "Melee", "Средняя"): [
        {"name": "Mars", "emoji": "🛡️", "tip": "Spear к стенам/деревьям станит, Arena контролит зону."},
        {"name": "Legion Commander", "emoji": "⚔️", "tip": "Blink Duel на сквизи цели, Overwhelming Odds farm."},
        {"name": "Night Stalker", "emoji": "🦇", "tip": "Void + Crippling Fear ночью = easy kill."},
        {"name": "Primal Beast", "emoji": "🦏", "tip": "Onslaught через всю драку, Pulverize держит цель."},
        {"name": "Doom", "emoji": "😈", "tip": "Doom выключает ключевого героя полностью."},
        {"name": "Spirit Breaker", "emoji": "🐂", "tip": "Charge создаёт давление глобально, Bash через BKB."},
        {"name": "Clockwerk", "emoji": "⚙️", "tip": "Hookshot инициация, Power Cogs изолируют."},
        {"name": "Tiny", "emoji": "🪨", "tip": "Avalanche + Toss combo, Tree Grab для cleave."},
        {"name": "Earthshaker", "emoji": "🔨", "tip": "Echo Slam devastates illusion heroes, Fissure block."},
    ],
    ("Offlane", "Melee", "Сложная"): [
        {"name": "Enigma", "emoji": "🌀", "tip": "Фармь лес Eidolons, Black Hole жди BKB'шников."},
        {"name": "Brewmaster", "emoji": "🍺", "tip": "Primal Split даёт 3 юнитов: Dispel, Cyclone, Stun."},
        {"name": "Beastmaster", "emoji": "🦁", "tip": "Hawk для vision, Roar пробивает BKB."},
        {"name": "Magnus", "emoji": "🦬", "tip": "RP + Skewer к команде, Empower буст для керри."},
        {"name": "Kunkka", "emoji": "⚓", "tip": "X себя, Ghost Ship в бой, X назад. Cleave огромный."},
        {"name": "Sand King", "emoji": "🦂", "tip": "Blink + Shift Epicenter, Caustic Finale для фарма."},
        {"name": "Elder Titan", "emoji": "🌍", "tip": "Natural Order снимает всю резисты, Spirit для сетапа."},
        {"name": "Faceless Void", "emoji": "⏰", "tip": "Chrono на 2-3 героев, Time Walk aggressive."},
    ],
    ("Offlane", "Ranged", "Легкая"): [
        {"name": "Venomancer", "emoji": "🐛", "tip": "Plague Wards push и vision, Poison Nova в драку."},
        {"name": "Necrophos", "emoji": "💚", "tip": "Heartstopper Aura изводит врагов, Scythe добивает."},
        {"name": "Razor", "emoji": "⚡", "tip": "Static Link кради урон керри, Eye бьёт tower."},
        {"name": "Viper", "emoji": "🐍", "tip": "Выигрывай линию, Nethertoxin break на Bristle/Spectre."},
        {"name": "Dragon Knight", "emoji": "🐲", "tip": "Tanky с Dragon Blood, Elder Form push towers."},
    ],
    ("Offlane", "Ranged", "Средняя"): [
        {"name": "Batrider", "emoji": "🦇", "tip": "Lasso тащи к команде, Sticky Napalm стакай."},
        {"name": "Dark Seer", "emoji": "🧠", "tip": "Ion Shell на крипа для harass, Vacuum + Wall combo."},
        {"name": "Death Prophet", "emoji": "👻", "tip": "Exorcism сносит башни и героев, Spirit Siphon heal."},
        {"name": "Pugna", "emoji": "💀", "tip": "Nether Blast на башни, Ward убивает casters."},
        {"name": "Leshrac", "emoji": "🦄", "tip": "Edict сносит tower, Pulse Nova constant damage."},
        {"name": "Pangolier", "emoji": "🦔", "tip": "Rolling Thunder инициация, Swashbuckle для damage."},
        {"name": "Phoenix", "emoji": "🔥", "tip": "Sun Ray heal и damage, Supernova reset."},
    ],
    ("Offlane", "Ranged", "Сложная"): [
        {"name": "Visage", "emoji": "👻", "tip": "Familiars drop stun, micro обязателен."},
        {"name": "Nature's Prophet", "emoji": "🌿", "tip": "Teleport split push, Sprout ловит врагов."},
        {"name": "Timbersaw", "emoji": "🪚", "tip": "Reactive Armor стакается, Timber Chain mobility."},
        {"name": "Invoker", "emoji": "🌟", "tip": "Quas Wex для контроля: Tornado, EMP, Cold Snap."},
        {"name": "Lone Druid", "emoji": "🐻", "tip": "Bear танкует tower, Savage Roar отталкивает."},
        {"name": "Broodmother", "emoji": "🕷️", "tip": "Spiderlings под tower, контролируй jungle."},
    ],

    # ============================================
    # MIDLANE ГЕРОИ
    # ============================================
    ("Midlane", "Melee", "Легкая"): [
        {"name": "Dragon Knight", "emoji": "🐲", "tip": "Passive regen на линии, Elder Form push mid."},
        {"name": "Huskar", "emoji": "🔥", "tip": "Burning Spear harass, чем ниже HP тем сильнее."},
        {"name": "Viper", "emoji": "🐍", "tip": "Poison Attack спам, выиграй любую линию."},
        {"name": "Bloodseeker", "emoji": "🩸", "tip": "Blood Rite зонит, Rupture на rotator."},
    ],
    ("Midlane", "Melee", "Средняя"): [
        {"name": "Templar Assassin", "emoji": "🗡️", "tip": "Refraction танкует harass, Meld burst."},
        {"name": "Storm Spirit", "emoji": "⛈️", "tip": "Ball Lightning за ману, не переусердствуй."},
        {"name": "Void Spirit", "emoji": "💜", "tip": "Dissimilate invuln, Remnant для damage."},
        {"name": "Alchemist", "emoji": "🧪", "tip": "Greevil's Greed = fast farm, give Aghs allies."},
        {"name": "Ember Spirit", "emoji": "🔥", "tip": "Remnant на fountain, aggressive trades."},
        {"name": "Spirit Breaker", "emoji": "🐂", "tip": "Charge на side lanes для ганков, rune control."},
        {"name": "Kunkka", "emoji": "⚓", "tip": "Tidebringer harass, X + Torrent + Boat combo."},
        {"name": "Night Stalker", "emoji": "🦇", "tip": "First night = kill potential, Hunter in Night."},
    ],
    ("Midlane", "Melee", "Сложная"): [
        {"name": "Invoker", "emoji": "🌟", "tip": "Exort: Forge + Cold Snap harass. 10 spells master."},
        {"name": "Meepo", "emoji": "🐭", "tip": "Poof burst, power spike на 3 Meepo. All must live."},
        {"name": "Pangolier", "emoji": "🦔", "tip": "Lucky Shot procs, Rolling Thunder difficult control."},
        {"name": "Broodmother", "emoji": "🕷️", "tip": "Spiderlings давят lane, ешь вражеский jungle."},
        {"name": "Monkey King", "emoji": "🐵", "tip": "Tree Dance для ганков, Jingu масtery stacks."},
        {"name": "Magnus", "emoji": "🦬", "tip": "Shockwave farm, setup kills для side lanes."},
    ],
    ("Midlane", "Ranged", "Легкая"): [
        {"name": "Zeus", "emoji": "⚡", "tip": "Arc Lightning last hit, Nimbus global presence."},
        {"name": "Sniper", "emoji": "🔫", "tip": "Shrapnel зонит, Assassinate добивает."},
        {"name": "Viper", "emoji": "🐍", "tip": "Poison Attack не тянет aggro, dominate lane."},
        {"name": "Skywrath Mage", "emoji": "🦅", "tip": "Arcane Bolt spam, Seal + Flare kill combo."},
        {"name": "Death Prophet", "emoji": "👻", "tip": "Crypt Swarm wave clear, Exorcism take tower."},
    ],
    ("Midlane", "Ranged", "Средняя"): [
        {"name": "Queen of Pain", "emoji": "👸", "tip": "Blink aggressive, Shadow Strike DoT, Sonic Wave pure."},
        {"name": "Lina", "emoji": "🔥", "tip": "Light Strike Array setup, Laguna Blade execute."},
        {"name": "Shadow Fiend", "emoji": "😈", "tip": "Raze для farm и harass, Requiem + Eul combo."},
        {"name": "Puck", "emoji": "🧚", "tip": "Orb escape и initiation, Coil держит врагов."},
        {"name": "Windranger", "emoji": "💨", "tip": "Shackle к creep = easy stun, Focus Fire melt."},
        {"name": "Outworld Destroyer", "emoji": "🔵", "tip": "Astral setup или save, Sanity Eclipse int diff."},
        {"name": "Leshrac", "emoji": "🦄", "tip": "Split Earth stun, Edict melts tower early."},
        {"name": "Necrophos", "emoji": "💚", "tip": "Death Pulse sustain, Reaper's Scythe threshold."},
        {"name": "Pugna", "emoji": "💀", "tip": "Nether Blast push, Ward punish spell spam."},
        {"name": "Razor", "emoji": "⚡", "tip": "Static Link steal damage от melee mids."},
    ],
    ("Midlane", "Ranged", "Сложная"): [
        {"name": "Tinker", "emoji": "🤖", "tip": "Rearm = infinite spells, Blink + Laser + Rocket."},
        {"name": "Arc Warden", "emoji": "⚡", "tip": "Tempest Double = два героя, Spark Wraith zone."},
        {"name": "Invoker", "emoji": "🌟", "tip": "Wex для tornado EMP, Exort для damage."},
        {"name": "Meepo", "emoji": "🐭", "tip": "Fastest level 25 in game if played well."},
        {"name": "Morphling", "emoji": "💧", "tip": "Adaptive Strike stun, Attribute Shift survive."},
        {"name": "Visage", "emoji": "👻", "tip": "Familiars harass and stun, Soul Assumption burst."},
    ],
}


# ============================================
# ОПРЕДЕЛЕНИЕ СОСТОЯНИЙ КОНЕЧНОГО АВТОМАТА
# ============================================

class HeroSelection(StatesGroup):
    """
    Группа состояний для подбора героя.
    Реализует конечный автомат из 3 состояний.
    """
    # Состояние 1: Выбор роли
    waiting_for_role = State()
    
    # Состояние 2: Выбор типа атаки
    waiting_for_attack_type = State()
    
    # Состояние 3: Выбор сложности
    waiting_for_difficulty = State()


# ============================================
# КЛАВИАТУРЫ
# ============================================

def get_role_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора роли"""
    buttons = [
        [KeyboardButton(text="⚔️ Carry"), KeyboardButton(text="🛡️ Support")],
        [KeyboardButton(text="💪 Offlane"), KeyboardButton(text="🎯 Midlane")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_attack_type_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора типа атаки"""
    buttons = [
        [KeyboardButton(text="🗡️ Melee (Ближний бой)")],
        [KeyboardButton(text="🏹 Ranged (Дальний бой)")],
        [KeyboardButton(text="⬅️ Назад"), KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_difficulty_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора сложности"""
    buttons = [
        [KeyboardButton(text="🟢 Легкая")],
        [KeyboardButton(text="🟡 Средняя")],
        [KeyboardButton(text="🔴 Сложная")],
        [KeyboardButton(text="⬅️ Назад"), KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_restart_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура после получения результата"""
    buttons = [
        [KeyboardButton(text="🔄 Подобрать другого героя")],
        [KeyboardButton(text="🎲 Случайный герой")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# ============================================
# МАППИНГ ЗНАЧЕНИЙ
# ============================================

ROLES_MAP = {
    "⚔️ Carry": "Carry",
    "🛡️ Support": "Support",
    "💪 Offlane": "Offlane",
    "🎯 Midlane": "Midlane"
}

ATTACK_TYPE_MAP = {
    "🗡️ Melee (Ближний бой)": "Melee",
    "🏹 Ranged (Дальний бой)": "Ranged"
}

DIFFICULTY_MAP = {
    "🟢 Легкая": "Легкая",
    "🟡 Средняя": "Средняя",
    "🔴 Сложная": "Сложная"
}

ROLE_DESCRIPTIONS = {
    "Carry": "Основной источник урона команды в поздней игре",
    "Support": "Помогает команде вардами, сейвами и контролем",
    "Offlane": "Танк и инициатор командных сражений",
    "Midlane": "Герой с высоким импактом в середине игры"
}


# ============================================
# ИНИЦИАЛИЗАЦИЯ БОТА
# ============================================

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# ============================================
# ОБРАБОТЧИКИ КОМАНД
# ============================================

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()
    
    await message.answer(
        "🎮 <b>Добро пожаловать в Dota 2 Hero Picker!</b>\n\n"
        "Я помогу тебе подобрать идеального героя "
        "на основе твоих предпочтений.\n\n"
        "🦸 <b>Доступные команды:</b>\n"
        "/pick - Подобрать героя\n"
        "/random - Случайный герой\n"
        "/heroes - Список всех героев\n"
        "/tips - Советы для новичков\n"
        "/cancel - Отменить подбор\n\n"
        "⚔️ <i>Готов к бою? Жми /pick!</i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    await message.answer(
        "📖 <b>Как пользоваться ботом</b>\n\n"
        "<b>Шаг 1:</b> Выбери роль\n"
        "• Carry - основной урон\n"
        "• Support - помощь команде\n"
        "• Offlane - танк/инициатор\n"
        "• Midlane - контроль центра\n\n"
        "<b>Шаг 2:</b> Выбери тип атаки\n"
        "• Melee - ближний бой\n"
        "• Ranged - дальний бой\n\n"
        "<b>Шаг 3:</b> Выбери сложность\n"
        "• Легкая - для новичков\n"
        "• Средняя - нужен опыт\n"
        "• Сложная - для профи\n\n"
        "🎯 Получи рекомендацию героя с советами!",
        parse_mode="HTML"
    )


@dp.message(Command("tips"))
async def cmd_tips(message: types.Message):
    """Советы для новичков"""
    await message.answer(
        "💡 <b>Советы для новичков Dota 2</b>\n\n"
        "1️⃣ <b>Начни с простых героев</b>\n"
        "Wraith King, Ogre Magi, Lich - твои друзья!\n\n"
        "2️⃣ <b>Покупай варды</b>\n"
        "Vision wins games! 🔮\n\n"
        "3️⃣ <b>Фармь крипов</b>\n"
        "Золото = предметы = сила 💰\n\n"
        "4️⃣ <b>Смотри на миникарту</b>\n"
        "Каждые 3-5 секунд! 🗺️\n\n"
        "5️⃣ <b>Не умирай зря</b>\n"
        "Лучше отступить, чем фидить 🏃\n\n"
        "6️⃣ <b>Коммуницируй</b>\n"
        "Пинги и чат помогают команде! 📢\n\n"
        "🎮 <i>GLHF - Good Luck, Have Fun!</i>",
        parse_mode="HTML"
    )


@dp.message(Command("random"))
@dp.message(F.text == "🎲 Случайный герой")
async def cmd_random(message: types.Message):
    """Случайный герой"""
    all_heroes = []
    for heroes in HEROES_DATABASE.values():
        all_heroes.extend(heroes)
    
    hero = random.choice(all_heroes)
    
    await message.answer(
        f"🎲 <b>Случайный герой:</b>\n\n"
        f"{hero['emoji']} <b>{hero['name']}</b>\n\n"
        f"💡 <i>{hero['tip']}</i>\n\n"
        f"⚔️ Удачи в игре!",
        parse_mode="HTML",
        reply_markup=get_restart_keyboard()
    )


@dp.message(Command("pick"))
@dp.message(F.text == "🔄 Подобрать другого героя")
async def cmd_pick(message: types.Message, state: FSMContext):
    """
    Начало подбора героя - переход в СОСТОЯНИЕ 1
    """
    await state.set_state(HeroSelection.waiting_for_role)
    
    await message.answer(
        "🎮 <b>Шаг 1 из 3: Выбор роли</b>\n\n"
        "На какой позиции ты хочешь играть?\n\n"
        "⚔️ <b>Carry</b> - фарми и побеждай в лейте\n"
        "🛡️ <b>Support</b> - помогай команде\n"
        "💪 <b>Offlane</b> - танкуй и инициируй\n"
        "🎯 <b>Midlane</b> - доминируй в центре",
        parse_mode="HTML",
        reply_markup=get_role_keyboard()
    )
    
    logger.info(f"Пользователь {message.from_user.id} начал подбор героя")


@dp.message(Command("cancel"))
@dp.message(F.text == "❌ Отмена")
async def cmd_cancel(message: types.Message, state: FSMContext):
    """Отмена подбора из любого состояния"""
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer(
            "❌ Нет активного подбора.\n"
            "Используй /pick для начала!",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    await state.clear()
    await message.answer(
        "❌ Подбор отменён.\n\n"
        "Для нового подбора используй /pick\n"
        "Или попробуй /random для случайного героя! 🎲",
        reply_markup=ReplyKeyboardRemove()
    )
    
    logger.info(f"Пользователь {message.from_user.id} отменил подбор")


# ============================================
# СОСТОЯНИЕ 1: ВЫБОР РОЛИ
# ============================================

@dp.message(StateFilter(HeroSelection.waiting_for_role))
async def process_role(message: types.Message, state: FSMContext):
    """
    Обработка выбора роли.
    Переход из СОСТОЯНИЯ 1 в СОСТОЯНИЕ 2.
    """
    role_text = message.text
    
    if role_text not in ROLES_MAP:
        await message.answer(
            "⚠️ Пожалуйста, выбери роль из предложенных кнопок:",
            reply_markup=get_role_keyboard()
        )
        return
    
    role = ROLES_MAP[role_text]
    
    # Сохраняем выбранную роль
    await state.update_data(role=role, role_text=role_text)
    
    # Переход в СОСТОЯНИЕ 2
    await state.set_state(HeroSelection.waiting_for_attack_type)
    
    await message.answer(
        f"✅ Роль: <b>{role}</b>\n"
        f"<i>{ROLE_DESCRIPTIONS[role]}</i>\n\n"
        f"🎮 <b>Шаг 2 из 3: Тип атаки</b>\n\n"
        f"Какой стиль боя тебе ближе?\n\n"
        f"🗡️ <b>Melee</b> - в гуще сражения\n"
        f"🏹 <b>Ranged</b> - атака с дистанции",
        parse_mode="HTML",
        reply_markup=get_attack_type_keyboard()
    )
    
    logger.info(f"Пользователь {message.from_user.id} выбрал роль: {role}")


# ============================================
# СОСТОЯНИЕ 2: ВЫБОР ТИПА АТАКИ
# ============================================

@dp.message(StateFilter(HeroSelection.waiting_for_attack_type), F.text == "⬅️ Назад")
async def back_to_role(message: types.Message, state: FSMContext):
    """Возврат к выбору роли"""
    await state.set_state(HeroSelection.waiting_for_role)
    
    await message.answer(
        "🎮 <b>Шаг 1 из 3: Выбор роли</b>\n\n"
        "На какой позиции ты хочешь играть?",
        parse_mode="HTML",
        reply_markup=get_role_keyboard()
    )


@dp.message(StateFilter(HeroSelection.waiting_for_attack_type))
async def process_attack_type(message: types.Message, state: FSMContext):
    """
    Обработка выбора типа атаки.
    Переход из СОСТОЯНИЯ 2 в СОСТОЯНИЕ 3.
    """
    attack_text = message.text
    
    if attack_text not in ATTACK_TYPE_MAP:
        await message.answer(
            "⚠️ Пожалуйста, выбери тип атаки из предложенных:",
            reply_markup=get_attack_type_keyboard()
        )
        return
    
    attack_type = ATTACK_TYPE_MAP[attack_text]
    
    # Сохраняем тип атаки
    await state.update_data(attack_type=attack_type, attack_text=attack_text)
    
    # Переход в СОСТОЯНИЕ 3
    await state.set_state(HeroSelection.waiting_for_difficulty)
    
    data = await state.get_data()
    
    await message.answer(
        f"✅ Роль: <b>{data['role']}</b>\n"
        f"✅ Тип атаки: <b>{attack_type}</b>\n\n"
        f"🎮 <b>Шаг 3 из 3: Сложность героя</b>\n\n"
        f"Какой уровень сложности тебе подходит?\n\n"
        f"🟢 <b>Легкая</b> - простые механики\n"
        f"🟡 <b>Средняя</b> - требует практики\n"
        f"🔴 <b>Сложная</b> - для опытных игроков",
        parse_mode="HTML",
        reply_markup=get_difficulty_keyboard()
    )
    
    logger.info(f"Пользователь {message.from_user.id} выбрал тип: {attack_type}")


# ============================================
# СОСТОЯНИЕ 3: ВЫБОР СЛОЖНОСТИ
# ============================================

@dp.message(StateFilter(HeroSelection.waiting_for_difficulty), F.text == "⬅️ Назад")
async def back_to_attack_type(message: types.Message, state: FSMContext):
    """Возврат к выбору типа атаки"""
    await state.set_state(HeroSelection.waiting_for_attack_type)
    
    await message.answer(
        "🎮 <b>Шаг 2 из 3: Тип атаки</b>\n\n"
        "Какой стиль боя тебе ближе?",
        parse_mode="HTML",
        reply_markup=get_attack_type_keyboard()
    )


@dp.message(StateFilter(HeroSelection.waiting_for_difficulty))
async def process_difficulty(message: types.Message, state: FSMContext):
    """
    Обработка выбора сложности.
    Завершение работы конечного автомата - выдача результата.
    """
    difficulty_text = message.text
    
    if difficulty_text not in DIFFICULTY_MAP:
        await message.answer(
            "⚠️ Пожалуйста, выбери сложность из предложенных:",
            reply_markup=get_difficulty_keyboard()
        )
        return
    
    difficulty = DIFFICULTY_MAP[difficulty_text]
    
    # Получаем все данные
    data = await state.get_data()
    role = data['role']
    attack_type = data['attack_type']
    
    # Формируем ключ для поиска героев
    key = (role, attack_type, difficulty)
    
    # Получаем список героев
    heroes = HEROES_DATABASE.get(key, [])
    
    # Очищаем состояние
    await state.clear()
    
    if heroes:
        # Выбираем случайного героя из подходящих
        hero = random.choice(heroes)
        
        # Формируем список всех подходящих героев
        heroes_list = "\n".join([f"  • {h['emoji']} {h['name']}" for h in heroes])
        
        await message.answer(
            f"🎯 <b>РЕЗУЛЬТАТ ПОДБОРА</b>\n\n"
            f"<b>Твои параметры:</b>\n"
            f"📍 Роль: {role}\n"
            f"⚔️ Тип: {attack_type}\n"
            f"📊 Сложность: {difficulty}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🏆 <b>Рекомендуемый герой:</b>\n\n"
            f"{hero['emoji']} <b>{hero['name']}</b>\n\n"
            f"💡 <b>Совет:</b> <i>{hero['tip']}</i>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 <b>Другие подходящие герои:</b>\n"
            f"{heroes_list}\n\n"
            f"⚔️ <i>GLHF! Удачной игры!</i>",
            parse_mode="HTML",
            reply_markup=get_restart_keyboard()
        )
    else:
        await message.answer(
            f"😔 К сожалению, не найдено героев с такими параметрами.\n\n"
            f"Попробуй другую комбинацию!",
            reply_markup=get_restart_keyboard()
        )
    
    logger.info(
        f"Пользователь {message.from_user.id} получил рекомендацию: "
        f"{role}/{attack_type}/{difficulty}"
    )


# ============================================
# КОМАНДА HEROES - СПИСОК ВСЕХ ГЕРОЕВ
# ============================================

@dp.message(Command("heroes"))
async def cmd_heroes(message: types.Message):
    """Показать список героев по ролям"""
    roles_heroes = {}
    
    for key, heroes in HEROES_DATABASE.items():
        role = key[0]
        if role not in roles_heroes:
            roles_heroes[role] = set()
        for hero in heroes:
            roles_heroes[role].add(f"{hero['emoji']} {hero['name']}")
    
    text = "📜 <b>ГЕРОИ DOTA 2 ПО РОЛЯМ</b>\n\n"
    
    for role in ["Carry", "Support", "Offlane", "Midlane"]:
        if role in roles_heroes:
            heroes_str = ", ".join(sorted(roles_heroes[role]))
            text += f"<b>{role}:</b>\n{heroes_str}\n\n"
    
    await message.answer(text, parse_mode="HTML")


# ============================================
# ОБРАБОТКА СООБЩЕНИЙ ВНЕ СОСТОЯНИЙ
# ============================================

@dp.message()
async def echo_handler(message: types.Message):
    """Обработчик сообщений вне состояний"""
    await message.answer(
        "🤔 Не понимаю команду.\n\n"
        "Используй:\n"
        "/pick - подобрать героя\n"
        "/random - случайный герой\n"
        "/help - помощь"
    )


# ============================================
# ЗАПУСК БОТА
# ============================================

async def main():
    """Основная функция запуска бота"""
    logger.info("🎮 Запуск Dota 2 Hero Picker Bot...")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())