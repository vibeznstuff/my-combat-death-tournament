// Loads animation frame images described by animation_mappings.json.
//
// Each character action maps to a list of [start, end] frame-number ranges
// (inclusive, descending ranges play in reverse). A "slow factor" repeats each
// frame N times to slow the animation down.

const imageCache = new Map();
const frameCache = new Map();

export async function loadMappings() {
  const response = await fetch('animation_mappings.json');
  if (!response.ok) {
    throw new Error(`Failed to load animation_mappings.json: ${response.status}`);
  }
  return response.json();
}

export function loadImage(url) {
  if (!imageCache.has(url)) {
    imageCache.set(url, new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error(`Failed to load image: ${url}`));
      img.src = encodeURI(url);
    }));
  }
  return imageCache.get(url);
}

function* frameNumbers(ranges) {
  for (const [start, end] of ranges) {
    const step = start > end ? -1 : 1;
    for (let i = start; i !== end + step; i += step) {
      yield i;
    }
  }
}

/**
 * Resolve an action's frame list to loaded images, repeating each frame
 * according to the slow factor. `slowFactor` overrides the mapping's default
 * for the action when given. Results are cached.
 */
export async function getFrames(mappings, character, action, slowFactor = null) {
  const config = mappings[character];
  const repeats = Math.max(1, slowFactor ?? config[`${action}_slow_factor`] ?? 1);
  const cacheKey = `${character}/${action}/${repeats}`;

  if (!frameCache.has(cacheKey)) {
    frameCache.set(cacheKey, (async () => {
      const urls = [];
      for (const i of frameNumbers(config.actions[action])) {
        urls.push(`${config.img_dir}${config.img_prefix}_${i}.png`);
      }
      const images = await Promise.all(urls.map(loadImage));
      return images.flatMap((img) => Array(repeats).fill(img));
    })());
  }
  return frameCache.get(cacheKey);
}

// Preload every action a character uses in a fight.
export function preloadCharacter(mappings, character) {
  const actions = Object.keys(mappings[character].actions);
  return Promise.all(actions.map((action) => getFrames(mappings, character, action)));
}
