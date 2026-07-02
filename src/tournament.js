import { Combatant } from './combatant.js';
import { simulateFight } from './fight.js';

export function generateCombatants(count) {
  return Array.from({ length: count }, () => new Combatant());
}

/**
 * Simulate a full single-elimination bracket.
 *
 * `combatants` must have a power-of-two length. Returns
 * { fights, champion } where fights are the per-fight records from
 * simulateFight, numbered in the order the fights happen.
 */
export function runTournament(combatants) {
  const fights = [];
  let roundNumber = 1;

  const runBracket = (bracket) => {
    if (bracket.length === 2) {
      const record = simulateFight(bracket[0], bracket[1], roundNumber);
      fights.push(record);
      roundNumber += 1;
      return bracket[record.winnerIndex];
    }
    const split = Math.floor(bracket.length / 2);
    const winnerOne = runBracket(bracket.slice(0, split));
    const winnerTwo = runBracket(bracket.slice(split));
    const record = simulateFight(winnerOne, winnerTwo, roundNumber);
    fights.push(record);
    roundNumber += 1;
    return [winnerOne, winnerTwo][record.winnerIndex];
  };

  const champion = runBracket(combatants);
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
