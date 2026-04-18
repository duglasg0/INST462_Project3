"""
Hit Song Probability Builder
Based on Spotify Wrapped 2025 Top 50 data.

Run with:
    pip install flask
    python hit_song_probability_builder.py

Then open http://localhost:5000 in your browser.
"""

from flask import Flask, request, jsonify

app = Flask(__name__)

GENRES = [
    {"name": "Pop",           "score": 1.00},
    {"name": "K-Pop/Pop",     "score": 0.96},
    {"name": "R&B/Soul",      "score": 0.88},
    {"name": "Indie Folk",    "score": 0.86},
    {"name": "Indie Pop",     "score": 0.80},
    {"name": "Hip-Hop",       "score": 0.78},
    {"name": "Country/Pop",   "score": 0.74},
    {"name": "Pop Rock",      "score": 0.72},
    {"name": "R&B/Pop",       "score": 0.70},
    {"name": "Reggaeton",     "score": 0.68},
    {"name": "Country",       "score": 0.66},
    {"name": "Synth-Pop",     "score": 0.64},
    {"name": "Afrobeats",     "score": 0.60},
    {"name": "Latin Pop",     "score": 0.54},
    {"name": "Hip-Hop/Pop",   "score": 0.50},
    {"name": "Alternative",   "score": 0.38},
    {"name": "Pop Punk",      "score": 0.34},
    {"name": "Indie Rock",    "score": 0.30},
    {"name": "Pop/Folk",      "score": 0.24},
]

WEIGHTS = {
    "genre":       0.30,
    "dance":       0.22,
    "valence":     0.18,
    "energy":      0.12,
    "bpm":         0.10,
    "acoustic":    0.05,
    "explicit":    0.03,
}


def score_feature(val, ideal, width):
    """Score a continuous feature by proximity to its ideal value."""
    dist = abs(val - ideal)
    return max(0.0, 1.0 - dist / width)


def calculate_probability(genre: str, dance: float, energy: float,
                           valence: float, acoustic: float,
                           bpm: int, explicit: bool) -> dict:
    """
    Calculate the hit probability for a song given its features.

    Parameters
    ----------
    genre    : Genre name (must match one of the GENRES list)
    dance    : Danceability  0.0 – 1.0
    energy   : Energy level  0.0 – 1.0
    valence  : Mood          0.0 – 1.0
    acoustic : Acousticness  0.0 – 1.0
    bpm      : Tempo in BPM  60 – 200
    explicit : True if the song is explicit

    Returns
    -------
    dict with keys: probability (int 0-99), label, verdict, factors, tips
    """
    genre_data = next((g for g in GENRES if g["name"] == genre), GENRES[0])

    factors = {
        "Genre fit":       genre_data["score"]                      * WEIGHTS["genre"],
        "Danceability":    score_feature(dance,   0.70, 0.35)       * WEIGHTS["dance"],
        "Mood (valence)":  score_feature(valence, 0.68, 0.40)       * WEIGHTS["valence"],
        "Energy":          score_feature(energy,  0.65, 0.40)       * WEIGHTS["energy"],
        "Tempo":           score_feature(bpm,     110,  50)         * WEIGHTS["bpm"],
        "Low acousticness":max(0.0, 1.0 - acoustic / 0.5)          * WEIGHTS["acoustic"],
        "Explicitness":    (0.75 if explicit else 1.0)              * WEIGHTS["explicit"],
    }

    total = sum(factors.values())
    pct = min(99, round(total * 100))

    if pct >= 85:
        label = "top charter"
        verdict = "Your song has all the hallmarks of a Spotify Wrapped hit."
    elif pct >= 70:
        label = "likely hit"
        verdict = "Strong chart potential — a few tweaks could push it higher."
    elif pct >= 50:
        label = "mid-charter"
        verdict = "Decent shot at charting, but something is holding it back."
    elif pct >= 35:
        label = "niche appeal"
        verdict = "Niche appeal — may find a dedicated audience but unlikely to dominate."
    else:
        label = "deep cut"
        verdict = "This combination rarely makes the top 50. Try adjusting your features."

    tips = []
    if dance < 0.60:
        tips.append("Boost danceability above 0.60 — it has the strongest correlation with streams (+0.34).")
    if valence < 0.55:
        tips.append("Raise the mood (valence) — top 50 songs average 0.67, leaning upbeat.")
    if acoustic > 0.25:
        tips.append("Reduce acousticness — hits are heavily produced (avg 0.15).")
    if bpm < 88 or bpm > 135:
        tips.append("Bring tempo closer to 90–130 BPM — the sweet spot for top charting songs.")
    if genre_data["score"] < 0.65:
        tips.append(f"{genre} is underrepresented in the top 50. Blending in Pop elements could help.")
    if explicit:
        tips.append("86% of top 50 songs are clean — explicit content slightly lowers broad appeal.")
    if not tips:
        tips.append("Looking good! Your song matches the profile of a Spotify Wrapped hit.")

    max_scores = {
        "Genre fit":        WEIGHTS["genre"],
        "Danceability":     WEIGHTS["dance"],
        "Mood (valence)":   WEIGHTS["valence"],
        "Energy":           WEIGHTS["energy"],
        "Tempo":            WEIGHTS["bpm"],
        "Low acousticness": WEIGHTS["acoustic"],
        "Explicitness":     WEIGHTS["explicit"],
    }

    return {
        "probability": pct,
        "label": label,
        "verdict": verdict,
        "factors": {k: {"earned": round(v * 100), "max": round(max_scores[k] * 100)} for k, v in factors.items()},
        "tips": tips,
    }


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hit Song Probability Builder</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, sans-serif; background: #f5f4f0; color: #1a1a18; min-height: 100vh; display: flex; justify-content: center; padding: 2rem 1rem; }
  .card { background: #fff; border: 0.5px solid rgba(0,0,0,0.12); border-radius: 14px; padding: 2rem; width: 100%; max-width: 680px; height: fit-content; }
  h1 { font-size: 18px; font-weight: 500; margin-bottom: 4px; }
  .sub { font-size: 13px; color: #888; margin-bottom: 1.5rem; }
  .sec { font-size: 11px; font-weight: 500; color: #aaa; letter-spacing: 0.07em; text-transform: uppercase; margin: 1.5rem 0 12px; }
  .genre-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 6px; margin-bottom: 0.5rem; }
  .genre-btn { font-size: 12px; padding: 6px 8px; border: 0.5px solid rgba(0,0,0,0.2); border-radius: 8px; background: #fff; color: #555; cursor: pointer; }
  .genre-btn.active { background: #534AB7; border-color: #534AB7; color: #fff; font-weight: 500; }
  .slider-row { display: grid; grid-template-columns: 140px 1fr 48px; align-items: center; gap: 12px; margin-bottom: 14px; }
  .slider-label { font-size: 13px; color: #666; text-align: right; }
  .slider-val { font-size: 13px; font-weight: 500; }
  input[type=range] { width: 100%; accent-color: #534AB7; }
  .toggle { display: flex; border: 0.5px solid rgba(0,0,0,0.2); border-radius: 8px; overflow: hidden; width: fit-content; }
  .tog-btn { font-size: 12px; padding: 6px 18px; background: #fff; color: #555; cursor: pointer; border: none; }
  .tog-btn.active { background: #534AB7; color: #fff; font-weight: 500; }
  hr { border: none; border-top: 0.5px solid rgba(0,0,0,0.1); margin: 1.5rem 0; }
  .prob-wrap { display: flex; flex-direction: column; align-items: center; margin: 8px 0 16px; }
  .verdict { font-size: 13px; color: #666; text-align: center; margin-top: 6px; min-height: 18px; }
  .factor-row { display: flex; align-items: center; margin-bottom: 7px; }
  .factor-name { font-size: 12px; color: #666; width: 130px; flex-shrink: 0; }
  .bar-wrap { flex: 1; margin: 0 10px; height: 6px; background: #eee; border-radius: 3px; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 3px; transition: width 0.3s; background: #534AB7; }
  .factor-pct { font-size: 12px; font-weight: 500; min-width: 44px; text-align: right; color: #534AB7; }
  .tips-list { list-style: none; }
  .tip-item { display: flex; gap: 8px; font-size: 12px; color: #555; margin-bottom: 7px; align-items: flex-start; }
  .tip-dot { width: 6px; height: 6px; border-radius: 50%; background: #534AB7; margin-top: 4px; flex-shrink: 0; }
</style>
</head>
<body>
<div class="card">
  <h1>Hit song probability builder</h1>
  <p class="sub">Based on Spotify Wrapped 2025 Top 50 data</p>

  <p class="sec">Genre</p>
  <div class="genre-grid" id="genreGrid"></div>

  <hr>
  <p class="sec">Audio features</p>

  <div class="slider-row">
    <span class="slider-label">Danceability</span>
    <input type="range" id="sl-dance" min="0" max="100" value="68" step="1">
    <span class="slider-val" id="out-dance">0.68</span>
  </div>
  <div class="slider-row">
    <span class="slider-label">Energy level</span>
    <input type="range" id="sl-energy" min="0" max="100" value="65" step="1">
    <span class="slider-val" id="out-energy">0.65</span>
  </div>
  <div class="slider-row">
    <span class="slider-label">Mood (valence)</span>
    <input type="range" id="sl-valence" min="0" max="100" value="67" step="1">
    <span class="slider-val" id="out-valence">0.67</span>
  </div>
  <div class="slider-row">
    <span class="slider-label">Acousticness</span>
    <input type="range" id="sl-acoustic" min="0" max="100" value="15" step="1">
    <span class="slider-val" id="out-acoustic">0.15</span>
  </div>
  <div class="slider-row">
    <span class="slider-label">Tempo (BPM)</span>
    <input type="range" id="sl-bpm" min="60" max="200" value="110" step="1">
    <span class="slider-val" id="out-bpm">110</span>
  </div>
  <div style="display:grid; grid-template-columns:140px 1fr; gap:12px; align-items:center; margin-bottom:14px;">
    <span class="slider-label">Explicit</span>
    <div class="toggle">
      <button class="tog-btn active" id="exp-no"  onclick="setExplicit(false)">Clean</button>
      <button class="tog-btn"        id="exp-yes" onclick="setExplicit(true)">Explicit</button>
    </div>
  </div>

  <hr>
  <p class="sec">Hit probability</p>
  <div class="prob-wrap">
    <svg width="160" height="160" viewBox="0 0 160 160">
      <circle cx="80" cy="80" r="66" fill="none" stroke="#e8e8e4" stroke-width="14"/>
      <circle cx="80" cy="80" r="66" fill="none" stroke-width="14" stroke-linecap="round"
        id="ringFill" stroke="#534AB7"
        stroke-dasharray="414.7" stroke-dashoffset="414.7"
        transform="rotate(-90 80 80)" style="transition:stroke-dashoffset 0.5s,stroke 0.5s;"/>
      <text x="80" y="76" text-anchor="middle" font-size="30" font-weight="500" fill="#534AB7" id="ringPct">0%</text>
      <text x="80" y="96" text-anchor="middle" font-size="12" fill="#888" id="ringLabel">calculating</text>
    </svg>
    <p class="verdict" id="verdict"></p>
  </div>

  <p class="sec" style="margin-bottom:10px;">Score breakdown</p>
  <div id="factorBreakdown"></div>

  <hr>
  <p class="sec">Tips to improve your score</p>
  <ul class="tips-list" id="tipsList"></ul>
</div>

<script>
const GENRES = """ + str([{"name": g["name"], "score": g["score"]} for g in GENRES]).replace("'", '"') + """;

let selectedGenre = 'Pop';
let isExplicit = false;

const grid = document.getElementById('genreGrid');
GENRES.forEach(g => {
  const btn = document.createElement('button');
  btn.className = 'genre-btn' + (g.name === 'Pop' ? ' active' : '');
  btn.textContent = g.name;
  btn.onclick = () => {
    document.querySelectorAll('.genre-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedGenre = g.name;
    recalc();
  };
  grid.appendChild(btn);
});

function setExplicit(val) {
  isExplicit = val;
  document.getElementById('exp-no').classList.toggle('active', !val);
  document.getElementById('exp-yes').classList.toggle('active', val);
  recalc();
}

[['sl-dance','out-dance',100,2],['sl-energy','out-energy',100,2],
 ['sl-valence','out-valence',100,2],['sl-acoustic','out-acoustic',100,2],
 ['sl-bpm','out-bpm',1,0]].forEach(([id, outId, div, dec]) => {
  document.getElementById(id).addEventListener('input', function() {
    document.getElementById(outId).textContent = div === 1 ? this.value : (this.value / div).toFixed(dec);
    recalc();
  });
});

async function recalc() {
  const params = new URLSearchParams({
    genre:    selectedGenre,
    dance:    document.getElementById('sl-dance').value / 100,
    energy:   document.getElementById('sl-energy').value / 100,
    valence:  document.getElementById('sl-valence').value / 100,
    acoustic: document.getElementById('sl-acoustic').value / 100,
    bpm:      document.getElementById('sl-bpm').value,
    explicit: isExplicit,
  });
  const res = await fetch('/api/score?' + params);
  const d = await res.json();

  const circ = 414.7;
  const offset = circ * (1 - d.probability / 100);
  const ring = document.getElementById('ringFill');
  ring.setAttribute('stroke-dashoffset', offset.toFixed(1));
  const color = d.probability >= 75 ? '#1D9E75' : d.probability >= 50 ? '#BA7517' : '#E24B4A';
  ring.setAttribute('stroke', color);
  document.getElementById('ringPct').textContent = d.probability + '%';
  document.getElementById('ringPct').setAttribute('fill', color);
  document.getElementById('ringLabel').textContent = d.label;
  document.getElementById('verdict').textContent = d.verdict;

  const breakdown = document.getElementById('factorBreakdown');
  breakdown.innerHTML = '';
  Object.entries(d.factors).forEach(([name, f]) => {
    const pct = Math.round((f.earned / Math.max(f.max, 1)) * 100);
    const row = document.createElement('div');
    row.className = 'factor-row';
    row.innerHTML = `<span class="factor-name">${name}</span>
      <div class="bar-wrap"><div class="bar-fill" style="width:${pct}%"></div></div>
      <span class="factor-pct">${f.earned}/${f.max}</span>`;
    breakdown.appendChild(row);
  });

  const tipsList = document.getElementById('tipsList');
  tipsList.innerHTML = '';
  d.tips.forEach(t => {
    const li = document.createElement('li');
    li.className = 'tip-item';
    li.innerHTML = `<span class="tip-dot"></span><span>${t}</span>`;
    tipsList.appendChild(li);
  });
}

recalc();
</script>
</body>
</html>"""


@app.route("/")
def index():
    return HTML_PAGE


@app.route("/api/score")
def api_score():
    genre    = request.args.get("genre", "Pop")
    dance    = float(request.args.get("dance", 0.68))
    energy   = float(request.args.get("energy", 0.65))
    valence  = float(request.args.get("valence", 0.67))
    acoustic = float(request.args.get("acoustic", 0.15))
    bpm      = int(request.args.get("bpm", 110))
    explicit = request.args.get("explicit", "false").lower() == "true"

    result = calculate_probability(genre, dance, energy, valence, acoustic, bpm, explicit)
    return jsonify(result)


@app.route("/api/score", methods=["POST"])
def api_score_post():
    data     = request.get_json(force=True)
    genre    = data.get("genre", "Pop")
    dance    = float(data.get("dance", 0.68))
    energy   = float(data.get("energy", 0.65))
    valence  = float(data.get("valence", 0.67))
    acoustic = float(data.get("acoustic", 0.15))
    bpm      = int(data.get("bpm", 110))
    explicit = bool(data.get("explicit", False))

    result = calculate_probability(genre, dance, energy, valence, acoustic, bpm, explicit)
    return jsonify(result)


if __name__ == "__main__":
    print("Hit Song Probability Builder")
    print("Open http://localhost:5000 in your browser")
    print("Press Ctrl+C to stop\n")
    app.run(debug=True, port=5000)
