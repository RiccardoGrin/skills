#!/usr/bin/env python3
"""Server lifecycle manager -- starts dev servers, waits for ports, runs a command, stops servers.

Handles single or multi-server setups (e.g., frontend + API).
Each --cmd/--port pair starts one server. All ports must be ready before the command runs.

Usage:
    python with_server.py --cmd CMD --port PORT [--cmd CMD --port PORT ...] [--wait SECS] -- COMMAND [ARGS...]

Examples:
    python with_server.py --cmd "npm start" --port 3000 -- python verify.py http://localhost:3000 --assert "text:Welcome"
    python with_server.py --cmd "npm run dev" --port 3000 --cmd "python api.py" --port 8000 -- python verify.py http://localhost:3000
"""

import os
import shlex
import subprocess
import sys
import time
import socket
import platform


IS_WINDOWS = platform.system() == "Windows"


def wait_for_port(port, host="localhost", timeout=30):
    """Wait for a TCP port to accept connections."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.5)
    return False


def stop_process(proc):
    """Stop a subprocess and its children, forcefully if needed."""
    if IS_WINDOWS:
        # On Windows, shell=True creates a process tree that proc.terminate()
        # won't fully kill. Use taskkill with /T to kill the entire tree.
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
    else:
        # On Unix, kill the entire process group to ensure all children stop.
        try:
            os.killpg(os.getpgid(proc.pid), 15)  # SIGTERM
            proc.wait(timeout=5)
        except Exception:
            try:
                os.killpg(os.getpgid(proc.pid), 9)  # SIGKILL
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass


def main():
    # Split args at --
    try:
        separator = sys.argv.index("--")
        our_args = sys.argv[1:separator]
        run_cmd = sys.argv[separator + 1:]
    except ValueError:
        print("Usage: python with_server.py --cmd CMD --port PORT -- COMMAND [ARGS...]", file=sys.stderr)
        print("Missing -- separator between server options and command to run", file=sys.stderr)
        sys.exit(1)

    if not run_cmd:
        print("No command specified after --", file=sys.stderr)
        sys.exit(1)

    # Parse our args (manual parsing for multi-value --cmd/--port)
    cmds = []
    ports = []
    wait_timeout = 30
    i = 0
    while i < len(our_args):
        if our_args[i] == "--cmd" and i + 1 < len(our_args):
            cmds.append(our_args[i + 1])
            i += 2
        elif our_args[i] == "--port" and i + 1 < len(our_args):
            ports.append(int(our_args[i + 1]))
            i += 2
        elif our_args[i] == "--wait" and i + 1 < len(our_args):
            wait_timeout = int(our_args[i + 1])
            i += 2
        else:
            print(f"Unknown option: {our_args[i]}", file=sys.stderr)
            sys.exit(1)

    if not cmds:
        print("At least one --cmd is required", file=sys.stderr)
        sys.exit(1)

    if len(ports) < len(cmds):
        print(
            f"Each --cmd needs a --port ({len(cmds)} command(s), {len(ports)} port(s))",
            file=sys.stderr,
        )
        sys.exit(1)

    # Start servers
    processes = []
    popen_kwargs = {}
    if IS_WINDOWS:
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        # Create a new process group so os.killpg can kill all children
        popen_kwargs["preexec_fn"] = os.setsid

    for cmd, port in zip(cmds, ports):
        print(f"Starting: {cmd} (waiting for port {port})", flush=True)
        if IS_WINDOWS:
            # Windows: keep shell=True for proper command parsing
            proc = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                **popen_kwargs,
            )
        else:
            # Unix: split command into list to avoid shell=True
            proc = subprocess.Popen(
                shlex.split(cmd),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                **popen_kwargs,
            )
        processes.append((proc, port, cmd))

    # Wait for all ports
    for proc, port, cmd in processes:
        if not wait_for_port(port, timeout=wait_timeout):
            print(
                f"Timeout: port {port} not available after {wait_timeout}s ({cmd})",
                file=sys.stderr,
            )
            for p, _, _ in processes:
                stop_process(p)
            sys.exit(1)
        print(f"  Port {port} ready", flush=True)

    # Run the command
    exit_code = 1
    try:
        result = subprocess.run(run_cmd)
        exit_code = result.returncode
    except KeyboardInterrupt:
        exit_code = 130
    finally:
        for proc, _, _ in processes:
            stop_process(proc)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
