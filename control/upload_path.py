import os
import re


def questionnaire_path(questionnaire):
    return os.path.join(
        questionnaire.control.reference_code,
        f'Q{questionnaire.numbering:02}',
    )


def questionnaire_file_path(instance, filename):
    return os.path.join(questionnaire_path(instance), filename)


class Prefixer(object):
    def __init__(self, file_object):
        if hasattr(file_object,'question'):
            self.questionnaire_num = file_object.question.theme.questionnaire.numbering
            self.theme_num = file_object.question.theme.numbering
            self.question_num = file_object.question.numbering
            self.full_basename = os.path.basename(file_object.file.name)
        else:
            self.questionnaire_num = file_object.questionnaire.numbering
            self.full_basename = os.path.basename(file_object.file.name)

    def make_file_prefix(self):
        return f'Q{self.questionnaire_num:02}-T{self.theme_num:02}-{self.question_num:02}'

    def make_deleted_file_prefix(self):
        return f'CORBEILLE-Q{self.questionnaire_num:02}-T{self.theme_num:02}-{self.question_num:02}'

    def strip_file_prefix(self):
        return re.sub(r'Q\d+-T\d+-\d+-', '', self.full_basename)

    def strip_deleted_file_prefix(self):
        return re.sub(r'CORBEILLE-Q\d+-T\d+-\d+-', '', self.full_basename)


class PathBuilder(object):
    def __init__(self, file_object, filename):
        self.filename = filename
        control_folder = ''
        questionnaire_num = ''
        if hasattr(file_object,'question'):
            control_folder = file_object.question.theme.questionnaire.control.reference_code or \
                f'CONTROLE-{file_object.question.theme.questionnaire.control.id}'
            questionnaire_num = file_object.question.theme.questionnaire.numbering
            theme_num = file_object.question.theme.numbering
            self.theme_folder = f'T{theme_num:02}'
            questionnaire_folder = f'Q{questionnaire_num:02}' 
            self.questionnaire_path = os.path.join(control_folder, questionnaire_folder)
            self.theme_path = os.path.join(self.questionnaire_path, self.theme_folder)
        else:
            control_folder = file_object.questionnaire.control.reference_code or \
            f'CONTROLE-{file_object.questionnaire.control.id}'
            questionnaire_num = file_object.questionnaire.numbering
            questionnaire_folder = f'Q{questionnaire_num:02}' 
            self.questionnaire_path = os.path.join(control_folder, questionnaire_folder)
        self.prefixer = Prefixer(file_object)

    def get_question_file_path(self):
        question_path = os.path.join(self.questionnaire_path, "ANNEXES-AUX-QUESTIONS")
        return os.path.join(question_path, self.filename)

    def get_questionnaire_pj_file_path(self):
        question_path = os.path.join(self.questionnaire_path, "PIECES-JOINTES-QUESTIONNAIRE")
        return os.path.join(question_path, self.filename)

    def get_response_file_path(self):
        prefix = self.prefixer.make_file_prefix()
        response_filename = f'{prefix}-{self.filename}'
        if os.path.exists(os.path.join(self.theme_path, response_filename)):
            return os.path.join(self.theme_path, response_filename)
        return os.path.join(self.theme_path, self.filename)

    def get_deleted_response_file_path(self):
        prefix = self.prefixer.make_deleted_file_prefix()
        response_filename = f'{prefix}-{self.filename}'
        path = os.path.join(self.questionnaire_path, "CORBEILLE", self.theme_folder)
        if os.path.exists(os.path.join(path, response_filename)):
            return os.path.join(path, response_filename)
        return os.path.join(path, self.filename)


def question_file_path(instance, filename):
    path = PathBuilder(file_object=instance, filename=filename)
    return path.get_question_file_path()

def questionnaire_pj_file_path(instance, filename):
    path = PathBuilder(file_object=instance, filename=filename)
    return path.get_questionnaire_pj_file_path()


def response_file_path(instance, filename):
    path = PathBuilder(file_object=instance, filename=filename)
    if instance.is_deleted:
        return path.get_deleted_response_file_path()
    return path.get_response_file_path()
