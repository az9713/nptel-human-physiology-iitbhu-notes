"""Build print plots from the unchanged Chapter 8 JavaScript teaching model.

Requires Node.js and Matplotlib 3.9.3. No anatomical rendering or patient data.
The separate browser renderer remains interactive; these are its default input
vector and two stated independent Hb states, with explicit axes for paper.
"""
from pathlib import Path
import hashlib
import json
import math
import platform
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "assets"
MODEL_SHA = "f47ce20be72ee276aa61032c0b9af61c365f3ffe0b639e083db570d4c4e31b78"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    model = A / "ch08-models.js"
    if sha(model) != MODEL_SHA:
        raise ValueError("Teaching model changed; review before rebuilding plots")
    js = """require('./assets/ch08-models.js');const m=globalThis.Ch08;
    const states=[15,7.5].map(hb=>{const c=m.content(hb,.98,100);
      return {hb,content:c,...m.balance(c.total,c.total*.75,5)};});
    process.stdout.write(JSON.stringify({volumes:m.volumes(.5),
      curve:Array.from({length:201},(_,i)=>({phase:i/200,volume:m.lung(i/200,.5).value})),
      oxygen:states}));"""
    data = json.loads(subprocess.run(["node", "-e", js], cwd=ROOT,
                                    capture_output=True, text=True, check=True).stdout)
    v = data["volumes"]
    assert math.isclose(v["tlc"], v["ic"] + v["frc"])
    assert math.isclose(v["tlc"], v["vc"] + v["rv"])
    for state in data["oxygen"]:
        assert math.isclose(state["delivery"], state["consumption"] + state["returned"])
    snapshot = A / "ch08-v2-plot-data.json"
    snapshot.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5,
                         "axes.titlesize": 11, "axes.labelsize": 10.5,
                         "svg.fonttype": "none", "svg.hashsalt": "physiology-ch08-v2",
                         "axes.spines.top": False, "axes.spines.right": False})
    metadata = {"Date": None, "Creator": "Matplotlib " + matplotlib.__version__}

    fig = plt.figure(figsize=(7.1, 3.45), facecolor="white")
    gs = fig.add_gridspec(1, 2, width_ratios=[3.7, 1.35], wspace=.32)
    ax, bands = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    ax.plot([p["phase"] for p in data["curve"]],
            [p["volume"] for p in data["curve"]], color="#08796b", lw=1.8)
    ax.plot([0], [v["frc"]], "o", color="#a45e00", ms=4, clip_on=False)
    ax.set(xlim=(0, 1), ylim=(0, 7), ylabel="Lung gas volume (L)",
           xlabel="Maneuver presentation phase (not respiratory time)")
    ax.set_xticks([i / 5 for i in range(6)])
    ax.set_yticks(range(8))
    ax.grid(axis="y", color="#ced5da", lw=.6)
    ax.set_axisbelow(True)
    colors = ["#5b7ba3", "#96765e", "#538f99", "#759f74"]
    bottom = 0
    for name, color in zip(["rv", "erv", "vt", "irv"], colors):
        height = v[name]
        bands.bar(.16, height, bottom=bottom, width=.32, color=color)
        bands.text(.40, bottom + height / 2,
                   name.upper() + " " + f"{height:.1f}", va="center")
        bottom += height
    bands.set(xlim=(-.05, 1.5), ylim=(0, 7), xticks=[], yticks=[])
    for spine in bands.spines.values():
        spine.set_visible(False)
    bands.set_title("Intervals (L)")
    fig.subplots_adjust(left=.10, right=.98, bottom=.29, top=.88)
    fig.text(.10, .08, "TLC 5.8 = IC 3.5 + FRC 2.3 = VC 4.6 + RV 1.2 L", fontsize=10)
    lung = A / "ch08-v2-lung-volumes-print.svg"
    fig.savefig(lung, metadata=metadata)
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(7.1, 4.6), sharex=True, facecolor="white")
    names = ["Incoming delivery", "Consumed", "Returning in venous blood"]
    keys = ["delivery", "consumption", "returned"]
    colors = ["#08796b", "#a86516", "#4266a0"]
    for ax, state in zip(axes, data["oxygen"]):
        values = [state[k] for k in keys]
        ax.barh(range(3), values, color=colors, height=.48)
        ax.set_yticks(range(3), names)
        ax.invert_yaxis()
        ax.set_xlim(0, 4500)
        ax.set_xticks([0, 1000, 2000, 3000, 4000, 4500])
        ax.grid(axis="x", color="#ced5da", lw=.6)
        ax.set_axisbelow(True)
        ax.set_title(f"Independent state: Hb {state['hb']:g} g/dL", loc="left")
        for i, value in enumerate(values):
            ax.text(value + 55, i, f"{value:.3f}", va="center", fontsize=10)
    axes[-1].set_xlabel("Oxygen rate (mL O₂/min); common 0–4500 scale")
    fig.subplots_adjust(left=.35, right=.97, bottom=.20, top=.91, hspace=.68)
    fig.text(.02, .045, "Synthetic inputs: saturation 0.98; flow 5 L/min; extraction 0.25;\n"
             "pressure 100 mmHg; Hb capacity 1.31 mL O₂/g; rates rounded to 0.001 mL/min.", fontsize=10)
    oxygen = A / "ch08-v2-oxygen-accounting-print.svg"
    fig.savefig(oxygen, metadata=metadata)
    plt.close(fig)

    record = {"date": "2026-11-09", "status": "Candidate; actual plot/PDF review pending",
              "purpose": "Print alternatives for two quantitative explorers; no anatomical imagery",
              "source": "Original synthetic Chapter8 model, not patient measurements",
              "parameters": {"vt_L": .5, "irv_L": 3, "erv_L": 1.1, "rv_L": 1.2,
                             "Hb_g_dL": [15, 7.5], "saturation": .98, "Q_L_min": 5,
                             "extraction": .25, "pressure_mmHg": 100, "capacity_mL_g": 1.31},
              "time": "Lung x is presentation phase; oxygen panels are independent states",
              "display_rate_rounding_mL_min": .001,
              "tools": {"python": platform.python_version(), "matplotlib": matplotlib.__version__,
                        "node": subprocess.run(["node", "--version"], capture_output=True,
                                                text=True, check=True).stdout.strip()},
              "reproduction": "python figures/ch08_static_plots_v2.py; model hash pinned; SVG salt/metadata fixed",
              "artifacts": {p.relative_to(ROOT).as_posix(): sha(p)
                            for p in [model, snapshot, lung, oxygen, Path(__file__)]}}
    (A / "ch08-v2-plot-provenance.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print("CH08_PRINT_PLOTS_BUILT")


if __name__ == "__main__":
    main()
