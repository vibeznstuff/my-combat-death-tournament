import {
  HEALTH_MULTIPLIER,
  HEALTH_INCREASE_BONUS,
  ELITE_THRESHOLD,
  MASTER_THRESHOLD,
  LEGENDARY_THRESHOLD,
} from './constants.js';
import { MALE_FIRST_NAMES, FEMALE_FIRST_NAMES, LAST_NAMES } from './names.js';

export const CLASS_STATS = {
  TANK: { strength: 10, defense: 10, agility: 3, stamina: 5, wisdom: 2 },
  MARTIAL_ARTIST: { strength: 5, defense: 5, agility: 9, stamina: 7, wisdom: 4 },
  TACTICIAN: { strength: 2, defense: 2, agility: 6, stamina: 10, wisdom: 10 },
  BERSERKER: { strength: 10, defense: 4, agility: 6, stamina: 10, wisdom: 0 },
  HEART: { strength: 5, defense: 10, agility: 5, stamina: 6, wisdom: 4 },
  HERO: { strength: 6, defense: 7, agility: 3, stamina: 4, wisdom: 10 },
  SAMURAI: { strength: 20, defense: 0, agility: 10, stamina: 0, wisdom: 10 },
  VIPER: { strength: 10, defense: 8, agility: 10, stamina: 0, wisdom: 2 },
  DRUNK: { strength: 10, defense: 8, agility: 1, stamina: 1, wisdom: 10 },
};

export const CLASS_LIST = Object.keys(CLASS_STATS);

// Bonus dice faces map to the stat that gets boosted; HEALTH scales max health instead.
const BONUS_STATS = ['strength', 'defense', 'agility', 'stamina', 'wisdom', 'HEALTH'];
const STAT_BONUS_POINTS = 5;

function randomChoice(list) {
  return list[Math.floor(Math.random() * list.length)];
}

function baseHealth(stats) {
  return Math.max(50, Math.round(stats.stamina * 4 + stats.defense * 6) * HEALTH_MULTIPLIER);
}

export class Combatant {
  constructor(profile = null) {
    this.spriteKey = null;
    this.isPlayer = false;
    if (profile === null) {
      this.setName();
      this.setClass();
    } else {
      // Player-created fighters keep exactly the stats they were given: no
      // rank bonuses and no gender stat modifiers.
      this.combatClass = 'NEW CHALLENGER';
      this.strength = profile.strength;
      this.defense = profile.defense;
      this.agility = profile.agility;
      this.stamina = profile.stamina;
      this.wisdom = profile.wisdom;
      this.maxHealth = baseHealth(profile);
      this.health = this.maxHealth;
      this.rank = 'MYSTERY';
      this.name = profile.name;
      this.gender = profile.gender;
      this.spriteKey = profile.spriteKey ?? null;
      this.isPlayer = Boolean(profile.isPlayer);
    }
  }

  setName() {
    if (Math.random() > 0.5) {
      this.gender = 'male';
      this.name = `${randomChoice(MALE_FIRST_NAMES)} ${randomChoice(LAST_NAMES)}`;
    } else {
      this.gender = 'female';
      this.name = `${randomChoice(FEMALE_FIRST_NAMES)} ${randomChoice(LAST_NAMES)}`;
    }
  }

  setClass() {
    this.combatClass = randomChoice(CLASS_LIST);
    const stats = CLASS_STATS[this.combatClass];

    this.strength = stats.strength;
    this.defense = stats.defense;
    this.agility = stats.agility;
    this.stamina = stats.stamina;
    this.wisdom = stats.wisdom;
    this.maxHealth = baseHealth(stats);
    this.health = this.maxHealth;

    // Assess rank: a single roll below a threshold awards that rank (and any
    // rarer threshold it also clears), granting more stat bonuses.
    const rankRoll = Math.random();
    this.rank = 'WARRIOR';
    let bonusCount = 0;

    if (rankRoll < ELITE_THRESHOLD) {
      this.rank = 'ELITE';
      bonusCount = 1;
    }
    if (rankRoll < MASTER_THRESHOLD) {
      this.rank = 'MASTER';
      bonusCount = 2;
    }
    if (rankRoll < LEGENDARY_THRESHOLD || this.name.toLowerCase() === 'the chosen one') {
      this.rank = 'LEGENDARY';
      bonusCount = 4;
    }

    // Apply stat bonuses, picked at random without replacement.
    const bonusPool = [...BONUS_STATS];
    for (let i = 0; i < bonusCount; i++) {
      const bonus = bonusPool.splice(Math.floor(Math.random() * bonusPool.length), 1)[0];
      if (bonus === 'HEALTH') {
        this.maxHealth = Math.round(this.maxHealth * HEALTH_INCREASE_BONUS);
        this.health = this.maxHealth;
      } else {
        this[bonus] += STAT_BONUS_POINTS;
      }
    }

    if (this.gender === 'male') {
      this.strength = Math.round(this.strength * 1.2);
      this.wisdom = Math.round(this.wisdom * 0.8);
    } else {
      this.defense = Math.round(this.defense * 0.8);
      this.agility = Math.round(this.agility * 1.2);
    }
  }

  recuperate() {
    this.health = Math.min(this.maxHealth, Math.round(this.health * 1.5));
  }

  // Post-victory reward in game mode: +1 to a chosen stat. Defense and
  // stamina raises also grow max health, since it derives from them.
  increaseStat(stat) {
    this[stat] += 1;
    const newMax = baseHealth(this);
    if (newMax > this.maxHealth) {
      this.health += newMax - this.maxHealth;
      this.maxHealth = newMax;
    }
  }

  // Pre-fight snapshot used by the playback UI and log exports.
  snapshot() {
    return {
      spriteKey: this.spriteKey,
      isPlayer: this.isPlayer,
      name: this.name,
      gender: this.gender,
      combatClass: this.combatClass,
      rank: this.rank,
      maxHealth: this.maxHealth,
      health: this.health,
      strength: this.strength,
      defense: this.defense,
      agility: this.agility,
      stamina: this.stamina,
      wisdom: this.wisdom,
    };
  }
}
