# pylint: disable=duplicate-code
# pylint: disable=too-many-lines
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=too-many-positional-arguments
# pylint: disable=unused-argument

"""Job API endpoints."""
from typing import List, Any
import math
import logging
from fastapi import APIRouter, HTTPException, Query
from jobspy import scrape_jobs
from src.models.job_models import DescriptionFormat, JobResponse, JobSearchParams
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JobSearchResponse(BaseModel):
    """Response model for job search results."""
    total_results: int
    jobs: List[JobResponse]

router = APIRouter()


def handle_nan(value: Any) -> Any:
    """Convert NaN values to None."""
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


@router.get("/jobs", response_model=JobSearchResponse)
async def get_jobs(
    site_name: str = Query(
        default="linkedin,indeed,glassdoor,google",
        description="Job sites to search. Ex: linkedin,indeed,glassdoor,google,zip_recruiter,naukri,bayt",
    ),
    search_term: str = Query(
        default=None,
        description="Search term for job titles. Ex: software engineer,python developer",
    ),
    google_search_term: str = Query(
        default=None,
        description="Specific search term for Google Jobs. Ex: software engineer jobs in New York since yesterday",
    ),
    location: str = Query(
        default=None,
        description="Location to search in. Ex: San Francisco, New York",
    ),
    distance: int = Query(
        default=50,
        description="Distance in miles from location. Example: 25",
    ),
    job_type: str = Query(
        default=None,
        description="Type of job position. Ex: fulltime,parttime,contract",
    ),
    proxies: str = Query(
        default=None,
        description="List of proxies. Ex: user:pass@host:port,localhost",
    ),
    is_remote: bool = Query(
        default=None,
        description="Filter for remote positions. Example: true",
    ),
    results_wanted: int = Query(
        default=100,
        description="Number of results per site. Example: 50",
    ),
    easy_apply: bool = Query(
        default=None,
        description="Filter for easy apply positions. Example: true",
    ),
    description_format: DescriptionFormat = Query(
        default=DescriptionFormat.MARKDOWN,
        description="Format for job descriptions",
    ),
    offset: int = Query(
        default=0,
        description="Starting offset for search results. Example: 25",
    ),
    hours_old: int = Query(
        default=None,
        description="Filter jobs by hours since posting. Example: 24",
    ),
    verbose: int = Query(
        default=2,
        ge=0,
        le=2,
        description="Verbosity level (0-2). Example: 1",
    ),
    linkedin_fetch_description: bool = Query(
        default=False,
        description="Fetch full LinkedIn descriptions. Example: true",
    ),
    linkedin_company_ids: str = Query(
        default=None,
        description="List of LinkedIn company IDs. Example: 1441,1442",
    ),
    country_indeed: str = Query(
        default=None,
        description="Country filter for Indeed/Glassdoor. Example: USA",
    ),
    enforce_annual_salary: bool = Query(
        default=None,
        description="Convert wages to annual salary. Example: true",
    ),
    ca_cert: str = Query(
        default=None,
        description="Path to CA Certificate file. Example: /path/to/cert.pem",
    ),
) -> JobSearchResponse:
    """
    Search for jobs across multiple job sites.

    Args:
        This API enables users to search for job listings across multiple platforms with rich
        filtering and customization options.It supports Google Jobs, LinkedIn, Indeed, Glassdoor, bayt,
        naukri and zip_recruiter, offering flexibility for various job-hunting needslike
        full time/part time/internships and that also in various locations.

    Returns:
        List of job results as per described schema.

    Raises:
        HTTPException: If there's an error in the search parameters or job scraping.
    """
    try:
        logger.info(f"Starting job search with parameters: site_name={site_name}, search_term={search_term}, location={location}")
        
        # Convert linkedin_company_ids from string to list
        if linkedin_company_ids:
            linkedin_company_ids = [int(id.strip()) for id in linkedin_company_ids.split(",")]

        # Split comma-separated inputs into lists
        search_terms = [term.strip() for term in search_term.split(",")] if search_term else [None]
        locations = [loc.strip() for loc in location.split(",")] if location else [None]
        job_types = [jt.strip() for jt in job_type.split(",")] if job_type else [None]
        sites = [site.strip() for site in site_name.split(",")] if site_name else []

        all_results = []
        total_jobs = 0

        # Iterate through all combinations of search parameters
        for search_term in search_terms:
            for location in locations:
                for job_type in job_types:
                    logger.info(f"Searching jobs with: term={search_term}, location={location}, type={job_type}")
                    
                    # Validate parameters
                    params = JobSearchParams(
                        site_name=sites,
                        search_term=search_term,
                        google_search_term=google_search_term,
                        location=location,
                        distance=distance,
                        job_type=job_type,
                        proxies=proxies,
                        is_remote=is_remote,
                        results_wanted=results_wanted,
                        easy_apply=easy_apply,
                        description_format=description_format,
                        offset=offset,
                        hours_old=hours_old,
                        verbose=verbose,
                        linkedin_fetch_description=linkedin_fetch_description,
                        linkedin_company_ids=linkedin_company_ids,
                        country_indeed=country_indeed,
                        enforce_annual_salary=enforce_annual_salary,
                        ca_cert=ca_cert,
                    )

                    # Perform job search
                    jobs = scrape_jobs(**params.model_dump(exclude_none=True))
                    total_jobs += len(jobs)
                    logger.info(f"Found {len(jobs)} jobs from current search")

                    # Convert to response model
                    for _, job in jobs.iterrows():
                        # Handle location properly
                        job_location = handle_nan(job.get("location", ""))
                        if not job_location:
                            city = handle_nan(job.get("city", ""))
                            state = handle_nan(job.get("state", ""))
                            job_location = ", ".join(filter(None, [city, state]))

                        result = JobResponse(
                            source_website=handle_nan(job.get("site", "")),
                            job_title=handle_nan(job.get("title", "")),
                            company=handle_nan(job.get("company")) or "Unknown Company",
                            location=job_location,
                            date_posted=str(handle_nan(job.get("date_posted", ""))),
                            job_type=handle_nan(job.get("job_type")),
                            salary=handle_nan(job.get("min_amount") or job.get("max_amount")),
                            currency=handle_nan(job.get("currency", "USD")),
                            is_remote=handle_nan(job.get("is_remote", False)),
                            job_description=handle_nan(job.get("description", "")),
                            experience_range=handle_nan(job.get("experience_range")),
                        )
                        all_results.append(result)

        logger.info(f"Total jobs found: {total_jobs}")
        return JobSearchResponse(
            total_results=total_jobs,
            jobs=all_results
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e)) from e
        
    except Exception as e:
        logger.error(f"Unexpected error during job search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching jobs: {str(e)}") from e
    