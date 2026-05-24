import re
import unicodedata

def search_pattern(pattern: str, content: str) -> bool:
    try:
        # Normalize the pattern
        pattern = unicodedata.normalize("NFC", pattern)
        
        # Validate and sanitize the pattern
        if not re.fullmatch(r"[a-zA-Z0-9\s.*+?^${}()|[\]\\]+", pattern):
            raise ValueError("Invalid pattern")
        
        # Limit pattern complexity
        if len(pattern) > 100:
            raise ValueError("Pattern too long")
        
        # Disallow nested quantifiers and other constructs that can cause excessive backtracking
        if re.search(r"\(\?[^)]*\)|\{[^}]*\{|\[[^\]]*\[", pattern):
            return False
        
        # Search for the pattern in the content
        if re.search(pattern, content):
            return True
        return False
    except (re.error, ValueError):
        return False