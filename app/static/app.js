/* ═══════════════════════════════════════════════════════════════
   app.js — Essay Scoring Dashboard Logic
   ═══════════════════════════════════════════════════════════════ */

'use strict';

// ─── Chart instances ─────────────────────────────────────────────────────────
let radarChart = null;
let compareChart = null;

// ─── Word counter ─────────────────────────────────────────────────────────────
document.getElementById('essay-input').addEventListener('input', function () {
  const words = this.value.trim().split(/\s+/).filter(Boolean).length;
  document.getElementById('word-counter').textContent = `${words} word${words !== 1 ? 's' : ''}`;
});

document.getElementById('use-gpt-toggle').addEventListener('change', function () {
  document.getElementById('gpt-label').textContent = this.checked ? 'On (slower)' : 'Off';
});

// ─── Grade helper ─────────────────────────────────────────────────────────────
function getGrade(score) {
  if (score >= 85) return { label: 'Excellent', color: '#34d399' };
  if (score >= 70) return { label: 'Good', color: '#38bdf8' };
  if (score >= 55) return { label: 'Average', color: '#fbbf24' };
  if (score >= 40) return { label: 'Below Average', color: '#fb923c' };
  return { label: 'Needs Work', color: '#f87171' };
}

function starsHTML(n) {
  const full = '⭐'.repeat(n);
  const empty = '☆'.repeat(5 - n);
  return full + empty;
}

// ─── Score Ring animation ─────────────────────────────────────────────────────
function animateRing(score) {
  const circumference = 2 * Math.PI * 60; // r=60
  const offset = circumference * (1 - score / 100);
  const ring = document.getElementById('ring-fill');
  ring.style.strokeDasharray = circumference;
  ring.style.strokeDashoffset = circumference;
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      ring.style.strokeDashoffset = offset;
    });
  });
}

// ─── Number counter animation ─────────────────────────────────────────────────
function animateNumber(el, target, duration = 1200, decimals = 1) {
  const start = performance.now();
  function step(now) {
    const t = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - t, 3);
    el.textContent = (target * ease).toFixed(decimals);
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// ─── Bar fill animation ───────────────────────────────────────────────────────
function animateBar(id, pct) {
  const el = document.getElementById(id);
  setTimeout(() => { el.style.width = pct + '%'; }, 80);
}

// ─── Radar Chart ─────────────────────────────────────────────────────────────
function renderRadar(scores) {
  const ctx = document.getElementById('radar-chart').getContext('2d');
  if (radarChart) radarChart.destroy();

  radarChart = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['Grammar', 'Coherence', 'Relevance', 'Argument'],
      datasets: [{
        label: 'Essay Score',
        data: [
          scores.grammar,
          scores.coherence,
          scores.relevance,
          scores.argument_strength,
        ],
        backgroundColor: 'rgba(56,189,248,0.15)',
        borderColor: '#38bdf8',
        borderWidth: 2,
        pointBackgroundColor: '#818cf8',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointRadius: 5,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        r: {
          min: 0, max: 100,
          ticks: {
            stepSize: 25,
            color: '#475569',
            backdropColor: 'transparent',
            font: { size: 10 }
          },
          grid: { color: '#1e3048' },
          angleLines: { color: '#1e3048' },
          pointLabels: {
            color: '#94a3b8',
            font: { size: 12, family: 'Inter' }
          }
        }
      },
      plugins: {
        legend: { display: false },
      },
      animation: { duration: 1200 }
    }
  });
}

// ─── Model Comparison Table ───────────────────────────────────────────────────
async function loadComparison() {
  try {
    const res = await fetch('/compare');
    const data = await res.json();

    const tbody = document.getElementById('compare-tbody');
    tbody.innerHTML = '';

    const models = data.filter(d => d.QWK !== 'N/A');
    const colors = ['#fbbf24', '#38bdf8', '#c084fc'];
    const dotClasses = ['dot-lstm', 'dot-bert', 'dot-gpt'];
    const qwkVals = [];
    const pearsonVals = [];
    const labels = [];

    data.forEach((row, i) => {
      const isGPT = row.QWK === 'N/A';
      const qwkBest = !isGPT && parseFloat(row.QWK) === Math.max(...data.filter(d => d.QWK !== 'N/A').map(d => parseFloat(d.QWK)));

      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>
          <span class="model-tag">
            <span class="model-dot ${dotClasses[i]}"></span>
            ${row.model}
          </span>
        </td>
        <td class="${qwkBest ? 'val-best' : ''}">${isGPT ? '<span class="val-na">N/A</span>' : row.QWK}</td>
        <td>${isGPT ? '<span class="val-na">N/A</span>' : row.Pearson_r}</td>
        <td>${isGPT ? '<span class="val-na">N/A</span>' : row.RMSE}</td>
        <td>${row.speed}s/essay</td>
        <td>${row.params_M}M</td>
      `;
      tbody.appendChild(tr);

      if (!isGPT) {
        labels.push(row.model.split(' ')[0]);
        qwkVals.push(parseFloat(row.QWK));
        pearsonVals.push(parseFloat(row.Pearson_r));
      }
    });

    renderCompareChart(labels, qwkVals, pearsonVals);
  } catch (e) {
    console.error('Compare fetch failed:', e);
  }
}

function renderCompareChart(labels, qwkVals, pearsonVals) {
  const ctx = document.getElementById('compare-chart').getContext('2d');
  if (compareChart) compareChart.destroy();

  compareChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'QWK',
          data: qwkVals,
          backgroundColor: 'rgba(56,189,248,0.7)',
          borderColor: '#38bdf8',
          borderWidth: 1,
          borderRadius: 6,
        },
        {
          label: 'Pearson r',
          data: pearsonVals,
          backgroundColor: 'rgba(129,140,248,0.7)',
          borderColor: '#818cf8',
          borderWidth: 1,
          borderRadius: 6,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          ticks: { color: '#94a3b8', font: { family: 'Inter' } },
          grid: { color: '#1e3048' }
        },
        y: {
          min: 0, max: 1,
          ticks: { color: '#94a3b8', font: { family: 'Inter', size: 10 } },
          grid: { color: '#1e3048' }
        }
      },
      plugins: {
        legend: {
          labels: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
        }
      },
      animation: { duration: 1000 }
    }
  });
}

// ─── Main Scoring function ────────────────────────────────────────────────────
async function scoreEssay() {
  const essay = document.getElementById('essay-input').value.trim();
  const prompt = document.getElementById('prompt-input').value.trim();
  const useGpt = document.getElementById('use-gpt-toggle').checked;
  const errEl = document.getElementById('error-msg');

  errEl.style.display = 'none';
  errEl.textContent = '';

  if (!essay || essay.split(/\s+/).filter(Boolean).length < 5) {
    errEl.textContent = '⚠️ Please enter an essay with at least 5 words.';
    errEl.style.display = 'block';
    return;
  }

  // Loading state
  const btn = document.getElementById('submit-btn');
  const spinner = document.getElementById('spinner');
  const btnText = document.getElementById('btn-text');
  btn.disabled = true;
  spinner.style.display = 'block';
  btnText.textContent = useGpt ? 'Loading AI Model (first time only)...' : 'Analyzing...';

  try {
    const res = await fetch('/score', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ essay, prompt, use_gpt: useGpt })
    });

    const data = await res.json();
    if (!res.ok || data.error) throw new Error(data.error || 'Server error');

    renderResults(data);
  } catch (err) {
    errEl.textContent = '❌ ' + err.message;
    errEl.style.display = 'block';
  } finally {
    btn.disabled = false;
    spinner.style.display = 'none';
    btnText.textContent = '⚡ Score Essay';
  }
}

function renderResults(data) {
  // ── Holistic Score ──
  const score = data.holistic_score;
  const grade = getGrade(score);
  document.getElementById('score-placeholder').style.display = 'none';
  const scoreDisplay = document.getElementById('score-display');
  scoreDisplay.style.display = 'flex';

  const numEl = document.getElementById('score-number');
  numEl.textContent = '0';
  numEl.style.webkitTextFillColor = 'transparent';
  animateNumber(numEl, score, 1400, 1);
  animateRing(score);

  const stars = data.stars || Math.min(5, Math.max(1, Math.round(score / 20)));
  document.getElementById('score-stars').innerHTML = starsHTML(stars);
  const gradeEl = document.getElementById('score-grade');
  gradeEl.textContent = grade.label;
  gradeEl.style.color = grade.color;

  // ── Rubric Bars ──
  document.getElementById('rubric-placeholder').style.display = 'none';
  document.getElementById('rubric-bars').style.display = 'flex';

  const r = data.rubric_scores;
  [
    ['grammar', 'b-grammar', 'v-grammar'],
    ['coherence', 'b-coherence', 'v-coherence'],
    ['relevance', 'b-relevance', 'v-relevance'],
    ['argument_strength', 'b-argument', 'v-argument'],
  ].forEach(([key, barId, valId]) => {
    animateBar(barId, r[key]);
    document.getElementById(valId).textContent = r[key].toFixed(1) + '%';
  });

  // ── Radar ──
  document.getElementById('radar-placeholder').style.display = 'none';
  document.getElementById('radar-container').style.display = 'block';
  renderRadar(r);

  // ── Features ──
  document.getElementById('features-placeholder').style.display = 'none';
  document.getElementById('features-grid').style.display = 'grid';
  const f = data.features;
  document.getElementById('f-words').textContent = f.word_count;
  document.getElementById('f-sents').textContent = f.sentence_count;
  document.getElementById('f-avglen').textContent = f.avg_sentence_length.toFixed(1);
  document.getElementById('f-vocab').textContent = (f.vocab_richness * 100).toFixed(0) + '%';
  document.getElementById('f-discourse').textContent = f.discourse_markers;
  document.getElementById('f-errors').textContent = f.grammar_errors;

  // ── Feedback ──
  console.log('Feedback data:', data.feedback); // Debug log
  document.getElementById('feedback-placeholder').style.display = 'none';
  document.getElementById('feedback-box').style.display = 'block';

  // Populating detailed errors
  const errList = data.features.grammar_error_list || [];
  const errContainer = document.getElementById('error-list-container');
  const errUl = document.getElementById('grammar-error-list');
  errUl.innerHTML = '';

  if (errList.length > 0) {
    errContainer.style.display = 'block';
    errList.forEach(err => {
      const li = document.createElement('li');
      li.style.color = '#f87171'; // Red-ish
      li.style.marginBottom = '0.4rem';
      li.style.fontSize = '0.9rem';
      li.innerHTML = `<span style="margin-right:0.5rem">🚩</span> ${err}`;
      errUl.appendChild(li);
    });
  } else {
    errContainer.style.display = 'none';
  }

  // Display feedback immediately (no animation)
  const feedbackEl = document.getElementById('feedback-text');
  if (data.feedback) {
    const formatted = data.feedback
      .replace(/\[!\]/g, '<br/><span style="color:#fbbf24">⚠️</span>')
      .replace(/\*\*Specific Suggestions:\*\*/g, '<br/><br/><strong style="color:#94a3b8">Specific Suggestions:</strong>')
      .replace(/\n/g, '<br/>');
    feedbackEl.innerHTML = formatted;
    feedbackEl.style.opacity = '1';
  } else {
    feedbackEl.innerHTML = '<span style="color:#f87171">No feedback available</span>';
  }
}

// Typewriter animation for feedback
function typeWriter(el, text, speed = 20) {
  // Convert markdown-style warnings to colored spans
  const formatted = text
    .replace(/⚠️ (Grammar|Coherence|Relevance|Argument):/g,
      '<br/><br/><span class="highlight">⚠️ $1:</span>')
    .replace(/\*\*Specific Suggestions:\*\*/g,
      '<br/><strong style="color:var(--text-dim)">Specific Suggestions:</strong>');

  let i = 0;
  const stripped = text;
  // Use innerHTML approach — render instantly then fade in
  el.style.opacity = '0';
  el.innerHTML = formatted;
  el.style.transition = 'opacity 0.5s';
  setTimeout(() => { el.style.opacity = '1'; }, 50);
}

// Submit on Ctrl+Enter
document.getElementById('essay-input').addEventListener('keydown', function (e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') scoreEssay();
});

// ─── On load ──────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  loadComparison();
});
