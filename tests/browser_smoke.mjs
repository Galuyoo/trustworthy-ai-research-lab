// Browser verification for the local Streamlit app; no third-party requests allowed.
import {createRequire} from 'node:module';
import {spawn} from 'node:child_process';
import {mkdir,writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {dirname,resolve} from 'node:path';
const require=createRequire(import.meta.url);
const {chromium:pw}=require('playwright');
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const out=process.env.LAB_QA_OUTPUT || root+'/browser-results';
await mkdir(out,{recursive:true});
const server=spawn(process.env.LAB_PYTHON || 'python',['-m','streamlit','run','streamlit_app.py','--server.port','8503','--server.address','127.0.0.1'],{cwd:root,stdio:['ignore','pipe','pipe']});
let log='',browser;
server.stdout.on('data',d=>log+=d);server.stderr.on('data',d=>log+=d);
const report={status:'running',resolutions:[],externalRequests:[],pageErrors:[],timingsMs:[],recording:null};
try{
 let ready=false;for(let i=0;i<60;i++){try{if((await fetch('http://127.0.0.1:8503/_stcore/health')).ok){ready=true;break;}}catch{}await new Promise(r=>setTimeout(r,250));}assert(ready);
 for(const size of [{name:'desktop',width:1440,height:1000},{name:'projector',width:1280,height:720},{name:'mobile',width:390,height:844}]){
  browser=await pw.launch({headless:true});
  const context=await browser.newContext({viewport:{width:size.width,height:size.height},deviceScaleFactor:1,reducedMotion:size.name==='mobile'?'reduce':'no-preference'});
  await context.route('**/*',route=>{if(new URL(route.request().url()).hostname!=='127.0.0.1'){report.externalRequests.push(route.request().url());return route.abort();}return route.continue();});
  const page=await context.newPage();page.on('pageerror',e=>report.pageErrors.push(String(e)));
  const text=t=>page.getByText(t,{exact:true}), button=t=>page.getByRole('button',{name:t,exact:true});
  const range=label=>page.getByTestId('stSlider').filter({hasText:label}).locator('input[type=range]');
  const idle=async()=>{await page.waitForTimeout(350);assert.equal(await page.getByTestId('stException').count(),0);};
  const screen=async name=>{await idle();await page.locator('[data-testid="stMain"]').evaluate(el=>el.scrollTop=0);await page.screenshot({path:out+'/'+name+'_'+size.name+'.png'});};
  const overflow=async()=>assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2),false);
  await page.goto('http://127.0.0.1:8503');await button('Begin the night →').waitFor();await idle();
  // A finite, meaningful signal animation; the OS setting disables it too.
  if(size.name==='mobile'){
   assert(await page.evaluate(()=>matchMedia('(prefers-reduced-motion: reduce)').matches));
   assert.equal(await page.locator('.hero-visual img').count(),1);
  }
  await screen('Introduction');await overflow();
  console.log(size.name+': introduction rendered');
  await button('Begin the night →').click();await text('The minimum service is feasible').waitFor();await idle();
  assert.equal(await page.getByRole('tab',{name:'1 · Energy',exact:true}).getAttribute('aria-selected'),'true');
  await screen('Energy');
  await button('Close call').click();await text('+6 Wh').waitFor();await idle();
  assert.equal(await range('Conservative planning reserve (%)').inputValue(),'10');
  const began=Date.now();
  await range('Conservative planning reserve (%)').focus();
  for(let i=0;i<5;i++)await page.keyboard.press('ArrowRight');
  await text('The reserve makes this plan infeasible').waitFor();await text('-5 Wh').waitFor();
  report.timingsMs.push({size:size.name,action:'reserve_10_to_15',ms:Date.now()-began});
  await idle();assert.equal(await range('Conservative planning reserve (%)').inputValue(),'15');
  await button('Impossible').click();await text('Not enough energy—even at the minimum').waitFor();
  await range('Conservative planning reserve (%)').press('Home');await text('Even with zero reserve: 72 Wh short').waitFor();
  await range('Move through the simulated night (%)').press('End');await text('Dawn · service missed').waitFor();
  await range('Move through the simulated night (%)').press('ArrowLeft');await text('Minimum service missed').waitFor();await idle();
  assert.equal(await range('Move through the simulated night (%)').inputValue(),'99');
  await screen('Unserved_night');
  await page.getByText('See the full night · brightness & remaining energy',{exact:true}).click();
  await page.getByTestId('stVegaLiteChart').filter({visible:true}).first().waitFor();
  await page.getByText('See the full night · brightness & remaining energy',{exact:true}).evaluate(el=>el.scrollIntoView({block:'start'}));await idle();
  await page.screenshot({path:out+'/Energy_curves_'+size.name+'.png'});
  await button('Follow the measurement →').click();await text('Reveal the verdict').waitFor();await idle();
  await text('Reveal the verdict').click();await page.getByText('The rules disagree.',{exact:false}).waitFor();await idle();
  assert(await page.getByRole('switch',{name:'Reveal the verdict',exact:true}).isChecked());
  const times=await page.getByTestId('stSlider').filter({visible:true}).locator('input[type=range]').evaluateAll(es=>es.map(e=>({value:e.value,label:e.getAttribute('aria-valuetext')})));
  assert.equal(times.length,3);
  await screen('Evidence');await overflow();
  await button('Receive at cutoff').click();await page.getByText('The rules agree: both timestamps pass',{exact:false}).waitFor();await idle();
  await range('Actual receipt time').press('ArrowRight');await page.getByText('The rules disagree.',{exact:false}).waitFor();await idle();
  await button('← Return to the lighting plan').click();await idle();
  assert.equal(await range('Available battery energy (Wh)').inputValue(),'120');
  assert.equal(await range('Conservative planning reserve (%)').inputValue(),'0');
  assert.equal(await range('Move through the simulated night (%)').inputValue(),'99');
  await page.getByRole('tab',{name:'2 · Evidence',exact:true}).click();await idle();
  assert(await page.getByRole('switch',{name:'Reveal the verdict',exact:true}).isChecked());
  await page.getByText('A second trap · what was issued then, and what is reconstructed later?',{exact:true}).click();
  await text('Use the later reconstructed input').click();await text('1 pp').waitFor();await idle();
  assert(await page.getByRole('switch',{name:'Use the later reconstructed input',exact:true}).isChecked());
  await page.getByText('Actual research · fixed historical audit results',{exact:true}).click();
  for(const count of ['184/782','126/782','345/348'])await text(count).waitFor();
  await page.getByText('Actual research · fixed historical audit results',{exact:true}).evaluate(el=>el.scrollIntoView({block:'start'}));await idle();
  await page.screenshot({path:out+'/Research_'+size.name+'.png'});await overflow();
  await button('↺ Reset evidence').click();await idle();
  assert.equal(await page.getByRole('switch',{name:'Reveal the verdict',exact:true}).isChecked(),false);
  assert.equal(await page.getByRole('switch',{name:'Use the later reconstructed input',exact:true}).isChecked(),false);
  await button('↺ Start over').click();await idle();
  assert.equal(await page.getByRole('tab',{name:'The system',exact:true}).getAttribute('aria-selected'),'true');
  await page.getByRole('tab',{name:'1 · Energy',exact:true}).click();await idle();
  assert.equal(await range('Available battery energy (Wh)').inputValue(),'480');
  assert.equal(await range('Move through the simulated night (%)').inputValue(),'35');
  await text('Presentation mode').click();await idle();
  assert.equal(await page.getByRole('switch',{name:'Presentation mode',exact:true}).isChecked(),false);
  await page.getByTestId('stVegaLiteChart').filter({visible:true}).first().waitFor();
  assert.equal(await range('Available battery energy (Wh)').inputValue(),'480');
  report.resolutions.push({...size,status:'passed',statePreserved:true,resetsPassed:true,cutoffCrossingPassed:true,overflow:false,reducedMotion:size.name==='mobile'});
  console.log(size.name+': all interaction checks passed');
  await browser.close();browser=undefined;
 }
 report.status='passed';
}catch(e){report.status='failed';report.error=String(e);console.error(e);console.error(log);process.exitCode=1;}
finally{if(browser)await browser.close();server.kill('SIGTERM');await writeFile(out+'/browser_test_results.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));}
