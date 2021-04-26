import functools

from rest_framework import status
from rest_framework.response import Response

from core.exceptions import BusinessLogicError


def restrict(*roles):
    """
    Restricts access to an endpoint based on logged in users role.

    For actions, this decorator must be applied AFTER action decorator.

    :param roles: list of UserRoles that should be allowed access to the endpoint
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapped_func(view, request, *args, **kwargs):
            # hint to developers if the setup is incorrect
            if not request.user:
                raise BusinessLogicError(
                    "restrict decorator can only be used on endpoints where login is required"
                )
            # restrict access based on user role and roles allowed for specific endpoint
            if request.user.role not in roles:
                return Response(
                    status=status.HTTP_403_FORBIDDEN,
                    data={"message": "Unauthorized."},
                )
            return func(view, request, *args, **kwargs)

        return wrapped_func

    return decorator
