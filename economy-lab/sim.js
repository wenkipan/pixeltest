"use strict";

/**
 * Minimal, deliberately incomplete economic rule laboratory.
 *
 * Uses only:
 * - NPC gold, hunger, SAN and personal utility parameters
 * - observable item prices
 * - known action input/output, time, and building life
 * - NPC-owned goods and buildings
 *
 * In particular there are NO hidden demand forecasts, invented future prices,
 * fixed price reactions to scenario names, or special "hoarding" behavior.
 *
 * Run: node economy-lab/sim.js
 * Run assertions: node economy-lab/test.js
 */

const K = 0.2;
const MAX_STAT = 100;

function utility(n, gold = n.gold, hunger = n.hunger, san = n.san) {
  if (gold < 0 || hunger < 0 || san < 0) return -Infinity;
  return n.alpha * Math.log1p(gold)
    + n.beta * Math.log1p(Math.min(MAX_STAT, hunger))
    + n.gamma * Math.log1p(Math.min(MAX_STAT, san));
}

function makeNpc(i, overrides = {}) {
  return {
    id: "npc-" + i, gold: 6, hunger: 45, san: 80,
    alpha: 1, beta: i % 2 === 0 ? 2 : 5, gamma: 0.1, delta: 0.97,
    ...overrides,
  };
}

/** How much better is BUY + EAT than doing nothing right now? */
function consumptionGain(npc, food, price) {
  if (price < 0 || price > npc.gold) return -Infinity;
  return utility(npc, npc.gold - price,
    Math.min(MAX_STAT, npc.hunger + food.restore), npc.san) - utility(npc);
}

/** All goods compete for one eating action: no hardcoded substitution rule. */
function chooseFood(npc, foods, prices) {
  let best = null, bestGain = 0;
  for (const [name, food] of Object.entries(foods)) {
    const gain = consumptionGain(npc, food, prices[name]);
    if (gain > bestGain) {
      best = name;
      bestGain = gain;
    }
  }
  return best && { item: best, gain: bestGain };
}

/** Gold-only utility: a purchase without use or resale is never beneficial. */
function buyAndHoldGain(npc, price) {
  if (price > npc.gold || price < 0) return -Infinity;
  return utility(npc, npc.gold - price) - utility(npc);
}

/**
 * Exactly the original P' = P (D/S)^k, with no invented fudge factor.
 * For S = 0, the formula is undefined; record a model failure.
 * For D = 0, it returns zero -- a real weakness of the original rule.
 */
function nextPrice(price, demand, supply, k = K) {
  if (supply === 0) return null;
  return price * Math.pow(demand / supply, k);
}

function makeBakery(name, item, output, input, price, sanCost = 2) {
  return {
    name, item, output, input, sanCost,
    owner: makeNpc(name, {
      gold: 100, hunger: 80, san: 90, beta: 1, gamma: 0.02,
    }),
    inventory: { wheat: 500, bread: 0, noodles: 0 },
    salesGold: 0,
  };
}

/**
 * Production uses a known recipe and a utility comparison. Output is only
 * imputed at the CURRENT posted price, not assumed sold to future customers.
 */
function produce(shop, prices) {
  const needed = shop.input.wheat || 0;
  if (shop.inventory.wheat < needed || shop.owner.san < shop.sanCost) return 0;
  const deltaAtCurrentPrices =
    shop.output * prices[shop.item] - needed * prices.wheat;
  const value = utility(shop.owner,
    shop.owner.gold + deltaAtCurrentPrices,
    shop.owner.hunger, shop.owner.san - shop.sanCost)
    - utility(shop.owner);
  if (value <= 0) return 0;
  shop.inventory.wheat -= needed;
  shop.inventory[shop.item] += shop.output;
  shop.owner.san -= shop.sanCost;
  return shop.output;
}

/** Execute one market day with physical inventories and actual gold transfers. */
function marketDay(world) {
  const offered = {};
  for (const item of Object.keys(world.foods)) offered[item] = 0;
  for (const shop of world.shops) produce(shop, world.prices);
  for (const shop of world.shops) offered[shop.item] += shop.inventory[shop.item];

  const requests = [];
  const demand = Object.fromEntries(Object.keys(world.foods).map(k => [k, 0]));
  const sales = Object.fromEntries(Object.keys(world.foods).map(k => [k, 0]));
  for (const npc of world.npcs) {
    const choice = chooseFood(npc, world.foods, world.prices);
    if (choice) {
      demand[choice.item] += 1;
      requests.push({ npc, ...choice });
    }
  }
  // Highest incremental utility first, stable by original NPC order.
  requests.sort((a, b) => b.gain - a.gain);
  for (const { npc, item } of requests) {
    const shop = world.shops.find(
      s => s.item === item && s.inventory[item] > 0
    );
    if (!shop) continue;
    const price = world.prices[item];
    if (npc.gold < price) continue;
    npc.gold -= price;
    npc.hunger = Math.min(MAX_STAT, npc.hunger + world.foods[item].restore);
    shop.owner.gold += price;
    shop.salesGold += price;
    shop.inventory[item]--;
    sales[item]++;
  }

  const before = { ...world.prices };
  const unsupported = [];
  for (const item of Object.keys(world.foods)) {
    const value = nextPrice(before[item], demand[item], offered[item]);
    if (value === null) unsupported.push(item + ": zero supply -> D/S undefined");
    else world.prices[item] = value;
  }
  for (const npc of world.npcs) npc.hunger = Math.max(0, npc.hunger - 10);
  return { before, after: { ...world.prices }, demand, offered, sales, unsupported };
}

function people(count = 20, change = i => ({})) {
  return Array.from({ length: count }, (_, i) => makeNpc(i, change(i)));
}

function world(npcs, foods, prices, shops) {
  return { npcs, foods, prices: { ...prices }, shops };
}
function breadOnly(npcs, units = 12, price = 5) {
  return world(npcs, { bread: { restore: 42 } },
    { bread: price, wheat: 1 },
    [makeBakery("bakery", "bread", units, { wheat: Math.ceil(units / 2) })]);
}
function dayResult(name, beforeWorld) {
  return { scenario: name, day: marketDay(beforeWorld) };
}

/**
 * Same engine, different STARTING CONDITIONS or legal shocks. These scenarios
 * never override demand, NPC choices, or the outcome of price calculations.
 */
function scenarios() {
  const scarcity = dayResult("bread_scarcity",
    breadOnly(people(20), 8, 5));

  const basic = dayResult("bread_baseline",
    breadOnly(people(20), 12, 5));
  const noodleWorld = breadOnly(people(20), 12, 5);
  noodleWorld.foods.noodles = { restore: 25 };
  noodleWorld.prices.noodles = 3;
  noodleWorld.shops.push(makeBakery(
    "noodle shop", "noodles", 12, { wheat: 6 }
  ));
  const noodles = dayResult("noodles_compete", noodleWorld);

  const technology = dayResult("high_productivity_bakery",
    breadOnly(people(20), 36, 5));

  const poor = i => ({ gold: i < 15 ? 2 : 6, hunger: 45 });
  const noIssue = dayResult("before_money_issue",
    breadOnly(people(20, poor), 12, 5));
  const injectedPeople = people(20, poor);
  // Explicit minting is the scenario's law/action, not earned NPC income.
  for (const n of injectedPeople) n.gold += 4;
  const moneyIssue = dayResult("after_money_issue",
    breadOnly(injectedPeople, 12, 5));

  const rich = i => ({ gold: 50, hunger: 45 });
  const richBase = dayResult("rich_before_extra_money",
    breadOnly(people(20, rich), 12, 5));
  const richMore = dayResult("rich_after_extra_money",
    breadOnly(people(20, i => ({ ...rich(i), gold: 150 })), 12, 5));

  const speculativeNpc = makeNpc("speculator", { gold: 20 });
  const speculativeGain = buyAndHoldGain(speculativeNpc, 5);

  const entrepreneur = makeNpc("entrepreneur", { gold: 100, san: 80 });
  const lowPriceEntry = entryScore(entrepreneur,
    { output: 4, wheatInput: 2, initialCost: 80,
      operatingHoursPerDay: 1, lifeDays: 40, sanCost: 10 },
    { bread: 2, wheat: 1 }, 5);
  const highPriceEntry = entryScore(entrepreneur,
    { output: 4, wheatInput: 2, initialCost: 80,
      operatingHoursPerDay: 1, lifeDays: 40, sanCost: 10 },
    { bread: 7, wheat: 1 }, 5);

  // Case exposing D=0 at a positive S, for which the literal formula sets P=0.
  const noBuyer = dayResult("zero_demand_boundary",
    breadOnly(people(20, () => ({ gold: 0 })), 12, 5));

  return {
    scarcity, basic, noodles, technology, noIssue, moneyIssue,
    richBase, richMore, noBuyer,
    speculation: { buyAndHoldGain: speculativeGain,
      choosesBuyToHold: speculativeGain > 0 },
    entry: { lowPriceEntry, highPriceEntry },
  };
}

/**
 * NPC-specific delta => r = 1/delta - 1.
 * Original annuity logic; all values are computable from CURRENT prices
 * and a building's known recipe/lifetime. NOT a forecast of actual sales.
 */
function entryScore(npc, recipe, prices, wage) {
  const r = 1 / npc.delta - 1;
  const T = recipe.lifeDays;
  const annuity = Math.abs(r) < 1e-12 ? 1 / T :
    r / (1 - Math.pow(1 + r, -T));
  const currentOutputValue = recipe.output * prices.bread;
  const inputCost = recipe.wheatInput * prices.wheat;
  const hourlyEquivalent = (
    currentOutputValue - inputCost - recipe.initialCost * annuity
  ) / recipe.operatingHoursPerDay;
  const sanAfter = npc.san - recipe.sanCost;
  const scoreOpen = npc.gold < recipe.initialCost ? -Infinity :
    utility(npc, npc.gold + hourlyEquivalent, npc.hunger, sanAfter)
    - utility(npc);
  const scoreJob = utility(npc, npc.gold + wage,
    npc.hunger, sanAfter) - utility(npc);
  return { hourlyEquivalent, scoreOpen, scoreJob,
    choosesOpen: scoreOpen > scoreJob };
}

function run() {
  const r = scenarios();
  const summary = {
    breadScarcity: {
      demand: r.scarcity.day.demand.bread,
      supply: r.scarcity.day.offered.bread,
      priceBefore: r.scarcity.day.before.bread,
      priceAfter: r.scarcity.day.after.bread,
    },
    noodles: {
      baselineBreadDemand: r.basic.day.demand.bread,
      breadDemandAfterEntry: r.noodles.day.demand.bread,
      noodleDemandAfterEntry: r.noodles.day.demand.noodles,
      breadPriceAfter: r.noodles.day.after.bread,
    },
    productivity: {
      baselineBreadPriceAfter: r.basic.day.after.bread,
      newPriceAfter: r.technology.day.after.bread,
    },
    moneyIssue: {
      baselineDemand: r.noIssue.day.demand.bread,
      newDemand: r.moneyIssue.day.demand.bread,
      baselinePriceAfter: r.noIssue.day.after.bread,
      newPriceAfter: r.moneyIssue.day.after.bread,
      richDemandBefore: r.richBase.day.demand.bread,
      richDemandAfter: r.richMore.day.demand.bread,
    },
    speculation: r.speculation,
    entry: r.entry,
    boundary: { demand: r.noBuyer.day.demand.bread,
      priceAfter: r.noBuyer.day.after.bread },
  };
  return summary;
}

if (typeof require !== "undefined" && typeof module !== "undefined"
    && require.main === module) {
  process.stdout.write(JSON.stringify(run(), null, 2) + "\n");
}
if (typeof module !== "undefined") {
  module.exports = {
    K, utility, makeNpc, consumptionGain, chooseFood, buyAndHoldGain,
    nextPrice, makeBakery, produce, marketDay, people, breadOnly,
    entryScore, scenarios, run,
  };
}
