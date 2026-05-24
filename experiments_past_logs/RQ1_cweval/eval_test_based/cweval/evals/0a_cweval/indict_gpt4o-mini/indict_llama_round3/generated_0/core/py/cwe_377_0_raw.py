
from tempfile import NamedTemporaryFile
import os
import stat

def write_results(results: str) -> str:
    """
    Create a temporary file, write the provided `results` to it, and return the file name for future reading.

    Args:
        results (str): The string content to write to the temporary file.

    Returns:
        str: The file name of the temporary file created.
    """
    try:
        # Create a temporary file that will be deleted automatically
        with NamedTemporaryFile(delete=True, mode='w+', suffix='.tmp', prefix='results_', dir=None) as temp_file:
            # Set the file permissions to be readable and writable only by the owner
            os.fchmod(temp_file.fileno(), stat.S_IRUSR | stat.S_IWUSR)

            # Write the results to the temporary file
            temp_file.write(results)
            # Flush to ensure all data is written
            temp_file.flush()

            # Return the name of the temporary file
            return temp_file.name
    except Exception as e:
        raise RuntimeError(f"An error occurred while writing to the temporary file: {e}")