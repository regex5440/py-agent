import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_files import run_python_file
from functions.write_file import write_file

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

MODEL = "gemini-2.0-flash-001"

FUNCTIONS_FOR_LLM={
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file
}

def main():
    prompt = ""
    withDebugging = False

    # Process the CLI passed arguments
    if len(sys.argv) > 1:
        for i in range(1,len(sys.argv)):
            arg = sys.argv[i]
            if arg == "--verbose":
                withDebugging = True
            else:
                prompt = arg
    if len(prompt) == 0:
        exit(1)

    schema_get_files_info = types.FunctionDeclaration(
        name="get_files_info",
        description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
        parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "directory": types.Schema(
                        type=types.Type.STRING,
                        description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
                    ),
                },
            ),
    )

    schema_get_file_content = types.FunctionDeclaration(
        name="get_file_content",
        description="Read contents of a file, restricted upto 10000 characters only",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="Name of the file with its relative path to the working directory. If not provided, returns an error message",
                ),
            },
        ),
    )

    schema_run_python_file = types.FunctionDeclaration(
        name="run_python_file",
        description="Run a python file with passed arguments, returns STDOUT or STDERR message without program output or error, respectively, depending upon the return code by program",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="Name of the file with its relative path to the working directory. If not provided, returns an error"
                ),
                "args": types.Schema(
                    type=types.Type.ARRAY,
                    description="Optional list of additional arguments to be passed to CLI when running the file",
                    items=types.Schema(
                        type=types.Type.STRING,
                    )
                )
            }
        )
    )

    schema_write_file = types.FunctionDeclaration(
        name="write_file",
        description="Writes content to a file",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="Name of the file with its relative path to the working directory. If not provided, returns error"
                ),
                "content": types.Schema(
                    type=types.Type.STRING,
                    description="Content to be written to the file"
                )
            }
        )  
    )

    available_functions = types.Tool(function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file
    ])

    if withDebugging:
        print(f"User prompt: {prompt}")
    
    messages = [
        types.Content(role="user",parts=[types.Part(text = prompt)])
    ]

    MAX_ITERATIONS = 20

    iteration = 0
    while iteration < MAX_ITERATIONS:
        iteration += 1
        response = client.models.generate_content(
            model=MODEL,
            contents=messages,
            config=types.GenerateContentConfig(system_instruction="""
            You are a helpful AI coding agent.

            When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

            - List files and directories
            - Read file contents
            - Execute Python files with optional arguments
            - Write or overwrite files

            All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
            """, tools=[available_functions])
        )

        if response.candidates != None:
            for candidate in response.candidates:
                content = candidate.content
                if type(content) == str:
                    print("Content:" + content)
                    messages.append(types.Content(role="user",parts=[types.Part(text = content)]))
        

        if response.function_calls != None:
            for func in response.function_calls:
                function_call_result = call_function(func,withDebugging)

                if function_call_result.parts != None and function_call_result.parts[0] != None and function_call_result.parts[0].function_response != None and function_call_result.parts[0].function_response.response != None:
                    messages.append(function_call_result)
                else:
                    raise TypeError("Calling function did not returned anything")
        else:
            print("Final Response:")
            print(response.text)
            break
        if withDebugging:
            print("Prompt tokens:",response.usage_metadata.prompt_token_count)
            print("Response tokens:",response.usage_metadata.candidates_token_count)


def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    called_func = FUNCTIONS_FOR_LLM[function_name]

    if called_func == None:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    
    if verbose:
        print(f"Calling function: {function_name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_name}")

    result = called_func("./calculator",**function_call_part.args)
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": result},
            )
        ],
    )

if __name__ == "__main__":
    main()
