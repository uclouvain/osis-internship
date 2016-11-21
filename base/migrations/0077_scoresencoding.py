# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0076_auto_20161104_1504'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DROP VIEW IF EXISTS app_scores_encoding;

            CREATE OR REPLACE VIEW app_scores_encoding AS
            SELECT row_number() OVER () as id,

                base_programmanager.id as program_manager_id,
                program_manager_person.id as pgm_manager_person_id,
                base_offeryear.id as offer_year_id,
                base_learningunityear.id as learning_unit_year_id,
                base_examenrollment.enrollment_state,

                count(base_examenrollment.id) as total_exam_enrollments,
                sum(case when base_examenrollment.score_final is not null or base_examenrollment.justification_final is not null then 1 else 0 end) exam_enrollments_encoded,
                sum(case when (base_examenrollment.score_draft is not null and base_examenrollment.score_final is null)
                              or (base_examenrollment.justification_draft is not null and base_examenrollment.justification_final is null)
                         then 1 else 0 end) scores_not_yet_submitted


            from base_examenrollment
            join base_sessionexam on base_sessionexam.id = base_examenrollment.session_exam_id
            join base_learningunityear on base_learningunityear.id = base_sessionexam.learning_unit_year_id

            join base_offeryearcalendar on base_offeryearcalendar.id = base_sessionexam.offer_year_calendar_id

            join base_learningunitenrollment on base_learningunitenrollment.id = base_examenrollment.learning_unit_enrollment_id
            join base_offerenrollment on base_offerenrollment.id = base_learningunitenrollment.offer_enrollment_id
            join base_offeryear on base_offeryear.id = base_offerenrollment.offer_year_id

            join base_programmanager on base_programmanager.offer_year_id = base_offeryear.id
            join base_person program_manager_person on program_manager_person.id = base_programmanager.person_id

            where base_offeryearcalendar.start_date <= CURRENT_TIMESTAMP::date
            and base_offeryearcalendar.end_date >=  CURRENT_TIMESTAMP::date

            group by
            base_programmanager.id,
            program_manager_person.id,
            base_offeryear.id,
            base_learningunityear.id,
            base_examenrollment.enrollment_state
            ;
            """
        ),
    ]
