from django.dispatch import Signal
from django.shortcuts import get_object_or_404


from rest_framework import decorators, status, viewsets
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from control.models import Control
from control.permissions import OnlyDemandeurCanAccess


soft_delete_signal = Signal()


class DeleteViewSet(viewsets.ViewSet):
    permission_classes = (OnlyDemandeurCanAccess,)

    def get_controls(self):
        return Control.objects.filter(access__in=self.request.user.profile.access.all())

    @decorators.action(detail=True, methods=['post'], url_path='delete-control')
    def delete_control(self, request, pk):
        control = get_object_or_404(self.get_controls(), pk=pk)
        if control not in request.user.profile.user_controls("demandeur"):
            e = PermissionDenied(
                detail=("Only demandeurs can delete controls."),
                code=status.HTTP_403_FORBIDDEN,
            )
            raise e
        if control in request.user.profile.user_controls("demandeur") and control.is_deleted:
            e = PermissionDenied(
                detail=("Only active control can be deleted."),
                code=status.HTTP_403_FORBIDDEN,
            )
            raise e
        control.delete()
        soft_delete_signal.send(
            sender=Control,
            session_user=request.user,
            obj=control)

        return Response({'status': f"Deleted {control}"})
