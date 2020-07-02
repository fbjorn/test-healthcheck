import asyncio
import time

import httpx
from invoke import Exit, task


async def check_backend():
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get("http://backend:8080/status", timeout=1)
        except Exception:
            return False
        else:
            if resp.status_code == 200:
                return True
    return False


def wait_for_backend(timeout=10):
    for _ in range(timeout):
        if asyncio.get_event_loop().run_until_complete(check_backend()):
            return
        else:
            time.sleep(1)


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
