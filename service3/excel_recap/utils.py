
import pandas as pd
from decimal import Decimal, InvalidOperation

from .models import BudgetRecord


def safe_decimal(value):
    try:
        if pd.isna(value):
            return None
        # Si c'est une string non numérique → None
        if isinstance(value, str):
            value = value.strip().replace(' ', '').replace(',', '.')
            if not value or not value.replace('.', '').replace('-', '').isdigit():
                return None
        return Decimal(str(round(float(value))))
    except (InvalidOperation, TypeError, ValueError):
        return None

def parse_excel(file, upload_instance):
    from .models import BudgetRecord

    if file.name.endswith('.xls'):
        engine = 'xlrd'
    else:
        engine = 'openpyxl'

    df = pd.read_excel(file, skiprows=2, header=None, engine=engine)

    records = []
    for _, row in df.iterrows():
        if len(row) < 6:
            continue

        def get(i):
            return safe_decimal(row.iloc[i]) if len(row) > i else None

        record = BudgetRecord(
            upload=upload_instance,
            activite=str(row.iloc[0]) if pd.notna(row.iloc[0]) else None,
            region=str(row.iloc[1])   if pd.notna(row.iloc[1]) else None,
            perm=str(row.iloc[2])     if pd.notna(row.iloc[2]) else None,
            famille=str(row.iloc[3])  if pd.notna(row.iloc[3]) else None,
            code_division=str(row.iloc[4]) if pd.notna(row.iloc[4]) else None,
            libelle=str(row.iloc[5])  if pd.notna(row.iloc[5]) else None,

            # Coût initial
            cout_initial_total=get(6),
            cout_initial_dont_dex=get(7),

            # Réalisation cumulée N-1
            realisation_cumul_n_mins1_total=get(8),
            realisation_cumul_n_mins1_dont_dex=get(9),

            # Réalisation S1 N
            real_s1_n_total=get(10),
            real_s1_n_dont_dex=get(11),

            # Prévision S2 N
            prev_s2_n_total=get(12),
            prev_s2_n_dont_dex=get(13),

            # Prévision clôture N
            prev_cloture_n_total=get(14),
            prev_cloture_n_dont_dex=get(15),

            # Prévision N+1
            prev_n_plus1_total=get(16),
            prev_n_plus1_dont_dex=get(17),

            # Reste à réaliser
            reste_a_realiser_total=get(18),
            reste_a_realiser_dont_dex=get(19),

            # Prévision N+2
            prev_n_plus2_total=get(20),
            prev_n_plus2_dont_dex=get(21),

            # Prévision N+3
            prev_n_plus3_total=get(22),
            prev_n_plus3_dont_dex=get(23),

            # Prévision N+4
            prev_n_plus4_total=get(24),
            prev_n_plus4_dont_dex=get(25),

            # Prévision N+5
            prev_n_plus5_total=get(26),
            prev_n_plus5_dont_dex=get(27),

            # Mensuel
            janvier_total=get(28),    janvier_dont_dex=get(29),
            fevrier_total=get(30),    fevrier_dont_dex=get(31),
            mars_total=get(32),       mars_dont_dex=get(33),
            avril_total=get(34),      avril_dont_dex=get(35),
            mai_total=get(36),        mai_dont_dex=get(37),
            juin_total=get(38),       juin_dont_dex=get(39),
            juillet_total=get(40),    juillet_dont_dex=get(41),
            aout_total=get(42),       aout_dont_dex=get(43),
            septembre_total=get(44),  septembre_dont_dex=get(45),
            octobre_total=get(46),    octobre_dont_dex=get(47),
            novembre_total=get(48),   novembre_dont_dex=get(49),
            decembre_total=get(50),   decembre_dont_dex=get(51),
        )
        records.append(record)

    BudgetRecord.objects.bulk_create(records)
    return len(records)

def auto_correct_records(qs):
    """
    Corrige automatiquement les records selon les 4 règles métier.
    Retourne le nombre de records corrigés et le détail.
    """
    TOLERANCE = 1
    corrected = []

    def val(x):
        return float(x or 0)

    for record in qs:
        changed = False

        # ── RÈGLE 1 : Prév.Clôture N = Réal.S1 + Prév.S2 ──────────────
        # On recalcule prev_cloture depuis les composantes (plus fiables)
        calc_cloture_total = val(record.real_s1_n_total) + val(record.prev_s2_n_total)
        if abs(calc_cloture_total - val(record.prev_cloture_n_total)) > TOLERANCE:
            record.prev_cloture_n_total = round(calc_cloture_total, 2)
            changed = True

        calc_cloture_dex = val(record.real_s1_n_dont_dex) + val(record.prev_s2_n_dont_dex)
        if abs(calc_cloture_dex - val(record.prev_cloture_n_dont_dex)) > TOLERANCE:
            record.prev_cloture_n_dont_dex = round(calc_cloture_dex, 2)
            changed = True

        # ── RÈGLE 2 : Reste à Réaliser = N+2 + N+3 + N+4 + N+5 ─────────
        calc_rar_total = (
            val(record.prev_n_plus2_total) + val(record.prev_n_plus3_total)
            + val(record.prev_n_plus4_total) + val(record.prev_n_plus5_total)
        )
        if abs(calc_rar_total - val(record.reste_a_realiser_total)) > TOLERANCE:
            record.reste_a_realiser_total = round(calc_rar_total, 2)
            changed = True

        calc_rar_dex = (
            val(record.prev_n_plus2_dont_dex) + val(record.prev_n_plus3_dont_dex)
            + val(record.prev_n_plus4_dont_dex) + val(record.prev_n_plus5_dont_dex)
        )
        if abs(calc_rar_dex - val(record.reste_a_realiser_dont_dex)) > TOLERANCE:
            record.reste_a_realiser_dont_dex = round(calc_rar_dex, 2)
            changed = True

        # ── RÈGLE 3 : Prév.N+1 = Somme des 12 mois ──────────────────────
        somme_mois = (
            val(record.janvier_total)   + val(record.fevrier_total)  +
            val(record.mars_total)      + val(record.avril_total)    +
            val(record.mai_total)       + val(record.juin_total)     +
            val(record.juillet_total)   + val(record.aout_total)     +
            val(record.septembre_total) + val(record.octobre_total)  +
            val(record.novembre_total)  + val(record.decembre_total)
        )
        if abs(somme_mois - val(record.prev_n_plus1_total)) > TOLERANCE:
            record.prev_n_plus1_total = round(somme_mois, 2)
            changed = True

        # ── RÈGLE 4 : Coût Global = Réal.Cumul N-1 + Clôture N + N+1 + RAR ──
        # On recalcule après les corrections précédentes (ordre important !)
        calc_cout_total = (
            val(record.realisation_cumul_n_mins1_total)
            + val(record.prev_cloture_n_total)   # déjà corrigé si besoin
            + val(record.prev_n_plus1_total)      # déjà corrigé si besoin
            + val(record.reste_a_realiser_total)  # déjà corrigé si besoin
        )
        if abs(calc_cout_total - val(record.cout_initial_total)) > TOLERANCE:
            record.cout_initial_total = round(calc_cout_total, 2)
            changed = True

        calc_cout_dex = (
            val(record.realisation_cumul_n_mins1_dont_dex)
            + val(record.prev_cloture_n_dont_dex)
            + val(record.prev_n_plus1_dont_dex)
            + val(record.reste_a_realiser_dont_dex)
        )
        if abs(calc_cout_dex - val(record.cout_initial_dont_dex)) > TOLERANCE:
            record.cout_initial_dont_dex = round(calc_cout_dex, 2)
            changed = True

        if changed:
            corrected.append(record)

    # Bulk update uniquement les records modifiés
    if corrected:
        FIELDS_TO_UPDATE = [
            'prev_cloture_n_total', 'prev_cloture_n_dont_dex',
            'reste_a_realiser_total', 'reste_a_realiser_dont_dex',
            'prev_n_plus1_total',
            'cout_initial_total', 'cout_initial_dont_dex',
        ]
        BudgetRecord.objects.bulk_update(corrected, FIELDS_TO_UPDATE)

    return len(corrected)