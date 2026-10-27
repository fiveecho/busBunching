# Learning log

This project was fundamentally a way to reinforce my understanding of controls and dynamical systems. After completing the second-year control systems course, although I enjoyed the ideas and intentions behind the teaching, I struggled when concepts became overly theoretical without linking to real-world examples. As such, I wanted to work on something with relevance to both my life and technical knowledge, concretely establishing concepts rather than taking face-value solutions and algorithmically solving problems.

Upon reflection, I was unhappy with my unfamiliarity with stability analysis, and wanted to see these control concepts applied to an actual system context. I chose bus bunching as an area of focus, one because I have joked about this particular bus service bunching with my friends many times, but also because it serves as a potent testbed for me to flesh out whatever theory I had learnt in my education. The connection to my future career in the land transportation sector was also a plus.

This project stretched me in ways I was not expecting. Coming in with a head of steam and hubris from what I thought was a technically rigorous continuous-time linear systems course, I was soon stumped by discretisation, stochasticity, multiple controllers and other issues I had brought upon myself. Through the implementation of this project, I had to pick up a few bits of knowledge through self-directed learning to ensure that this project was not just a shell of what I had envisioned it to be, including detours into linear algebra, difference equations, saturation in feedback loops, modal analysis, stochastic modelling, and other concepts I had not met in my formal education. Much of this came from working through problems with Claude Code, and then reviewing the results in my own simulations. Below I have documented the concepts I picked up.

## Control and dynamics

### Lags and delays cost phase differently

A first-order lag 1/(τs + 1) approaches its target gradually, never overshoots, and costs at most 90° of phase. A pure delay e^{−sτ} gives the same response shifted in time, and costs phase without limit as frequency rises, which makes it the more dangerous of the two. A real driver is roughly both: a short reaction delay, then a gradual adjustment. A zero-order hold behaves roughly like a delay of half a period.

### Bus bunching is an unstable plant driven by a disturbance


### Stabilising an open-loop-unstable plant needs a minimum gain as well as a maximum
*Worked out through discussion, building on Daganzo and Pilachowski (2011).*

Per mode, the plant is 1/(s − β_θ), with a right-half-plane pole set by the boarding rate β. The controller has to supply enough negative feedback to beat it: α > β/2, which is T_c below about 74 min. The update delay caps the gain from above. So the controller has a stability window, not just an upper limit.

In Nyquist terms, with one open-loop RHP pole, the plot must encircle −1 once anticlockwise; avoiding it is not enough. Leaving out Daganzo and Pilachowski's cancellation term is what made this lower edge appear. With that term, their law is stable for any positive gain.

The upper edge, at 2T < T_c (about 20 s at a 10 s display refresh), is the same as their condition αΔt < 0.5: the sampled pole is z = 1 − KT. I reproduced it for my setup and then checked it against their eigenvalues (eq. 25).

### Diagonalising a platoon: the graph Laplacian
*Worked through myself, following Lestas and Vinnicombe (2007, section III), with help from Claude.*

For the spring law on an open chain with "ghost" end buses, I:

1. bounded the eigenvalues to [0, 4] with Gershgorin discs;
2. solved the interior recurrence;
3. showed its characteristic roots lie on the unit circle, because their product is 1;
4. treated the ghost buses as mirror boundary conditions (y₀ = y₁ and y_{N+1} = y_N).

That gives λ_k = 2 − 2cos(kπ/N), with mode shapes cos((n − ½)kπ/N). I also checked the repeated-root cases: λ = 0 is the "all buses equally late" mode, and λ = 4 is not an eigenvalue of the open chain.

- **Lesson:** a shift-invariant system is diagonalised by waves (e^{inθ}), in the same way an LTI system is diagonalised by e^{st}. Boundaries decide which waves fit.

### Ring versus open chain, and the limits of eigenvalues
*Worked out through discussion; checked numerically.*

On a ring, the boarding matrix and the spring matrix share eigenvectors, so the coupled pole has a closed form: s(θ) = (β − 2α)(1 − cos θ) + iβ sin θ. On the open chain they do not, so I computed the eigenvalues numerically instead. The stability edge matched the ring formula to within 0.3%.

The boarding coupling is one-sided, so the matrix is non-normal. Disturbances can then grow for a while as they travel down the chain, even when every eigenvalue is stable. This is related to string stability.

- **Lesson:** eigenvalues settle asymptotic stability, but not how large a disturbance gets on the way.

### Boarding is a first derivative, the spring is a Laplacian

I was uneasy about using the spring's eigenvectors to analyse the boarding matrix, since they are different matrices. The fix was to notice that boarding acts like a first derivative along the platoon, and to split it exactly:

lₙ − lₙ₋₁ = ½(2lₙ − lₙ₋₁ − lₙ₊₁) + ½(lₙ₊₁ − lₙ₋₁)

That is, B = ½L + C + D, where:

- **½L** is half the Laplacian, an anti-diffusion term;
- **C** is a centred difference (skew-symmetric). It is transport: patterns travel along the platoon without growing;
- **D** is a pair of end terms.

The whole system is then −(α − β/2)L + βC + βD. Half of B is the Laplacian, which is why the spring's eigenvectors work. The stability edge is simply net diffusion α − β/2 reaching zero.

- **Lesson:** C is skew-symmetric, so its eigenvalues are purely imaginary. On its own it rotates patterns (travelling waves) without growing or shrinking them. On a ring it shares the Laplacian's eigenvectors, so it only shifts each pole vertically and cannot change stability.
- **Lesson (worked out through discussion):** any square matrix splits uniquely into a symmetric part and a skew-symmetric part, M = ½(M + Mᵀ) + ½(M − Mᵀ), much as a function splits into even and odd parts. For dx/dt = Mx, d‖x‖²/dt = 2xᵀMx only sees the symmetric part, because xᵀCx = 0 for any skew-symmetric C. So the symmetric part decides growth and the skew part only rotates. It is the natural first move when a non-symmetric matrix appears and the tools I have (real eigenvalues, Gershgorin, orthogonal modes) need symmetry. The same split appears through Taylor expansion: a backward difference is a centred derivative plus half a second difference, f(n) − f(n−1) ≈ f′ − ½f″. This is the "numerical diffusion" of one-sided (upwind) differencing in computational fluid dynamics, with the opposite sign here.

### Discrete or continuous? One model, with continuous as a limit




### Saturation: slow-only control and headroom
*Worked out through discussion; measured in simulation.*

Capping the command at the cruise speed removes half the restoring force: a bus that is behind cannot catch up. Headroom δ moves the operating point below the cap so both halves work again, at the cost of trip time. A stronger gain can partly make up for missing headroom.

- **Lesson:** a saturation inside a loop changes how the controller should be designed, not just how well it performs.

### Instability over a finite time is gradual

Just past the 74 min edge, errors grow, but slowly: about 1.75× over an hour, against about 25× with no control. So over a one-hour trip, performance worsens smoothly rather than collapsing. Aggregate metrics are monotonic in the gain, so they cannot locate the edge. Only a growth rate can.

## Stochastic modelling and statistics

- **Zero-mean noise is not neutral for a quadratic metric.** E[(h + Δ)²] = h² + Var(Δ). Overtaking (re-sorting arrivals) removes some of that increase. This explained why excess wait time stayed flat across the expressway: independent noise split up bunched pairs.
- **Modelling assumptions shape results.** That un-bunching only happens because each bus draws its own expressway speed. Real buses close together share traffic. This led me to reconsider what the noise standard deviation means: differences between buses, not day-to-day variation.
- **Truncating a distribution can change its mean and its spread.** Bounds of [15, 45] km/h raised the mean as noise grew. Bounds at ±1σ cut the actual sd to 0.54σ. Symmetric ±3σ bounds fixed both.
- **Independent samples.** Buses within one run share a history, so confidence intervals must use one value per run. Pooling every trip would have made them about 5× too narrow.

## Metrics

- **Excess wait time is quadratic in headway.** Passengers arrive at a steady rate, so a gap of length h collects passengers in proportion to h, and each waits h/2 on average. The total waiting in that gap is therefore proportional to h × h/2 = h²/2. Long gaps cost twice over: more people are caught in them, and each one waits longer. For example, gaps of 100 s and 500 s give 66.7 s more average wait than two even 300 s gaps, even though the mean headway is the same.
- **EWT cannot see a shift common to all buses.** If every bus is late by the same amount, EWT is zero. That is the λ = 0 mode, which the spring law does not control either.
- **EWT assumes the mean headway equals H.** It can go negative when control speeds buses up.

## Engineering practice

- **Pass parameters explicitly, rather than through module-level globals.** A global is hidden state, and it would silently reset in parallel worker processes.
- **Write the batch loop once** (`run_batch`). New experiments become short scripts, and every experiment computes its metrics the same way.
- **Predict, then simulate.** Most results here (the stability window, the oscillation onset, the boarding-noise amplification) were predicted first and then checked. The expressway effect was the exception: a surprise in the data, explained afterwards with a targeted test.
