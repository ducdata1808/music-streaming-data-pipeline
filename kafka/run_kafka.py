import subprocess
import time
import signal
import sys
import os
from typing import Optional, List, Dict, Any # for type hint
from colorama import Fore, Style, init # for color output

KAFKA_DIR = "/home/duc1808/kafka/kafka_2.13-3.6.1"

VERBOSE = True # show log message

class Background_colors:
    RED = "\033[41m"
    GREEN = "\033[42m"
    YELLOW = "\033[43m"
    BLUE = "\033[44m"
    MAGENTA = "\033[45m"
    CYAN = "\033[46m"
    END = "\033[0m"

# print message with color
def verbose_output(message: str) -> None:
    if VERBOSE:
        print(f"{message}{Background_colors.END}")

# list to store running processes
processes = []

def signal_handler(sig, frame):
    verbose_output(
        f"{Background_colors.RED} Closing Kafka and Zookeeper..."
    )
    for p in reversed(processes):
        try:
            p.terminate()
            p.wait()
        except Exception as e:
            verbose_output(
                f"{Background_colors.RED} Error closing process: {e}"
            )
    verbose_output(
        f"{Background_colors.GREEN} Closed successfully."
    )
    sys.exit(0)

def main():
    # register signal handler to close
    signal.signal(signal.SIGINT, signal_handler)

    if not os.path.exists(KAFKA_DIR):
        verbose_output(
            f"{Background_colors.RED} Kafka directory not found: {KAFKA_DIR}"
        )
        sys.exit(1)

    verbose_output(
        f"{Background_colors.GREEN} Starting Zookeeper..."
    )
    zk_process = subprocess.Popen(
        ["bin/zookeeper-server-start.sh", "config/zookeeper.properties"],
        cwd=KAFKA_DIR,
        stdout=subprocess.DEVNULL,  # hide zookeeper log
        stderr=subprocess.STDOUT
    )
    processes.append(zk_process)

    # wait 5 seconds for zookeeper to start
    time.sleep(5)

    verbose_output(
        f"{Background_colors.GREEN} Starting Kafka Broker..."
    )
    kafka_process = subprocess.Popen(
        ["bin/kafka-server-start.sh", "config/server.properties"],
        cwd=KAFKA_DIR,
        stdout=subprocess.DEVNULL,  # hide kafka log
        stderr=subprocess.STDOUT
    )
    processes.append(kafka_process)

    verbose_output(
        f"{Background_colors.GREEN} Zookeeper and Kafka are running in background!"
    )
    verbose_output(
        f"{Background_colors.GREEN} Press Ctrl+C to close both.\n"
    )

    # keep main thread running to catch Ctrl+C
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
