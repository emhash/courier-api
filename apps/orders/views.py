from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer
from .permissions import (
    IsUserRole, 
    IsAdminRole, 
    IsOwnerOrAdmin, 
    IsAssignedDeliveryManOrAdmin
)


class OrderCreateView(APIView):
    permission_classes = [IsUserRole]
    
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save(customer=request.user)
        
        output_serializer = OrderSerializer(order)
        response_data = output_serializer.data.copy()
        
        # if checkout URL was created
        if hasattr(serializer, 'checkout_url') and serializer.checkout_url:
            response_data["checkout_url"] = serializer.checkout_url
            response_data["message"] = "Order created successfully. Redirect user to checkout_url to complete payment."
        elif hasattr(order, 'payment'):
            if order.payment.status == 'SUCCEEDED':
                response_data["message"] = "Order created and payment completed successfully"
            else:
                response_data["message"] = "Order created with payment setup - confirmation may be required"
        else:
            response_data["message"] = "Order created successfully"
            
        return Response(response_data, status=status.HTTP_201_CREATED)


class OrderListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.role == 'admin':
            queryset = Order.objects.all()
        elif user.role == 'delivery_man':
            queryset = Order.objects.filter(delivery_man=user)
        elif user.role == 'user':
            queryset = Order.objects.filter(customer=user)
        else:
            queryset = Order.objects.none()
        
        serializer = OrderSerializer(queryset, many=True)
        return Response({
            "message": "Orders retrieved successfully",
            "orders": serializer.data
        })


class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk):
        return get_object_or_404(Order, pk=pk)
    
    def get(self, request, pk):
        order = self.get_object(pk)
        user = request.user
        
        if user.role == 'admin':
            pass
        elif user.role == 'user' and order.customer_id == user.id:
            pass
        elif user.role == 'delivery_man' and order.delivery_man_id == user.id:
            pass
        else:
            raise PermissionDenied("You don't have permission to view this order.")
        
        serializer = OrderSerializer(order)
        response_data = serializer.data.copy()
        response_data["message"] = "Order retrieved successfully"
        return Response(response_data)


class OrderUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk):
        return get_object_or_404(Order, pk=pk)
    
    def put(self, request, pk):
        order = self.get_object(pk)
        user = request.user
        
        if user.role == 'user':
            raise PermissionDenied("Users cannot modify orders once created.")
        
        if user.role == 'delivery_man':
            if order.delivery_man_id != user.id:
                raise PermissionDenied("You can only update orders assigned to you.")
            if 'status' not in request.data:
                raise PermissionDenied("Delivery man can only update status.")
            
            serializer = OrderSerializer(order, data={'status': request.data['status']}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response_data = serializer.data.copy()
            response_data["message"] = "Order status updated successfully"
            return Response(response_data)
        
        if user.role == 'admin':
            serializer = OrderSerializer(order, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response_data = serializer.data.copy()
            response_data["message"] = "Order updated successfully"
            return Response(response_data)
        
        raise PermissionDenied("You don't have permission to update this order.")
    
    def patch(self, request, pk):
        return self.put(request, pk)


class OrderDeleteView(APIView):
    permission_classes = [IsAdminRole]
    
    def get_object(self, pk):
        return get_object_or_404(Order, pk=pk)
    
    def delete(self, request, pk):
        order = self.get_object(pk)
        order.delete()
        return Response({
            "message": "Order deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT) 