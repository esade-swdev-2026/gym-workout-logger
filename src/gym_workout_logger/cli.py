import typer

app = typer.Typer(help="Replace this with your project's command-line interface.")


@app.callback()
def main() -> None:
    """A terminal gym workout logger."""


@app.command()
def add_exercise(
    name: str,
    muscle_group: str = typer.Option("full body", "--muscle-group"),
) -> None:
    """Add an exercise to your workout."""
    if not name.strip():
        typer.echo("Exercise name cannot be empty.", err=True)
        raise typer.Exit(code=1)

    if not muscle_group.strip():
        typer.echo("Muscle group cannot be empty.", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Exercise: {name.strip()} | Muscle group: {muscle_group.strip()}")


if __name__ == "__main__":
    app()
