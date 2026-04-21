# REGION_MAPPING = {
#     'B': "Hassi-R'mel",
#     'C': 'Houad-Berkaoui',
#     'D': 'Hassi-Messaoud',
#     'E': 'Rhourde El Baguel',
#     'K': 'Gassi-Touil',
#     'L': 'Rhourde-Nouss',
#     'M': 'TIN-Fouyé-Tabankort',
#     'N': 'Ohanet',
#     'P': 'Stah',
#     'T': 'In-Aménas',
#     'Secteur': 'Secteur Hors-Région',
#     'DAT': 'Dir. Appro et Transport',
#     'HSE': 'Département HSE',
#     'INF': 'Dir. Informatique',
#     'DMG': 'Dir. Informatique (DMG)',
# }

ACTIVITE_MAPPING = {
    'A': 'Pétrole',
    'B': 'Gaz',
}

# FAMILLE_ORDER = [
#     'Etudes',
#     'Maintenance Puits',
#     'Installations Spécifiques',
#     'Maintenance des Installations',
#     'Installations Générales',
#     'Infrastructures Sociales',
#     'Equipements',
# ]

# def get_famille_nom(code):
#     """
#     Convertit un code famille (ex: 2.61) vers son nom complet.
#     Règle : on prend le préfixe avant le point pour déterminer la famille.
#     Exception : 3.1x → Maintenance des Installations
#     """
#     code = str(code).strip()

#     FAMILLE_PREFIXES = {
#         '1': 'Etudes',
#         '2': 'Maintenance Puits',
#         '3': 'Installations Spécifiques',
#         '4': 'Installations Générales',
#         '5': 'Infrastructures Sociales',
#         '6': 'Equipements',
#     }

#     # Cas spécial 3.1x → Maintenance des Installations
#     parts = code.split('.')
#     if parts[0] == '3' and len(parts) > 1 and parts[1].startswith('1'):
#         return 'Maintenance des Installations'

#     prefix = parts[0]
#     return FAMILLE_PREFIXES.get(prefix, code)