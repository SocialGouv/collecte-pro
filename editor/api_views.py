from rest_framework import generics

from .serializers import UpdateEditorSerializer
from control.models import Control, Questionnaire
from control.permissions import OnlyInspectorCanChange


class UpdateEditor(generics.UpdateAPIView):
    serializer_class = UpdateEditorSerializer
    permission_classes = (OnlyInspectorCanChange,)

    def get_queryset(self):
        queryset = Questionnaire.objects  \
            .filter(control__in=Control.objects.filter(access__in=self.request.user.profile.access.all()))  \
            .filter(is_draft=True)
        return queryset
