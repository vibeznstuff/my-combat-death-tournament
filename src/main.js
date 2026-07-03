import {
  FIGHTER_COUNT,
  DEFAULT_COOLDOWN,
  DODGE_THRESHOLD,
  DAMAGE_MULTIPLIER,
  HEALTH_MULTIPLIER,
} from './constants.js';
import { Combatant, baseHealth } from './combatant.js';
import { generateCombatants, tournamentSteps, tournamentLogCsv, fightLogCsv } from './tournament.js';
import { loadMappings, loadImage } from './sprites.js';
import { TournamentRenderer } from './renderer.js';

// Character creation: total ability points and per-stat ceiling. Randomized
// classes allocate 30 points, but they also enjoy gender stat multipliers
// and a shot at Elite/Master/Legendary bonuses that the player never gets
// (Samurai even starts from 40 points) — the larger budget offsets that.
// The cap of 15 forces real specialization trade-offs (maxing three stats
// zeroes the other two) while staying below the degenerate Stamina builds
// that DEFAULT_COOLDOWN (20) allows at higher values.
const STATS = ['strength', 'defense', 'agility', 'stamina', 'wisdom'];
const STAT_BUDGET = 45;
const STAT_MAX = 15;

// Plain-language guide shown in the creator, derived from the live game
// constants so it stays accurate if they're tuned.
const HP_PER_DEFENSE = 6 * HEALTH_MULTIPLIER;
const HP_PER_STAMINA = 4 * HEALTH_MULTIPLIER;
const DODGE_PCT = Math.round((1 - DODGE_THRESHOLD) * 100);
const DODGE_PCT_AT_MAX = Math.round((1 - DODGE_THRESHOLD ** STAT_MAX) * 100);
const STAT_INFO = {
  strength: `Hit harder. Each hit deals (your Strength − foe's Defense) × ${DAMAGE_MULTIPLIER} damage, so every point is +${DAMAGE_MULTIPLIER} damage per hit against everyone.`,
  defense: `Take less damage. Each point cancels one point of the attacker's Strength (hits always deal at least ${DAMAGE_MULTIPLIER}). Also worth +${HP_PER_DEFENSE} max health per point.`,
  agility: `Land more hits. Each attack lands 1 to Agility hits, and the higher-Agility fighter strikes first. High Agility makes Strength count multiple times.`,
  stamina: `Attack more often. You attack every ${DEFAULT_COOLDOWN} − Stamina moments, so each point shortens the wait between attacks. Also worth +${HP_PER_STAMINA} max health per point.`,
  wisdom: `Dodge attacks. Each point grants an extra ${DODGE_PCT}% roll to fully evade an incoming attack (${STAT_MAX} points ≈ ${DODGE_PCT_AT_MAX}% dodge chance).`,
};

function statLabel(stat) {
  return stat.charAt(0).toUpperCase() + stat.slice(1);
}

const el = (id) => document.getElementById(id);
const canvas = el('arena');
const startButton = el('start');
const modeSelect = el('mode');
const fighterCountSelect = el('fighter-count');
const speedSelect = el('speed');
const watchLabel = el('watch-label');
const watchModeSelect = el('watch-mode');
const creator = el('creator');
const statusLine = el('status');
const downloads = el('downloads');
const overlay = el('overlay');

fighterCountSelect.value = String(FIGHTER_COUNT);

let mappingsPromise = null;
let renderer = null;
let creatorBuilt = false;
let selectedAvatar = null;
const statValues = { strength: 9, defense: 9, agility: 9, stamina: 9, wisdom: 9 };

const getMappings = () => (mappingsPromise ??= loadMappings());

function download(filename, text) {
  const url = URL.createObjectURL(new Blob([text], { type: 'text/csv' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

// ---------------------------------------------------------------------------
// Character creator

function pointsRemaining() {
  return STAT_BUDGET - STATS.reduce((sum, stat) => sum + statValues[stat], 0);
}

function refreshCreator() {
  el('points-remaining').textContent = `${pointsRemaining()} of ${STAT_BUDGET} points remaining`;
  el('max-health-preview').textContent = `Max Health: ${baseHealth(statValues)}`;
  for (const stat of STATS) {
    el(`stat-value-${stat}`).textContent = statValues[stat];
    el(`stat-inc-${stat}`).disabled = pointsRemaining() === 0 || statValues[stat] >= STAT_MAX;
    el(`stat-dec-${stat}`).disabled = statValues[stat] === 0;
  }
}

// Sprite frames carry large transparent margins; crop to the visible pixels
// so avatar thumbnails show the fighter at a sensible size.
async function spriteThumbnail(url) {
  const img = await loadImage(url);
  const scratch = document.createElement('canvas');
  scratch.width = img.width;
  scratch.height = img.height;
  const ctx = scratch.getContext('2d');
  ctx.drawImage(img, 0, 0);
  const { data } = ctx.getImageData(0, 0, scratch.width, scratch.height);
  let minX = scratch.width, minY = scratch.height, maxX = -1, maxY = -1;
  for (let y = 0; y < scratch.height; y++) {
    for (let x = 0; x < scratch.width; x++) {
      if (data[(y * scratch.width + x) * 4 + 3] > 0) {
        minX = Math.min(minX, x);
        minY = Math.min(minY, y);
        maxX = Math.max(maxX, x);
        maxY = Math.max(maxY, y);
      }
    }
  }
  if (maxX < minX) return url; // fully transparent frame; use as-is
  const cropped = document.createElement('canvas');
  cropped.width = maxX - minX + 1;
  cropped.height = maxY - minY + 1;
  cropped.getContext('2d').drawImage(img, -minX, -minY);
  return cropped.toDataURL();
}

async function buildCreator() {
  if (creatorBuilt) return;
  creatorBuilt = true;
  const mappings = await getMappings();

  const grid = el('avatar-grid');
  for (const [key, config] of Object.entries(mappings)) {
    const firstRestFrame = config.actions.rest[0][0];
    const button = document.createElement('button');
    button.type = 'button';
    button.dataset.avatar = key;
    const img = document.createElement('img');
    const frameUrl = `${config.img_dir}${config.img_prefix}_${firstRestFrame}.png`;
    spriteThumbnail(frameUrl).then((src) => { img.src = src; });
    img.alt = config.img_prefix;
    button.append(img, document.createTextNode(config.img_prefix));
    button.addEventListener('click', () => {
      selectedAvatar = key;
      for (const other of grid.children) other.classList.toggle('selected', other === button);
    });
    grid.append(button);
  }
  // Preselect a random avatar so the form is always valid.
  const buttons = [...grid.children];
  buttons[Math.floor(Math.random() * buttons.length)].click();

  const rows = el('stat-rows');
  for (const stat of STATS) {
    const card = document.createElement('div');
    card.className = 'stat-card';

    const header = document.createElement('div');
    header.className = 'stat-header';
    const label = document.createElement('span');
    label.className = 'stat-name';
    label.textContent = statLabel(stat);
    const controls = document.createElement('span');
    controls.className = 'stat-controls';
    for (const [suffix, delta, text] of [['dec', -1, '−'], ['value', 0, ''], ['inc', 1, '+']]) {
      if (suffix === 'value') {
        const value = document.createElement('span');
        value.className = 'value';
        value.id = `stat-value-${stat}`;
        controls.append(value);
        continue;
      }
      const button = document.createElement('button');
      button.type = 'button';
      button.id = `stat-${suffix}-${stat}`;
      button.textContent = text;
      button.addEventListener('click', () => {
        statValues[stat] += delta;
        refreshCreator();
      });
      controls.append(button);
    }
    header.append(label, controls);

    const description = document.createElement('p');
    description.className = 'stat-description';
    description.textContent = STAT_INFO[stat];

    card.append(header, description);
    rows.append(card);
  }
  refreshCreator();
}

modeSelect.addEventListener('change', () => {
  const gameMode = modeSelect.value === 'game';
  creator.hidden = !gameMode;
  watchLabel.hidden = !gameMode;
  if (gameMode) buildCreator();
});

// ---------------------------------------------------------------------------
// Overlay prompts (pause the flow until the player chooses)

function overlayPrompt(build) {
  return new Promise((resolve) => {
    overlay.innerHTML = '';
    overlay.hidden = false;
    build((value) => {
      overlay.hidden = true;
      overlay.innerHTML = '';
      resolve(value);
    });
  });
}

function promptStatBoost(fighter) {
  return overlayPrompt((done) => {
    const title = document.createElement('h2');
    title.textContent = 'Victory!';
    const prompt = document.createElement('p');
    prompt.textContent = 'Choose a stat to train (+1):';
    const choices = document.createElement('div');
    choices.className = 'choices';
    for (const stat of STATS) {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = `${statLabel(stat)} ${fighter[stat]} → ${fighter[stat] + 1}`;
      button.title = STAT_INFO[stat];
      button.addEventListener('click', () => {
        fighter.increaseStat(stat);
        done();
      });
      choices.append(button);
    }
    overlay.append(title, prompt, choices);
  });
}

function promptGameOver(roundNumber) {
  return overlayPrompt((done) => {
    const title = document.createElement('h2');
    title.className = 'game-over';
    title.textContent = 'GAME OVER';
    const prompt = document.createElement('p');
    prompt.textContent = `Your fighter was defeated in round ${roundNumber}.`;
    const choices = document.createElement('div');
    choices.className = 'choices';
    for (const [value, label] of [['watch', 'Continue Watching'], ['end', 'End Tournament']]) {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = label;
      button.addEventListener('click', () => done(value));
      choices.append(button);
    }
    overlay.append(title, prompt, choices);
  });
}

// ---------------------------------------------------------------------------
// Tournament flow

function createCustomFighter() {
  const name = el('fighter-name').value.trim() || el('fighter-name').placeholder;
  return new Combatant({
    ...statValues,
    name,
    gender: selectedAvatar.split('_').pop(),
    spriteKey: selectedAvatar,
    isPlayer: true,
  });
}

async function startTournament() {
  startButton.disabled = true;
  downloads.hidden = true;
  overlay.hidden = true;
  renderer?.stop();

  try {
    const mappings = await getMappings();
    const gameMode = modeSelect.value === 'game';
    const count = Number(fighterCountSelect.value);
    const totalFights = count - 1;

    let custom = null;
    if (gameMode) {
      await buildCreator();
      custom = createCustomFighter();
    }
    const combatants = custom ? [custom, ...generateCombatants(count - 1)] : generateCombatants(count);

    statusLine.textContent = `${count} fighters enter... only one leaves.`;
    renderer = new TournamentRenderer(canvas, mappings, {
      speed: () => Number(speedSelect.value),
      totalFights,
    });
    await renderer.start();

    const watchAll = !gameMode || watchModeSelect.value === 'all';
    const records = [];
    let customAlive = Boolean(custom);
    let continueWatching = false;
    let endedEarly = false;
    let champion = null;

    for (const step of tournamentSteps(combatants)) {
      records.push(step.record);
      champion = step.winner;
      const mine = custom !== null && step.fighters.includes(custom);

      const watch = !custom || (customAlive ? watchAll || mine : continueWatching);
      if (watch) {
        await renderer.playFight(step.record);
      } else {
        renderer.applyResult(step.record);
      }

      if (mine && customAlive) {
        if (step.winner === custom) {
          if (step.record.roundNumber < totalFights) {
            await promptStatBoost(custom);
          }
        } else {
          customAlive = false;
          const choice = await promptGameOver(step.record.roundNumber);
          if (choice === 'end') {
            endedEarly = true;
            break;
          }
          continueWatching = true;
        }
      }
    }

    if (endedEarly) {
      renderer.showBanner('GAME OVER', '#ff5148');
      statusLine.textContent = `Game over — ${custom.name} fell in round ${records.at(-1).roundNumber}. Better luck next time!`;
    } else if (custom !== null && champion === custom) {
      renderer.showBanner('You have won the tournament!', '#ffd54a');
      statusLine.textContent = `${custom.name} (that's you!) has won the tournament!`;
    } else {
      renderer.showBanner(`${champion.name} has won the tournament!`);
      statusLine.textContent =
        `${champion.name} (${champion.combatClass.replaceAll('_', ' ')}, ${champion.rank}) has won the tournament!`;
    }

    el('download-tournament').onclick = () => download('tournament_log.csv', tournamentLogCsv(records));
    el('download-fights').onclick = () => download('fight_log.csv', fightLogCsv(records));
    downloads.hidden = false;
  } catch (error) {
    statusLine.textContent = `Something went wrong: ${error.message}`;
    throw error;
  } finally {
    startButton.disabled = false;
    startButton.textContent = modeSelect.value === 'game' ? 'Play Again' : 'New Tournament';
  }
}

startButton.addEventListener('click', startTournament);
