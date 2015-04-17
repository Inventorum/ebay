# encoding: utf-8
from __future__ import absolute_import, unicode_literals


def batch_queryset(qs, batch_size=10000):
    """
    Divides the given queryset ``qs`` in batches with the given ``batch_size``

    :param qs: The queryset that needs to be batched
    :type qs: django.db.models.query.QuerySet
    :param batch_size: The size of each batch

    :return: batches as iterator
    :rtype: collections.Iterable[django.db.models.query.QuerySet]
    """
    total = qs.count()
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        yield qs[start:end]