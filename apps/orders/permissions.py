from rest_framework import permissions


class OrderPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if view.action == 'create':
            return request.user.role == 'user'
        
        return True
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admin has full access
        if user.role == 'admin':
            return True
        
        # Users can only view their own orders
        if user.role == 'user':
            return obj.customer_id == user.id and view.action in ['retrieve']
        
        # Delivery men can view and update status of assigned orders
        if user.role == 'delivery_man':
            if obj.delivery_man_id == user.id:
                return view.action in ['retrieve', 'update', 'partial_update']
        
        return False


class IsUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'user'


class IsDeliveryManRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'delivery_man'


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.role == 'admin' or obj.customer_id == user.id


class IsAssignedDeliveryManOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.role == 'admin' or (user.role == 'delivery_man' and obj.delivery_man_id == user.id) 