"""CLI tools for fluent-telegrinder.

Compilation note
----------------
`fluent.runtime` has no binary bytecode format — there is only the text FTL
parser (fluent.syntax.FluentParser) and an in-memory AST→resolver Compiler
that runs at bundle-load time.

`ftg compile` pre-parses every .ftl file and pickles the
resulting `fluent.syntax.ast.Resource` objects into .ftlc files.
At runtime FluentConfig can load those pickled resources directly, skipping
the text parser entirely.

Benefits
  - Faster startup: no text-parsing overhead for large locale sets.
  - No change to per-message formatting speed (the runtime Compiler still
    walks the AST to build resolver objects; it's already very fast).

Usage
    ftg compile locales/
    ftg compile locales/ --output locales_compiled/ --force
"""

from __future__ import annotations

import pickle
from pathlib import Path

import typer
from fluent.syntax import FluentParser

app = typer.Typer(
    name="ftg",
    help="Fluent translation toolkit for telegrinder.",
    no_args_is_help=True,
)


@app.command()
def compile(  # noqa: A001
    folder: Path = typer.Argument(  # noqa: B008
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        help=(
            "Root folder with locale subdirectories containing "
            ".ftl files (e.g. locales/)."
        ),
    ),
    output: Path | None = typer.Option(  # noqa: B008
        None,
        "--output",
        "-o",
        help=(
            "Output folder for .ftlc files. "
            "Mirrors the source folder structure. "
            "Defaults to the same location as each .ftl file."
        ),
    ),
    force: bool = typer.Option(  # noqa: B008
        False,  # noqa: FBT003
        "--force",
        "-f",
        help="Overwrite existing .ftlc files.",
    ),
) -> None:
    """Pre-compile .ftl files into .ftlc (pickled AST) for faster startup.

    Parses every .ftl file found recursively under FOLDER and serialises the
    parsed AST (fluent.syntax.ast.Resource) with pickle.  The resulting .ftlc
    files are later loaded by FluentConfig(use_compiled=True), which skips the
    text-parsing step entirely.

    Example::

        ftg compile locales/
        # or to a separate output tree:
        ftg compile locales/ -o locales_compiled/ --force
    """
    parser = FluentParser(with_spans=False)
    compiled = 0
    skipped = 0
    errors = 0

    ftl_files = sorted(folder.rglob("*.ftl"))
    if not ftl_files:
        typer.echo(
            typer.style(
                f"No .ftl files found under {folder}",
                fg=typer.colors.YELLOW,
            ),
        )
        raise typer.Exit(1)

    for ftl_file in ftl_files:
        if output is not None:
            rel = ftl_file.parent.relative_to(folder)
            out_dir = output / rel
        else:
            out_dir = ftl_file.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / (ftl_file.stem + ".ftlc")

        if out_file.exists() and not force:
            typer.echo(
                typer.style("SKIP  ", fg=typer.colors.BRIGHT_BLACK)
                + str(ftl_file)
                + typer.style(
                    " (use --force to overwrite)",
                    fg=typer.colors.BRIGHT_BLACK,
                ),
            )
            skipped += 1
            continue

        try:
            source = ftl_file.read_text(encoding="utf-8")
            resource = parser.parse(source)
        except Exception as exc:  # noqa: BLE001
            typer.echo(
                typer.style("ERROR ", fg=typer.colors.RED)
                + str(ftl_file)
                + f": {exc}",
            )
            errors += 1
            continue

        with out_file.open("wb") as fh:
            pickle.dump(resource, fh, protocol=pickle.HIGHEST_PROTOCOL)

        typer.echo(
            typer.style("OK    ", fg=typer.colors.GREEN)
            + str(ftl_file)
            + typer.style(f" → {out_file}", fg=typer.colors.BRIGHT_BLACK),
        )
        compiled += 1

    parts = []
    if compiled:
        parts.append(
            typer.style(f"{compiled} compiled", fg=typer.colors.GREEN),
        )
    if skipped:
        parts.append(
            typer.style(f"{skipped} skipped", fg=typer.colors.BRIGHT_BLACK),
        )
    if errors:
        parts.append(
            typer.style(f"{errors} errors", fg=typer.colors.RED),
        )
    typer.echo("\n" + ", ".join(parts) + ".")

    if errors:
        raise typer.Exit(1)
