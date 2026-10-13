"use strict";
const assert=require("node:assert/strict");
const {create,tick,simulate,potentialLaborSupply}=require("./integrated");
const {nextPrice,makeNpc}=require("./sim");
const {BUILDINGS}=require("./payroll");

// User's six known recipes, including construction requirements.
assert.equal(Object.keys(BUILDINGS).length,6);
assert.deepEqual(BUILDINGS.farm.input,{water:1});
assert.deepEqual(BUILDINGS.mill.output,{flour:1});
assert.deepEqual(BUILDINGS.bakery.input,{electricity:2,water:1,flour:1});
assert.deepEqual(BUILDINGS.bakery.output,{bread:2});
assert.deepEqual(BUILDINGS.riceField.output,{rice:3});
assert.deepEqual(BUILDINGS.sand.output,{cement:2});
assert.deepEqual(BUILDINGS.ironMine.output,{iron:2});

const noMigration=simulate(120,{immigration:false});
const migration=simulate(120,{immigration:true});
assert.equal(noMigration.immigrants,0);
assert.ok(migration.immigrants>0);
assert.ok(migration.population>noMigration.population);
assert.ok(migration.firstImmigrant.hour>0);
assert.ok(migration.firstImmigrant.food>=0.5*(migration.firstImmigrant.population-1));
assert.ok(migration.buildings>6);
assert.ok(migration.completed>0);
for(const good of ["barley","flour","bread","rice","cement","iron"])
  assert.ok(migration.output[good]>0,good+" was not produced");
assert.ok(migration.sales.bread>0 && migration.sales.rice>0);
assert.ok(migration.workHours>0 && migration.wagesPaid>0);
assert.ok(migration.history.every(x=>Math.abs(x.totalGold-migration.initialGold)<1e-6));
assert.ok(migration.history.every(x=>x.priceBread>0 && x.priceRice>0));
assert.ok(migration.history.every(x=>Number.isFinite(x.priceBread+x.priceRice)));
assert.ok(migration.final.starving>noMigration.final.starving);
assert.ok(migration.final.migrantsStarving>0);

// All physical goods remain nonnegative, no reserve is refilled, no NPC gold is minted.
const world=create({surplus:0.5});
let paid=false, built=false, migrated=false;
for(let i=0;i<120;i++){
  const h=tick(world);
  if(h.wages>0)paid=true;
  if(world.buildings.length>6)built=true;
  if(world.births>0)migrated=true;
  assert.ok(Math.abs(world.npcs.reduce((s,n)=>s+n.gold,0)-world.initialGold)<1e-6);
  for(const n of world.npcs){assert.ok(n.gold>=-1e-7 && n.hunger>=0 && n.san>=0);}
  for(const building of world.buildings)
    for(const quantity of Object.values(building.stock))assert.ok(quantity>=0);
  for(const [good,stock]of Object.entries(world.raw))
    assert.ok(stock>=0 && stock<={wood:100,water:3000,electricity:3000}[good]);
}
assert.ok(paid && built && migrated);

// Wage is an endogenous commodity, with one unified D/S price rule.
const shortageWorld=create({wage:1,immigration:false});
const offered=potentialLaborSupply(shortageWorld);
const shortage=tick(shortageWorld);
assert.ok(shortage.laborDemand>shortage.laborSupply);
assert.equal(shortage.laborSupply,offered.size);
assert.ok(shortage.wageAfter>shortage.wageBefore);
assert.ok(shortage.unfilledJobs>0);
const surplusWorld=create({wage:6,immigration:false});
const surplus=tick(surplusWorld);
assert.ok(surplus.laborDemand<surplus.laborSupply);
assert.ok(surplus.wageAfter<surplus.wageBefore);
// More available workers, identical funded demand, lower market wage.
const basicLaborWorld=create({wage:3,immigration:false,construction:false});
const extraLaborWorld=create({wage:3,immigration:false,construction:false});
for(let i=0;i<10;i++)extraLaborWorld.npcs.push(
  makeNpc("extra-"+i,{gold:0,hunger:65,san:85,alpha:1,beta:3,gamma:0.1})
);
const basicLabor=tick(basicLaborWorld),extraLabor=tick(extraLaborWorld);
assert.equal(basicLabor.laborDemand,extraLabor.laborDemand);
assert.ok(extraLabor.laborSupply>basicLabor.laborSupply);
assert.ok(extraLabor.wageAfter<basicLabor.wageAfter);
for(const simRun of [migration,noMigration]){
 for(const hour of simRun.history){
  assert.ok(hour.wageAfter>0 && Number.isFinite(hour.wageAfter));
  assert.ok(hour.working<=hour.laborSupply);
  assert.ok(hour.laborDemand>=hour.working);
  assert.ok(Math.abs(hour.wageAfter-
    nextPrice(hour.wageBefore,hour.laborDemand,hour.laborSupply,0.2))<1e-10);
 }
}

// Crucial counterexample: no paid labor => no food production => hunger.
const noWages=simulate(30,{wage:0,construction:false,immigration:false});
assert.equal(noWages.workHours,0);
assert.equal(noWages.output.bread,0);
assert.equal(noWages.output.rice,0);
assert.ok(noWages.final.starving>0);

// Threshold sensitivity: low threshold causes additional, potentially unemployed migration.
const aggressive=simulate(120,{surplus:0.3});
const conservative=simulate(120,{surplus:1});
assert.ok(aggressive.immigrants>migration.immigrants);
assert.ok(conservative.immigrants<=migration.immigrants);
console.log("Integrated economy checks passed.",
  {control: noMigration.final, immigration: migration.final,
   newPeople:migration.immigrants, construction:migration.completed,
   aggressiveMigration:aggressive.immigrants});
