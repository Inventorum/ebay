# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from collections import defaultdict
from django.utils.translation import ugettext
from rest_framework import serializers


class CategorySpecificsValidatorError(serializers.ValidationError):
    pass


class CategorySpecificsValidator(object):
    def __init__(self, category, specifics):
        self.category = category
        self.specifics = specifics
        self.errors = []

    def validate(self, raise_exception=False):
        self._validate_specific_values_if_max_values_are_ok()
        self._validate_specific_values_if_min_values_are_ok()
        self._validate_specific_values_categories_are_correct()

        if self.errors and raise_exception:
            raise CategorySpecificsValidatorError(self.errors)

    def _validate_specific_values_if_min_values_are_ok(self):
        specific_values_ids_count = defaultdict(lambda: 0)
        for sv in self.specifics:
            specific_values_ids_count[sv.pk] += 1

        required_ones = dict(self.category.specifics.required().values_list('id', 'min_values'))

        missing_ids = []
        for specific_id, min_value in required_ones.iteritems():
            send_value = specific_values_ids_count.get(specific_id, None)
            if not send_value or send_value < min_value:
                missing_ids.append(specific_id)

        if missing_ids:
            self.errors.append(ugettext('You need to pass all required specifics (missing: %(missing_ids)s)!')
                               % {'missing_ids': list(missing_ids)})


    def _validate_specific_values_if_max_values_are_ok(self):
        specific_values_ids_count = defaultdict(lambda: 0)
        for sv in self.specifics:
            specific_values_ids_count[sv.pk] += 1

        max_values = dict(self.category.specifics.required().values_list('id', 'max_values'))

        too_many_values_ids = []
        for specific_id, max_value in max_values.iteritems():
            send_value = specific_values_ids_count.get(specific_id, None)
            if send_value and send_value > max_value:
                too_many_values_ids.append(specific_id)

        if too_many_values_ids:
            self.errors.append(ugettext('You send too many values for one specific '
                                        '(specific_ids: %(too_many_values_ids)s)!')
                               % {'too_many_values_ids': list(too_many_values_ids)})


    def _validate_specific_values_categories_are_correct(self):
        wrong_ids = [sv.id for sv in self.specifics
                     if sv.category_id != self.category.id]

        if wrong_ids:
            self.errors.append(ugettext('Some specifics are assigned to different category than product! '
                                        '(wrong specific ids: %(wrong_ids)s)') % {'wrong_ids': wrong_ids})
