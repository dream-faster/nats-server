import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Palette
BG      = "#0E1726"
PANEL   = "#152033"
INK     = "#E6EDF3"
MUTE    = "#8B98A5"
RED     = "#E5484D"
REDFILL = "#2A1518"
GREEN   = "#30C77E"
GRNFILL = "#10271C"
TEAL    = "#2DD4BF"
GOLD    = "#F5B14C"

MONO = {"family": "DejaVu Sans Mono"}
SANS = {"family": "DejaVu Sans"}

fig = plt.figure(figsize=(16, 10), dpi=150)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 160); ax.set_ylim(0, 100); ax.axis("off")
fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
ax.add_patch(plt.Rectangle((0, 0), 160, 100, color=BG, zorder=-10))


def box(x, y, w, h, fc, ec, lw=2.0, r=0.03, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r*100}",
                                linewidth=lw, edgecolor=ec, facecolor=fc, zorder=z))


def txt(x, y, s, size, color=INK, font=SANS, weight="normal", ha="center", va="center", z=6):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, weight=weight, zorder=z, **font)


def node(cx, top_y, bot_y, accent, hub_lines, spoke_lines):
    w, h = 34, 11
    # hub
    box(cx - w/2, top_y, w, h, PANEL, accent, 2.4)
    txt(cx, top_y + h - 3.4, "HUB", 14, INK, SANS, "bold")
    for i, (s, c) in enumerate(hub_lines):
        txt(cx, top_y + h - 6.6 - i*2.7, s, 10.5, c, MONO)
    # spoke
    box(cx - w/2, bot_y, w, h, PANEL, "#3A4B66", 2.0)
    txt(cx, bot_y + h - 3.4, "SPOKE  ·  cell", 12.5, INK, SANS, "bold")
    for i, (s, c) in enumerate(spoke_lines):
        txt(cx, bot_y + h - 6.6 - i*2.7, s, 10, c, SANS)


HUB_TOP, HUB_BOT = 66, 30   # hub box y, spoke box y
LINK_TOP, LINK_BOT = HUB_TOP, HUB_BOT + 11  # gap between boxes


def chip(cx, cy, label, accent, big=False):
    w = 24 if big else 18
    box(cx - w/2, cy - 3.0, w, 6.0, BG, accent, 2.2, r=0.03, z=7)
    txt(cx, cy, label, 11.5 if big else 10.5, accent, MONO, "bold", z=8)


# ---- Title ----
txt(80, 95.0, "_LR_  ·  Leafnode interest, collapsed", 29, INK, MONO, "bold")
txt(80, 89.6, "one subscription per spoke on the hub  —  no matter how many devices connect", 14.5, MUTE, SANS)

# ---- Column captions ----
txt(42, 82.5, "BEFORE", 17, RED, SANS, "bold")
txt(118, 82.5, "AFTER", 17, GREEN, SANS, "bold")

# ================= BEFORE (cx=42) =================
node(42, HUB_TOP, HUB_BOT, RED,
     [("interest table", MUTE), ("50,000 entries", GOLD)],
     [("50,000 devices", MUTE), ("50,000 local subs", MUTE)])
# dense ribbon of interest strands crossing the leaf link
import numpy as np
for x in np.linspace(35, 49, 17):
    ax.plot([x, x], [LINK_BOT, LINK_TOP], color=RED, lw=1.1, alpha=0.5, zorder=1)
chip(42, (LINK_TOP + LINK_BOT)/2, "50,000 subs", RED, big=True)
txt(42, 24.5, "leaf link carries one interest entry PER inbox", 9.5, MUTE, SANS)

# ================= AFTER (cx=118) =================
node(118, HUB_TOP, HUB_BOT, GREEN,
     [("_LR_.<spoke>.>", GREEN), ("1 entry", GOLD)],
     [("50,000 devices", MUTE), ("50,000 local subs (kept)", MUTE)])
ax.plot([118, 118], [LINK_BOT, LINK_TOP], color=GREEN, lw=3.0, zorder=1)
chip(118, (LINK_TOP + LINK_BOT)/2, "1 sub", GREEN)
txt(118, 24.5, "one wildcard routes every reply back to this spoke", 9.5, MUTE, SANS)

# ================= Center transform =================
arrow = FancyArrowPatch((62, 48), (98, 48), arrowstyle="-|>", mutation_scale=26,
                        linewidth=3.0, color=TEAL, zorder=3)
ax.add_patch(arrow)
txt(80, 52.5, "collapse", 12, TEAL, SANS, "bold")

# ================= Headline metric banner =================
box(20, 4.5, 120, 14.5, "#101A2B", "#26344A", 1.6, r=0.04)
txt(57, 13.6, "50,000", 30, RED, MONO, "bold", ha="right")
txt(66, 13.6, "→", 26, TEAL, MONO, "bold")
txt(78, 13.0, "1", 38, GREEN, MONO, "bold", ha="left")
txt(108, 15.0, "subscriptions on the hub, per spoke", 13.5, INK, SANS, "bold")
txt(108, 10.6, "≈ 50,000× fewer  ·  10→1 measured  ·  O(devices) → O(nodes)", 11, MUTE, SANS)
txt(108, 7.4, "transparent to clients  ·  reuses the proven gateway  _GR_  routing", 10, MUTE, SANS)

fig.savefig("hero_lr.png", facecolor=BG, bbox_inches=None)
print("wrote hero_lr.png")
