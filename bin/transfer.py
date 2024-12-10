import lsst.daf.butler as dafButler
import argparse
from pathlib import Path
import yaml
import os
import sys
from subprocess import Popen, PIPE
import atexit
import selectors
from time import time

processes = []

def cleanup():
    for p in processes:
        p.kill()

atexit.register(cleanup)

def popen(*args, **kwargs):
    global processes
    p = Popen(*args, **kwargs)
    processes.append(p)
    return p

def _log(*args, file=sys.stderr, **kwargs):
    print(*args, file=file, **kwargs)

def _print(p):
    sel = selectors.DefaultSelector()
    sel.register(p.stdout, selectors.EVENT_READ)
    sel.register(p.stderr, selectors.EVENT_READ)

    while True:
        for key, _ in sel.select():
            data = key.fileobj.read1().decode()
            if not data:
                return p
            if key.fileobj is p.stdout:
                print(data, end="")
            else:
                print(data, end="", file=sys.stderr)


def _copy(cmd, local_directory, remote, remote_directory):
    ssh_cmd = [
        "ssh",
        remote,
        "mkdir", "-p", remote_directory
    ]
    _log(f"[_copy_{cmd[0]}] cmd:", *ssh_cmd)
    ssh = popen(ssh_cmd, stdout=PIPE, stderr=PIPE, cwd=local_directory)
    _print(ssh)
    
    _log(f"[_copy_{cmd[0]}] cmd:", f"cd {local_directory} &&", *cmd)
    p = popen(cmd, stdout=PIPE, stderr=PIPE, cwd=local_directory)
    _print(p)
    return p

def _copy_tar_ssh(local_directory, remote, remote_directory):
    tar_cmd = [
        "tar", 
        "-chf", "-", 
        "."
    ]
    _log("[_copy_tar_ssh] tar:", f"cd {local_directory} &&", *tar_cmd)
    tar = popen(tar_cmd, stdout=PIPE, stderr=PIPE, cwd=local_directory)
    ssh_cmd = [
        "ssh", 
        remote, 
        "bash", 
            "-c", 
            f"'mkdir -p {remote_directory} && cd {remote_directory} && tar -xvf -'"
    ]
    _log("[_copy_tar_ssh] cmd:", *ssh_cmd)
    ssh = popen(ssh_cmd, stdin=tar.stdout, stdout=PIPE, stderr=PIPE)
    _print(ssh)
    return ssh

def _copy_scp(local_directory, remote, remote_directory):
    cmd = [
        "scp", 
        "-r", 
        ".", 
        f"{remote}:{remote_directory}"
    ]
    return _copy(cmd, local_directory, remote, remote_directory)

def _copy_rsync(local_directory, remote, remote_directory):
    cmd = [
        "rsync", 
        "-avL", 
        ".", 
        f"{remote}:{remote_directory}"
    ]
    return _copy(cmd, local_directory, remote, remote_directory)

def _copy_bbcp(local_directory, remote, remote_directory):
    cmd = [
        "bbcp", 
        "-a", "--mkdir", "--progress", "5", "--recursive", "--symlinks", "follow", 
        ".", 
        f"{remote}:{remote_directory}"
    ]
    return _copy(cmd, local_directory, remote, remote_directory)

def copy(local_directory, remote, remote_directory, method='tar+ssh'):
    match method:
        case "tar+ssh":
            call = _copy_tar_ssh
        case "scp":
            call = _copy_scp
        case "rsync":
            call = _copy_rsync
        case "bbcp":
            call = _copy_bbcp
        case "rclone":
            call = _copy_rclone
        case _:
            raise Exception(f"copy method {method} not supported")
    t1 = time()
    p = call(local_directory, remote, remote_directory)
    p.wait()
    t2 = time()
    print(f"[copy] {p.args[0]} returned status code {p.returncode}", file=sys.stderr)
    print("[copy] finished copy in", t2 - t1, "seconds", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("local_directory", type=str)
    parser.add_argument("remote", type=str)
    parser.add_argument("remote_directory", type=str)
    parser.add_argument("--method", type=str, default="rsync")
    args = parser.parse_args()

    copy(args.local_directory, args.remote, args.remote_directory, method=args.method)


if __name__ == "__main__":
    main()
