# encoding: utf-8
from django.db.models import signals

from .models import DirtynessRegistry
from .models import EbayItemModel


def register_if_changed(sender, instance, **kwargs):
    """Registers an `EbayItemModel` as dirty every time `publishing_status` changes.
    """
    old_instance = None
    try:
        old_instance = sender.objects.get(id=instance.pk)
    except sender.DoesNotExist:
        pass

    if old_instance is not None and old_instance.publishing_status != instance.publishing_status:
        DirtynessRegistry.objects.register(instance)


def register_if_new(sender, instance, created, **kwargs):
    """Registers every new `EbayItemModel` as dirty.
    """
    if created:
        DirtynessRegistry.objects.register(instance)


signals.pre_save.connect(register_if_changed,
                         sender=EbayItemModel,
                         dispatch_uid=__name__)

signals.post_save.connect(register_if_new,
                          sender=EbayItemModel,
                          dispatch_uid=__name__)
