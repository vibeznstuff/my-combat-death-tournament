import { FIGHTER_COUNT } from './constants.js';
import { Combatant } from './combatant.js';
import { generateCombatants, tournamentSteps, tournamentLogCsv, fightLogCsv } from './tournament.js';
import { loadMappings, loadImage } from './sprites.js';
import { TournamentRenderer } from './renderer.js';

// Character creation: total ability points and per-stat ceiling. Randomized
// classes allocate 30 points (Samurai excepted), so this keeps custom
// fighters on an even footing.
const STATS = ['strength', 'defense', 'agility', 'stamina', 'wisdom'];
const STAT_BUDGET = 30;
const STAT_MAX = 10;

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
const statValues = { strength: 6, defense: 6, agility: 6, stamina: 6, wisdom: 6 };

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
    const row = document.createElement('div');
    row.className = 'stat-row';
    const label = document.createElement('span');
    label.textContent = stat.charAt(0).toUpperCase() + stat.slice(1);
    const controls = document.createElement('span');
    controls.className = 'stat-row';
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
    row.append(label, controls);
    rows.append(row);
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
      const label = stat.charAt(0).toUpperCase() + stat.slice(1);
      button.textContent = `${label} ${fighter[stat]} → ${fighter[stat] + 1}`;
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
