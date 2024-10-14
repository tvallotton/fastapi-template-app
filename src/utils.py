from fastapi import Response


def redirect(path: str, status=200):
    return Response(status_code=status, headers={"Hx-Location": path})
