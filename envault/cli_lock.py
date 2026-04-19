"""CLI commands for vault lock management."""
from __future__ import annotations

import click

from envault import lock as _lock


@click.group("lock", help="Manage vault lock state.")
def lock_cmd() -> None:
    pass


@lock_cmd.command("status")
@click.option("--vault", required=True, help="Path to the vault file.")
def lock_status(vault: str) -> None:
    """Show whether the vault is currently locked."""
    if _lock.is_locked(vault):
        pid = _lock.owner_pid(vault)
        click.echo(f"LOCKED (pid {pid})")
    else:
        click.echo("UNLOCKED")


@lock_cmd.command("acquire")
@click.option("--vault", required=True, help="Path to the vault file.")
@click.option("--timeout", default=5.0, show_default=True, help="Seconds to wait.")
def lock_acquire(vault: str, timeout: float) -> None:
    """Acquire the vault lock (for scripting / manual use)."""
    try:
        path = _lock.acquire(vault, timeout=timeout)
        click.echo(f"Lock acquired: {path}")
    except _lock.LockError as exc:
        raise click.ClickException(str(exc))


@lock_cmd.command("release")
@click.option("--vault", required=True, help="Path to the vault file.")
def lock_release(vault: str) -> None:
    """Release the vault lock."""
    lp = _lock._lock_path(vault)
    if not lp.exists():
        raise click.ClickException(f"No lock file found at '{lp}'.")
    _lock.release(lp)
    click.echo("Lock released.")
