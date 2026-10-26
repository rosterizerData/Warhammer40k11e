"""Adeptus Custodes Crusade: the 10e bloc (Magisterium Lex Ultima Endeavours, Earning of a Name, Artefacts of the Vaults,
4 Requisitions, 3 Badges) already exists in the book. This spec only imports the four Agendas from the 10e section
(the 11e codex has no Crusade section). Source: Wahapedia crus10_adeptus-custodes."""
SLUG, ED, FACTION = "adeptus-custodes", "10", "Adeptus Custodes"
LISTS = dict(agendas=True, requisitions=False, badges=False)


def build(cz):
    # the hand-built bloc carried a misspelt duplicate of the BSData-imported trait (same text)
    n = cz.L.del_assets(cz.book, ["Battle Trait§Genalchimic Warding"])
    cz.note(f"existing bloc kept; agendas only; misspelt duplicate trait removed: {n}")
