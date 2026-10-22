# Genestealer Cults 11e wargear options (Waha Datasheets_options). See loadouts.py for the format.
# Brood Brothers (Astra Militarum) and Tyranid units come from the dependencies and are wired in their own books.
SPEC = {
    "Magus": {"_unit": {"static": ["Autopistol", "Force stave"]}},   # datasheet loadout name; same profile as "Magus stave"
    "Benefictus": {"_rename": {"Psychic Cascade": "R:Psionic Cascade"}},
    "Goliath Truck": {"_rename": {"Goliath wheels": "Armoured hull"}},
    "Neophyte Hybrids": {"_rename": {"Leader pistol": "Anointed pistol"}},
}
