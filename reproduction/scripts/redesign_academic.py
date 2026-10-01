from pathlib import Path
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1]
p=R/'site/index.html';s=BeautifulSoup(p.read_text(),'html.parser')
def fragment(html):return BeautifulSoup(html,'html.parser')
s.title.string='HarnessEval-W: Agentifying the Evaluation of Visual Worlds | Reproduction Study'
s.header.replace_with(fragment('''<header><a class="brand" href="#">HarnessEval-W</a><nav aria-label="Project sections"><a href="#overview">Overview</a><a href="#method">Method</a><a href="#workbench">Evaluation</a><a href="#construction">Dataset</a><a href="#laboratory">Experiments</a><a href="#reproduction">Reproducibility</a></nav><a class="source-link" href="https://github.com/hellomuffin/harnesseval-w-visual-lab">Repository</a></header>'''))
s.select_one('.hero').replace_with(fragment('''
<section class="project-heading">
  <h1>HarnessEval-W: Agentifying the<br class="desktop-break"> Evaluation of Visual Worlds</h1>
  <p class="authors"><a href="https://mirros-lab.github.io/HarnessEval-W/">MirroS Team</a></p>
  <p class="publication">arXiv:2608.16859 · 2026</p>
  <div class="resource-links"><a href="https://arxiv.org/abs/2608.16859">Paper</a><a href="https://github.com/MirroS-Lab/HarnessEval-W">Official Code</a><a href="https://huggingface.co/datasets/MirroS-Lab/HarnessEval-W">Dataset</a><a href="https://github.com/hellomuffin/harnesseval-w-visual-lab">Reproduction Code</a></div>
  <p class="reproduction-label">Independent reproduction study and interactive supplementary material</p>
</section>
<section id="overview" class="overview-section">
  <h2>Overview</h2>
  <p class="abstract">HarnessEval-W evaluates interactive world models through <strong>case-specific skill routing and hierarchical agentic evaluation</strong>. It organizes evaluation into three axes: Observation Quality, Transition Correctness, and World Persistence. Given an initial observation and an action specification, the harness selects specialized skills, collects visual and numerical evidence from the generated rollout, and aggregates the results into interpretable scores.</p>
  <div class="scope-note"><b>Scope of this reproduction.</b> We re-evaluate six released Seedance 2.0 Standard videos, execute all 11 skills on benchmark videos or controlled fixtures, and generate an additional Wan 2.2 rollout. Semantic evaluation uses Qwen3-VL-8B in place of the authors’ judge. The full 330-case, 18-model study and human-preference analysis are not reproduced.</div>
  <figure class="teaser-figure"><div class="teaser-content"><video id="hero-video" muted autoplay loop playsinline controls aria-label="Intentional-transition benchmark rollout"></video><div class="teaser-description"><span class="tiny-label">Representative evaluation case</span><h3>Intentional Transition Correctness</h3><dl><dt>Input</dt><dd>Initial observation and text-based state-change instruction</dd><dt>Rollout</dt><dd>Author-supplied Seedance 2.0 Standard generation</dd><dt>Evaluation</dt><dd>Target visibility, action execution, final state, and protected-anchor preservation</dd></dl><a href="#workbench" class="text-link">View the evaluation trace →</a></div></div><figcaption><b>Figure 1.</b> An intentional-transition case. Evaluation assesses the requested state change and preservation of the surrounding scene; visual plausibility alone is insufficient.</figcaption></figure>
</section>
<section id="method" class="section method-section">
  <div class="section-heading"><div><h2>Hierarchical Agentic Evaluation</h2><p>Case-conditioned routing combines specialized VLM judgments with pretrained visual metrics.</p></div><a class="text-link" href="https://arxiv.org/html/2608.16859v2#S3">Paper §3</a></div>
  <figure class="method-figure"><div class="method-pipeline"><div class="method-node"><span>Case specification</span><b>Initial observation + action</b><small>Target entities, expected outcomes, protected anchors</small></div><span class="method-arrow" aria-hidden="true">→</span><div class="method-node"><span>Skill routing</span><b>Case-specific evaluation plan</b><small>Core, observation, and diagnostic skills</small></div><span class="method-arrow" aria-hidden="true">→</span><div class="method-node method-execution"><span>Skill execution</span><b>Analyze → Verify</b><small>Expected specification → eight semantic judgments</small><hr><b>Numerical backends</b><small>Visual quality, motion, geometry, and persistence</small></div><span class="method-arrow" aria-hidden="true">→</span><div class="method-node"><span>Score aggregation</span><b>Evidence and case scores</b><small>Core-skill mean + observation-quality mean</small></div></div><figcaption><b>Figure 2.</b> Evaluation flow in the released implementation. Semantic skills use one Analyze call and one Verify call containing eight judgments; numerical skills invoke specialized models or deterministic checks. This execution structure differs from independent per-question verifier agents.</figcaption></figure>
  <h3 class="subsection-title">Evaluation Axes and Settings</h3>
  <div class="axis-map"><article><h4>Observation Quality</h4><p>Evaluated across all probe families.</p><ul><li>Render Quality <span>Obs-R</span></li><li>Physical Observation Quality <span>Obs-P</span></li></ul></article><article><h4>Transition Correctness</h4><p>State updates under interventions.</p><ul><li>Exploratory Transition <span>Trans-E</span></li><li>Intentional Transition <span>Trans-I</span></li><li>Physical Transition <span>Trans-P</span></li></ul></article><article><h4>World Persistence</h4><p>State consistency over time and viewpoint changes.</p><ul><li>Drift Resistance <span>Pers-D</span></li><li>Revisit Consistency <span>Pers-R</span></li><li>Offscreen Evolution <span>Pers-O</span></li></ul></article></div>
</section>
'''))
for selector in ['.intro-strip','main > .axis-map']:
 node=s.select_one(selector)
 if node:node.decompose()
# Replace section headings and descriptions, keeping all experimental controls intact.
sections={
 'workbench':('Benchmark Cases and Evaluation Traces','Six released rollouts, one from each probe family. Compare the independent rerun with the authors’ recorded evaluation.'),
 'construction':('Agentic Benchmark Construction','Scene sampling, initial-observation generation, grounded action planning, and case validation.'),
 'laboratory':('Controlled Experiments','Evaluate sensitivity to temporal interventions, physical-law violations, and changes in semantic judgments.'),
 'reproduction':('Reproducibility Results and Limitations','Execution coverage, score comparisons, implementation discrepancies, and the scope of claims supported by this reproduction.')}
for key,(title,desc) in sections.items():
 node=s.find(id=key);node.select_one('h2').string=title;node.select_one('.section-heading p').string=desc
 for e in node.select('.section-heading .eyebrow'):e.decompose()
skill=s.select_one('.skill-section');skill['id']='skills';skill.select_one('h2').string='Specialized Evaluation Skills';skill.select_one('.section-heading p').string='The released registry contains 11 skills. Select a skill to inspect its evaluation objective, backend, and execution coverage.'
for e in skill.select('.eyebrow'):e.decompose()
replacements={
 'View initial world ↗':'Initial observation', 'REQUESTED ACTION':'Action specification',
 'SAMPLED HERE FROM THE REAL VIDEO · CLICK A FRAME TO SEEK':'Rollout frame samples · select a timestamp to seek',
 'EVIDENCE EXPLORER':'Evaluation trace','Fresh local run':'Independent rerun','Author-supplied run':'Released evaluation',
 '1 Route':'Skill routing','2 Analyze':'Analyze','3 Verify':'Verify','4 Grade':'Aggregation',
 'Sample a scene':'Structured scene sampling','Materialize the world':'Initial-observation generation',
 'Plan a grounded action':'Grounded action planning','Validate before admission':'Case validation',
 'TRY THE LOCAL VALIDATOR':'Case-validation experiment','Change the action. Keep the initial world.':'Validation under alternative action specifications',
 'The 100-case public set':'Public Benchmark Subset (100 Cases)',
 'How much does visibility matter?':'Intentional-Change Score Aggregation',
 'Original vs. frozen vs. reversed':'Temporal Intervention Controls',
 'Can the semantic judge detect a missing or reversed action? The controlled videos are derived from the same mug rollout.':'Original, frame-frozen, and temporally reversed versions of the same mug rollout are evaluated with the same semantic protocol.',
 'What-if input · not a new VLM judgment':'User-specified judgments · deterministic aggregation',
 'FRESH EXECUTION':'Independent execution','Agreement with human preferences':'Human-Preference Alignment',
 'CHECK THE IMPLEMENTATION':'Implementation analysis','Where the release differs':'Paper–Implementation Discrepancies',
 'Two semantic calls.':'Semantic evaluation architecture.', 'Physics has a coverage limit.':'Physical-law coverage.',
 'Physical observation differs.':'Physical-observation aggregation.', 'Six is not 330.':'Dataset coverage.',
 'Open execution receipts, sources and reproduction commands':'Execution Records and Reproduction Protocol',
 'Download audit ↓':'Download Reproduction Report',
 'A single example can expose a failure. It cannot establish population accuracy or reproduce the paper’s 5,000 human A/B judgments.':'These controlled examples characterize evaluator behavior. They do not estimate population-level accuracy or reproduce the 5,000 human pairwise judgments reported in the paper.'}
for text in list(s.find_all(string=True)):
 old=str(text)
 for a,b in replacements.items():old=old.replace(a,b)
 if old!=str(text):text.replace_with(old)
# A compact experimental protocol makes the comparison conditions explicit.
s.find(id='workbench').select_one('.section-heading').insert_after(fragment('''<div class="protocol-note"><b>Comparison protocol.</b> Both runs evaluate the same released videos. New routing plans are generated independently, while metric execution uses the released plans to hold the selected evaluation tasks fixed. The rerun substitutes Qwen3-VL-8B for the semantic judge and uses documented runtime adaptations.</div>'''))
s.footer.replace_with(fragment('''<footer><p><b>HarnessEval-W — Independent Reproduction Study</b><br>Original research and released benchmark assets: MirroS Team. Model substitutions and reproduction limits are documented above.</p><a href="https://github.com/hellomuffin/harnesseval-w-visual-lab">Source and execution artifacts</a></footer>'''))
s.main.append(fragment('''<section id="citation" class="section citation-section"><h2>Citation</h2><p>Please cite the original paper when referring to HarnessEval-W.</p><pre>@article{mirros2026harnessevalw,
  title   = {HarnessEval-W: Agentifying the Evaluation of Visual Worlds},
  author  = {{MirroS Team}},
  journal = {arXiv preprint arXiv:2608.16859},
  year    = {2026}
}</pre><p><a href="https://mirros-lab.github.io/HarnessEval-W/">Official project page</a> · <a href="https://arxiv.org/abs/2608.16859">arXiv record</a> · <a href="https://github.com/hellomuffin/harnesseval-w-visual-lab">Independent reproduction repository</a></p></section>'''))
p.write_text(str(s))
# Revise dynamic interface copy as well as static headings.
changes={
 'Choose the questions first.':'Case-Specific Skill Routing',
 'Define what success would look like.':'Expected-Specification Analysis',
 'Inspect the evidence.':'Semantic and Numerical Verification',
 'Keep the verdict decomposable.':'Case-Level Score Aggregation',
 'A new world, a grounded test':'Constructed Intentional-Transition Case',
 'A new world-model rollout, end to end.':'Image-to-Video Generation and Semantic Evaluation',
 'The accepted case above becomes an actual image-to-video model input. Watch what the model did, then inspect the released semantic grader’s judgment.':'The validated case is evaluated end to end: image-to-video generation with Wan 2.2 TI2V 5B, followed by the released Analyze–Verify semantic evaluation protocol.',
 'Same clips. Two grading protocols.':'WBench Protocol Comparison',
 'Do the scores survive a local rerun?':'Released Scores and Independent Rerun',
 'SAME VIDEOS · TWO EVALUATIONS':'Matched-rollout comparison',
 'A REAL REFERENCE / RETURN FRAME PAIR':'Reference–return frame correspondence',
 'real bundled rollouts decoded':'released rollouts evaluated',
 'fresh numeric task results':'numerical skill evaluations',
 'public cases downloaded':'public benchmark cases',
 'Inspect actual expected specifications, eight judgments, diagnostics, sampled frames and deterministic aggregation. A written reason is inspectable evidence, not proof of correctness.':'The exported traces expose expected specifications, eight semantic judgments, sampled frames, diagnostics, and deterministic aggregation. Explanatory text alone does not validate judgment accuracy.',
 'Real Analyze/Verify calls run':'Analyze/Verify inference is executed',
 'Our three-clip protocol check above is real, but':'The three-clip protocol comparison above is executed independently, but',
 'Inspect what the validator accepted and rejected.':'Case-Validation Outcomes',
 'These are saved model executions. This hosted site does not run a GPU or send your input to a model.':'Recorded VLM judgments for accepted and rejected case proposals. Results are from GPU execution; the hosted interface does not initiate new inference.',
 'NEW CASE · RECONSTRUCTED PIPELINE':'Reconstructed construction pipeline',
 'GENERATED ON A LOCAL GPU':'Independent image-to-video generation',
 'FRESH INTENTIONAL-CHANGE GRADE':'Intentional-change semantic score',
 'RECORDED LOCAL GPU VALIDATION':'Recorded validation experiment',
 'fresh local judge':'independent semantic evaluation',
 'Three independent local evaluations':'Repeated-Evaluation Consistency',
 'What-if input':'User-specified judgments',
 'New initial world':'Generated initial observation',
 'New local planner output':'Independent routing plan',
 'Shipped case plan':'Released routing plan',
 'Fresh inference · local Qwen3-VL-8B + pretrained metric backends · bundled video':'Independent rerun · Qwen3-VL-8B and pretrained metric backends · released rollout',
 'Author-supplied cached evidence · not independently generated here':'Released evaluation · author-supplied cached evidence',
 'Fresh numeric evidence from the core skill’s tools.':'Numerical outputs from the primary evaluation skill.',
 'Worlds under examination':'HarnessEval-W reproduction study'
}
for path in [R/'site/app.js',R/'scripts/export_pages.py']:
 text=path.read_text()
 for a,b in changes.items():text=text.replace(a,b)
 # Remove decorative indices from the case and skill menus.
 text=text.replace('<span>0${i+1}</span>','').replace('<span class="skill-no">${String(i+1).padStart(2,\'0\')}</span>','')
 path.write_text(text)
