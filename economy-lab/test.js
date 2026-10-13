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

// Deliberately record failures, rather than disguising them with new rules.
assert.equal(sim.nextPrice(5, 0, 10), 0);
assert.equal(sim.nextPrice(5, 3, 0), null);
assert.equal(r.boundary.priceAfter, 0);

// Verify the original formula is implemented literally.
assert.ok(Math.abs(sim.nextPrice(5, 20, 8) - 5 * (20 / 8) ** 0.2) < 1e-12);

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

// Multi-period stability probe -- expect to EXPOSE the current price=0 trap.
const follow = sim.breadOnly(sim.people(20), 12, 5);
const history = Array.from({ length: 8 }, (_, i) => {
  const state = sim.marketDay(follow);
  return { day: i + 1, price: state.after.bread,
    demand: state.demand.bread, offered: state.offered.bread,
    sold: state.sales.bread,
    unsupported: state.unsupported };
});
assert.ok(history.some(d => d.price === 0), "expected price-zero failure");
assert.ok(history.filter(d => d.price === 0).length >= 2,
  "expected persistent price-zero failure");

console.log("All economic-rule checks passed.");
console.log(JSON.stringify({ scenarioResults: r, eightDayHistory: history }, null, 2));
