# Generated by Django 3.2.13 on 2022-07-04 09:06

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('user_profiles', '0023_auto_20221115_1147'),
    ]

    operations = [
        migrations.RunSQL("alter table user_profiles_userprofile_controls add column access_type varchar(255)"),
        migrations.RunSQL("UPDATE user_profiles_userprofile_controls SET access_type = 'repondant'"),
        migrations.RunSQL("INSERT INTO user_profiles_access (id, access_type, control_id, userprofile_id) SELECT id, access_type, control_id, userprofile_id FROM user_profiles_userprofile_controls uc"),
        migrations.RunSQL("UPDATE user_profiles_access SET access_type = 'demandeur' WHERE user_profiles_access.userprofile_id in ( select uc.userprofile_id from user_profiles_userprofile_controls uc inner join user_profiles_userprofile u on uc.userprofile_id = u.user_id  WHERE u.profile_type = 'inspector')"),
    ]
