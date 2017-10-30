import asyncio
from proxybroker import Broker

proxyList = []
async def show(proxies):
    while True:
        proxy = await proxies.get()
        if proxy is None:
            break
        print('Found proxy: %s' % proxy)
        strProxy = str(proxy)
        proxyList.append({'http':strProxy.split("] ",1)[1].split(">",1)[0]})

proxies = asyncio.Queue()
broker = Broker(proxies)
tasks = asyncio.gather(
    broker.find(types=['HTTP', 'HTTPS'], limit=10),
    show(proxies))

loop = asyncio.get_event_loop()
loop.run_until_complete(tasks)

print(proxyList)
