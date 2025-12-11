from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow safe methods for everyone, write methods only for resource owner.
    Assumes view has .get_object() returning object with 'user' attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return getattr(obj, "User", None) == request.user


class IsGroupAdmin(permissions.BasePermission):
    """
    Allow write operations only to group admin(s).
    Assumes group object has members with role field.
    """

    def has_object_permission(self, request, view, obj):
        # obj could be GroupSavingPlan or GroupMember depending on the view
        # If obj is GroupSavingPlan, check membership
        user = request.user
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        # if viewed object is GroupSavingPlan, check whether user is admin
        try:
            group = obj if obj.__class__.__name__ == "GroupSavingPlan" else obj.group
            return group.members.filter(user=user, role="Admin").exists()
        except Exception:
            return False

class IsWalletOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsAdminOrSelf(permissions.BasePermission):
    """Allow admins full access; allow users to view/update their own user object."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == "Admin"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == "Admin" or getattr(obj, "pk", None) == getattr(request.user, "pk", None)


class IsAuthenticatedUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user 
            and request.user.is_authenticated 
            and request.user.role == "Admin"
        )
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.role == "Admin"
            or obj == request.user
        )
