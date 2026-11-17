"""Start over: empty the payments refunds, the runs, the approvals and the cut results."""
import os, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(ROOT, "data", "state")

if os.path.isdir(STATE):
    shutil.rmtree(STATE)
os.makedirs(STATE)
print("reset: data/state/ emptied")
