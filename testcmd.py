import subprocess
import time

procs = subprocess.Popen(['a.bat', "usr_msg[1:]".encode()], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)

while True:
    # Poll the process to check if it's still running
    status = procs.poll()

    # If process is still running, fetch current stdout and stderr
    if status is None:
        # Read stdout and stderr without blocking
        stdout_line = procs.stdout.readline()
        stderr_line = procs.stderr.readline()

        # If there's new output on stdout or stderr, print it
        if stdout_line:
            print("Standard Output:", stdout_line.strip())
        if stderr_line:
            print("Standard Error:", stderr_line.strip())

        # Sleep a bit to prevent a busy-wait loop
        time.sleep(1)
    # else:
    #     # Process has finished
    #     print(f"Process finished with exit code {status}")
    #     # Capture any remaining output
    #     stdout, stderr = procs.communicate()
    #     if stdout:
    #         print("Final Standard Output:", stdout.strip())
    #     if stderr:
    #         print("Final Standard Error:", stderr.strip())
    #     break