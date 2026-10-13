"use strict";
// Parameter sensitivity is an experiment, not an additional NPC behavior rule.
const { newWorld, step } = require("./payroll");
function run(wage, alpha, beta, gamma, hours=60) {
  const w=newWorld(wage);
  for(const person of [w.owner,...w.workers]) Object.assign(person,{alpha,beta,gamma});
  const history=Array.from({length:hours},()=>step(w));
  const prices=history.slice(Math.floor(hours/2)).map(x=>x.price);
  const mean=prices.reduce((a,b)=>a+b,0)/prices.length;
  const cv=Math.sqrt(prices.reduce((a,b)=>a+(b-mean)**2,0)/prices.length)/mean;
  return {wage,alpha,beta,gamma,
    meanPrice:+mean.toFixed(4),priceCV:+cv.toFixed(4),
    endingPrice:+history.at(-1).price.toFixed(4),
    jobs:history.filter(x=>x.hired).length,
    hungerReachedZero:history.some(x=>x.zeroHunger>0)};
}
function sweep() {
  const rows=[];
  for(const wage of [3,4,5,6,7])
  for(const alpha of [0.5,1,2])
  for(const beta of [2,3,5])
  for(const gamma of [0.05,0.1,0.3])
    rows.push(run(wage,alpha,beta,gamma));
  const noHunger=rows.filter(x=>!x.hungerReachedZero&&x.jobs>=50);
  return {cases:rows.length,noHungerCases:noHunger.length,
    examples:[
      run(3,1,3,0.1),run(4,1,3,0.1),
      run(6,1,3,0.1),run(4,2,3,0.1),
    ]};
}
if(require.main===module) console.log(JSON.stringify(sweep(),null,2));
module.exports={run,sweep};
