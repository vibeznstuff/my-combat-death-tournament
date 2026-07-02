// Canvas playback of simulated fights: replays a fight's event log with the
// character sprite animations, health bars, timer and leaderboard. Fight
// sequencing is driven externally via playFight()/applyResult(), so callers
// decide which fights to watch, skip, or interleave with UI prompts.

import { MAX_FIGHT_MOMENTS } from './constants.js';
import { getFrames, preloadCharacter, loadImage } from './sprites.js';

const WIDTH = 1000;
const HEIGHT = 550;
const FRAME_RATE = 35;
const TICKS_PER_FRAME = 3; // each animation frame is shown for this many ticks

const HOME = [
  { x: -90, y: 135 }, // player one (left, sprites flipped to face right)
  { x: 445, y: 130 }, // player two (right)
];
const CONTACT_DISTANCE = 90; // attacker stops this far from the defender
const BACKGROUND_URL = 'sprite_sheets/dark_forest_br.png';

// Baseline countdown speed, in fight "moments" per second of playback.
const MOMENTS_PER_SECOND = 24;
const RANKED = new Set(['ELITE', 'MASTER', 'LEGENDARY']);

function classLabel(combatClass) {
  return combatClass.replaceAll('_', ' ').toLowerCase()
    .replace(/\b\w/g, (ch) => ch.toUpperCase());
}

function displayName(info) {
  return info.isPlayer ? `${info.name} (You)` : info.name;
}

function characterKey(info) {
  return info.spriteKey ?? `${info.combatClass.toLowerCase()}_${info.gender}`;
}

function leaderboardKey(info) {
  const name = RANKED.has(info.rank) ? `${info.name} (${info.rank})` : displayName(info);
  return `${name} - ${classLabel(info.combatClass)}`;
}

class Player {
  constructor(index, info, mappings) {
    this.index = index;
    this.info = info;
    this.mappings = mappings;
    this.character = characterKey(info);
    this.config = mappings[this.character];
    this.flip = index === 0; // player one sprites face left; mirror them
    this.home = HOME[index];
    this.x = this.home.x;
    this.y = this.home.y;
    this.maxHealth = info.maxHealth;
    this.health = info.health;
    this.displayHealth = info.health;
    this.frames = [];
    this.tick = 0;
    this.action = null;
    this.loop = true;
  }

  preload() {
    return preloadCharacter(this.mappings, this.character);
  }

  // Frames are preloaded per fight, so the cached promise resolves
  // immediately; the async gap is at most one tick on a cold cache.
  async setAction(action, { slowFactor = null, loop = true } = {}) {
    this.action = action;
    this.loop = loop;
    this.tick = 0;
    this.frames = await getFrames(this.mappings, this.character, action, slowFactor);
  }

  rest() {
    this.x = this.home.x;
    return this.setAction('rest');
  }

  get animationDone() {
    return !this.loop && this.tick >= this.frames.length * TICKS_PER_FRAME - 1;
  }

  advance() {
    const limit = this.frames.length * TICKS_PER_FRAME;
    if (this.loop) {
      this.tick = (this.tick + 1) % limit;
    } else {
      this.tick = Math.min(this.tick + 1, limit - 1);
    }
    // Ease the displayed health toward the actual value after a hit.
    if (this.displayHealth > this.health) {
      const drain = Math.max(3, (this.displayHealth - this.health) * 0.12);
      this.displayHealth = Math.max(this.health, this.displayHealth - drain);
    }
  }

  draw(ctx) {
    const img = this.frames[Math.floor(this.tick / TICKS_PER_FRAME)];
    if (!img) return;
    if (this.flip) {
      ctx.save();
      ctx.translate(this.x + img.width, this.y);
      ctx.scale(-1, 1);
      ctx.drawImage(img, 0, 0);
      ctx.restore();
    } else {
      ctx.drawImage(img, this.x, this.y);
    }
  }
}

export class TournamentRenderer {
  /**
   * @param canvas target canvas (1000x550)
   * @param mappings parsed animation_mappings.json
   * @param options { speed, totalFights } — speed is a multiplier ref read live
   */
  constructor(canvas, mappings, { speed = () => 1, totalFights = 0 } = {}) {
    this.ctx = canvas.getContext('2d');
    this.mappings = mappings;
    this.speed = speed;
    this.totalFights = totalFights;
    this.leaderboard = new Map();
    this.state = 'idle';
    this.stateTimer = 0;
    this.background = null;
    this.players = [];
    this.fight = null;
    this.banner = null;
    this.bannerColor = '#fff';
    this.stopped = false;
    this.resolvePlayback = null;
  }

  async start() {
    this.background = await loadImage(BACKGROUND_URL);
    let last = performance.now();
    const tickMs = 1000 / FRAME_RATE;
    const step = (now) => {
      if (this.stopped) return;
      // Fixed-rate ticks decoupled from display refresh; the speed setting
      // runs extra ticks per interval so everything scales uniformly.
      while (now - last >= tickMs) {
        last += tickMs;
        const ticks = Math.max(1, Math.round(this.speed()));
        for (let i = 0; i < ticks; i++) this.update();
      }
      this.draw();
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  stop() {
    this.stopped = true;
  }

  // Play one fight record; resolves once the win banner has been shown.
  playFight(record) {
    return new Promise((resolve) => {
      this.resolvePlayback = resolve;
      this.loadFight(record);
    });
  }

  // Record a fight on the leaderboard without playing it back.
  applyResult(record) {
    this.updateLeaderboard(record);
  }

  // Show a persistent center-screen banner (used between fights).
  showBanner(text, color = '#fff') {
    this.banner = text;
    this.bannerColor = color;
  }

  async loadFight(record) {
    this.fight = record;
    this.players = record.combatants.map((info, i) => new Player(i, info, this.mappings));
    this.state = 'loading';
    this.banner = null;
    this.bannerColor = '#fff';
    await Promise.all(this.players.map((p) => p.preload()));
    await Promise.all(this.players.map((p) => p.rest()));
    this.eventIndex = 0;
    this.guiTimer = MAX_FIGHT_MOMENTS;
    this.setState('intro', 1.5);
  }

  setState(state, seconds = 0) {
    this.state = state;
    this.stateTimer = Math.round(seconds * FRAME_RATE);
  }

  nextEvent() {
    return this.fight.events[this.eventIndex] ?? null;
  }

  update() {
    for (const player of this.players) player.advance();
    if (this.stateTimer > 0) {
      this.stateTimer -= 1;
      if (this.stateTimer > 0) return;
    }

    switch (this.state) {
      case 'idle':
      case 'loading':
        break;
      case 'intro':
        this.setState('countdown');
        break;
      case 'countdown':
        this.runCountdown();
        break;
      case 'approach':
        this.runApproach();
        break;
      case 'impact':
        this.runImpact();
        break;
      case 'ko':
        this.runKo();
        break;
      case 'fightEnd':
        this.finishFight();
        break;
    }
  }

  runCountdown() {
    const event = this.nextEvent();
    if (!event) {
      // Defensive: logs always end with a 'win' event.
      this.setState('fightEnd', 1);
      return;
    }

    if (this.guiTimer > event.timeRemaining) {
      // Tick the fight clock down toward the next event, never letting a
      // quiet stretch drag past ~5 seconds.
      const gap = this.guiTimer - event.timeRemaining;
      const rate = Math.max(MOMENTS_PER_SECOND, gap / 5) / FRAME_RATE;
      this.guiTimer = Math.max(event.timeRemaining, this.guiTimer - rate);
      return;
    }

    this.eventIndex += 1;
    switch (event.type) {
      case 'start':
        break;
      case 'attack':
      case 'dodge':
        this.beginAttack(event);
        break;
      case 'defeat':
        this.beginKo(1 - event.attacker);
        break;
      case 'win':
        // Reached without a preceding KO only when time ran out.
        this.beginKo(1 - this.fight.winnerIndex);
        break;
    }
  }

  beginAttack(event) {
    this.currentEvent = event;
    const attacker = this.players[event.attacker];
    attacker.setAction('dash_attack');
    this.dashSpeed = 0;
    this.setState('approach');
  }

  runApproach() {
    const event = this.currentEvent;
    const attacker = this.players[event.attacker];
    const defender = this.players[1 - event.attacker];
    const direction = event.attacker === 0 ? 1 : -1;
    const target = defender.home.x - direction * CONTACT_DISTANCE;

    this.dashSpeed += 1;
    attacker.x += direction * this.dashSpeed;

    const arrived = direction === 1 ? attacker.x >= target : attacker.x <= target;
    if (!arrived) return;
    attacker.x = target;

    if (event.type === 'dodge') {
      defender.setAction('dodge');
      this.dodgeStartX = defender.x;
    } else {
      defender.setAction('injured', { slowFactor: 3, loop: false });
      defender.health = event.health[defender.index];
    }
    this.setState('impact');
  }

  runImpact() {
    const event = this.currentEvent;
    const defender = this.players[1 - event.attacker];

    if (event.type === 'dodge') {
      // Slide the defender back over the course of the dodge animation.
      const progress = Math.min(1, (defender.tick + 1) / (defender.frames.length * TICKS_PER_FRAME));
      const direction = defender.index === 0 ? -1 : 1;
      defender.x = this.dodgeStartX + direction * defender.config.dodge_space * progress;
      if (progress < 1) return;
    } else if (!defender.animationDone || defender.displayHealth > defender.health) {
      return;
    }

    for (const player of this.players) player.rest();
    this.setState('countdown');
  }

  beginKo(loserIndex) {
    const loser = this.players[loserIndex];
    const winner = this.players[1 - loserIndex];
    loser.setAction('defeat', { loop: false });
    winner.x = winner.home.x; // snap the winner home before the victory pose
    winner.setAction('victory', { loop: false });
    this.setState('ko');
  }

  runKo() {
    if (this.players.every((p) => p.animationDone)) {
      this.updateLeaderboard(this.fight);
      const winner = this.fight.combatants[this.fight.winnerIndex];
      this.banner = `${displayName(winner)} wins the fight!`;
      this.setState('fightEnd', 3);
    }
  }

  updateLeaderboard(record) {
    const winner = record.combatants[record.winnerIndex];
    const loser = record.combatants[1 - record.winnerIndex];
    const winnerKey = leaderboardKey(winner);
    this.leaderboard.delete(leaderboardKey(loser));
    this.leaderboard.set(winnerKey, (this.leaderboard.get(winnerKey) ?? 0) + 1);
  }

  finishFight() {
    this.state = 'idle';
    this.banner = null; // persistent end-of-tournament banners are set by the caller
    const resolve = this.resolvePlayback;
    this.resolvePlayback = null;
    resolve?.();
  }

  draw() {
    const ctx = this.ctx;
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, WIDTH, HEIGHT);
    if (this.background) ctx.drawImage(this.background, 0, 0, WIDTH, HEIGHT);

    if (this.state === 'loading') {
      this.drawCenteredText('Loading fighters...', 28, 250);
      return;
    }

    if (this.players.length > 0) {
      // Draw the acting player last so they render on top.
      const order = [...this.players].sort(
        (a, b) => (a.action === 'dash_attack' ? 1 : 0) - (b.action === 'dash_attack' ? 1 : 0),
      );
      for (const player of order) player.draw(ctx);
      this.drawHud();
    } else {
      this.drawLeaderboard();
    }

    if (this.banner) this.drawCenteredText(this.banner, 36, 250, this.bannerColor);
  }

  drawHud() {
    const ctx = this.ctx;
    for (const player of this.players) {
      const { info, maxHealth, displayHealth } = player;
      const barX = player.index === 0 ? 50 : WIDTH - maxHealth - 50;
      const healthX = player.index === 0 ? 50 : WIDTH - displayHealth - 50;

      ctx.fillStyle = '#fff';
      ctx.fillRect(barX - 2, 73, maxHealth + 4, 34);
      ctx.fillStyle = '#f00';
      ctx.fillRect(barX, 75, maxHealth, 30);
      if (displayHealth > 0) {
        ctx.fillStyle = '#0f0';
        ctx.fillRect(healthX, 75, displayHealth, 30);
      }

      const rank = RANKED.has(info.rank) ? ` (${info.rank.charAt(0)}${info.rank.slice(1).toLowerCase()})` : '';
      ctx.fillStyle = '#fff';
      ctx.textAlign = player.index === 0 ? 'left' : 'right';
      const edgeX = player.index === 0 ? 50 : WIDTH - 50;
      ctx.font = '17px sans-serif';
      ctx.fillText(`${displayName(info)}${rank}`, edgeX, 50);
      ctx.font = '14px sans-serif';
      ctx.fillText(classLabel(info.combatClass), edgeX, 66);
    }

    ctx.textAlign = 'center';
    ctx.font = '21px sans-serif';
    ctx.fillStyle = '#fff';
    ctx.fillText(`Round ${this.fight.roundNumber} of ${this.totalFights}`, WIDTH / 2, 40);
    ctx.fillText(String(Math.ceil(this.guiTimer)), WIDTH / 2, 98);
    this.drawLeaderboard();
  }

  drawLeaderboard() {
    const ctx = this.ctx;
    // Top eight by wins.
    const standings = [...this.leaderboard.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8);
    ctx.textAlign = 'center';
    ctx.fillStyle = '#fff';
    ctx.font = '12px sans-serif';
    standings.forEach(([player, wins], i) => {
      ctx.fillText(`${player} [${wins} Win${wins === 1 ? '' : 's'}]`, WIDTH / 2, 130 + (i + 1) * 14);
    });
    ctx.textAlign = 'left';
  }

  drawCenteredText(text, size, y, color = '#fff') {
    const ctx = this.ctx;
    ctx.font = `bold ${size}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.fillStyle = '#000';
    ctx.fillText(text, WIDTH / 2 + 2, y + 2);
    ctx.fillStyle = color;
    ctx.fillText(text, WIDTH / 2, y);
    ctx.textAlign = 'left';
  }
}
