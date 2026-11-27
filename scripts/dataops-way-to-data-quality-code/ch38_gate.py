"""Воспроизвести код завершения задачи TestGen без Databricks и удалённого сервера."""
import subprocess
import sys


def gate(failures):
    summary = {"failed_ct": failures}
    suite_key = "silver-suite"
    failed = int(summary.get("failed_ct", 0) or 0)
    if failed > 0:
        sys.exit(f"FAIL: {failed} test(s) failed in {suite_key}.")


def run_cases():
    for failures in (0, 2):
        task = subprocess.run(
            [sys.executable, __file__, str(failures)], capture_output=True, text=True
        )
        print(f"failed_ct={failures}, код={task.returncode}, следующий шаг={task.returncode == 0}")
        if task.stderr:
            print(task.stderr.strip())


if __name__ == "__main__":
    if len(sys.argv) > 1:
        gate(int(sys.argv[1]))
    else:
        run_cases()
