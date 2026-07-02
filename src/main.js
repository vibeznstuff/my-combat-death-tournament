import { FIGHTER_COUNT } from './constants.js';
import { generateCombatants, runTournament, tournamentLogCsv, fightLogCsv } from './tournament.js';
import { loadMappings } from './sprites.js';
import { TournamentRenderer } from './renderer.js';

const canvas = document.getElementById('arena');
const startButton = document.getElementById('start');
const fighterCountSelect = document.getElementById('fighter-count');
const speedSelect = document.getElementById('speed');
const statusLine = document.getElementById('status');
const downloads = document.getElementById('downloads');

fighterCountSelect.value = String(FIGHTER_COUNT);

let mappingsPromise = null;
let renderer = null;

function download(filename, text) {
  const url = URL.createObjectURL(new Blob([text], { type: 'text/csv' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

async function startTournament() {
  startButton.disabled = true;
  statusLine.textContent = 'Simulating tournament...';
  downloads.hidden = true;
  renderer?.stop();

  try {
    mappingsPromise ??= loadMappings();
    const mappings = await mappingsPromise;

    const combatants = generateCombatants(Number(fighterCountSelect.value));
    const { fights, champion } = runTournament(combatants);

    document.getElementById('download-tournament').onclick = () =>
      download('tournament_log.csv', tournamentLogCsv(fights));
    document.getElementById('download-fights').onclick = () =>
      download('fight_log.csv', fightLogCsv(fights));

    statusLine.textContent = `${combatants.length} fighters enter... only one leaves.`;
    renderer = new TournamentRenderer(canvas, mappings, fights, {
      speed: () => Number(speedSelect.value),
      onFinish: () => {
        statusLine.textContent =
          `${champion.name} (${champion.combatClass.replaceAll('_', ' ')}, ${champion.rank}) has won the tournament!`;
        downloads.hidden = false;
        startButton.disabled = false;
      },
    });
    await renderer.start();
  } catch (error) {
    statusLine.textContent = `Something went wrong: ${error.message}`;
    startButton.disabled = false;
    throw error;
  }

  startButton.disabled = false;
  startButton.textContent = 'New Tournament';
}

startButton.addEventListener('click', startTournament);
