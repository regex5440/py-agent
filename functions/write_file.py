import os

def write_file(working_directory, file_path, content):
    full_path = os.path.join(working_directory, file_path)
    abs_full_path = os.path.abspath(full_path)
    abs_wdir = os.path.abspath(working_directory)

    if not abs_full_path.startswith(abs_wdir):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    
    try:
        with open(abs_full_path, "w") as f:
            f.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except: 
        return f'Error: Unable to write to {file_path}'