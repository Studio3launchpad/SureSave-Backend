from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    """
    Allow safe methods for everyone, write methods only for resource owner.
    Assumes view has .get_object() returning object with 'user' attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return getattr(obj, "user", None) == request.user


class IsGroupAdmin(BasePermission):
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
            return group.members.filter(user=user, role="admin").exists()
        except Exception:
            return False

class IsWalletOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user