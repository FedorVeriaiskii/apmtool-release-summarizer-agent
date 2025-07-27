# Central prompts module - imports all prompt functions for easy access

# Import all prompt functions to make them available from this module
from .oneagent_prompts import get_oneagent_version_prompt, get_oneagent_summary_prompt

# Export the functions for easy importing
__all__ = [
    'get_oneagent_version_prompt',
    'get_oneagent_summary_prompt'
]
