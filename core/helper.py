# -*- coding: utf-8 -*-
from core.models import Space


def embigo_default_rights():
    return "00000000"

def embigo_main_space():
    return Space.objects.get(uid="00000000-0000-0000-0000-000000000000")