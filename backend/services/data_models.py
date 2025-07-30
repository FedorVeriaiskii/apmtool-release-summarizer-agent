# Data models for Dynatrace release notes processing services

from pydantic import BaseModel, Field


class ComponentLatestReleaseVersion(BaseModel):
    """Pydantic model for component version response"""
    version: str = Field("the latest version")


class ComponentLatestReleaseSummary(BaseModel):
    """Pydantic model for component release summary response"""
    latestVersion: str = Field(description="The latest version of the component")
    breaking_changes: str = Field(description="Breaking changes and deprecations in the latest release")
    announcements: str = Field(description="Important announcements and general information")
    technology_support: str = Field(description="Technology support updates, compatibility, and platform changes")
    new_features: str = Field(description="New features and capabilities introduced in the latest release")
    resolved_issues: str = Field(description="Bug fixes and resolved issues in the latest release")
