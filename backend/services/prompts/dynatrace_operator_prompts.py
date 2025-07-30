# Dynatrace Operator-specific prompts for release notes processing

def get_dynatrace_operator_version_prompt() -> str:
    """Returns prompt to extract latest Dynatrace Operator version from docs"""
    return (
        "open https://docs.dynatrace.com/docs/whats-new/dynatrace-operator;\n"
        "find the latest version in the table column 'version'. The latest version is the largest number. Print only that number."
    )

def get_dynatrace_operator_summary_prompt(version: str) -> str:
    """Returns prompt to generate comprehensive summary for specific Dynatrace Operator version"""
    return f"""
        Please access the Dynatrace Operator release notes page for version {version} and provide a comprehensive summary.
        
        1. First, navigate to https://docs.dynatrace.com/docs/whats-new/dynatrace-operator/ and find the release notes for version {version}
        2. Read the ENTIRE page content, not just a preview
        3. Extract and categorize the information into the following specific sections:

        Your response must be structured with these exact categories:

        **BREAKING CHANGES**: Extract any breaking changes, deprecated Kubernetes resources, removed operator functionality, or changes that might affect existing Dynatrace Operator deployments. If none exist, state "No breaking changes reported for this version."

        **ANNOUNCEMENTS**: Extract important operator announcements, general information, roadmap updates, or high-level communications about the Dynatrace Operator release. If none exist, state "No major announcements for this version."

        **TECHNOLOGY SUPPORT**: Extract information about Kubernetes version support updates, platform compatibility changes, new supported container orchestration features, or infrastructure requirements for the operator. If none exist, state "No technology support updates for this version."

        **NEW FEATURES**: Extract new operator features, capabilities, Kubernetes integration enhancements, or functionality additions introduced in this version. If none exist, state "No new features in this version."

        **RESOLVED ISSUES**: Extract bug fixes, resolved operator issues, performance improvements, or stability enhancements for Kubernetes deployments. If none exist, state "No resolved issues reported for this version."

        Please ensure you access the complete content of the release notes and categorize each piece of information appropriately.
        """
