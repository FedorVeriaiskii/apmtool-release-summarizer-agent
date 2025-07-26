def get_oneagent_version_prompt() -> str:
    return (
        "open https://docs.dynatrace.com/managed/whats-new/oneagent;\n"
        "find the latest version in the table column 'version'. The latest version is the largest number. Print only that number."
        # "search for the latest version in the 'version' table column. latest version is the biggest number. output that number only"
    )

def get_oneagent_summary_prompt(version: str) -> str:
    return f"""
             Please access the Dynatrace OneAgent release notes page for version {version} and provide a comprehensive summary.
        
            1. First, navigate to https://docs.dynatrace.com/docs/whats-new/oneagent/ and find the release notes for version {version}
            2. Read the ENTIRE page content, not just a preview
            3. Extract and summarize ALL the key features, improvements, bug fixes, and changes mentioned
            4. Include details about:
            - New features and capabilities
            - Performance improvements
            - Bug fixes
            - Breaking changes or deprecations
            - Security updates
            5. Provide a structured summary with clear sections
            
            Please ensure you access the complete content of the release notes, not just a preview or beginning portion.

        """