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
        3. Extract and categorize the information into the following specific sections:

        Your response must be structured with these exact categories:

        **BREAKING CHANGES**: Extract any breaking changes, deprecations, removed features, or changes that might affect existing ActiveGate implementations. If none exist, state "No breaking changes reported for this version."

        **ANNOUNCEMENTS**: Extract important announcements, general information, roadmap updates, or high-level communications about the ActiveGate release. If none exist, state "No major announcements for this version."

        **TECHNOLOGY SUPPORT**: Extract information about technology support updates, platform compatibility changes, new supported technologies, operating system support, or infrastructure requirements for ActiveGate. If none exist, state "No technology support updates for this version."

        **NEW FEATURES**: Extract new ActiveGate features, capabilities, enhancements, or functionality additions introduced in this version. If none exist, state "No new features in this version."

        **RESOLVED ISSUES**: Extract bug fixes, resolved issues, performance improvements, or stability enhancements for ActiveGate. If none exist, state "No resolved issues reported for this version."

        Please ensure you access the complete content of the release notes and categorize each piece of information appropriately.
        """
