"""Functional Data Inclusion API connector for fetching programs and services."""

import logging
from typing import Any

import httpx

from utils.errors import PipelineError


logger = logging.getLogger(__name__)


# Type aliases
DataInclusionStructure = dict[str, Any]
DataInclusionService = dict[str, Any]
DataInclusionProgram = dict[str, Any]
PaginatedResponse = dict[str, Any]
FilterParams = dict[str, Any]


# Constants
BASE_URL = "https://api.data.inclusion.gouv.fr"
API_VERSION = "v1"
DEFAULT_PAGE_SIZE = 5000
MAX_PAGE_SIZE = 10000


async def fetch_structure(
    structure_id: str,
    token: str,
) -> DataInclusionStructure:
    """Fetch a single structure by ID from Data Inclusion API.

    Args:
        structure_id: Unique structure identifier
        token: Bearer token for API authentication

    Returns:
        Detailed structure data

    Raises:
        PipelineError: If fetch fails
    """
    try:
        logger.debug(
            "Fetching structure from Data Inclusion",
            extra={"structure_id": structure_id},
        )

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/{API_VERSION}/structures/{structure_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0,
            )
            response.raise_for_status()

        structure = response.json()

        logger.debug(
            "Structure fetched successfully",
            extra={"structure_id": structure_id},
        )

        return structure
    except httpx.HTTPError as e:
        logger.error(
            "Failed to fetch structure from Data Inclusion",
            extra={"structure_id": structure_id, "error": str(e)},
        )
        raise PipelineError(f"Failed to fetch structure {structure_id}: {str(e)}") from e
    except Exception as e:
        logger.error(
            "Unexpected error fetching structure",
            extra={"structure_id": structure_id, "error": str(e)},
        )
        raise PipelineError(f"Unexpected error fetching structure: {str(e)}") from e


async def fetch_service(
    service_id: str,
    token: str,
) -> DataInclusionService:
    """Fetch a single service by ID from Data Inclusion API.

    Args:
        service_id: Unique service identifier
        token: Bearer token for API authentication

    Returns:
        Detailed service data

    Raises:
        PipelineError: If fetch fails
    """
    try:
        logger.debug(
            "Fetching service from Data Inclusion",
            extra={"service_id": service_id},
        )

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/{API_VERSION}/services/{service_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0,
            )
            response.raise_for_status()

        service = response.json()

        logger.debug(
            "Service fetched successfully",
            extra={"service_id": service_id},
        )

        return service
    except httpx.HTTPError as e:
        logger.error(
            "Failed to fetch service from Data Inclusion",
            extra={"service_id": service_id, "error": str(e)},
        )
        raise PipelineError(f"Failed to fetch service {service_id}: {str(e)}") from e
    except Exception as e:
        logger.error(
            "Unexpected error fetching service",
            extra={"service_id": service_id, "error": str(e)},
        )
        raise PipelineError(f"Unexpected error fetching service: {str(e)}") from e


async def list_structures(
    token: str,
    page: int = 1,
    size: int = DEFAULT_PAGE_SIZE,
    filters: FilterParams | None = None,
) -> PaginatedResponse:
    """List structures from Data Inclusion API with optional filters.

    Args:
        token: Bearer token for API authentication
        page: Page number (default: 1)
        size: Page size (default: 5000, max: 10000)
        filters: Optional filter parameters (sources, code_region, code_departement, etc.)

    Returns:
        Paginated response with structures

    Raises:
        PipelineError: If fetch fails
    """
    try:
        logger.debug(
            "Listing structures from Data Inclusion",
            extra={"page": page, "size": size},
        )

        # Validate and normalize page size
        size = min(size, MAX_PAGE_SIZE)

        params = {"page": page, "size": size}
        if filters:
            params.update(filters)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/{API_VERSION}/structures",
                headers={"Authorization": f"Bearer {token}"},
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()

        data = response.json()

        logger.debug(
            "Structures listed successfully",
            extra={"page": page, "total": data.get("total", 0)},
        )

        return data
    except httpx.HTTPError as e:
        logger.error(
            "Failed to list structures from Data Inclusion",
            extra={"error": str(e)},
        )
        raise PipelineError(f"Failed to list structures: {str(e)}") from e
    except Exception as e:
        logger.error(
            "Unexpected error listing structures",
            extra={"error": str(e)},
        )
        raise PipelineError(f"Unexpected error listing structures: {str(e)}") from e


async def list_services(
    token: str,
    page: int = 1,
    size: int = DEFAULT_PAGE_SIZE,
    filters: FilterParams | None = None,
) -> PaginatedResponse:
    """List services from Data Inclusion API with optional filters.

    Args:
        token: Bearer token for API authentication
        page: Page number (default: 1)
        size: Page size (default: 5000, max: 10000)
        filters: Optional filter parameters (thematiques, frais, publics, modes_accueil, types, etc.)

    Returns:
        Paginated response with services

    Raises:
        PipelineError: If fetch fails
    """
    try:
        logger.debug(
            "Listing services from Data Inclusion",
            extra={"page": page, "size": size},
        )

        # Validate and normalize page size
        size = min(size, MAX_PAGE_SIZE)

        params = {"page": page, "size": size}
        if filters:
            params.update(filters)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/{API_VERSION}/services",
                headers={"Authorization": f"Bearer {token}"},
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()

        data = response.json()

        logger.debug(
            "Services listed successfully",
            extra={"page": page, "total": data.get("total", 0)},
        )

        return data
    except httpx.HTTPError as e:
        logger.error(
            "Failed to list services from Data Inclusion",
            extra={"error": str(e)},
        )
        raise PipelineError(f"Failed to list services: {str(e)}") from e
    except Exception as e:
        logger.error(
            "Unexpected error listing services",
            extra={"error": str(e)},
        )
        raise PipelineError(f"Unexpected error listing services: {str(e)}") from e


async def search_services(
    token: str,
    code_commune: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    page: int = 1,
    size: int = DEFAULT_PAGE_SIZE,
    filters: FilterParams | None = None,
) -> PaginatedResponse:
    """Search services by location from Data Inclusion API.

    Services are filtered by geographic proximity and optional criteria.
    Results are sorted by distance (closest first) when location is provided.

    Args:
        token: Bearer token for API authentication
        code_commune: INSEE code of commune (5 digits) for geographic filtering
        lat: Latitude for geographic search (requires lon)
        lon: Longitude for geographic search (requires lat)
        page: Page number (default: 1)
        size: Page size (default: 5000, max: 10000)
        filters: Optional filter parameters (thematiques, frais, publics, modes_accueil, types, etc.)

    Returns:
        Paginated response with services sorted by distance

    Raises:
        PipelineError: If search fails
    """
    try:
        logger.debug(
            "Searching services from Data Inclusion",
            extra={"code_commune": code_commune, "lat": lat, "lon": lon, "page": page},
        )

        # Validate and normalize page size
        size = min(size, MAX_PAGE_SIZE)

        params = {"page": page, "size": size}

        if code_commune:
            params["code_commune"] = code_commune
        if lat is not None and lon is not None:
            params["lat"] = lat
            params["lon"] = lon

        if filters:
            params.update(filters)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/{API_VERSION}/search/services",
                headers={"Authorization": f"Bearer {token}"},
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()

        data = response.json()

        logger.debug(
            "Services searched successfully",
            extra={"page": page, "total": data.get("total", 0)},
        )

        return data
    except httpx.HTTPError as e:
        logger.error(
            "Failed to search services from Data Inclusion",
            extra={"error": str(e)},
        )
        raise PipelineError(f"Failed to search services: {str(e)}") from e
    except Exception as e:
        logger.error(
            "Unexpected error searching services",
            extra={"error": str(e)},
        )
        raise PipelineError(f"Unexpected error searching services: {str(e)}") from e


async def get_program_by_id(
    program_id: str,
    token: str,
) -> DataInclusionProgram:
    """Get a program (service) by ID - alias for fetch_service.

    Args:
        program_id: Unique program/service identifier
        token: Bearer token for API authentication

    Returns:
        Program data

    Raises:
        PipelineError: If fetch fails
    """
    return await fetch_service(program_id, token)


# Helper functions


def _build_filter_params(
    sources: list[str] | None = None,
    thematiques: list[str] | None = None,
    frais: str | None = None,
    publics: list[str] | None = None,
    modes_accueil: list[str] | None = None,
    types: list[str] | None = None,
    code_region: str | None = None,
    code_departement: str | None = None,
    score_qualite_minimum: float | None = None,
) -> FilterParams:
    """Build filter parameters for Data Inclusion API requests.

    Args:
        sources: List of source identifiers to filter by
        thematiques: List of thematic categories
        frais: Fee type (gratuit, payant)
        publics: List of target audiences
        modes_accueil: List of reception modes
        types: List of service types
        code_region: INSEE region code
        code_departement: INSEE department code
        score_qualite_minimum: Minimum quality score (0-1)

    Returns:
        Dictionary of filter parameters
    """
    filters = {}

    if sources:
        filters["sources"] = sources
    if thematiques:
        filters["thematiques"] = thematiques
    if frais:
        filters["frais"] = frais
    if publics:
        filters["publics"] = publics
    if modes_accueil:
        filters["modes_accueil"] = modes_accueil
    if types:
        filters["types"] = types
    if code_region:
        filters["code_region"] = code_region
    if code_departement:
        filters["code_departement"] = code_departement
    if score_qualite_minimum is not None:
        filters["score_qualite_minimum"] = score_qualite_minimum

    return filters
