"use strict";
const assert = require("node:assert/strict");
const sim = require("./sim");

const r = sim.run();

// Rule-level / one-day scenario tests.
assert.ok(r.breadScarcity.priceAfter > r.breadScarcity.priceBefore);
assert.ok(r.noodles.breadDemandAfterEntry < r.noodles.baselineBreadDemand);
assert.ok(r.noodles.noodleDemandAfterEntry > 0);
assert.ok(r.productivity.newPriceAfter < r.productivity.baselineBreadPriceAfter);
assert.ok(r.moneyIssue.newDemand > r.moneyIssue.baselineDemand);
assert.equal(r.moneyIssue.richDemandBefore, r.moneyIssue.richDemandAfter);
assert.equal(r.speculation.choosesBuyToHold, false);
assert.equal(r.entry.lowPriceEntry.choosesOpen, false);
assert.equal(r.entry.highPriceEntry.choosesOpen, true);

// Price never reaches exactly zero with strictly positive starting prices.
assert.ok(sim.nextPrice(5, 0, 10) > 0);
assert.ok(sim.nextPrice(5, 3, 0) > 5);
assert.equal(sim.nextPrice(5, 0, 0), 5);
assert.ok(r.boundary.priceAfter > 0 && r.boundary.priceAfter < 5);

// Verify the updated bounded price equation.
assert.ok(Math.abs(sim.nextPrice(5, 20, 8)
  - 5 * (1 + 0.2 * (20 - 8) / (20 + 8 + 1))) < 1e-12);
for (let d = 0; d <= 100; d += 5) {
  for (let s = 0; s <= 100; s += 5) {
    const p = sim.nextPrice(5, d, s);
    assert.ok(p > 4 && p < 6.00000001);
  }
}

// Production consumes REAL input inventory; purchases transfer existing gold.
const w = sim.breadOnly(sim.people(20), 8, 5);
const sumGold = () => w.npcs.reduce((x, n) => x + n.gold, 0)
  + w.shops.reduce((x, s) => x + s.owner.gold, 0);
const moneyBefore = sumGold();
const wheatBefore = w.shops[0].inventory.wheat;
const day = sim.marketDay(w);
assert.equal(w.shops[0].inventory.wheat, wheatBefore - 4);
assert.equal(day.sales.bread, 8);
assert.ok(Math.abs(sumGold() - moneyBefore) < 1e-8);

// Multi-period stability probe -- positive price, but economic collapse may still occur.
const follow = sim.breadOnly(sim.people(20), 12, 5);
const history = Array.from({ length: 8 }, (_, i) => {
  const state = sim.marketDay(follow);
  return { day: i + 1, price: state.after.bread,
    demand: state.demand.bread, offered: state.offered.bread,
    sold: state.sales.bread,
    unsupported: state.unsupported };
});
assert.ok(history.every(d => d.price > 0), "zero price trap must be removed");
assert.ok(history.at(-1).price < history[0].price,
  "without wage income, demand loss still depresses prices");

console.log("All economic-rule checks passed.");
console.log(JSON.stringify({ scenarioResults: r, eightDayHistory: history }, null, 2));
