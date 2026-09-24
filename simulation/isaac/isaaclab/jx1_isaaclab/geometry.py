"""Torch geometry shared by the Isaac Lab terms (no Isaac imports, so rl/tests can check it against the numpy version)."""
import torch


def project_to_polygon(p: torch.Tensor, poly: torch.Tensor) -> torch.Tensor:
    """Project points p (N, 2) into the convex polygon poly (k, 2) (same algorithm as rl/jx1_rl/policy_io.py)."""
    a, b = poly, torch.roll(poly, -1, dims=0)
    e = b - a
    area = 0.5 * torch.sum(a[:, 0] * b[:, 1] - b[:, 0] * a[:, 1])
    s = 1.0 if area >= 0 else -1.0
    d = p[:, None, :] - a[None]
    inside = torch.all(s * (e[:, 0] * d[..., 1] - e[:, 1] * d[..., 0]) >= -1e-12, dim=1)
    t = torch.clamp((d * e).sum(-1) / (e * e).sum(-1), 0.0, 1.0)
    c = a[None] + t[..., None] * e[None]
    best = c[torch.arange(p.shape[0], device=p.device), torch.argmin(((c - p[:, None, :]) ** 2).sum(-1), dim=1)]
    return torch.where(inside[:, None], p, best)
