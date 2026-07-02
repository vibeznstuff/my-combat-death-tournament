import {
  MAX_FIGHT_MOMENTS,
  DEFAULT_COOLDOWN,
  DODGE_THRESHOLD,
  DAMAGE_MULTIPLIER,
} from './constants.js';

function uniform(a, b) {
  return a + Math.random() * (b - a);
}

// A combatant gets `wisdom` dodge dice per moment; each roll above
// DODGE_THRESHOLD is a successful dodge.
function rollsDodge(combatant) {
  for (let i = 0; i < combatant.wisdom; i++) {
    if (Math.random() > DODGE_THRESHOLD) return true;
  }
  return false;
}

/**
 * Simulate a single fight to completion.
 *
 * Mutates both combatants' health. Returns the fight record consumed by the
 * playback renderer and log exports:
 *   { roundNumber, fightName, combatants: [snapshot, snapshot], events, winnerIndex }
 *
 * Events are { timeRemaining, text, type, attacker, health: [h1, h2] } where
 * type is 'start' | 'attack' | 'dodge' | 'defeat' | 'win' and attacker is the
 * index (0 or 1) of the acting combatant where applicable.
 */
export function simulateFight(combatantOne, combatantTwo, roundNumber) {
  const fighters = [combatantOne, combatantTwo];
  const fightName = `${combatantOne.name} vs ${combatantTwo.name}`;
  const snapshots = fighters.map((f) => f.snapshot());

  let fightTimer = MAX_FIGHT_MOMENTS;
  const events = [];
  const logEvent = (type, text, attacker = null) => {
    events.push({
      timeRemaining: fightTimer,
      text,
      type,
      attacker,
      health: [combatantOne.health, combatantTwo.health],
    });
  };

  logEvent('start', 'Fight starts!');

  const cooldowns = fighters.map((f) => DEFAULT_COOLDOWN - f.stamina);
  const damage = [
    Math.max(combatantOne.strength - combatantTwo.defense, 1),
    Math.max(combatantTwo.strength - combatantOne.defense, 1),
  ];

  // Resolves fighter `i` attacking their opponent; returns true on a KO.
  const performAttack = (i) => {
    const attacker = fighters[i];
    const defender = fighters[1 - i];
    const hits = Math.round(uniform(1, Math.max(1, attacker.agility)));
    defender.health = Math.round(Math.max(0, defender.health - damage[i] * hits * DAMAGE_MULTIPLIER));
    logEvent('attack', `${attacker.name} Attacks ${defender.name}!`, i);
    if (defender.health === 0) {
      logEvent('defeat', `${defender.name} has been Defeated!`, i);
      return true;
    }
    return false;
  };

  let winnerIndex = null;

  while (combatantOne.health > 0 && combatantTwo.health > 0 && fightTimer > 0) {
    fightTimer -= 1;

    const dodged = fighters.map(rollsDodge);
    const attacking = [false, false];

    for (const i of [0, 1]) {
      cooldowns[i] = Math.max(cooldowns[i] - 1, 0);
      if (cooldowns[i] === 0) {
        attacking[i] = true;
        cooldowns[i] = DEFAULT_COOLDOWN - fighters[i].stamina;
        if (dodged[1 - i]) {
          logEvent('dodge', `${fighters[1 - i].name} dodged ${fighters[i].name}'s Attack!`, i);
          attacking[i] = false;
        }
      }
    }

    // Higher agility strikes first; ties are settled by a coin flip.
    let order;
    if (combatantOne.agility > combatantTwo.agility) {
      order = [0, 1];
    } else if (combatantTwo.agility > combatantOne.agility) {
      order = [1, 0];
    } else {
      order = Math.random() > 0.5 ? [0, 1] : [1, 0];
    }

    for (const i of order) {
      if (attacking[i] && performAttack(i)) {
        winnerIndex = i;
        break;
      }
    }
    if (winnerIndex !== null) break;
  }

  if (winnerIndex === null) {
    // Time ran out: the fighter with more health remaining wins.
    winnerIndex = combatantOne.health > combatantTwo.health ? 0 : 1;
  }

  const winner = fighters[winnerIndex];
  logEvent('win', `${winner.name} wins the fight!`, winnerIndex);

  winner.recuperate();

  return { roundNumber, fightName, combatants: snapshots, events, winnerIndex };
}
