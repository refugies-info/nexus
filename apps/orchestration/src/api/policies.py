"""Policy validation API endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from db.repositories.policy import PolicyRepository
from services.policy import validate_program
from utils.errors import PipelineError


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/policies", tags=["policies"])


# Dependencies
def get_policy_repository() -> PolicyRepository:
    """Get policy repository instance."""
    return PolicyRepository()


@router.post("/validate", status_code=status.HTTP_200_OK)
async def validate_program_endpoint(
    program_id: str,
    program_data: dict[str, Any],
    policy_repo: PolicyRepository = Depends(get_policy_repository),  # noqa: B008
) -> dict[str, Any]:
    """Validate a program against editorial policy rules.

    Args:
        program_id: Unique program identifier
        program_data: Program data to validate
        policy_repo: Policy repository instance

    Returns:
        Validation result with decision and audit trail

    Raises:
        HTTPException: If validation fails
    """
    try:
        logger.info(
            "Validating program against policy rules",
            extra={"program_id": program_id},
        )

        # Get policy rules
        policy_rules = await policy_repo.get_policy_rules()

        if not policy_rules:
            logger.warning(
                "No policy rules found for validation",
                extra={"program_id": program_id},
            )
            return {
                "program_id": program_id,
                "valid": True,
                "decision": "approved",
                "reason": "No policy rules configured",
                "audit_trail": [],
            }

        # Validate program
        validation_result = await validate_program(
            program_id=program_id,
            program_data=program_data,
            policy_rules=policy_rules,
        )

        # Store validation decision
        decision_record = await policy_repo.create_policy_decision(
            program_id=program_id,
            decision="rejected" if not validation_result.get("valid") else "approved",
            reason=validation_result.get("reason"),
            audit_trail=validation_result.get("audit_trail", []),
            policy_version=validation_result.get("policy_version"),
        )

        logger.info(
            "Program validation completed",
            extra={
                "program_id": program_id,
                "valid": validation_result.get("valid"),
            },
        )

        return {
            "program_id": program_id,
            "decision_id": decision_record.get("id"),
            "valid": validation_result.get("valid"),
            "decision": "rejected" if not validation_result.get("valid") else "approved",
            "reason": validation_result.get("reason"),
            "audit_trail": validation_result.get("audit_trail", []),
        }

    except PipelineError as e:
        logger.error(
            "Policy validation failed",
            extra={"program_id": program_id, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Policy validation failed: {str(e)}",
        ) from e
    except Exception as e:
        logger.error(
            "Unexpected error during policy validation",
            extra={"program_id": program_id, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during policy validation",
        ) from e


@router.get("/decisions/{program_id}", status_code=status.HTTP_200_OK)
async def get_policy_decision(
    program_id: str,
    policy_repo: PolicyRepository = Depends(get_policy_repository),  # noqa: B008
) -> dict[str, Any]:
    """Get the policy validation decision for a program.

    Args:
        program_id: Unique program identifier
        policy_repo: Policy repository instance

    Returns:
        Policy validation decision record

    Raises:
        HTTPException: If decision not found or retrieval fails
    """
    try:
        logger.debug(
            "Retrieving policy decision",
            extra={"program_id": program_id},
        )

        decision = await policy_repo.get_policy_decision(program_id)

        if not decision:
            logger.warning(
                "Policy decision not found",
                extra={"program_id": program_id},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No policy decision found for program {program_id}",
            )

        logger.debug(
            "Policy decision retrieved",
            extra={"program_id": program_id},
        )

        return decision

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to retrieve policy decision",
            extra={"program_id": program_id, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error retrieving policy decision",
        ) from e
