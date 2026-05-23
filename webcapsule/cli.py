"""
cli.py - WebCapsule command-line interface.

Four commands, each self-contained and easy to script:

  webcapsule save URL [--collection NAME] [--no-screenshot] [--tag TAG]...
  webcapsule search QUERY [--limit N]
  webcapsule list [--limit N]
  webcapsule open PATH
  webcapsule export PATH [--format zip|tar]
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from webcapsule import (
    __version__,
    archive,
    fetcher,
    markdown_gen,
    metadata,
    parser,
    screenshot,
    search,
)

app = typer.Typer(
    name="webcapsule",
    help="Turn fragile links into durable knowledge.",
    add_completion=False,
)
console = Console()

# Default archive root: ~/webcapsule
_DEFAULT_ARCHIVE = Path.home() / "webcapsule"


def _archive_root() -> Path:
    """Return the archive root from the environment or the default."""
    root = Path(os.environ.get("WEBCAPSULE_ARCHIVE", _DEFAULT_ARCHIVE))
    root.mkdir(parents=True, exist_ok=True)
    return root


def _open_path(path: Path) -> None:
    """Open *path* using the platform default application."""
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
        return

    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.run([opener, str(path)], check=True)


# ---------------------------------------------------------------------------
# webcapsule save
# ---------------------------------------------------------------------------


@app.command()
def save(
    url: Annotated[str, typer.Argument(help="URL of the page to archive.")],
    collection: Annotated[
        str, typer.Option("--collection", "-c", help="Collection / topic folder.")
    ] = "general",
    tag: Annotated[
        list[str] | None, typer.Option("--tag", "-t", help="Tag to attach (repeatable).")
    ] = None,
    no_screenshot: Annotated[
        bool, typer.Option("--no-screenshot", help="Skip screenshot capture.")
    ] = False,
    force_browser: Annotated[
        bool, typer.Option("--browser", help="Force headless browser (useful for SPAs).")
    ] = False,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Fetch and parse without writing a capsule.")
    ] = False,
    force: Annotated[
        bool, typer.Option("--force", help="Save even if this URL was archived recently.")
    ] = False,
) -> None:
    """Save a web page as a self-contained knowledge capsule."""

    root = _archive_root()
    tags = tag or []

    if not force and not dry_run:
        recent = archive.find_recent_capsule(root, url)
        if recent:
            console.print(
                "[yellow]Skipped:[/] this URL was archived in the last 24 hours.\n"
                f"  [dim]{recent}[/]\n"
                "Use [bold]--force[/] to save it again."
            )
            raise typer.Exit()

    try:
        with console.status(f"[bold cyan]Fetching[/] {url}"):
            raw_html = fetcher.fetch(url, force_browser=force_browser)
    except Exception as exc:
        console.print(f"[bold red]Error:[/] could not fetch {url}\n  {exc}")
        raise typer.Exit(code=1) from None

    try:
        with console.status("[bold cyan]Parsing content..."):
            page = parser.parse(raw_html)
    except Exception as exc:
        console.print(f"[bold red]Error:[/] content parsing failed\n  {exc}")
        raise typer.Exit(code=1) from None

    try:
        with console.status("[bold cyan]Extracting metadata..."):
            meta = metadata.extract(raw_html, url, page, tags=tags)
    except Exception as exc:
        console.print(f"[bold red]Error:[/] metadata extraction failed\n  {exc}")
        raise typer.Exit(code=1) from None

    try:
        with console.status("[bold cyan]Generating Markdown..."):
            md = markdown_gen.generate(page, url, tags=tags)
    except Exception as exc:
        console.print(f"[bold red]Error:[/] Markdown generation failed\n  {exc}")
        raise typer.Exit(code=1) from None

    if dry_run:
        console.print("[bold green]OK Dry run complete[/]")
        console.print(f"  Title: {meta.get('title') or page.title or '-'}")
        console.print(f"  Words: {meta.get('word_count', 0)}")
        console.print("  No files written.")
        raise typer.Exit()

    screenshot_bytes: bytes | None = None
    if not no_screenshot:
        import tempfile

        with console.status("[bold cyan]Capturing screenshot..."):
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = Path(tmp.name)
            try:
                screenshot.capture(url, tmp_path)
                screenshot_bytes = tmp_path.read_bytes()
            except Exception as exc:
                console.print(f"[yellow]Warning:[/] screenshot failed ({exc})")
            finally:
                if tmp_path.exists():
                    tmp_path.unlink()

    try:
        with console.status("[bold cyan]Writing capsule..."):
            capsule_dir = archive.write_capsule(
                archive_root=root,
                collection=collection,
                url=url,
                raw_html=raw_html,
                page=page,
                markdown=md,
                metadata=meta,
                screenshot_data=screenshot_bytes,
            )
    except Exception as exc:
        console.print(f"[bold red]Error:[/] could not write capsule to disk\n  {exc}")
        raise typer.Exit(code=1) from None

    try:
        with console.status("[bold cyan]Indexing..."):
            search.index_capsule(root, capsule_dir, meta)
    except Exception as exc:
        console.print(
            f"[yellow]Warning:[/] search indexing failed ({exc}). Run 'webcapsule rebuild-index' to fix."
        )

    console.print(f"\n[bold green]OK Capsule saved[/]\n  [dim]{capsule_dir}[/]")


# ---------------------------------------------------------------------------
# webcapsule search
# ---------------------------------------------------------------------------


@app.command("search")
def search_cmd(
    query: Annotated[str, typer.Argument(help="Full-text search query.")],
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results to show.")] = 20,
) -> None:
    """Search your archive with full-text search."""

    root = _archive_root()
    results = search.search(root, query, limit=limit)

    if not results:
        console.print("[yellow]No results found.[/]")
        raise typer.Exit(code=1)

    table = Table(title=f'Results for "{query}"', show_lines=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("Title", style="bold")
    table.add_column("Archived", style="cyan", width=12)
    table.add_column("URL", style="dim", overflow="fold")

    for i, r in enumerate(results, start=1):
        table.add_row(str(i), r["title"] or "-", (r["archived"] or "")[:10], r["url"])

    console.print(table)


# ---------------------------------------------------------------------------
# webcapsule list
# ---------------------------------------------------------------------------


@app.command("list")
def list_cmd(
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max entries to show.")] = 50,
) -> None:
    """List all archived capsules, newest first."""

    root = _archive_root()
    capsules = search.list_all(root, limit=limit)

    if not capsules:
        console.print(
            "[yellow]No capsules archived yet. Run [bold]webcapsule save URL[/] to start."
        )
        raise typer.Exit()

    table = Table(title="Your WebCapsule Archive", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Title", style="bold")
    table.add_column("Archived", style="cyan", width=12)
    table.add_column("Words", justify="right", width=7)
    table.add_column("Tags", style="magenta")

    for i, c in enumerate(capsules, start=1):
        table.add_row(
            str(i),
            c["title"] or "-",
            (c["archived"] or "")[:10],
            str(c["word_count"] or 0),
            c["tags"] or "-",
        )

    console.print(table)
    console.print(f"\n[dim]Archive root: {root}[/]")


# ---------------------------------------------------------------------------
# webcapsule open
# ---------------------------------------------------------------------------


@app.command("open")
def open_cmd(
    path: Annotated[Path, typer.Argument(help="Capsule directory or file to open.")],
) -> None:
    """Open a capsule in the default application."""

    target = path.expanduser()
    if not target.exists():
        console.print(f"[red]Error:[/] path does not exist: {target}")
        raise typer.Exit(code=1)

    if target.is_dir() and (target / "README.md").exists():
        target = target / "README.md"

    try:
        _open_path(target)
    except Exception as exc:
        console.print(f"[red]Error:[/] could not open {target}\n  {exc}")
        raise typer.Exit(code=1) from None

    console.print(f"[bold green]OK Opened:[/] {target}")


# ---------------------------------------------------------------------------
# webcapsule export
# ---------------------------------------------------------------------------


@app.command()
def export(
    output: Annotated[Path, typer.Argument(help="Destination path for the exported archive.")],
    fmt: Annotated[str, typer.Option("--format", "-f", help="Export format: zip or tar.")] = "zip",
) -> None:
    """Export the entire archive as a portable ZIP or TAR file."""

    root = _archive_root()

    if fmt not in ("zip", "tar"):
        console.print("[red]Error:[/] --format must be 'zip' or 'tar'.")
        raise typer.Exit(code=1)

    # shutil.make_archive expects the path without extension.
    base = str(output).removesuffix(f".{fmt}").removesuffix(".tar.gz")
    fmt_arg = "gztar" if fmt == "tar" else "zip"

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(f"Exporting archive as {fmt}...", total=None)
        result = shutil.make_archive(base, fmt_arg, root_dir=root.parent, base_dir=root.name)

    console.print(f"[bold green]OK Exported:[/] {result}")


# ---------------------------------------------------------------------------
# webcapsule rebuild-index
# ---------------------------------------------------------------------------


@app.command("rebuild-index")
def rebuild_index_cmd() -> None:
    """Rebuild the search index from all capsule metadata.json files on disk."""

    root = _archive_root()
    with console.status("[bold cyan]Rebuilding search index..."):
        count = search.rebuild_index(root)
    console.print(f"[bold green]OK Indexed {count} capsule(s)[/]")


# ---------------------------------------------------------------------------
# webcapsule version / entry point
# ---------------------------------------------------------------------------


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool, typer.Option("--version", "-V", help="Show version and exit.")
    ] = False,
) -> None:
    if version:
        console.print(f"WebCapsule {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


if __name__ == "__main__":
    app()
