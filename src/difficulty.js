// Game Mode difficulty tiers and per-avatar default builds.
//
// Each tier sets the character creation point budget and per-stat cap.
// Every avatar has a themed default build per tier, drawn from the
// character's look and fighting style; picking an avatar applies its build
// as a starting point the player can tweak. Every build spends the tier's
// full budget and respects its cap (enforced by tests).

export const DIFFICULTIES = {
  easy: { budget: 45, cap: 15 },
  normal: { budget: 40, cap: 12 },
  hard: { budget: 35, cap: 10 },
};

// Builds are [strength, defense, agility, stamina, wisdom].
const BUILDS = {
  hero_male: {
    archetype: 'Brawler',
    easy: [12, 9, 9, 9, 6],
    normal: [10, 8, 8, 8, 6],
    hard: [9, 7, 7, 7, 5],
  },
  hero_female: {
    archetype: 'Swift Blade',
    easy: [8, 3, 15, 7, 12],
    normal: [7, 3, 12, 7, 11],
    hard: [6, 3, 10, 7, 9],
  },
  heart_female: {
    archetype: 'Psychic Guard',
    easy: [7, 10, 7, 9, 12],
    normal: [6, 9, 6, 8, 11],
    hard: [5, 8, 6, 7, 9],
  },
  heart_male: {
    archetype: 'Rushdown',
    easy: [13, 7, 12, 8, 5],
    normal: [11, 6, 11, 7, 5],
    hard: [10, 5, 9, 7, 4],
  },
  samurai_male: {
    archetype: 'Glass Cannon',
    easy: [15, 0, 15, 0, 15],
    normal: [12, 2, 12, 2, 12],
    hard: [10, 3, 10, 2, 10],
  },
  samurai_female: {
    archetype: 'Duelist',
    easy: [12, 3, 13, 5, 12],
    normal: [11, 3, 11, 5, 10],
    hard: [10, 2, 9, 5, 9],
  },
  martial_artist_female: {
    archetype: 'Scrapper',
    easy: [9, 8, 11, 11, 6],
    normal: [8, 7, 10, 10, 5],
    hard: [7, 6, 9, 8, 5],
  },
  martial_artist_male: {
    archetype: 'Speedster',
    easy: [8, 6, 14, 13, 4],
    normal: [7, 5, 12, 12, 4],
    hard: [6, 5, 10, 10, 4],
  },
  berserker_male: {
    archetype: 'Berserker',
    easy: [14, 4, 12, 15, 0],
    normal: [12, 4, 12, 12, 0],
    hard: [10, 5, 10, 10, 0],
  },
  berserker_female: {
    archetype: 'Grappler',
    easy: [15, 8, 7, 12, 3],
    normal: [12, 8, 6, 11, 3],
    hard: [10, 7, 6, 9, 3],
  },
  tactician_male: {
    archetype: 'Tactician',
    easy: [6, 6, 9, 12, 12],
    normal: [5, 6, 8, 10, 11],
    hard: [4, 5, 7, 9, 10],
  },
  tactician_female: {
    archetype: 'Kickboxer',
    easy: [9, 7, 10, 7, 12],
    normal: [8, 6, 9, 6, 11],
    hard: [7, 5, 8, 6, 9],
  },
  tank_female: {
    archetype: 'Agile Tank',
    easy: [9, 12, 12, 8, 4],
    normal: [8, 11, 11, 7, 3],
    hard: [7, 10, 9, 6, 3],
  },
  tank_male: {
    archetype: 'Juggernaut',
    easy: [12, 15, 3, 12, 3],
    normal: [10, 12, 4, 10, 4],
    hard: [9, 10, 3, 9, 4],
  },
  viper_female: {
    archetype: 'Ninja',
    easy: [11, 5, 15, 10, 4],
    normal: [10, 4, 12, 10, 4],
    hard: [9, 4, 10, 9, 3],
  },
  viper_male: {
    archetype: 'Demon Fist',
    easy: [15, 5, 12, 8, 5],
    normal: [12, 5, 10, 8, 5],
    hard: [10, 5, 8, 7, 5],
  },
  drunk_male: {
    archetype: 'Counter Fighter',
    easy: [14, 10, 6, 3, 12],
    normal: [12, 9, 5, 3, 11],
    hard: [10, 8, 5, 3, 9],
  },
  drunk_female: {
    archetype: 'Evasive Dancer',
    easy: [8, 4, 13, 8, 12],
    normal: [7, 4, 11, 8, 10],
    hard: [6, 3, 10, 7, 9],
  },
};

const BUILD_STATS = ['strength', 'defense', 'agility', 'stamina', 'wisdom'];

function toStatObject(values) {
  return Object.fromEntries(BUILD_STATS.map((stat, i) => [stat, values[i]]));
}

// { avatarKey: { archetype, builds: { easy|normal|hard: {strength, ...} } } }
export const AVATAR_BUILDS = Object.fromEntries(
  Object.entries(BUILDS).map(([key, { archetype, ...tiers }]) => [
    key,
    {
      archetype,
      builds: Object.fromEntries(
        Object.entries(tiers).map(([tier, values]) => [tier, toStatObject(values)]),
      ),
    },
  ]),
);
