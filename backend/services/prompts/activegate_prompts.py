# ActiveGate-specific prompts for Dynatrace release notes processing

def get_activegate_version_prompt() -> str:
    """Returns prompt to extract latest ActiveGate version from docs"""
    return (
        "open https://docs.dynatrace.com/managed/whats-new/activegate;\n"
        "find the latest version in the table column 'version'. The latest version is the largest number. Print only that number."
    )

def get_activegate_summary_prompt(version: str) -> str:
    """Returns prompt to generate comprehensive summary for specific ActiveGate version"""
    return f"""
             Please access the Dynatrace ActiveGate release notes page for version {version} and provide a comprehensive summary.

            1. First, navigate to https://docs.dynatrace.com/docs/whats-new/activegate/ and find the release notes for version {version}
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
