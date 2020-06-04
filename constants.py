global ROUND_NUMBER
ROUND_NUMBER = 1

# For N levels of tournament brackets fights, use 2 ** N for FIGHTER_COUNT
FIGHTER_COUNT = 2 ** 5

# How long the matches will last before time runs out. When the timer runs out,
# the figher with the least health remaining with lose the fight
MAX_FIGHT_MOMENTS = 300

# Factor for scaling the default damage dealt of combatants
DAMAGE_MULTIPLIER = 3

# Factor for scaling the default health of combatants
HEALTH_MULTIPLIER = 3

# The default cool down steps for all combatants to perform an attack action
# The actual cooldown for combatants will be this value minus their STAMINA value
DEFAULT_COOLDOWN = 20

# On a "Dodge" dice roll, probability of successfully dodging
DODGE_THRESHOLD = 0.9

# For stat bonus increases, the amount that a combatant's health will increase by
HEALTH_INCREASE_BONUS = 1.5

# Probability of combatant being ELITE rank
ELITE_THRESHOLD = 0.25

# Probability of combatant being MASTER rank
# Must be greater than ELITE_THRESHOLD
MASTER_THRESHOLD = 0.10

# Probability of combatant being LEGENDARY rank
# Must be greater than MASTER_THRESHOLD
LEGENDARY_THRESHOLD = 0.01