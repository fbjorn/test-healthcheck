import socket
import time

from invoke import Exit, task


def wait_for_db(timeout=10):
    for _ in range(timeout):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(("db", 5432))
            s.close()
            return
        except socket.error:
            pass
        time.sleep(1)


@task()
def server(ctx):
    wait_for_db()

    import backend.main

    backend.main.run_server()


@task()
def check(ctx):
    code = 0
    code += ctx.run("flake8", shell="/bin/sh", warn=True).exited  # noqa
    code += ctx.run("mypy backend", shell="/bin/sh", warn=True).exited  # noqa
    if code != 0:
        raise Exit(code)


@task(pre=[check])
def test(ctx):
    ctx.run("pytest", shell="/bin/sh")  # noqa
