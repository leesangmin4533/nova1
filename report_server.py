import json
from pathlib import Path
import io

from flask import Flask, render_template_string, request, send_file, abort
import matplotlib.pyplot as plt

app = Flask(__name__)

LOG_DIR = Path.home() / "Desktop" / "NOVA_LOGS"


def list_log_files():
    return sorted(LOG_DIR.glob("session_log_*.json"), reverse=True)


def load_log(path: Path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f.read().splitlines()]


def analyze(entries):
    counts = {"BUY": 0, "SELL": 0, "HOLD": 0, "FAILURE": 0}
    strat = {}
    for e in entries:
        action = e.get("action")
        if action in counts:
            counts[action] += 1
        if action == "SELL":
            s = e.get("strategy", "unknown")
            r = e.get("return_rate", 0.0)
            strat.setdefault(s, []).append(r)
    avg = {k: (sum(v)/len(v) if v else 0.0) for k, v in strat.items()}
    return counts, avg


@app.route("/report")
def report():
    files = list_log_files()
    if not files:
        return "\u274c \ub85c\uadf8 \ud30c\uc77c\uc774 \uc5c6\uc2b5\ub2c8\ub2e4."  # '❌ 로그 파일이 없습니다.'
    requested = request.args.get("file")
    target = LOG_DIR / requested if requested else files[0]
    if not target.exists():
        target = files[0]
    logs = load_log(target)
    counts, avg_returns = analyze(logs)
    opts = []
    for f in files:
        sel = "selected" if f == target else ""
        opts.append(f'<option value="{f.name}" {sel}>{f.name}</option>')
    template = """
    <!doctype html>
    <html lang=\"ko\">
    <head><meta charset=\"utf-8\"><title>NOVA Report</title></head>
    <body>
    <h1>NOVA \uacb0\uacfc \ub9ac\ud3ec\ud2b8</h1>
    <form method=\"get\" action=\"/report\">\n<select name=\"file\" onchange=\"this.form.submit()\">%s</select></form>
    <h2>{{ fname }}</h2>
    <ul>
      {% for k,v in counts.items() %}<li>{{ k }}: {{ v }}</li>{% endfor %}
    </ul>
    <h3>\uc804\ub7b5\ubcc4 \ud3c9\uade0 \uc218\uc775\ub960</h3>
    <ul>
      {% for k,v in avg.items() %}<li>{{ k }}: {{ '%.2f%%' % (v*100) }}</li>{% endfor %}
    </ul>
    <img src=\"/plot?file={{ fname }}\" alt=\"plot\">
    </body></html>""" % "".join(opts)
    return render_template_string(template, fname=target.name, counts=counts, avg=avg_returns)


@app.route("/plot")
def plot():
    file_name = request.args.get("file")
    if not file_name:
        abort(400)
    path = LOG_DIR / file_name
    if not path.exists():
        abort(404)
    logs = load_log(path)
    _, avg_returns = analyze(logs)
    fig, ax = plt.subplots()
    if avg_returns:
        ax.bar(list(avg_returns.keys()), [v * 100 for v in avg_returns.values()])
        ax.set_ylabel("Return (%)")
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return send_file(buf, mimetype="image/png")


if __name__ == "__main__":
    app.run(port=7860)
