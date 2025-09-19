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
            data_types = [
                ('espaces_de_depot_par_utilisateur', 'Nombre d\'espaces'),
                ('questionnaires_par_utilisateur', 'Nombre de questionnaires'),
                ('questions_par_utilisateur', 'Nombre de questions'),
                ('themes_par_utilisateur', 'Nombre de themes')
            ]
            
            for data_type, data_label in data_types:
                csv_buffer = StringIO()
                csv_writer = csv.writer(csv_buffer, delimiter=';') 
                with connection.cursor() as cursor:
                    cursor.callproc('get_top_20', [data_type])
                    results = cursor.fetchall()
                    csv_writer.writerow(['Utilisateur', data_label])
                    csv_writer.writerows(results)
                
                zip_file.writestr(f'collecte-pro_S{current_week_number}_TOP20_{data_type}.csv', csv_buffer.getvalue())
        
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="collecte-pro_S{current_week_number}_TOP20.zip"'
    
        return response

    def call_get_espace_depot_modele(request):
        generation_date = datetime.now().strftime("%Y-%m-%d")
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer, delimiter=';')

        with connection.cursor() as cursor:
            cursor.callproc('get_espace_depot_modele')
            results = cursor.fetchall()
            csv_writer.writerow(['id_espace_depot', 'reference_code', 'nombre_de_duplication', 'date_derniere_duplication', 'top_model_coche'])
            csv_writer.writerows(results)

        response = HttpResponse(csv_buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="identification_modele_{generation_date}.csv"'

        return response
    
    def call_get_espace_depot_elig_supp(request):
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer, delimiter=';')

        with connection.cursor() as cursor:
            cursor.callproc('get_espace_depot_elig_supp')
            results = cursor.fetchall()
            csv_writer.writerow(['id_espace_depot', 'espace_depot', 'procedure', 'organisme_interroge','date_traitement'])
            csv_writer.writerows(results)

        response = HttpResponse(csv_buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="espace_depot_elig_supp.csv"'

        return response
    
    def call_get_repondants_orphelins(request):
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer, delimiter=';')

        with connection.cursor() as cursor:
            cursor.callproc('get_repondants_orphelins')
            results = cursor.fetchall()
            csv_writer.writerow([
                'user_id', 
                'username', 
                'profile_type', 
                'date_inscription', 
                'date_derniere_connexion', 
                'status', 
                'id_control_associe', 
                'date_extraction'
            ])

            csv_writer.writerows(results)

        response = HttpResponse(csv_buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="repondants_orphelins.csv"'

        return response
    
    def fetch_statistique_data(self, action):
        with connection.cursor() as cursor:
            cursor.callproc('get_statistiques', [action])
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
    
