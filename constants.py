global ROUND_NUMBER
ROUND_NUMBER = 1

# For N levels of tournament brackets fights, use 2 ** N for FIGHTER_COUNT
FIGHTER_COUNT = 2 ** 5
MAX_FIGHT_MOMENTS = 300
DAMAGE_MULTIPLIER = 3
HEALTH_MULTIPLIER = 3
DEFAULT_COOLDOWN = 20
DODGE_THRESHOLD = 0.9
HEALTH_INCREASE_BONUS = 1.5

# Probability of combatant being ELITE rank
ELITE_THRESHOLD = 0.25

# Probability of combatant being MASTER rank
# Must be greater than ELITE_THRESHOLD
MASTER_THRESHOLD = 0.10

# Probability of combatant being LEGENDARY rank
# Must be greater than MASTER_THRESHOLD
LEGENDARY_THRESHOLD = 0.01