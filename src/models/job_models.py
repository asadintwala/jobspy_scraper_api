"""Job models for the API."""
from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator


class JobType(str, Enum):
    """Enum for job types."""

    FULLTIME = "fulltime"
    PARTTIME = "parttime"
    INTERNSHIP = "internship"
    CONTRACT = "contract"


class DescriptionFormat(str, Enum):
    """Enum for description formats."""

    MARKDOWN = "markdown"
    HTML = "html"


class JobResponse(BaseModel):
    """Response model for job data."""

    total_results: int = Field(..., description="Total number of jobs found")
    source_website: str = Field(..., description="Website where the job was found")
    job_title: str = Field(..., description="Title of the job")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    date_posted: str = Field(..., description="Date when the job was posted")
    job_type: Optional[str] = Field(None, description="Type of job (fulltime, parttime, etc.)")
    salary: Optional[float] = Field(None, description="Job salary")
    currency: Optional[str] = Field(None, description="Salary currency")
    is_remote: Optional[bool] = Field(None, description="Whether the job is remote")
    job_description: Optional[str] = Field(None, description="Detailed job description")
    experience_range: Optional[str] = Field(None, description="Required experience range")


class JobSearchParams(BaseModel):
    """Parameters for job search."""

    site_name: Optional[Union[List[str], str]] = Field(
        default=["linkedin", "indeed", "zip_recruiter", "glassdoor", "google", "bayt"],
        description="Job sites to search. Example: linkedin,indeed",
    )
    search_term: Optional[str] = Field(
        default=None,
        description="Search term for job titles. Example: software engineer",
    )
    google_search_term: Optional[str] = Field(
        default=None,
        description="Specific search term for Google Jobs. Example: software engineer jobs in New York since yesterday",
    )
    location: Optional[str] = Field(
        default=None,
        description="Location to search in. Example: San Francisco, CA",
    )
    distance: Optional[int] = Field(
        default=50,
        description="Distance in miles from location. Example: 25",
    )
    job_type: Optional[str] = Field(
        default=None,
        description="Type of job position. Example: fulltime",
    )
    proxies: Optional[List[str]] = Field(
        default=None,
        description="List of proxies. Example: user:pass@host:port,localhost",
    )
    is_remote: Optional[bool] = Field(
        default=None,
        description="Filter for remote positions. Example: true",
    )
    results_wanted: Optional[int] = Field(
        default=100,
        description="Number of results per site. Example: 50",
    )
    easy_apply: Optional[bool] = Field(
        default=None,
        description="Filter for easy apply positions. Example: true",
    )
    description_format: Optional[DescriptionFormat] = Field(
        default=DescriptionFormat.MARKDOWN,
        description="Format for job descriptions",
    )
    offset: Optional[int] = Field(
        default=0,
        description="Starting offset for search results. Example: 25",
    )
    hours_old: Optional[int] = Field(
        default=None,
        description="Filter jobs by hours since posting. Example: 24",
    )
    verbose: Optional[int] = Field(
        default=2,
        ge=0,
        le=2,
        description="Verbosity level (0-2). Example: 1",
    )
    linkedin_fetch_description: Optional[bool] = Field(
        default=False,
        description="Fetch full LinkedIn descriptions. Example: true",
    )
    linkedin_company_ids: Optional[List[int]] = Field(
        default=None,
        description="List of LinkedIn company IDs. Example: 1441,1442",
    )
    country_indeed: Optional[str] = Field(
        default=None,
        description="Country filter for Indeed/Glassdoor. Example: USA",
    )
    enforce_annual_salary: Optional[bool] = Field(
        default=None,
        description="Convert wages to annual salary. Example: true",
    )
    ca_cert: Optional[str] = Field(
        default=None,
        description="Path to CA Certificate file. Example: /path/to/cert.pem",
    )

    @field_validator("site_name")
    @classmethod
    def validate_site_name(cls, v: Optional[Union[List[str], str]]) -> Optional[List[str]]:
        """Validate site names."""
        if v is None:
            return None
        valid_sites = {"linkedin", "indeed", "zip_recruiter", "glassdoor", "google", "bayt"}
        if isinstance(v, str):
            sites = {site.strip().lower() for site in v.split(",")}
        else:
            sites = {site.strip().lower() for site in v}
        invalid_sites = sites - valid_sites
        if invalid_sites:
            raise ValueError(
                f"Invalid site names: {', '.join(invalid_sites)}. "
                f"Valid sites are: {', '.join(valid_sites)}"
            )
        return list(sites)

    @field_validator("job_type")
    @classmethod
    def validate_job_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate job types."""
        if v is None:
            return v
        valid_types = {t.value for t in JobType}
        types = {t.strip().lower() for t in v.split(",")}
        invalid_types = types - valid_types
        if invalid_types:
            raise ValueError(
                f"Invalid job types: {', '.join(invalid_types)}. "
                f"Valid types are: {', '.join(valid_types)}"
            )
        return v

    @field_validator("proxies")
    @classmethod
    def validate_proxies(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate proxy format."""
        if v is None:
            return v
        if isinstance(v, str):
            v = [p.strip() for p in v.split(",")]
        return v 
                    