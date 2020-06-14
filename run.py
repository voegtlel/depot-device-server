import os
from wsgiref.simple_server import make_server


def main():
    import server

    with make_server('127.0.0.1', 8002, server.app) as httpd:
        print("Server up at localhost:8002")
        httpd.serve_forever()


if __name__ == '__main__':
    import watchgod

    class PythonConfigWatcher(watchgod.DefaultDirWatcher):
        ignored_dirs = watchgod.DefaultDirWatcher.ignored_dirs | {'venv'}

        def should_watch_file(self, entry):
            return entry.name.endswith(('.py', '.pyx', '.pyd', '.yaml'))

    watchgod.run_process(os.getcwd(), main, watcher_cls=PythonConfigWatcher)
