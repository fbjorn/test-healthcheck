import socket
import time

from invoke import Exit, task


def wait_for_backend(timeout=10):
    for _ in range(timeout // 2):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(("backend", 8080))
            s.close()
            return
        except socket.error:
            pass
        time.sleep(2)


@task()
def worker(ctx):
    wait_for_backend()

    from worker.main import run_worker

    run_worker()


@task()
def check(ctx):
    code = 0
    code += ctx.run("flake8", shell="/bin/sh", warn=True).exited  # noqa
    code += ctx.run("mypy worker", shell="/bin/sh", warn=True).exited  # noqa
    if code != 0:
        raise Exit(code)


@task(pre=[check])
def test(ctx):
    ctx.run("pytest", shell="/bin/sh")  # noqa
