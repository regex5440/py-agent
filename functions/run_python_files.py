import os
from subprocess import run

def run_python_file(working_directory, file_path, args=[]):
    full_path = os.path.join(working_directory, file_path)
    abs_full_path = os.path.abspath(full_path)
    abs_wdir = os.path.abspath(working_directory)

    if not abs_full_path.startswith(abs_wdir):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.exists(abs_full_path):
        return f'Error: File "{file_path}" not found.'
    
    if not file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'

# try:
    cmd = ["python3", abs_full_path]
    cmd.extend(args)
    ranObj = run(args = cmd, timeout=30, cwd=abs_wdir, capture_output=True)
    output = ""
    # if ranObj.returncode == 0:
    if len(ranObj.stdout) > 0:
        output += f'STDOUT: {ranObj.stdout}'
    else:
        output += f'STDERR: {ranObj.stderr}\n'
    
    if ranObj.returncode != 0:
        output += f'Process exited with code {ranObj.returncode}'

    if len(output) > 0:
        return output
    return "No output produced"
    # except:
    #     return f"Error: executing Python file: {file_path}"
    