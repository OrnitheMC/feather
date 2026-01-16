import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from queue import Queue, Empty
from threading import Thread
from typing import Callable, Tuple, Optional


class AbstractThreadExecutor:
    def __init__(self):
        self.__name: str = self.__class__.__name__
        self.__stopped_looping: bool = False
        self._executor_thread: Optional[Thread] = None

    def should_keep_looping(self) -> bool:
        return not self.__stopped_looping

    def stop(self) -> None:
        self.__stopped_looping = True

    def start(self) -> Thread:
        self._executor_thread: Optional[Thread] = self.start_thread(self.loop, (), self.__name)
        return self._executor_thread

    def loop(self) -> None:
        while self.should_keep_looping():
            self.tick()

    def tick(self) -> None:
        raise NotImplementedError()

    def join(self) -> None:
        if self._executor_thread is None:
            raise RuntimeError()
        self._executor_thread.join()

    @staticmethod
    def start_thread(func: Callable, args: Tuple, name: Optional[str] = None) -> Thread:
        thread: Thread = Thread(target=func, args=args, name=name, daemon=True)
        thread.start()
        return thread


class BuildExecutor(AbstractThreadExecutor):
    def __init__(self, max_processes: int = 4):
        super().__init__()
        self._max_processes: int = max_processes
        self._queue: Queue[str] = Queue(maxsize=10_000)
        self._running_processes: dict[Thread, GradleProcess] = {}
        self._timeout: Optional[datetime] = None
        self._BUILD_TEMP_DIR: str = "build_temp"
        if not os.path.exists(self._BUILD_TEMP_DIR):
            os.mkdir(self._BUILD_TEMP_DIR)
        self._exit_code: int = 0

    def schedule(self, version: str) -> None:
        print(f"Scheduled version {version}")
        self._queue.put(version)

    def tick(self) -> None:
        time.sleep(0.5)
        self._process_checker()
        if len(self._running_processes) >= self._max_processes:
            return
        if self._queue.empty():
            return
        try:
            version: str = self._queue.get(block=False)
            if self._is_being_processed(version):
                return
            gradle_process: GradleProcess = GradleProcess(self._BUILD_TEMP_DIR, version)
            process: Thread = self.start_thread(gradle_process.start, (), version)
            self._running_processes[process] = gradle_process
        except Empty:
            pass

    def _is_being_processed(self, version: str) -> bool:
        for thread, process in self._running_processes.copy().items():
            if process.get_version() == version:
                return True
        return False

    def get_exit_code(self) -> int:
        return self._exit_code

    def _process_checker(self) -> None:
        for thread, process in self._running_processes.copy().items():
            if thread.is_alive():
                continue
            if process.get_exit_code() != 0:
                print(f"{process.get_version()} got exit code {process.get_exit_code()}")
                self._exit_code = process.get_exit_code()
                sys.exit(process.get_exit_code())
            self._running_processes.pop(thread)
        if len(self._running_processes) > 0 or not self._queue.empty():
            self._timeout = None
            return
        if self._timeout is None:
            self._timeout = datetime.now() + timedelta(seconds=15)
        elif datetime.now() > self._timeout:
            time.sleep(2)
            print("Done!")
            self.stop()

    def stop(self) -> None:
        super().stop()
        if os.path.exists(self._BUILD_TEMP_DIR):
            shutil.rmtree(self._BUILD_TEMP_DIR)


class GradleProcess:
    def __init__(self, build_dir: str, version: str):
        self._version: str = version
        self._build_dir: str = build_dir
        self._version_dir: str = os.path.join(self._build_dir, self._version)
        self._gradle_command: str = "gradlew" if os.name == "nt" else "./gradlew"
        self._process: Optional[subprocess.Popen] = None
        self._times_run: int = 0
        self._TO_COPY: list[str] = ["gradle", "src", "mappings", "unpick-definitions", "build.gradle", "gradle.properties", "gradlew", "gradlew.bat", "named-mappings-builds.json", "nests-builds.json", "settings.gradle"]

    def start(self) -> None:
        while self._should_retry():
            self._times_run += 1
            print(f"Version {self._version}")
            self._delete_dir()
            os.mkdir(self._version_dir)
            self._get_ready()
            self._run_gradle_command()
            self._process_listener()
            while self._process.poll() is None:
                time.sleep(0.5)
            self._delete_dir()
            if self.get_exit_code() == 0:
                return

    def _should_retry(self) -> bool:
        return self._times_run <= 2

    def _delete_dir(self) -> None:
        if os.path.isdir(self._version_dir):
            shutil.rmtree(self._version_dir)

    def _get_ready(self) -> None:
        for element in self._TO_COPY:
            if os.path.isdir(element):
                shutil.copytree(element, os.path.join(self._version_dir, element))
            else:
                shutil.copy(element, os.path.join(self._version_dir, element))

    def get_exit_code(self) -> int:
        return self._process.returncode

    def get_version(self) -> str:
        return self._version

    def _run_gradle_command(self) -> None:
        env = os.environ.copy()
        env["MC_VERSION"] = self._version
        # shell=True, check=True, env=env
        self._process = subprocess.Popen(
            f"{self._gradle_command} publish --stacktrace",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            env=env,
            cwd=self._version_dir
        )

    def _process_listener(self) -> None:
        while True:
            try:
                text: bytes = next(iter(self._process.stdout))
            except StopIteration:
                break
            else:
                print(f"[{self._version}] {text.decode('utf-8')[:-1]}")


def main():
    versions: list[str] = os.getenv("MC_VERSIONS", "").split(",")
    builder: BuildExecutor = BuildExecutor(max_processes=1)  # single process... for now
    builder.start()
    for version in versions:
        if not version.strip():
            continue
        builder.schedule(version)
    builder.join()
    print("Bye~")
    sys.exit(builder.get_exit_code())


if __name__ == '__main__':
    main()
