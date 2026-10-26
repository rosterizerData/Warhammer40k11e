"""Necrons Crusade: the Awakening a Tomb World bloc is hand-built and already carries the Necron and Awakening Agendas in
its Mission Record override (tracking "Necron Agenda"), so agendas are not re-imported. Requisitions keep their texts;
the three Crusade Badges get their condition texts from the section."""
SLUG, ED, FACTION = "necrons", "11", "Necrons"
LISTS = dict(agendas=False, requisitions=True, badges=True)
