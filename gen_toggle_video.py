"""
Stochastic Toggle Switch — time-trajectory background video.
Pre-computes several independent Gillespie/CLE trajectories of a bistable
gene circuit, then renders them as scrolling time-series on a black canvas.
Cyan = Protein A, Crimson = Protein B.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import imageio

# ── Parameters ────────────────────────────────────────────────────────────────
ALPHA  = 40.0    # max production rate
N_HILL = 2.5     # Hill cooperativity
GAMMA  = 1.0     # degradation
NOISE  = 1.5     # CLE noise amplitude

N_TRAJ   = 6     # independent cells shown
T_TOTAL  = 800   # total simulated time per trajectory
DT       = 0.05  # CLE time-step

FPS      = 30
DURATION = 25    # seconds of video
N_FRAMES = FPS * DURATION
W, H     = 1920, 1080
DPI      = 100

# Time window shown at any moment (in sim-time units)
WINDOW = T_TOTAL * 0.35

rng = np.random.default_rng(42)

# ── Pre-compute all trajectories ───────────────────────────────────────────────
print("Simulating trajectories …")
n_steps = int(T_TOTAL / DT)
t_arr   = np.linspace(0, T_TOTAL, n_steps)

trajs = []   # list of (A_arr, B_arr) each shape (n_steps,)
for k in range(N_TRAJ):
    A = np.zeros(n_steps)
    B = np.zeros(n_steps)
    # random initial attractor
    if rng.random() < 0.5:
        A[0], B[0] = 38 + rng.normal(0, 2), 2 + abs(rng.normal(0, 1))
    else:
        A[0], B[0] = 2 + abs(rng.normal(0, 1)), 38 + rng.normal(0, 2)

    for i in range(1, n_steps):
        a, b = A[i-1], B[i-1]
        pA = ALPHA / (1.0 + (b / 8.0) ** N_HILL)
        pB = ALPHA / (1.0 + (a / 8.0) ** N_HILL)
        sqdt = np.sqrt(DT) * NOISE
        dA = (pA - GAMMA * a) * DT + np.sqrt(max(pA + GAMMA * a, 0)) * rng.standard_normal() * sqdt
        dB = (pB - GAMMA * b) * DT + np.sqrt(max(pB + GAMMA * b, 0)) * rng.standard_normal() * sqdt
        A[i] = max(0.0, a + dA)
        B[i] = max(0.0, b + dB)

    trajs.append((A, B))
    print(f"  trajectory {k+1}/{N_TRAJ} done")

# ── Figure layout ─────────────────────────────────────────────────────────────
CYAN = '#00E5FF'
CRIM = '#FF1744'

fig, axes = plt.subplots(N_TRAJ, 1,
                          figsize=(W / DPI, H / DPI), dpi=DPI,
                          facecolor='black')
fig.subplots_adjust(left=0.0, right=1.0, top=0.97, bottom=0.03,
                    hspace=0.35)

# Y-axis range: a bit above the high attractor (~40)
YMAX = 55

line_artists = []
for ax, (A, B) in zip(axes, trajs):
    ax.set_facecolor('black')
    ax.set_ylim(0, YMAX)
    ax.set_xlim(0, WINDOW)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    # thin horizontal guide at half-max
    ax.axhline(YMAX * 0.5, color='#ffffff10', linewidth=0.5, zorder=0)

    lA, = ax.plot([], [], color=CYAN, lw=1.2, alpha=0.9, solid_capstyle='round')
    lB, = ax.plot([], [], color=CRIM, lw=1.2, alpha=0.9, solid_capstyle='round')
    line_artists.append((lA, lB))

# ── Render frames ─────────────────────────────────────────────────────────────
# The "camera" starts at t=0 and scrolls to t = T_TOTAL - WINDOW
t_start_max = T_TOTAL - WINDOW
t_starts = np.linspace(0, t_start_max, N_FRAMES)

out_path = 'images/home/toggle-switch.mp4'
writer = imageio.get_writer(out_path, fps=FPS, codec='libx264',
                             quality=8, output_params=['-pix_fmt', 'yuv420p'])

print(f"Rendering {N_FRAMES} frames …")
import io

for f, t0 in enumerate(t_starts):
    if f % 60 == 0:
        print(f"  frame {f}/{N_FRAMES}")

    t1 = t0 + WINDOW
    mask = (t_arr >= t0) & (t_arr <= t1)
    t_win = t_arr[mask] - t0   # shift to [0, WINDOW]

    for ax, (lA, lB), (A, B) in zip(axes, line_artists, trajs):
        ax.set_xlim(0, WINDOW)
        lA.set_data(t_win, A[mask])
        lB.set_data(t_win, B[mask])

    buf = io.BytesIO()
    fig.savefig(buf, format='raw', dpi=DPI, facecolor='black')
    buf.seek(0)
    img = np.frombuffer(buf.getvalue(), dtype=np.uint8).reshape(H, W, 4)
    writer.append_data(img[:, :, :3])

writer.close()
plt.close(fig)
print(f"Saved → {out_path}")
