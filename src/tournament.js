import { Combatant } from './combatant.js';
import { simulateFight } from './fight.js';

export function generateCombatants(count) {
  return Array.from({ length: count }, () => new Combatant());
}

/**
 * Lazily simulate a single-elimination bracket, one fight per step.
 *
 * `combatants` must have a power-of-two length. Yields
 * { record, fighters: [Combatant, Combatant], winner: Combatant } per fight,
 * in the order the fights happen. Each fight is only simulated when its step
 * is pulled, so callers may mutate combatants (e.g. award stat boosts)
 * between steps and have the changes apply to later fights.
 */
export function* tournamentSteps(combatants) {
  let roundNumber = 1;

  function* bracket(list) {
    let finalists;
    if (list.length === 2) {
      finalists = list;
    } else {
      const split = Math.floor(list.length / 2);
      finalists = [yield* bracket(list.slice(0, split)), yield* bracket(list.slice(split))];
    }
    const record = simulateFight(finalists[0], finalists[1], roundNumber);
    roundNumber += 1;
    const winner = finalists[record.winnerIndex];
    yield { record, fighters: finalists, winner };
    return winner;
  }

  yield* bracket(combatants);
}

// Simulate a full bracket in one go; returns { fights, champion }.
export function runTournament(combatants) {
  const fights = [];
  let champion = null;
  for (const step of tournamentSteps(combatants)) {
    fights.push(step.record);
    champion = step.winner;
  }
  return { fights, champion };
}

function csvEscape(value) {
  const str = String(value);
  return /[",\n]/.test(str) ? `"${str.replaceAll('"', '""')}"` : str;
}

function toCsv(header, rows) {
  return [header, ...rows].map((row) => row.map(csvEscape).join(',')).join('\n') + '\n';
}

// CSV export matching the original tournament_log.csv format.
export function tournamentLogCsv(fights) {
  const header = [
    'round_number', 'combatant_number', 'fight_name', 'combatant', 'gender', 'combat_class', 'rank',
    'max_health', 'health', 'strength', 'defense', 'agility', 'stamina', 'wisdom', 'fight_result',
    'remaining_health',
  ];
  const rows = [];
  for (const fight of fights) {
    const finalHealth = fight.events[fight.events.length - 1].health;
    fight.combatants.forEach((c, i) => {
      rows.push([
        fight.roundNumber, i + 1, fight.fightName, c.name, c.gender, c.combatClass, c.rank,
        c.maxHealth, c.health, c.strength, c.defense, c.agility, c.stamina, c.wisdom,
        i === fight.winnerIndex ? 'Won' : 'Lost', finalHealth[i],
      ]);
    });
  }
  return toCsv(header, rows);
}

// CSV export matching the original fight_log.csv format.
export function fightLogCsv(fights) {
  const header = [
    'round_number', 'fight_name', 'time_elapsed', 'event', 'combatant_one', 'combatant_one_health',
    'combatant_one_dodged', 'combatant_one_attacked', 'combatant_two', 'combatant_two_health',
    'combatant_two_dodged', 'combatant_two_attacked',
  ];
  const rows = [];
  for (const fight of fights) {
    for (const event of fight.events) {
      const attacked = [event.attacker === 0, event.attacker === 1];
      const isDodge = event.type === 'dodge';
      const isAttack = event.type === 'attack' || isDodge;
      rows.push([
        fight.roundNumber, fight.fightName, event.timeRemaining, event.text,
        fight.combatants[0].name, event.health[0],
        isDodge && attacked[1], isAttack && attacked[0],
        fight.combatants[1].name, event.health[1],
        isDodge && attacked[0], isAttack && attacked[1],
      ]);
    }
  }
  return toCsv(header, rows);
}
