from rich.console import Console
from rich.highlighter import RegexHighlighter
from rich.theme import Theme

from app.environment import LOG_LEVEL


class SQLHighlighter(RegexHighlighter):
    base_style = "query."
    highlights = [
        r"(?P<symbol>[^\w])",
        r"(?P<identifier>\w+)",
        r'(?P<identifier>"[^"]+")',
        r"(?P<literal>'[^']+')",
        r"(?:[^\w]|^)(?P<keyword>"
        r"select|values|insert into|returning|on conflict|and|or|not|create"
        r"|drop|delete|default|in|from|on|join|inner|left|right|update|set"
        r"|where|having|order by)(?:[^\w]|$)",
    ]


theme = Theme(
    {
        "query.keyword": "bold #699fe6",
        "query.identifier": "",
        "query.literal": "bold #7be071",
        "query.symbol": "#ed9ee9",
    }
)

console = Console(highlighter=SQLHighlighter(), theme=theme)


def log_sql(sql):
    if LOG_LEVEL in ["INFO", "DEBUG"]:
        console.print(
            "[green]INFO[/green][white]:[/white]\t ", sql.replace("\n", "\n\t  ")
        )
