from django.dispatch import Signal
from control.models import Control
from control.serializers import ControlSerializer
from rest_framework import decorators
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from django.db.models import Q

from control.permissions import UserDemandeurAccess

from .models import Access, UserProfile
from .serializers import UserProfileSerializer, RemoveControlSerializer


# These signals are triggered after the user is deleted via the API
user_api_post_remove = Signal()


class UserProfileViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    serializer_class = UserProfileSerializer
    search_fields = ('=user__email',)
    permission_classes = (UserDemandeurAccess,)

    def get_queryset(self):
        if len(self.request.user.profile.user_controls("demandeur")) > 0:
            return UserProfile.objects.distinct()
        else:
            return UserProfile.objects.filter(
                Q(access__control__is_deleted=False) &
                Q(access__control__in=self.request.user.profile.user_controls("all"))
            ).distinct()

    @decorators.action(detail=True, methods=['post'], url_path='remove-control')
    def remove_control(self, request, pk):
        profile = self.get_object()
        serializer = RemoveControlSerializer(data=request.data)
        if serializer.is_valid():
            control_id = serializer.data['control']
            control = Control.objects.get(pk=control_id)
            user_api_post_remove.send(
                sender=UserProfile, session_user=self.request.user, user_profile=profile,
                control=control)
            Access.objects.filter(Q(control=control_id) & Q(userprofile=profile)).first().delete()
            return Response({'status': f"Removed control {control}"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=['get'])
    def current(self, request, pk=None):
        serializer = UserProfileSerializer(request.user.profile)
        return Response(serializer.data)

    @decorators.action(detail=True, methods=['get'], url_path='controls-inspected')
    def controls_inspected(self, request, pk):
        profile = self.get_object()
        controls_inspected = profile.user_controls('demandeur')
        serialized_controls = ControlSerializer(controls_inspected, many=True)
        return Response(serialized_controls.data)
