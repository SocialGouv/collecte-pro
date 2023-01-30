from rest_framework import permissions
from rest_framework.exceptions import ParseError

from control.models import Control, Question, QuestionFile, Questionnaire, QuestionnaireFile, Theme, ResponseFile
from django.db.models import Q


def get_control_from_object(obj):
    control = obj
    if isinstance(obj, Control):
        control = obj
    elif isinstance(obj, Questionnaire):
        control = obj.control
    elif isinstance(obj, Theme):
        control = obj.questionnaire.control
    elif isinstance(obj, Question):
        control = obj.theme.questionnaire.control
    elif isinstance(obj, QuestionFile):
        control = obj.question.theme.questionnaire.control
    elif isinstance(obj, QuestionnaireFile):
        control = obj.questionnaire.control
    elif isinstance(obj, ResponseFile):
        control = obj.question.theme.questionnaire.control
    return control


class OnlyAuthenticatedCanAccess(permissions.BasePermission):
    message_format = 'Accessing this resource is not allowed.'

    def has_permission(self, request, view):
        return request.user.is_authenticated


class OnlyInspectorCanCreate(permissions.BasePermission):
    message_format = 'Accessing this resource is not allowed.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.profile.is_inspector


class OnlyDemandeurCanAccess(permissions.BasePermission):
    message_format = 'Accessing this resource is not allowed.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        control = get_control_from_object(obj)
        if control.is_deleted:
            return False
        for access in control.access.all():
            if access.userprofile.user.id == request.user.id:
                return access.access_type == "demandeur"
        return False


class OnlyRepondantCanAccess(permissions.BasePermission):
    message_format = 'Accessing this resource is not allowed.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        control = get_control_from_object(obj)
        if control.is_deleted:
            return False
        for access in control.access.all():
            if access.userprofile.user.id == request.user.id:
                return access.access_type == "repondant"
        return False


class OnlyDemandeurCanChange(permissions.BasePermission):
    message_format = 'Adding or changing this resource is not allowed.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        control = get_control_from_object(obj)
        if control.is_deleted:
            return False
        for access in control.access.all():
            if access.userprofile.user.id == request.user.id:
                return access.access_type == "demandeur"
        return False


class OnlyEditorCanChangeQuestionnaire(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        questionnaire = obj
        if not questionnaire.editor:
            return False
        if questionnaire.editor == request.user:
            return True
        return False

class ControlDemandeurAccess(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        control = get_control_from_object(obj)
        if control.is_deleted:
            return False

        return request.user.profile.access.filter(Q(control=control) & Q(access_type='demandeur')).exists()

class UserDemandeurAccess(permissions.BasePermission):

    def has_permission(self, request, view):
        return not request.user.is_anonymous

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.data.get('control'):
            return False
        control_id = request.data.get('control')
        return request.user.profile.access.filter(Q(control=control_id) & Q(access_type='demandeur')).exists()

class ControlIsNotDeleted(permissions.BasePermission):
    message_format = 'Accessing this resource is not allowed.'

    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, 'control'):
            raise ParseError(detail='Missing attribute "control" during permission check')
        return not obj.control.is_deleted


class QuestionnaireIsDraft(permissions.BasePermission):
    message_format = 'Accessing this resource is not allowed.'

    def has_object_permission(self, request, view, obj):
        """
        Checks if the questionnaire is draft.
        Expects either an instance of a questionnaire object, or an object
        that relate to a questionnaire via its `questionnaire` attribute.
        """
        if isinstance(obj, Questionnaire):
            questionnaire = obj
        elif hasattr(obj, 'questionnaire'):
            questionnaire = obj.questionnaire
        else:
            raise ParseError(detail='Could not get "questionnaire" during permission check')
        return questionnaire.is_draft
