from sanic import Sanic

import sanic, sanic.exceptions, asyncio, json

from uuid_extensions import uuid7str

app = Sanic("ding")

class QueuePool:
    def __init__(self):
        self.queues: dict[str, asyncio.Queue] = {}

    def __call__(self, id):
        if q := self.queues.get(id):
            return q
        self.queues[id] = asyncio.Queue(8)
        return self.queues[id]

    def __getitem__(self, id):
        return self.queues[id]

@app.before_server_start
async def set_up_queues(app, _loop):
    app.ctx.queues = QueuePool()

@app.get("/")
async def slash(request):
    return sanic.html("""
<!DOCTYPE html>
<html>
    <head><title>nahhhhhhh</title><style>body{font-family:sans-serif;background-color:white;color:black;}@media (prefers-color-scheme: dark){body{background-color:black;color:white;}}</style></head>
    <body><h1>You shall not pass!</h1><p>This is an <b>API-only</b> server and definitely not an FBI honeypot.</p></body>
</html>
    """)

async def feed(queue: asyncio.Queue):
    while True:
        item = await queue.get()
        yield item
        queue.task_done()
        await asyncio.sleep(0)

@app.websocket("/ws/<item>")
async def ws(_request, ws, item):
    async for res in feed(app.ctx.queues(item)):
        await ws.send(json.dumps(res))

@app.get("/stream/<item>")
async def get(request, item):
    response = await request.respond(content_type="application/jsonl")
    async for res in feed(app.ctx.queues(item)):
        await response.send(json.dumps(res))
    await response.eof()

@app.post("/post/<item>")
async def post(request, item):
    data = request.json
    try:
        queue: asyncio.Queue = app.ctx.queues[item]
    except KeyError:
        return sanic.json("ok:nosend")
    await queue.put(data)
    return sanic.json("ok")
