import os
MAX_CHAR_LIMIT = 10000
def get_file_content(working_directory, file_path):
    full_path = os.path.join(working_directory, file_path)

    abs_full_path = os.path.abspath(full_path)
    abs_wdir = os.path.abspath(working_directory)

    if not abs_full_path.startswith(abs_wdir):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.isfile(abs_full_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        file_content_string = ""
        with open(abs_full_path, "r") as f:
            file_content_string = f.read(MAX_CHAR_LIMIT)
        if os.path.getsize(abs_full_path) > MAX_CHAR_LIMIT:
            file_content_string += f'\n[...File "{file_path}" truncated at {MAX_CHAR_LIMIT} characters]'
        return file_content_string
    except:
        return f'Error: File reading error'