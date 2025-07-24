def get_oneagent_version_prompt() -> str:
    return (
        "open https://docs.dynatrace.com/managed/whats-new/oneagent;\n"
        "find the latest version in the table column 'version'. The latest version is the largest number. Print only that number."
        # "search for the latest version in the 'version' table column. latest version is the biggest number. output that number only"
    )

def get_oneagent_summary_prompt(version: str) -> str:
    return f"""
        Summarize the contents of the Dynatrace OneAgent release notes version {version} according to the following requirements:

        - Retain all h1 and h2 headers from the original document, preserving their textual content and order as they appear on the page.
        - For each h2 block, generate a concise bulleted summary that covers the main points and key updates within the block. Present this summary immediately beneath the corresponding h2 header.
        - Do not alter or combine header sequences; preserve the structural flow of h1 and h2 sections strictly as in the original.
        - Do not summarize headers or rephrase their wording—summarize only the content beneath h2 headers.
        - Each bulleted summary should capture the essential details, updates, and fixes, using clear language.
        - Ensure the final output only contains headers at the h1 and h2 level and concise, bulleted summaries beneath h2 headers.
        - If a section contains no substantive information (e.g., “No changes for this release”), note this with a single bullet: • No notable changes in this section.

        Output format:
        - The response must use markdown.
        - Headers should be formatted as markdown h1 and h2, mirroring the original document.
        - Below each h2 header, place the bulleted summary.

        Example:

        # [h1 header from the document]

        ## [h2 Header 1]

        - Bullet summarizing content point A
        - Bullet summarizing content point B

        ## [h2 Header 2]

        - Bullet summarizing content point C

        (Reminder: Main objectives—retain h1/h2 headers and sequence, summarize only h2 blocks as bulleted markdown lists, do not rephrase headers, and ignore content below h2 level.)
    """
