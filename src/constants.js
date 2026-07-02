// Tournament & combat tuning knobs.

// For N levels of tournament bracket fights, use 2 ** N for FIGHTER_COUNT
export const FIGHTER_COUNT = 2 ** 5;

// How long the matches will last before time runs out. When the timer runs out,
// the fighter with the least health remaining will lose the fight
export const MAX_FIGHT_MOMENTS = 300;

// Factor for scaling the default damage dealt of combatants
export const DAMAGE_MULTIPLIER = 3;

// Factor for scaling the default health of combatants
export const HEALTH_MULTIPLIER = 3;

// The default cooldown steps for all combatants to perform an attack action.
// The actual cooldown for a combatant is this value minus their stamina.
export const DEFAULT_COOLDOWN = 20;

// On a "Dodge" dice roll, probability of successfully dodging
export const DODGE_THRESHOLD = 0.9;

// For stat bonus increases, the factor that a combatant's health will increase by
export const HEALTH_INCREASE_BONUS = 1.5;

// Probability thresholds for combatant ranks. A single U(0,1) roll below a
// threshold awards that rank, so each must be greater than the next.
export const ELITE_THRESHOLD = 0.25;
export const MASTER_THRESHOLD = 0.1;
export const LEGENDARY_THRESHOLD = 0.01;
