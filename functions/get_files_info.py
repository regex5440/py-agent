import os

def get_files_info(working_directory, directory="."):
    full_path = os.path.join(working_directory, directory)
    abs_full_path = os.path.abspath(full_path)
    # Check if the full path is within the working directory
    if not abs_full_path.startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    if not os.path.isdir(abs_full_path):
        return f'Error: "{directory}" is not a directory'
    
    items = os.listdir(abs_full_path)
    output = ""
    for item in items:
        item_path = os.path.join(abs_full_path, item)
        if not os.path.exists(item_path):
            output += f'- {item}: Error: file {item} no longer exists\n'
            continue
        output += f'- {item}: file_size={os.path.getsize(item_path)} bytes, is_dir={os.path.isdir(item_path)}\n'
    return output
