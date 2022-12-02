from django import template
from django.db.models import Q


register = template.Library()


@register.simple_tag(takes_context=True)
def get_user_questionnaires(context, control):
    user = context['request'].user
    questionnaires = control.questionnaires.all()
    if user.profile.access.filter(Q(control=control) & Q(access_type='repondant')).exists():
        questionnaires = questionnaires.filter(is_draft=False)
    return questionnaires
