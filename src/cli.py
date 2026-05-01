"""CLI entry point for to-vibe."""

import click

from to_vibe import __version__


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """to-vibe: AI 代码工程化 TUI 工具"""
    pass


@main.command()
@click.argument("project_path", type=click.Path(exists=True), default=".")
def run(project_path: str) -> None:
    """运行 to-vibe 工程化流程"""
    click.echo(f"to-vibe run {project_path}")
    # TODO: 启动 TUI 应用


@main.command()
def learn() -> None:
    """从已有 artifacts 中提取学习记忆"""
    click.echo("to-vibe learn")
    # TODO: 运行 Learn 模块


if __name__ == "__main__":
    main()