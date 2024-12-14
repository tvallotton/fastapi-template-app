from string import Formatter


def escape_ident(ident):
    ident = ident.replace('"', '""')
    return f'"{ident}"'


def escape_expr(expr):
    expr = str(expr)
    expr = expr.replace("'", "''")
    return f"'{expr}'"


class SQLFormatter(Formatter):
    def format_field(self, value, format_spec):
        match format_spec:
            case "" | "value":
                value = self.escape_value(value)
            case "ident":
                value = escape_ident(value)

            case "raw":
                return super().format_field(value, "")

        return super().format_field(value, "")

    def escape_value(self, expr):
        if isinstance(expr, list):
            return self.escape_array(expr)
        if isinstance(expr, bytes):
            return self.escape_bytes(expr)
        return escape_expr(expr)

    def escape_bytes(self, bytes: bytes):
        return f"'\\x{bytes.hex()}'"

    def escape_array(self, array: list[str]):
        values = ",".join(map(escape_expr, array))
        return f"array[{values}]"
