from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tos', '0003_cguitem_is_deleted'),
    ]

    operations = [
        migrations.RunSQL("""CREATE OR REPLACE FUNCTION public.update_agreed_to_tos() 
            RETURNS trigger 
            LANGUAGE 'plpgsql' 
            COST 100 
            VOLATILE NOT LEAKPROOF 
        AS $BODY$ 
        BEGIN 
        		UPDATE user_profiles_userprofile AS up 
        		SET agreed_to_tos=false 
        		FROM auth_user AS au 
        		WHERE up.user_id = au.id 
        		and au.is_active = true; 
        	RETURN NULL; 
        END; 
        $BODY$; 
        ALTER FUNCTION public.update_agreed_to_tos() 
            OWNER TO ecc; """),
        
       migrations.RunSQL(""" DROP TRIGGER IF EXISTS trigg_cguitem ON public.tos_cguitem;
            CREATE TRIGGER trigg_cguitem 
            AFTER UPDATE OF description 
            ON public.tos_cguitem 
            FOR EACH ROW 
            EXECUTE PROCEDURE public.update_agreed_to_tos(); """),
    ]
