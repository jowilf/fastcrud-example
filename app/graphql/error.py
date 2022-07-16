from ariadne import format_error as ariadne_format_error
from fastapi import HTTPException
from graphql import GraphQLError
from pydantic import ValidationError


def format_error(error: GraphQLError, debug: bool = False) -> dict:
    if isinstance(error.original_error, HTTPException):
        return dict(
            error=str(error.original_error.detail),
            code=error.original_error.status_code,
        )
    elif isinstance(error.original_error, ValidationError):
        return dict(detail=error.original_error.errors(), code=422)
    if debug:
        # If debug is enabled, reuse Ariadne's formatting logic
        return ariadne_format_error(error, debug)
    return dict(error="An unknown error occurred.", code=500)
