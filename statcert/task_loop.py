from contextlib import AsyncExitStack


async def strategy_naive_sequential(coroutines):
    return [await coro() for coro in coroutines]


async def run_operation(
    operations,
    records,
    strategy=strategy_naive_sequential,
    callback=None,
):
    def create_task(rec):
        async def task():
            for operation in operations:
                inp = operation.prepare_entry(rec)
                res = await operation.execute(**inp)
                [rec.append(info) for info in res]
                if callback:
                    await callback(rec)

            return rec

        return task

    coros = [create_task(rec) for rec in records]

    async with AsyncExitStack() as stack:
        for operation in operations:
            await stack.enter_async_context(operation)

        results = await strategy(coros)

    return results
