# Future-perturbation test

A deterministic pipeline that claims pre-cutoff outputs depend only on pre-cutoff inputs should normally be invariant when only post-cutoff inputs are perturbed.

CutoffGuard exposes a small helper for this test. A detected change is actionable evidence of future dependence. Stability is weaker evidence: it only supports the specific perturbation family and output surface exercised.
