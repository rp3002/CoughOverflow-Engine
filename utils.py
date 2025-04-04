# utils.py
import subprocess
import os

# [1] Adapted with assistance from ChatGPT to execute an external binary with proper file paths and return a boolean result.
def run_overflowengine(image_path, result_path):
    """
    Run the overflowengine tool on the input image and save the result.
    
    Args:
        image_path (str): Path to the input image
        result_path (str): Path to save the result
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        result = subprocess.run(
            ["./overflowengine", "--input", image_path, "--output", result_path],
            check=True,
            cwd=".",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"OverflowEngine output: {result.stdout.decode()}")
        print(f"OverflowEngine error: {result.stderr.decode()}")
        
        # Check if the result file was created
        if os.path.exists(result_path):
            return True
        else:
            print("Result file was not created")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error running OverflowEngine: {e}")
        print(f"stderr: {e.stderr.decode()}")
        return False
