import asyncio as io
import os
import subprocess
from argparse import ArgumentParser
import importlib
import signal

p = print

parser = ArgumentParser("Anonyxwatch")
parser.add_argument("--app", dest="app", required=True, help="example => watchdog.py --app main:app")

args = parser.parse_args()

class Monitor:
    def __init__(self):
        self.previous_size = None
        self.system = os.name
        self.cool_down = 3
        self.process = None

    async def get_directory_size(self, path='.'):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        return total_size

    async def initiate(self):
        self.previous_size = await self.get_directory_size()

    def start_server(self):
        script, app_name = str(args.app).split(':')
        if self.system == 'nt':
            py_ = 'python'
            clear_cmd = 'cls'
        else:
            py_ = 'python3'
            clear_cmd = 'clear'

        os.system(clear_cmd)
        self.process = subprocess.Popen([py_, '-m', script, '.py'], shell=False)

    def stop_server(self):
        if self.process:
            self.process.terminate()
            self.process.wait()

    async def monitor(self):
        while True:
            if (current_size := await self.get_directory_size()) != self.previous_size:
                self.previous_size = current_size
                return True
            else:
                if self.system != 'nt':
                    try:
                        result = subprocess.run(['git', 'pull'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        if result.returncode != 0:
                            p(f"Git pull error: {result.stderr.decode('utf-8')}")
                    except Exception as e:
                        p(f"Error during git pull: {str(e)}")

            await io.sleep(self.cool_down)

    async def run(self):
        try:
            await self.initiate()
            self.start_server()

            if await self.monitor():
                self.stop_server()
                p("Restarting server...")
                return

        except Exception as e:
            p(e)

def runner():
    while True:
        try:
            io.run(Monitor().run())
        except KeyboardInterrupt:
            break
        except Exception as e:
            p(e)
            break

if __name__ == "__main__":
    runner()
