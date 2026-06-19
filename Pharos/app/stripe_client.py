"""Stripe subscription check.

Checks RESTRICTED, read-only keys scoped to Customers + Subscriptions only, across
EVERY configured Stripe account (the one behind Substack, plus the main account for
direct Pharos signups). Subscriptions can't be merged across Stripe accounts, so we
join on the subscriber's email: an active subscription in ANY account grants access.
If no key is configured, returns False and the entitlement layer falls back to the
allowlist + paid-seed cross-check.
"""
from __future__ import annotations

from . import config

_ACTIVE = {"active", "trialing", "past_due"}


def _account_has_active(email: str, api_key: str) -> bool:
    """True if `email` has an active subscription in the Stripe account for `api_key`."""
    try:
        import stripe
    except ImportError:
        return False
    try:
        customers = stripe.Customer.list(email=email, limit=10, api_key=api_key)
        for cust in customers.auto_paging_iter():
            subs = stripe.Subscription.list(customer=cust.id, status="all", limit=20, api_key=api_key)
            for sub in subs.auto_paging_iter():
                if sub.status in _ACTIVE:
                    return True
    except Exception:
        # never let a Stripe hiccup hard-fail a login; treat as "not found here"
        return False
    return False


def stripe_active(email: str) -> bool:
    email = (email or "").strip().lower()
    if not email or not config.STRIPE_API_KEYS:
        return False
    # active in EITHER the Substack account or the direct/main account -> entitled
    return any(_account_has_active(email, key) for key in config.STRIPE_API_KEYS)
