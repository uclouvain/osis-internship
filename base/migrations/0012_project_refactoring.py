from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL(
            """DO $$
            BEGIN
                IF EXISTS (select * from pg_class where relname='django_content_type') THEN
                    UPDATE django_content_type SET app_label='base' WHERE app_label='core';
                END IF;
            END;
            $$;"""
        ),
        # FOR r IN select * FROM pg_tables
        # WHERE schemaname = 'public' and tablename like 'core_%'
        # LOOP
        #     EXECUTE 'ALTER TABLE IF EXISTS '|| r.tablename ||' RENAME TO regexp_replace('|| r.tablename ||','core','base');';
        # END LOOP;
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS core_academiccalendar RENAME TO base_academiccalendar;"
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS core_academicyear RENAME TO base_academicyear;"
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS core_attribution RENAME TO base_attribution;"
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS core_examenrollment RENAME TO base_examenrollment;"
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS core_examenrollmenthistory RENAME TO base_examenrollmenthistory;"
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS core_learningunit RENAME TO base_learningunit;"
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS core_learningunitenrollment RENAME TO base_learningunitenrollment;"
            "ALTER TABLE IF EXISTS core_learningunitenrollment RENAME TO base_learningunitenrollment;"
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS core_learningunityear RENAME TO base_learningunityear;"
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS core_offer RENAME TO base_offer;"
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS core_offerenrollment RENAME TO base_offerenrollment;"
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS core_offeryear RENAME TO base_offeryear;"
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS core_offeryearcalendar RENAME TO base_offeryearcalendar;"
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS core_organization RENAME TO base_organization;"
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS core_person RENAME TO base_person;"
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS core_programmemanager RENAME TO base_programmemanager;"
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS core_sessionexam RENAME TO base_sessionexam;"
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS core_structure RENAME TO base_structure;"
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS core_student RENAME TO base_student;"
        ),
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS core_tutor RENAME TO base_tutor;"
        ),
        migrations.RunSQL(
            """DO $$
            BEGIN
                IF EXISTS (select * from pg_class where relname='django_migrations') THEN
                    UPDATE django_migrations SET app='base' WHERE app='core';
                END IF;
            END;
            $$;"""
        ),
    ]