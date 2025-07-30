# Dynatrace API-specific prompts for release notes processing

def get_dynatrace_api_version_prompt() -> str:
    """Returns prompt to extract latest Dynatrace API version from docs"""
    return (
        "open https://docs.dynatrace.com/docs/whats-new/dynatrace-api;\n"
        "find the latest version in the table column 'version'. The latest version is the largest number. Print only that number."
    )

def get_dynatrace_api_summary_prompt(version: str) -> str:
    """Returns prompt to generate comprehensive summary for specific Dynatrace API version"""
    return f"""
        Please access the Dynatrace API changelog page for version {version} and provide a comprehensive summary.
        
        1. First, navigate to https://docs.dynatrace.com/docs/whats-new/dynatrace-api/ and find the release notes for version {version}
        2. Read the ENTIRE page content, not just a preview
        3. Extract and categorize the information into the following specific sections:

        Your response must be structured with these exact categories:

        **BREAKING CHANGES**: Extract any breaking API changes, deprecated endpoints, removed functionality, or changes that might affect existing API integrations. If none exist, state "No breaking changes reported for this version."

        **ANNOUNCEMENTS**: Extract important API announcements, general information, roadmap updates, or high-level communications about the API release. If none exist, state "No major announcements for this version."

        **TECHNOLOGY SUPPORT**: Extract information about API technology support updates, SDK compatibility changes, new supported programming languages, authentication updates, or integration requirements. If none exist, state "No technology support updates for this version."

        **NEW FEATURES**: Extract new API endpoints, capabilities, enhancements, or functionality additions introduced in this version. If none exist, state "No new features in this version."

        **RESOLVED ISSUES**: Extract API bug fixes, resolved issues, performance improvements, or stability enhancements. If none exist, state "No resolved issues reported for this version."

        Please ensure you access the complete content of the release notes and categorize each piece of information appropriately.
        """
