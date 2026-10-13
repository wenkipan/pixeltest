"use strict";
/**
 * Six-building, multi-agent, hourly economy experiment.
 * All actions use known recipes, current prices, actual gold, hunger and SAN.
 * Wood, water, and electricity have FINITE initial reserves because no
 * production methods for those goods were supplied by the game designer.
 */
const {makeNpc,utility,chooseFood,nextPrice}=require("./sim");
const {BUILDINGS}=require("./payroll");
const ORDER=["farm","riceField","sand","ironMine","mill","bakery"];
const FOODS={bread:{restore:50},rice:{restore:30}};
const PRICES={barley:4,flour:8,bread:7,rice:4,cement:3,iron:3,wood:0,water:0,electricity:0};
function person(id,x={}){return makeNpc(id,{gold:6,hunger:65,san:85,alpha:1,beta:3,gamma:0.1,delta:0.97,...x});}
function create(opts={}){
 const w={hour:0,wage:opts.wage??3,k:opts.k??0.2,
  immigration:opts.immigration!==false,construction:opts.construction!==false,
  surplus:opts.surplus??0.5,raw:{water:3000,electricity:3000,wood:100},
  prices:{...PRICES},npcs:[],buildings:[],projects:[],births:0,birthsLog:[],buildLog:[]};
 const owners=ORDER.map(id=>person("owner-"+id,{gold:opts.ownerGold??90}));
 const workers=Array.from({length:opts.workers??9},(_,i)=>person("worker-"+i,{gold:opts.workerGold??3}));
 w.npcs=[...owners,...workers];
 w.initialGold=w.npcs.reduce((s,n)=>s+n.gold,0);
 w.buildings=ORDER.map((kind,i)=>({kind,owner:owners[i],stock:{}}));
 return w;
}
function total(w,good,owner){
 return w.buildings.reduce((s,b)=>s+(!owner||b.owner===owner?(b.stock[good]||0):0),0);
}
function value(w,items){return Object.entries(items).reduce((a,[g,q])=>a+q*w.prices[g],0);}
function workerValue(n,w,cost) {
 if(n.san<cost)return -Infinity;
 return utility(n,n.gold+w.wage,n.hunger,n.san-cost)-utility(n,n.gold,n.hunger,Math.min(100,n.san+10));
}
function hire(w,free,cost){
 let best=null,score=0;
 for(const n of free){const gain=workerValue(n,w,cost);if(gain>score){best=n;score=gain;}}
 return best;
}
function priceForInput(w,owner,item,qty){
 return item in w.raw?0:Math.max(0,qty-total(w,item,owner))*w.prices[item];
}
function affordable(w,owner,item,qty) {
 return item in w.raw?w.raw[item]>=qty:
  total(w,item)>=qty&&owner.gold+1e-8>=priceForInput(w,owner,item,qty);
}
function consumeInput(w,owner,item,qty,demand,stats){
 if(!affordable(w,owner,item,qty))return false;
 if(item in w.raw){w.raw[item]-=qty;return true;}
 let left=qty;
 const owners=w.buildings.filter(b=>b.owner===owner&&(b.stock[item]||0)>0);
 const others=w.buildings.filter(b=>b.owner!==owner&&(b.stock[item]||0)>0);
 demand[item]+=Math.max(0,qty-total(w,item,owner));
 for(const b of [...owners,...others]){
  const amount=Math.min(left,b.stock[item]);b.stock[item]-=amount;left-=amount;
  if(b.owner!==owner){let cost=amount*w.prices[item];owner.gold-=cost;b.owner.gold+=cost;stats.tradedGold+=cost;}
  if(!left)break;
 }
 if(left)throw Error("input inventory inconsistent");
 return true;
}
function work(w,free,demand,stats){
 // Topological flow: farmland -> mill -> bakery, alongside rice and minerals.
 for(const kind of ORDER)for(const b of w.buildings.filter(x=>x.kind===kind)){
  const r=BUILDINGS[kind];
  if(value(w,r.output)-value(w,r.input)-w.wage<=0)continue;
  const n=hire(w,free,r.san);
  if(!n)continue;
  const inputs=Object.entries(r.input);
  const cost=inputs.reduce((v,[item,qty])=>v+priceForInput(w,b.owner,item,qty),0);
  if(b.owner.gold+1e-8<cost+w.wage)continue;
  if(!inputs.every(([item,qty])=>affordable(w,b.owner,item,qty))){
   for(const [item,qty] of inputs)if(!(item in w.raw)){
    const shortage=Math.max(0,qty-total(w,item,b.owner));
    if(b.owner.gold+1e-8>=shortage*w.prices[item])demand[item]+=shortage;
   }
   continue;
  }
  for(const [item,qty]of inputs)consumeInput(w,b.owner,item,qty,demand,stats);
  b.owner.gold-=w.wage;n.gold+=w.wage;n.san-=r.san;
  free.splice(free.indexOf(n),1);stats.jobs++;stats.wages+=w.wage;
  stats.jobsByKind[kind]=(stats.jobsByKind[kind]||0)+1;
  for(const [g,q]of Object.entries(r.output)){
   b.stock[g]=(b.stock[g]||0)+q;
   stats.made[g]=(stats.made[g]||0)+q;
  }
 }
}
function annuity(owner,years=120){
 const dh=Math.pow(owner.delta,1/24);
 const r=1/dh-1;
 return r/(1-Math.pow(1+r,-years));
}
function considerBuild(w,owner) {
 if(w.projects.some(p=>p.owner===owner))return null;
 let best=null,score=0;
 for(const kind of ORDER){
  const r=BUILDINGS[kind],margin=value(w,r.output)-value(w,r.input)-w.wage;
  if(margin<=0)continue;
  const materials=Object.entries(r.build).filter(([k])=>k!=="laborHours");
  const cost=value(w,Object.fromEntries(materials))+r.build.laborHours*w.wage;
  if(owner.gold<cost)continue;
  if(!materials.every(([item,q])=>affordable(w,owner,item,q)))continue;
  const equiv=margin-cost*annuity(owner);
  const gain=utility(owner,owner.gold+equiv)-utility(owner);
  if(gain>score){score=gain;best={kind,owner,materials,hours:r.build.laborHours};}
 }
 return best;
}
function beginBuilds(w,demand,stats){
 if(!w.construction)return;
 for(const owner of w.npcs){
  const plan=considerBuild(w,owner);
  if(!plan)continue;
  const materialsCost=plan.materials.reduce((a,[k,q])=>a+priceForInput(w,owner,k,q),0);
  if(owner.gold+1e-8<materialsCost+plan.hours*w.wage)continue;
  if(!plan.materials.every(([k,q])=>affordable(w,owner,k,q)))continue;
  for(const [k,q]of plan.materials)consumeInput(w,owner,k,q,demand,stats);
  w.projects.push(plan);
  w.buildLog.push({hour:w.hour,kind:plan.kind,event:"start",owner:owner.id});
 }
}
function advanceBuilds(w,free,stats){
 const ongoing=[];
 for(const p of w.projects){
  const n=hire(w,free,10);
  if(!n||p.owner.gold<w.wage){ongoing.push(p);continue;}
  p.owner.gold-=w.wage;n.gold+=w.wage;n.san-=10;
  free.splice(free.indexOf(n),1);stats.jobs++;stats.wages+=w.wage;
  p.hours--;
  if(p.hours>0)ongoing.push(p);
  else {
   w.buildings.push({kind:p.kind,owner:p.owner,stock:{}});
   w.buildLog.push({hour:w.hour,kind:p.kind,event:"complete",owner:p.owner.id});
  }
 }
 w.projects=ongoing;
}
function eating(w,demand,stats){
 for(const n of [...w.npcs].sort((a,b)=>a.hunger-b.hunger)){
  const choice=chooseFood(n,FOODS,w.prices);
  if(!choice)continue;
  demand[choice.item]++;
  const b=w.buildings.find(x=>(x.stock[choice.item]||0)>0);
  if(!b)continue;
  const price=w.prices[choice.item];
  n.gold-=price;b.owner.gold+=price;b.stock[choice.item]--;
  n.hunger=Math.min(100,n.hunger+FOODS[choice.item].restore);
  stats.sold[choice.item]=(stats.sold[choice.item]||0)+1;
  stats.tradedGold+=price;
 }
}
function tick(w){
 w.hour++;
 const before=Object.fromEntries(Object.keys(w.prices).map(k=>[k,total(w,k)]));
 const demand=Object.fromEntries(Object.keys(w.prices).map(k=>[k,0]));
 const stats={jobs:0,wages:0,tradedGold:0,made:{},sold:{},jobsByKind:{}};
 const free=[...w.npcs];
 work(w,free,demand,stats);
 beginBuilds(w,demand,stats);
 advanceBuilds(w,free,stats);
 eating(w,demand,stats);
 for(const g of Object.keys(w.prices))
  if(!(g in w.raw))w.prices[g]=nextPrice(w.prices[g],demand[g],before[g]+(stats.made[g]||0),w.k);
 for(const n of w.npcs){
  n.hunger=Math.max(0,n.hunger-10);
  if(free.includes(n))n.san=Math.min(100,n.san+10);
 }
 const food=total(w,"bread")+total(w,"rice");
 if(w.immigration&&food>=w.surplus*w.npcs.length){
  const migrant=person("migrant-"+w.births,{gold:0});
  w.npcs.push(migrant);w.births++;
  w.birthsLog.push({hour:w.hour,food,population:w.npcs.length});
 }
 return {hour:w.hour,population:w.npcs.length,immigrants:w.births,
   food,starving:w.npcs.filter(n=>n.hunger===0).length,
   migrantsStarving:w.npcs.filter(n=>n.id.startsWith("npc-migrant-")&&n.hunger===0).length,
   totalGold:w.npcs.reduce((s,n)=>s+n.gold,0),
   buildings:w.buildings.length,working:stats.jobs,wages:stats.wages,tradedGold:stats.tradedGold,
   priceBread:w.prices.bread,priceRice:w.prices.rice,
   barley:stats.made.barley||0,flour:stats.made.flour||0,
   bread:stats.made.bread||0,rice:stats.made.rice||0,
   cement:stats.made.cement||0,iron:stats.made.iron||0,
   breadSold:stats.sold.bread||0,riceSold:stats.sold.rice||0};
}
function simulate(hours=120,options={}){
 const w=create(options);const history=[];
 for(let i=0;i<hours;i++)history.push(tick(w));
 const sum=k=>history.reduce((a,r)=>a+r[k],0);
 return {hours,options,initialGold:w.initialGold,population:w.npcs.length,
  immigrants:w.births,firstImmigrant:w.birthsLog[0]||null,
  buildings:w.buildings.length,
  completed:w.buildLog.filter(x=>x.event==="complete").length,
  buildingTypes:Object.fromEntries(ORDER.map(k=>[k,w.buildings.filter(b=>b.kind===k).length])),
  workHours:sum("working"),wagesPaid:sum("wages"),tradedGold:sum("tradedGold"),
  output:Object.fromEntries(["barley","flour","bread","rice","cement","iron"].map(k=>[k,sum(k)])),
  sales:{bread:sum("breadSold"),rice:sum("riceSold")},rawLeft:w.raw,
  birthEvents:w.birthsLog,buildEvents:w.buildLog,
  final:history.at(-1),history};
}
if(require.main===module) console.log(JSON.stringify({
 control:simulate(120,{immigration:false}),
 migration:simulate(120,{immigration:true})},null,2));
module.exports={create,tick,simulate,ORDER,PRICES,FOODS};
