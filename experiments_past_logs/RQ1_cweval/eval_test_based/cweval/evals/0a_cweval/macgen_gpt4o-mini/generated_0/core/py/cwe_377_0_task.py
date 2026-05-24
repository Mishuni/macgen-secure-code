from tempfile import NamedTemporaryFile

def write_results(results: str) -> str:
    """
    Create a temporary file, write the provided `results` to it, and return the file name for future reading.

    Args:
        results (str): The string content to write to the temporary file.

    Returns:
        str: The file name of the temporary file created.
    """
    if not isinstance(results, str) or len(results) == 0:
        raise ValueError("Invalid input: results must be a non-empty string.")
    
    # Sanitize input by removing non-printable characters
    results = ''.join(c for c in results if c.isprintable())
    
    try:
        with NamedTemporaryFile(delete=True, mode='w', encoding='utf-8') as temp_file:
            temp_file.write(results)
            temp_file.flush()  # Ensure all data is written before closing
            return temp_file.name
    except OSError:
        raise RuntimeError("Failed to write to temporary file.")