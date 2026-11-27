import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const html = readFileSync(new URL('../assets/Adaptive_Energy_Management_Simulator.html', import.meta.url), 'utf8');
const script = html.split('<script>')[1].split('</script>')[0];

function simulator() {
  // Load the actual standalone script, with a lightweight DOM and manual clock.
  const element = () => ({
    addEventListener() {}, setAttribute() {}, removeAttribute() {},
    classList: {toggle() {}, contains: () => false},
    style: {}, dataset: {}, getBoundingClientRect: () => ({width: 1100, height: 255}),
    value: '1',
  });
  const elements = new Map();
  const lookup = key => {
    if (!elements.has(key)) elements.set(key, element());
    return elements.get(key);
  };
  const context = vm.createContext({
    document: {querySelector: lookup, getElementById: id => lookup('#' + id), querySelectorAll: () => []},
    window: {addEventListener() {}}, matchMedia: () => ({matches: false}),
    requestAnimationFrame: () => 1, cancelAnimationFrame() {},
  });
  const exposed = script.replace('renderLegend();\nreset();\n})();', `
    globalThis.sim = {
      beginPlay, nextStage, tick, togglePause, scenarioChanged, compare,
      define(overrides) { Object.assign(state, overrides); },
      run: () => rolling,
      view: () => playView(lastResults),
      summary: () => lastResults,
    };
  })();`);
  assert.notEqual(exposed, script);
  vm.runInContext(exposed, context);
  return context.sim;
}

test('Mixed starts at 68% and derives the two reference nights in order', () => {
  const sim = simulator();
  sim.beginPlay();
  assert.equal(sim.run().round.candidate, undefined);
  assert.equal(sim.view().cutoff, 0);
  assert.equal(sim.view().forecast, null);
  sim.nextStage();
  assert.equal(sim.run().round.candidate.dawn, 49);
  assert.equal(sim.run().round.candidate.dusk, 94);
  assert.equal(sim.view().cutoff, 0);
  sim.nextStage();
  assert.equal(sim.run().round.choice.loss, 32);
  assert.equal(sim.run().round.prediction.dawn, 36);
  assert.equal(sim.run().round.prediction.dusk, 81);
  assert.equal(sim.run().round.outcomes, undefined);
  sim.nextStage();
  assert.equal(sim.view().cutoff, 1);
  assert.equal(sim.run().round.outcomes.adaptive.dawn, 36);
  sim.nextStage();
  assert.equal(sim.view().cutoff, 2);
  assert.equal(sim.run().round.outcomes.adaptive.dusk, 81);
  assert.equal(sim.view().forecast, null);
  sim.nextStage();
  assert.equal(sim.run().round.starts.adaptive, 81);
  sim.nextStage();
  sim.nextStage();
  assert.equal(sim.run().round.choice.loss, 21);
  assert.equal(sim.run().round.prediction.dawn, 60);
  assert.equal(sim.run().round.prediction.dusk, 70);
});

test('Every rolling strategy produces the same checkpoints and loss as its static comparison', () => {
  for (const gains of [[45,10,38,8,34,16], [12,5,8,4,7,10], [43,46,40,50,42,37]]) {
    const sim = simulator();
    sim.define({gains});
    sim.beginPlay();
    const staticResults = sim.compare();
    for (let night = 0; night < gains.length; night++) {
      sim.nextStage(); sim.nextStage(); sim.nextStage();
      for (const key of Object.keys(staticResults)) {
        assert.deepEqual(sim.run().round.outcomes[key], staticResults[key].entries[night]);
      }
      sim.nextStage(); sim.nextStage();
    }
    assert.equal(sim.run(), null);
    assert.deepEqual(sim.summary(), staticResults);
  }
});

test('Conservative forecast reduction affects predictions and preserves the realised gain', () => {
  const sim = simulator();
  sim.define({haircut: 10});
  sim.beginPlay();
  sim.nextStage(); sim.nextStage();
  assert.equal(sim.run().round.expected, 35);
  assert.equal(sim.run().round.prediction.dusk, 71);
  sim.nextStage(); sim.nextStage();
  assert.equal(sim.run().round.outcomes.adaptive.dusk, 81);
});

test('Minimum lighting and reserve conflicts survive forecast and simulation', () => {
  const sim = simulator();
  sim.define({initial: 20, reserve: 20, minLoss: 25, gains: [12,5,8,4,7,10]});
  sim.beginPlay();
  sim.nextStage(); sim.nextStage();
  assert.equal(sim.run().round.choice.conflict, true);
  assert.equal(sim.run().round.choice.loss, 25);
  assert.equal(sim.run().round.prediction.dawn, 0);
  sim.nextStage();
  assert.equal(sim.run().round.outcomes.adaptive.dawn, 0);
});

test('Pause freezes time and scenario edits discard predictions and playback', () => {
  const sim = simulator();
  sim.beginPlay();
  sim.tick(0); sim.tick(500);
  sim.togglePause();
  sim.tick(12000);
  assert.equal(sim.run().stage, 0);
  assert.equal(sim.run().elapsed, 500);
  sim.togglePause();
  sim.tick(14000); sim.tick(15600);
  assert.equal(sim.run().stage, 1);
  sim.scenarioChanged();
  sim.tick(20000);
  assert.equal(sim.run(), null);
  assert.equal(sim.view().forecast, null);
  assert.equal(sim.view().cutoff, 12);
});

test('Normal speed progresses through six complete nights in 66 seconds of stage time', () => {
  const sim = simulator();
  sim.beginPlay();
  const durations = [2000, 2000, 3000, 2000, 2000];
  let now = 0;
  for (let night = 0; night < 6; night++) {
    for (let stage = 0; stage < durations.length; stage++) {
      assert.equal(sim.run().night, night);
      assert.equal(sim.run().stage, stage);
      sim.tick(now);
      sim.tick(now + durations[stage] - 1);
      assert.equal(sim.run().stage, stage);
      now += durations[stage];
      sim.tick(now);
    }
  }
  assert.equal(now, 66000);
  assert.equal(sim.run(), null);
  assert.equal(sim.view().cutoff, 12);
});
