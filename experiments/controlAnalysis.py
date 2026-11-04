import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq
from model import FIGURES
from model.helpers import AVERAGE_BOARD_TIME, AVERAGE_PASSENGER_RATE, distance
from model.controlFunction import Z_STOP, V_ART

# Linearised platoon, in lateness l_n (s behind nominal schedule), time in seconds:
#   plant:      dl/dt = beta B l + u + w      (boarding feedback; u = slow-down fraction, w = disturbance)
#   controller: u = -alpha L l                (spring law, alpha = 1/T_c)
# Free ends: a missing neighbour is a ghost at the ideal headway (error 0).

N = 12                 # buses on the road at once (about a 60 min trip / 5 min headway)
T_C = 600              # controller time constant (s); alpha = 1/T_c
T_REFRESH = 10         # display refresh = control_period (s); sample-and-hold ~ delay of T/2
TAUS = [0, 30, 300]    # driver lag time constants (s) to compare

# boarding gain: each second of extra headway adds b*q seconds of dwell per stop, one stop every T_S seconds
N_BOARDING_STOPS = len(distance) - 2                     # stops 1..29 (no boarding at origin or terminal)
T_S = Z_STOP[-1] / V_ART / N_BOARDING_STOPS              # nominal time per boarding stop, dwell included
BETA = AVERAGE_BOARD_TIME * AVERAGE_PASSENGER_RATE / T_S  # 1/s
ALPHA = 1 / T_C


def laplacian(n):
    """Spring coupling: row k holds the coefficients of l_j in -u_k/alpha. Corners are 1 (ghost neighbour)."""
    L = 2 * np.eye(n) - np.eye(n, k=1) - np.eye(n, k=-1)
    L[0, 0] = L[-1, -1] = 1
    return L


def boarding(n):
    """Boarding coupling: row k is l_k - l_{k-1} (front headway error). Front bus has a ghost leader, so row 0 is 0."""
    B = np.eye(n) - np.eye(n, k=-1)
    B[0, 0] = 0
    return B


def loop_tf(w, K, p, tau, T=T_REFRESH):
    """Per-mode open loop L(jw) = K e^{-jwT/2} / ((tau jw + 1)(jw - p))."""
    s = 1j * w
    return K * np.exp(-s * T / 2) / ((tau * s + 1) * (s - p))


def margins(K, p, tau, T=T_REFRESH):
    """Crossover, phase margin and the two gain margins of the per-mode loop (analytic phase, no wrapping)."""
    # phase of L(jw) = -180 + atan(w/p) - atan(w tau) - w T/2 (deg after conversion)
    excess = lambda w: np.arctan(w / p) - np.arctan(w * tau) - w * T / 2   # phase above -180 deg (rad)
    wc = brentq(lambda w: abs(loop_tf(w, K, p, tau, T)) - 1, 1e-9, 10)
    pm = np.degrees(excess(wc))
    gm_low = K / p                                       # gain can drop by this factor before the boarding edge
    w180 = brentq(excess, wc, 10)                        # phase returns to -180 deg (lag + delay)
    gm_high = 1 / abs(loop_tf(w180, K, p, tau, T))       # gain can rise by this factor
    return wc, pm, gm_low, w180, gm_high


def encirclements(K, p, tau, T=T_REFRESH):
    """Net anticlockwise encirclements of -1 by L(jw), w from -inf to inf."""
    w = np.logspace(-8, 3, 400001)
    w = np.concatenate((-w[::-1], [0.0], w))
    phase = np.unwrap(np.angle(1 + loop_tf(w, K, p, tau, T)))
    return (phase[-1] - phase[0]) / (2 * np.pi)


if __name__ == "__main__":
    L, B = laplacian(N), boarding(N)
    print(f"beta = {BETA * 3600:.2f} /h (T_s = {T_S:.0f} s per boarding stop), alpha = {ALPHA * 3600:.2f} /h")
    print(f"lower stability edge: alpha > beta/2, i.e. T_c < {2 / BETA / 60:.0f} min")

    # 1. diagonalise: columns of V are the eigenvectors (modes) of L; V^T L V is diagonal exactly
    lam, V = np.linalg.eigh(L)
    print("\nlambda_k:", np.round(lam, 3))
    print("open-chain formula 2 - 2cos(k pi/N):", np.round(2 - 2 * np.cos(np.arange(N) * np.pi / N), 3))
    Bm = V.T @ B @ V
    off = Bm - np.diag(np.diag(Bm))
    print("diag(V^T B V):", np.round(np.diag(Bm), 3), " (compare lambda/2; exact)")
    print(f"largest off-diagonal of V^T B V: {np.abs(off).max():.2f} (travelling-wave coupling, dropped)")

    # per-mode loops: K_k = alpha lambda_k, p_k = beta lambda_k / 2; check against the exact coupled system
    K, p = ALPHA * lam, BETA * np.diag(Bm)
    exact = np.linalg.eigvals(BETA * B - ALPHA * L)
    print("\nclosed-loop poles (1/h), exact      :", np.round(np.sort(exact.real)[:4] * 3600, 2), "...")
    print("closed-loop poles (1/h), per mode   :", np.round(np.sort(p - K)[:4] * 3600, 2), "...")

    # 2. open-loop analysis of the fastest mode (largest lambda: highest crossover, so lag and delay hurt most)
    k = np.argmax(lam)
    print(f"\nfastest mode: lambda = {lam[k]:.3f}, K = {K[k]:.2e} /s, plant pole p = {p[k]:.2e} /s "
          f"(time constant {1 / p[k] / 60:.0f} min), K/p = {K[k] / p[k]:.1f}")
    print(f"{'tau (s)':>8s} {'w_c (rad/s)':>12s} {'PM (deg)':>9s} {'GM low':>7s} {'GM high':>8s} {'anticlockwise enc.':>19s}")
    for tau in TAUS:
        wc, pm, gm_low, w180, gm_high = margins(K[k], p[k], tau)
        print(f"{tau:8d} {wc:12.2e} {pm:9.1f} {gm_low:7.1f} {gm_high:8.1f} {encirclements(K[k], p[k], tau):19.2f}")
    print("GM low: gain can fall by this factor before the boarding edge. GM high: can rise by this factor;\n"
          "with tau = 0 its w180 is near the sampling limit pi/T, where e^{-sT/2} is a poor model of the refresh.")

    # 3. guaranteed bound without diagonalising: Gershgorin discs of the full matrix beta B - alpha L
    M = BETA * B - ALPHA * L
    right_edges = np.diag(M) + np.abs(M).sum(axis=1) - np.abs(np.diag(M))
    print(f"\nGershgorin: all discs in Re <= 0 if alpha >= beta, i.e. T_c <= {1 / BETA / 60:.0f} min; "
          f"at T_c = {T_C / 60:.0f} min the largest right edge is {right_edges.max():.1e} (<= 0 means guaranteed)")

    # 4. sampled model of the display refresh: the command is held for T, so each refresh multiplies
    #    the mode's error by z; stable iff -1 < z < 1. z < 1 is exactly K > p (the lower limit).
    Kf, pf, T = K[k], p[k], T_REFRESH
    z = np.exp(pf * T) - Kf / pf * (np.exp(pf * T) - 1)
    z_cont = np.exp(-(Kf - pf) * T)                       # the continuous pole s = -(K - p), sampled every T
    K_max = pf * (np.exp(pf * T) + 1) / (np.exp(pf * T) - 1)   # z = -1
    print(f"sampled pole (fastest mode): z = {z:.4f}, continuous equivalent {z_cont:.4f} "
          f"(differ by {abs(z - z_cont) / z_cont:.1%}); (K - p)T = {(Kf - pf) * T:.3f} per refresh")
    print(f"time scales: instability 1/p = {1 / pf / 60:.0f} min, correction 1/(K - p) = {1 / (Kf - pf) / 60:.1f} min, "
          f"refresh {T} s")
    print(f"upper limit (z = -1): K < {K_max:.3f} /s, i.e. T_c > {lam[k] / K_max:.1f} s "
          f"(about 2T); sampled gain margin {K_max / Kf:.1f}")

    # Nyquist plot: one open-loop RHP pole, so stability needs one anticlockwise encirclement of -1
    fig, axs = plt.subplots(1, 2, figsize=(12, 5.5))
    w = np.logspace(-6, 1, 20000)
    for tau in TAUS:
        Lw = loop_tf(w, K[k], p[k], tau)
        for ax in axs:
            line, = ax.plot(Lw.real, Lw.imag, label=f'tau = {tau} s')
            ax.plot(Lw.real, -Lw.imag, color=line.get_color(), ls='--', lw=0.8)    # negative frequencies
            i = np.searchsorted(w, 1e-3)
            ax.annotate('', xy=(Lw.real[i + 50], Lw.imag[i + 50]), xytext=(Lw.real[i], Lw.imag[i]),
                        arrowprops=dict(arrowstyle='->', color=line.get_color()))
    for ax, lim in zip(axs, (8.5, 1.6)):
        ax.plot(-1, 0, 'rx', ms=10, mew=2)
        ax.axhline(0, color='grey', lw=0.5); ax.axvline(0, color='grey', lw=0.5)
        ax.set(xlim=(-lim, lim * 0.35), ylim=(-lim * 0.65, lim * 0.65), aspect='equal', xlabel='Re', ylabel='Im')
    axs[0].set_title(f'Nyquist, fastest mode (T_c = {T_C / 60:.0f} min, refresh {T_REFRESH} s)')
    axs[1].set_title('zoom near -1 (solid: w > 0, dashed: w < 0)')
    axs[0].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / 'nyquist.png', dpi=150)
    plt.show()
