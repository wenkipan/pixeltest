"use strict";
// Minimal labor-flow probe, separate from sim.js's one-day scenario tests.
// Only observable prices, personal gold/hunger/SAN/preferences,
// deterministic item recipes, and a configurable hourly wage are used.
const { utility, makeNpc, consumptionGain, nextPrice } = require("./sim");

const BUILDINGS = {
  mill: { name:"磨房", build:{cement:10,wood:10,laborHours:10},
    san:10, input:{electricity:1,barley:1}, output:{flour:1} },
  farm: { name:"农田", build:{wood:5,laborHours:5},
    san:10, input:{water:1}, output:{barley:1} },
  riceField: { name:"水稻田", build:{cement:5,iron:5,wood:5,laborHours:8},
    san:12, input:{water:3}, output:{rice:3} },
  bakery: { name:"面包房", build:{cement:15,iron:5,wood:5,laborHours:12},
    san:10, input:{electricity:2,water:1,flour:1}, output:{bread:2} },
  sand: { name:"沙地", build:{iron:5,laborHours:5},
    san:14, input:{}, output:{cement:2} },
  ironMine: { name:"铁矿场", build:{cement:10,wood:10,laborHours:15},
    san:20, input:{}, output:{iron:2} },
};

const sumValue=(recipe,price)=>
  Object.entries(recipe).reduce((v,[item,quantity])=>v+quantity*price[item],0);

function workerGain(n,job,wage) {
  return utility(n,n.gold+wage,n.hunger,n.san-job.san) -
    utility(n,n.gold,n.hunger,Math.min(100,n.san+10));
}
function work(worker,owner,stock,job,wage,prices) {
  if (worker.san<job.san || owner.gold<wage) return false;
  if (Object.entries(job.input).some(([item,n])=>(stock[item]||0)<n)) return false;
  if (workerGain(worker,job,wage)<=0) return false;
  // A mark-to-market production decision, not a predicted sale.
  if (sumValue(job.output,prices)-sumValue(job.input,prices)-wage<=0) return false;
  owner.gold-=wage; worker.gold+=wage; worker.san-=job.san;
  for(const [item,n] of Object.entries(job.input))stock[item]-=n;
  for(const [item,n] of Object.entries(job.output))stock[item]=(stock[item]||0)+n;
  return true;
}
function newWorld(wage,workerCount=4) {
  const owner=makeNpc("owner",{gold:100,hunger:60,san:80,alpha:1,beta:3,gamma:0.1});
  const workers=Array.from({length:workerCount},(_,i)=>
    makeNpc(i,{gold:0,hunger:60,san:80,alpha:1,beta:3,gamma:0.1}));
  return { owner,workers,wage,prices:{bread:5,flour:2,water:0.2,electricity:0.2},
    stock:{bread:0,flour:100,water:100,electricity:200},time:0 };
}
function step(w) {
  w.time++;
  const job=BUILDINGS.bakery;
  const workers=[...w.workers].sort((a,b)=>workerGain(b,job,w.wage)-workerGain(a,job,w.wage));
  let hired=null;
  for(const worker of workers){
    if(work(worker,w.owner,w.stock,job,w.wage,w.prices)){hired=worker;break;}
  }
  const available=w.stock.bread;
  const people=[...w.workers,w.owner];
  let demand=0,sold=0;
  for(const p of people.sort((a,b)=>a.hunger-b.hunger)){
    const price=w.prices.bread;
    if(consumptionGain(p,{restore:40},price)<=0)continue;
    demand++;
    if(w.stock.bread<=0)continue;
    w.stock.bread--;p.gold-=price;w.owner.gold+=price;
    p.hunger=Math.min(100,p.hunger+40);sold++;
  }
  for(const p of people){
    p.hunger=Math.max(0,p.hunger-10);
    if(p!==hired)p.san=Math.min(100,p.san+10);
  }
  w.prices.bread=nextPrice(w.prices.bread,demand,available);
  return {hour:w.time,price:w.prices.bread,demand,supply:available,sold,
    hired:Boolean(hired),wagePaid:hired?w.wage:0,
    ownerGold:w.owner.gold,workerGold:w.workers.reduce((a,p)=>a+p.gold,0),
    totalGold:people.reduce((a,p)=>a+p.gold,0),
    zeroHunger:people.filter(p=>p.hunger===0).length};
}
function simulate(wage,hours=30){
  const w=newWorld(wage),history=[];
  for(let i=0;i<hours;i++)history.push(step(w));
  return {wage,hours,totalJobs:history.filter(x=>x.hired).length,
    totalWages:history.reduce((a,x)=>a+x.wagePaid,0),
    totalSales:history.reduce((a,x)=>a+x.sold,0),
    firstZeroHunger:history.find(x=>x.zeroHunger>0)?.hour??null,
    ending:history.at(-1),history};
}
if(require.main===module){
  console.log(JSON.stringify({noWage:simulate(0),wage3:simulate(3),
    wage6:simulate(6),buildings:BUILDINGS},null,2));
}
module.exports={BUILDINGS,workerGain,work,newWorld,step,simulate};
