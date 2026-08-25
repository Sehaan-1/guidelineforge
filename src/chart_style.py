import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
PAPER = '#f7f6f1'
CARD = '#fffdf8'
INK = '#1d1d1b'
MUTE = '#77716a'
HAIR = '#d9d5ca'
GRID = '#e7e4da'
R1C = '#98a4b0'
R2C = '#2f4a3e'
GOOD = '#3a6d51'
BAD = '#b23a2c'
AMBER = '#b8892f'
SLATE = '#44586a'
CMAP_HEAT = LinearSegmentedColormap.from_list('gf_heat', ['#b23a2c', '#d9a15a', '#e8e2cf', '#7fa189', '#3a6d51'])
CMAP_CONF = LinearSegmentedColormap.from_list('gf_conf', ['#fffdf8', '#9fb0c0', '#44586a', '#1c2a36'])
SERIF = 'DejaVu Serif'
SANS = 'DejaVu Sans'
MONO = 'DejaVu Sans Mono'

def base_rc():
    plt.rcParams.update({'figure.facecolor': PAPER, 'axes.facecolor': CARD, 'savefig.facecolor': PAPER, 'font.family': SANS, 'font.size': 9.5, 'text.color': INK, 'axes.edgecolor': HAIR, 'axes.labelcolor': MUTE, 'xtick.color': MUTE, 'ytick.color': MUTE, 'axes.linewidth': 0.8, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.7, 'axes.axisbelow': True, 'xtick.labelsize': 8.8, 'ytick.labelsize': 8.8, 'figure.dpi': 150})

def titles(fig, ax, kicker, title, note=None):
    fig.canvas.draw()
    y0 = ax.get_position().y1
    x0 = ax.get_position().x0
    fig.text(x0, y0 + 0.095, kicker.upper(), family=MONO, fontsize=7.5, color=MUTE)
    fig.text(x0, y0 + 0.057, title, family=SERIF, fontsize=14.5, fontweight='bold', color=INK)
    if note:
        fig.text(x0, y0 + 0.024, note, fontsize=8.6, color=MUTE, style='italic')

def source(fig, text, y=0.008):
    import textwrap
    for i, ln in enumerate(textwrap.wrap(text, 150)[:2]):
        fig.text(0.02, y + (1 - i) * 0.017, ln, family=MONO, fontsize=6.6, color=MUTE)

def target_vline(ax, x, label, y_frac=0.97):
    ax.axvline(x, color=BAD, lw=1.0, ls=(0, (4, 2)), zorder=1)
    ax.text(x, y_frac * ax.get_ylim()[1] if ax.get_ylim()[1] > 1 else y_frac, f' {label}', color=BAD, fontsize=8, ha='left', va='top', transform=ax.get_xaxis_transform() if y_frac < 2 else None)

def dumbbell(ax, labels, v1, v2, target=None, xlim=(0.3, 1.02), v1_name='Round 1', v2_name='Round 2', delta_at=1.05):
    import numpy as np
    y = np.arange(len(labels))[::-1]
    for yi, a, b in zip(y, v1, v2):
        ax.plot([a, b], [yi, yi], color=HAIR, lw=2.2, zorder=2, solid_capstyle='round')
    ax.scatter(v1, y, s=46, facecolor='white', edgecolor=R1C, lw=1.6, zorder=3, label=v1_name)
    ax.scatter(v2, y, s=52, color=R2C, zorder=4, label=v2_name)
    for yi, a, b in zip(y, v1, v2):
        d = b - a
        cc = GOOD if d >= 0 else BAD
        ax.text(a - 0.012, yi, f'{a:.2f}', ha='right', va='center', family=MONO, fontsize=7.8, color=MUTE)
        ax.text(b + 0.012, yi, f'{b:.2f}', ha='left', va='center', family=MONO, fontsize=8.2, fontweight='bold', color=INK)
        ax.text(delta_at, yi, f'+{d:.2f}' if d > 0 else f'{d:.2f}', ha='left', va='center', family=MONO, fontsize=8, color=cc)
    if target is not None:
        ax.axvline(target, color=BAD, lw=1.0, ls=(0, (4, 2)), zorder=1)
        ax.text(target + 0.008, -0.62, f'target {target:.2f}', color=BAD, fontsize=7.6, ha='left', va='bottom', family=MONO)
    ax.set_yticks(y, labels)
    ax.set_xlim(*xlim)
    ax.set_ylim(-0.7, len(labels) - 0.3)
    ax.xaxis.set_major_formatter(lambda v, p: f'{v:.1f}')
    ax.grid(axis='y', visible=False)
    return ax

def legend_strip(fig, x, y, entries):
    xx = x
    for color, filled, label in entries:
        fig.text(xx, y, '●' if filled else '○', color=color, fontsize=9)
        fig.text(xx + 0.012, y, label, fontsize=8.2, color=MUTE)
        xx += 0.012 + 0.011 * len(label) + 0.03

def legend_in_ax(ax, x, y, entries, step=0.17):
    xx = x
    for color, filled, label in entries:
        ax.text(xx, y, '●' if filled else '○', color=color, fontsize=9, va='center')
        ax.text(xx + step * 0.16, y, label, fontsize=8.2, color=MUTE, va='center')
        xx += step * 0.16 + step * 0.02 * len(label) + step * 0.55
