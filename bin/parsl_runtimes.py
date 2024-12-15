from pathlib import Path
import os
from datetime import datetime
import re
import astropy.table
import sys
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)

# https://stackoverflow.com/questions/46258499/how-to-read-the-last-line-of-a-file-in-python
def tail(filename, n=1):
    lines = []
    with open(filename, 'rb') as f:
        try:  # catch OSError in case of a one line file 
            f.seek(-2, os.SEEK_END) # seek to end of file
            for i in range(n):
                while f.read(1) != b'\n': # read 1 byte until last new line
                    f.seek(-2, os.SEEK_CUR) 
                lines.append(f.readline().decode())
        except OSError:
            f.seek(0)
                    
    return lines

def head(filename, n=1):
    lines = []
    with open(filename, 'r') as f:
        for i in range(n):
            lines.append(f.readline())
    return lines

def parse_manager_params(filename):
    cores = -1
    workers = -1
    workers_spawn = -1
    logger.debug("parsing %s", filename)
    with open(filename, "r") as f:
        while l := f.readline():
            if all([x != -1 for x in [cores, workers, workers_spawn]]):
                break

            if cores == -1 and "cores_per_worker:" in l:
                cores = float(l.split("cores_per_worker:")[1].strip())
            if workers == -1 and "max_workers_per_node:" in l:
                workers = float(l.split("max_workers_per_node:")[1].strip())
            if workers == -1 and "max_workers:" in l:
                workers = float(l.split("max_workers:")[1].strip())
            
            if workers_spawn == -1:
                m = re.compile(".*Manager will spawn (\d+) workers.*").match(l)
                if m:
                    workers_spawn = int(m.groups()[0])

    return float(cores), float(workers), float(workers_spawn)

def worker_usage(worker):
    tasks_complete = 0
    work = 0
    logger.debug("parsing %s", worker)
    with open(worker, "r") as f:
        received = None
        completed = None
        while l := f.readline():
            if re.compile(".*Received executor task.*").match(l):
                received = datetime.fromisoformat("T".join(l.split(" ")[0:2]))
            if re.compile(".*Completed executor task.*").match(l):
                completed = datetime.fromisoformat("T".join(l.split(" ")[0:2]))
                
            if received and completed:
                work += (completed - received).total_seconds()
                tasks_complete += 1
                received = None
                completed = None
    return tasks_complete, work


def workflow_cpu_usage(runinfo_dir):
    usage = []
    for manager in Path(runinfo_dir).rglob("manager.log"):
        start = datetime.fromisoformat("T".join(head(manager)[0].split(" ")[0:2]))
        end = datetime.fromisoformat("T".join(tail(manager)[0].split(" ")[0:2]))
        
        cores, workers, workers_spawn = parse_manager_params(manager)
        if workers_spawn > 0:
            workers = workers_spawn

        tasks = 0
        work = 0
        for worker in manager.parent.glob("worker_*.log"):
            t, w = worker_usage(worker)
            tasks += t
            work += w
        
        usage.append(
            {
                "executor": manager.parent.parent.parent.name,
                "block_number": manager.parent.parent.name,
                "block_id": manager.parent.name,
                "start": start,
                "end": end,
                "dt": (end - start).total_seconds(),
                "cores": cores,
                "workers": workers,
                "tasks": tasks,
                "work": work,
            }
        )
    return astropy.table.Table(usage)    
        
def parse_workflow(execute):
    
    runinfo_parent = []
    p = Path(execute)
    while p.name != "runinfo":
        p = p.parent
        runinfo_parent.append(p.name)
    
    runinfo_parent = runinfo_parent[::-1]
    runinfo_parent = runinfo_parent[:runinfo_parent.index("task_logs")]
    runinfo_parent = "/".join(runinfo_parent)
        
    split = execute.name.rstrip("stderr")[:-1].split("_")[3:]
    if len(split) == 2:
        subset, proc = split
        step = ""
    elif len(split) == 3:
        subset, proc, step = split
    else:
        raise Exception()
        
    run_id = ""
    run_info_prefix = ""
    run_info = ""
    logger.debug("parsing %s", execute)
    with open(execute, "r") as f:
        while l := f.readline():
            m = re.compile(".*Run id is: (.*)\n").match(l)
            if m is not None:
                run_id = m.groups()[0]
            
            m = re.compile(".*run_dir='(.*)'.*").match(l)
            if m is not None:
                run_info_prefix = m.groups()[0]
                
            if run_info_prefix:
                m = re.compile(f'.*--logdir=.*{run_info_prefix}/([\w|\d|/]+)/.*').match(l)
                if m is not None:
                    run_info = str(Path(run_info_prefix) / m.groups()[0])
            if run_id and run_info:
                break

    return {
        "subset": subset,
        "proc": proc,
        "step": step,
        "run_id": run_id,
        "runinfo": run_info,
        "runinfo_parent": runinfo_parent,
    }    

def usage_for_workflows(workflows):
    workflow_usage = []
    for w in workflows:
        if w['runinfo']:
            usage = workflow_cpu_usage(w['runinfo'])
            if len(usage) > 0:
                usage['run_id'] = w['run_id']
                workflow_usage.append(usage)
            else:
                print("no usage info can be parsed from", w['runinfo'], file=sys.stderr)

    workflow_usage = astropy.table.vstack(workflow_usage)

    return astropy.table.join(workflows, workflow_usage, keys=['run_id'])

def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("runinfo_dir", type=Path)
    parser.add_argument("search", type=str)
    parser.add_argument("--output", nargs="?", default=sys.stdout)
    parser.add_argument("--format", default="ascii.fast_csv")
    parser.add_argument("--log-level", default="INFO")

    args = parser.parse_args()

    logger.setLevel(getattr(logging, args.log_level.upper()))

    workflows = []
    for p in Path(args.runinfo_dir).rglob(args.search):
        workflows.append(parse_workflow(p))
    workflows = astropy.table.Table(workflows)

    workflows_with_usage = usage_for_workflows(workflows)

    workflows_with_usage.write(args.output, format=args.format)

if __name__ == "__main__":
    main()
