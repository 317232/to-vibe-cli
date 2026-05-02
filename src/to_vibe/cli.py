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
    """运行 to-vibe 工程化流程 (启动 TUI)"""
    click.echo(f"to-vibe run {project_path}")
    click.echo("启动 TUI 应用...")

    # TUI owns the full pipeline via PipelineIntegration running inside ToVibeApp
    from to_vibe.tui.app import ToVibeApp
    app = ToVibeApp(project_path=project_path)
    app.run()


@main.command()
def learn() -> None:
    """从已有 artifacts 中提取学习记忆"""
    from to_vibe.config import load_config as load_vibe_config
    from to_vibe.learn.learn import LegacyLearnCollector

    click.echo("to-vibe learn")
    click.echo("从 pipeline artifacts 中收集学习记忆...")

    config = load_vibe_config(".")
    collector = LegacyLearnCollector(".", config.learn)
    learn_result = collector.collect()

    click.echo(f"学习完成: {learn_result.items_learned} 条记忆")


if __name__ == "__main__":
    main()