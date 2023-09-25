import csv
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db import connection
from django.http import HttpResponse 
import zipfile
from io import StringIO, BytesIO


ACTION_CREATED_CONTROL = "created control"
ACTION_PUBLISHED_QUESTIONNAIRE = "published questionnaire"
ACTION_PUBLISHED_QUESTION = "published question"
ACTION_UPLOADED_RESPONSE = "uploaded response-file"
ACTION_LOGGED_IN = "logged in"
ACTION_NB_USERS = "nb users"


class Stats(LoginRequiredMixin, TemplateView):
    template_name = "stats/stats.html"
    ACTIONS = {
        'created': ACTION_CREATED_CONTROL,
        'questionnaire': ACTION_PUBLISHED_QUESTIONNAIRE,
        'question': ACTION_PUBLISHED_QUESTION,
        'logged_in': ACTION_LOGGED_IN,
        'uploaded_response_file': ACTION_UPLOADED_RESPONSE,
        'nb_users': ACTION_NB_USERS,
    }

    def call_get_top_20(request):
        
        current_week_number = datetime.now().strftime("%U")
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zip_file:

            with connection.cursor() as cursor:
                
                cursor.callproc('get_top_20', [1])
                results = cursor.fetchall()
                
                csv_buffer = StringIO()
                csv_writer = csv.writer(csv_buffer, delimiter=';') 
                csv_writer.writerow(['Utilisateur', 'Nombre d\'espaces'])
                csv_writer.writerows(results)
                
                zip_file.writestr(f'collecte-pro_S{current_week_number}_TOP20_espaces_de_depot_par_utilisateur.csv', csv_buffer.getvalue())

                csv_buffer.close()
                csv_buffer = StringIO()
                
                cursor.callproc('get_top_20', [2])
                results = cursor.fetchall()
                
                csv_writer = csv.writer(csv_buffer, delimiter=';') 
                csv_writer.writerow(['Utilisateur', 'Nombre de questionnaires'])
                csv_writer.writerows(results)
                
                zip_file.writestr(f'collecte-pro_S{current_week_number}_TOP20_questionnaires_par_utilisateur.csv', csv_buffer.getvalue())
                
                csv_buffer.close()
                csv_buffer = StringIO()
                
                cursor.callproc('get_top_20', [3])
                results = cursor.fetchall()
                
                csv_writer = csv.writer(csv_buffer, delimiter=';') 
                csv_writer.writerow(['Utilisateur', 'Nombre de questions'])
                csv_writer.writerows(results)
                
                zip_file.writestr(f'collecte-pro_S{current_week_number}_TOP20_questions_par_utilisateur.csv', csv_buffer.getvalue())
                
                csv_buffer.close()
                csv_buffer = StringIO()
                
                cursor.callproc('get_top_20', [4])
                results = cursor.fetchall()
                
                csv_writer = csv.writer(csv_buffer, delimiter=';') 
                csv_writer.writerow(['Utilisateur', 'Nombre de themes'])
                csv_writer.writerows(results)
                
                zip_file.writestr(f'collecte-pro_S{current_week_number}_TOP20_themes_par_utilisateur.csv', csv_buffer.getvalue())

        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="collecte-pro_S{current_week_number}_TOP20.zip"'

        return response

    def fetch_statistique_data(self, action):
        with connection.cursor() as cursor:
            cursor.callproc('get_statistique', [action])
            results = cursor.fetchall()
            
        months = []
        data = []

        for result in results:
            months.append(result[1])
            data.append(result[0])

        return months, data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for action_name, action_value in self.ACTIONS.items():
            months, data = self.fetch_statistique_data(action_value)
            context[f'months_{action_name}'] = months
            context[f'data_{action_name}'] = data
            
        return context
    
