from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.views.generic import DetailView, RedirectView
from django.views.generic.detail import SingleObjectMixin
from django.db.models import Max, Case, When, Value, DateTimeField, F

from datetime import datetime
from django.utils.timezone import make_aware

from ordered_model.admin import OrderedModelAdmin
from ordered_model.admin import OrderedTabularInline, OrderedInlineModelAdminMixin

from soft_deletion.admin import SoftDeletedAdminControle, IsActiveFilter, IsModelFilter

from .models import Control, Questionnaire, Theme, Question, QuestionFile, ResponseFile, QuestionnaireFile
from .questionnaire_duplicate import QuestionnaireDuplicateMixin
from user_profiles.models import UserProfile


class ParentLinksMixin(object):
    def link_to_question(self, obj):
        question = getattr(obj, 'question', None)
        if not question:
            return '-'
        url = reverse("admin:control_question_change", args=[question.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            question
        )
    link_to_question.short_description = 'Question'

    def link_to_theme(self, obj):
        theme = getattr(obj, 'theme', None)
        if not theme:
            return '-'
        url = reverse("admin:control_theme_change", args=[theme.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            theme
        )
    link_to_theme.short_description = 'Theme'

    def link_to_questionnaire(self, obj):
        questionnaire = getattr(obj, 'questionnaire', None)
        if not questionnaire:
            return '-'
        url = reverse("admin:control_questionnaire_change", args=[questionnaire.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            questionnaire
        )
    link_to_questionnaire.short_description = 'Questionnaire'

    def link_to_control(self, obj):
        control = getattr(obj, 'control', None)
        if not control:
            return '-'
        url = reverse("admin:control_control_change", args=[control.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            control
        )
    link_to_control.short_description = 'Control'


class QuestionnaireInline(OrderedTabularInline):
    model = Questionnaire
    fields = (
        'id', 'title', 'description', 'uploaded_file', 'generated_file', 'end_date',
        'order', 'move_up_down_links')
    readonly_fields = ('id', 'move_up_down_links',)
    extra = 1


@admin.register(Control)
class ControlAdmin(SoftDeletedAdminControle, OrderedInlineModelAdminMixin, OrderedModelAdmin):
    list_display = ('id', 'title', 'depositing_organization', 'reference_code', 'get_last_response_file_action', 'created_date')
    search_fields = (
        'title', 'reference_code', 'questionnaires__title', 'questionnaires__description')
    inlines = (QuestionnaireInline, )
    list_filter = (IsActiveFilter,IsModelFilter,)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(_last_response_date=Max('questionnaires__last_response_file_action'))

        col_index = 5  

        ordering_param = request.GET.get('o', '') 
        is_desc = False
        for part in ordering_param.split('.'):
            if part.lstrip('-') == str(col_index):
                is_desc = part.startswith('-')
                break

        default_value = make_aware(datetime(2000, 1, 1)) if is_desc else make_aware(datetime(2099, 1, 1))

        qs = qs.annotate(
            _date_for_sort=Case(
                When(_last_response_date__isnull=True, then=Value(default_value)),
                default=F('_last_response_date'),
                output_field=DateTimeField(),
            )
        )
        return qs

    @admin.display(description='Date la plus récente', ordering='_date_for_sort')
    def get_last_response_file_action(self, obj):
        questionnaire = obj.questionnaires.order_by('-last_response_file_action').first()
        if questionnaire and questionnaire.last_response_file_action:
            return questionnaire.last_response_file_action
        return "Aucun"



class ThemeInline(OrderedTabularInline):
    model = Theme
    fields = (
        'id', 'title', 'order', 'move_up_down_links')
    readonly_fields = ('id', 'order', 'move_up_down_links')
    extra = 1


class QuestionnaireFileInline(OrderedTabularInline):
    model = QuestionnaireFile
    fields = (
        'id', 'file', 'order', 'move_up_down_links')
    readonly_fields = ('id', 'order', 'move_up_down_links')
    extra = 1


@admin.register(Questionnaire)
class QuestionnaireAdmin(QuestionnaireDuplicateMixin, OrderedInlineModelAdminMixin, OrderedModelAdmin, ParentLinksMixin):
    save_as = True
    list_display = (
        'id', 'numbering', 'title', 'order', 'link_to_control', 'is_draft', 'editor',
        'sent_date', 'end_date', 'last_response_file_action', 'created_date')
    list_editable = ('order',)
    readonly_fields = ('order', 'editor')
    search_fields = ('title', 'description')
    list_filter = ('control', 'is_draft')
    raw_id_fields = ('editor', 'control')
    actions = ['megacontrol_admin_action']
    inlines = (ThemeInline, QuestionnaireFileInline, )


class QuestionInline(OrderedTabularInline):
    model = Question
    fields = ('id', 'description', 'order', 'move_up_down_links')
    readonly_fields = ('id', 'order', 'move_up_down_links')


@admin.register(Theme)
class ThemeAdmin(OrderedInlineModelAdminMixin, OrderedModelAdmin, ParentLinksMixin):
    list_display = ('id', 'numbering', 'title', 'link_to_questionnaire', 'link_to_control')
    search_fields = ('title',)
    list_filter = ('questionnaire__control',)
    fields = (
        'id', 'title', 'questionnaire', 'link_to_control')
    readonly_fields = ('id', 'link_to_control')
    inlines = (QuestionInline,)


class QuestionFileInline(OrderedTabularInline):
    model = QuestionFile
    max_num = 4
    fields = ('file', 'order', 'move_up_down_links')
    readonly_fields = ('order', 'move_up_down_links')


class ResponseFileInline(OrderedTabularInline):
    model = ResponseFile
    max_num = 4
    fields = ('file',)


@admin.register(Question)
class QuestionAdmin(OrderedInlineModelAdminMixin, OrderedModelAdmin, ParentLinksMixin):
    list_display = ('id', 'numbering', 'description', 'link_to_theme', 'link_to_questionnaire',
        'link_to_control')
    fields = (
        'id', 'description', 'theme', 'link_to_questionnaire', 'link_to_control')
    readonly_fields = ('id', 'link_to_questionnaire', 'link_to_control')
    raw_id_fields = ('theme',)
    list_filter = ('theme__questionnaire__control',)
    search_fields = ('description',)
    inlines = (QuestionFileInline, ResponseFileInline,)


@method_decorator(staff_member_required, name='dispatch')
class MegacontrolConfirm(QuestionnaireDuplicateMixin, DetailView):
    template_name = "ecc/megacontrol_confirm.html"
    context_object_name = 'questionnaire'

    def get_queryset(self):
        return Questionnaire.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['controls_to_copy_to'] = self.get_controls_to_copy_to(self.object)
        return context


@method_decorator(staff_member_required, name='dispatch')
class Megacontrol(LoginRequiredMixin, QuestionnaireDuplicateMixin, SingleObjectMixin, RedirectView):
    url = f'/{settings.ADMIN_URL}control/questionnaire/'
    model = Questionnaire

    def get_queryset(self):
        return Questionnaire.objects.all()

    def get(self, *args, **kwargs):
        questionnaire = self.get_object()
        created_questionnaires = self.do_megacontrol(questionnaire)

        message = format_html(
            'Vous avez créé les <b>{}</b> questionnaires suivants : <ul>',
            len(created_questionnaires)
        )
        for created_questionnaire in created_questionnaires:
            message = format_html(
                """
                {}
                <li>
                    <a href="/{}control/questionnaire/{}/change/">
                        <b> {} : {} </b>
                    </a>
                    dans l\'espace <b>{}</b>
                </li>
                """,
                message,
                settings.ADMIN_URL,
                created_questionnaire.id,
                created_questionnaire.id,
                created_questionnaire,
                created_questionnaire.control
            )
        message = format_html('{}</ul>', message)
        messages.success(self.request, message)

        return super().get(*args, **kwargs)

admin.site.register(QuestionFile)
admin.site.register(QuestionnaireFile)
admin.site.register(ResponseFile)