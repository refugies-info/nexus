# Carif-Oref CSV Structure Documentation

## Overview

The Carif-Oref (Conseil en Orientation et Formation des Adultes) DIAN (Dispositif d'Information et d'Aide à la Navigation) export provides training program data in CSV format.

**Source**: https://www.intercariforef.org/dian/?...&excsv=1

## CSV Format

**Delimiter**: Semicolon (`;`)
**Encoding**: UTF-8 with BOM
**Line Endings**: Unix (LF)

## Column Structure

| Column Name | Field | Type | Example | Notes |
|-------------|-------|------|---------|-------|
| **ID formation** | `id_formation` | String | `24_26891724_1561867574708` | Unique identifier, required |
| **Intitulé** | `name` | String | `Français langue étrangère (FLE)` | Program title, required |
| **Début** | `start_date` | Date | `17/09/2029` | Format: DD/MM/YYYY |
| **Fin** | `end_date` | Date | `07/12/2029` | Format: DD/MM/YYYY |
| **Adressse de la formation** | `address` | String | `IBIS STYLE TOULON CENTRE PORT` | Training location |
| **Région** | `region` | String | `Provence-Alpes-Côte d'Azur` | French region name |
| **Code Postal** | `postal_code` | String | `83000` | Postal/zip code |
| **Ville** | `city` | String | `Toulon` | City name |
| **Organisme responsable** | `responsible_org` | String | `Proxima centauri company` | Organization responsible |
| **Organisme formateur** | `training_org` | String | `Proxima centauri company` | Training provider |
| **Financeurs** | `funders` | String | `Entreprise` | Funding source(s), can be empty |
| **Tel** | `phone` | String | `06 13 56 40 79` | Contact phone number |

## Data Characteristics

### ID Formation
- **Format**: `[dept]_[org_id]_[training_id]` or similar
- **Example**: `24_26891724_1561867574708`
- **Uniqueness**: Unique within DIAN export
- **Required**: Yes

### Name (Intitulé)
- **Format**: French text, often includes training level (A1, A2, B1, etc.)
- **Examples**:
  - "Français langue étrangère (FLE)"
  - "Examen DELF Tout Public - Diplôme d'Etudes Langue Française"
  - "Certificat de capacité à l'enseignement du français langue étrangère - FLE"
- **Required**: Yes

### Dates
- **Format**: DD/MM/YYYY (French date format)
- **Examples**: `17/09/2029`, `02/12/2026`
- **Parsing**: Must convert to ISO 8601 (YYYY-MM-DD) for storage
- **Validation**: End date should be >= start date

### Region
- **Format**: Full French region name
- **Examples**:
  - "Provence-Alpes-Côte d'Azur"
  - "Île-de-France"
  - "Bourgogne-Franche-Comté"
  - "Auvergne-Rhône-Alpes"
- **Mapping**: Can be mapped to department codes (75=Paris, 69=Lyon, etc.)

### Postal Code
- **Format**: 5-digit French postal code
- **Examples**: `83000`, `75001`, `89000`
- **Validation**: Must be 5 digits

### Phone
- **Format**: French phone number with spaces
- **Examples**: `06 13 56 40 79`, `0146946269`
- **Parsing**: Remove spaces for normalization

### Funders
- **Format**: Comma-separated values or empty
- **Examples**: `Entreprise`, `Bénéficiaire de l'action`, empty string
- **Optional**: Can be empty

## Sample Records

### French Language Course (FLE)
```csv
"ID formation";"Intitulé";"Début";"Fin";"Adressse de la formation";"Région";"Code Postal";"Ville";"Organisme responsable";"Organisme formateur";"Financeurs";"Tel"
24_26891724_1561867574708;"Français langue étrangère (FLE)";17/09/2029;07/12/2029;"IBIS STYLE TOULON CENTRE PORT";"Provence-Alpes-Côte d'Azur";83000;Toulon;"Proxima centauri company";"Proxima centauri company";;"06 13 56 40 79"
```

### DELF Exam
```csv
10_2592317F10_382836S382836S;"Examen DELF Tout Public  - Diplôme d'Etudes Langue Française";02/12/2026;02/12/2026;"GRETA 89";Bourgogne-Franche-Comté;89000;Auxerre;"GRETA 89";"GRETA 89";Entreprise;0386721040
```

### Professional Certification
```csv
03_1802266F03_2443020S2443020S;"Certificat de capacité à l'enseignement du français langue étrangère - FLE";30/11/2026;18/12/2026;"Cavilam - Alliance Française";Auvergne-Rhône-Alpes;03200;Vichy;"Cavilam - Alliance Française";"Centre d'approches vivantes des langues et des médias";"Bénéficiaire de l'action";0470308383
```

## Parsing Implementation

### Python CSV Parser

```python
import csv
import io
from datetime import datetime

def parse_carif_oref_csv(csv_content: str) -> list[dict]:
    """Parse Carif-Oref CSV into normalized records."""
    records = []
    csv_file = io.StringIO(csv_content)
    reader = csv.DictReader(csv_file, delimiter=";")

    for row in reader:
        record = {
            "id_formation": row.get("ID formation", "").strip(),
            "name": row.get("Intitulé", "").strip(),
            "start_date": row.get("Début", "").strip(),
            "end_date": row.get("Fin", "").strip(),
            "address": row.get("Adressse de la formation", "").strip(),
            "region": row.get("Région", "").strip(),
            "postal_code": row.get("Code Postal", "").strip(),
            "city": row.get("Ville", "").strip(),
            "responsible_org": row.get("Organisme responsable", "").strip(),
            "training_org": row.get("Organisme formateur", "").strip(),
            "funders": row.get("Financeurs", "").strip(),
            "phone": row.get("Tel", "").strip(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        # Only include records with essential fields
        if record["id_formation"] and record["name"]:
            records.append(record)

    return records
```

## Data Quality Considerations

### Common Issues
1. **Encoding**: File may have UTF-8 BOM - handle with `encoding='utf-8-sig'`
2. **Quotes**: Fields with special characters are quoted
3. **Empty Fields**: Represented as empty string between delimiters
4. **Typos**: "Adressse" has extra 's' (not a typo in source data)
5. **Date Format**: Always DD/MM/YYYY, never ISO format

### Validation Rules
- `id_formation` must be non-empty and unique
- `name` must be non-empty
- `start_date` and `end_date` must be valid dates in DD/MM/YYYY format
- `postal_code` should be 5 digits
- `phone` should be valid French format

### Normalization
- Convert dates from DD/MM/YYYY to ISO 8601 (YYYY-MM-DD)
- Strip leading/trailing whitespace from all fields
- Normalize phone numbers (remove spaces)
- Convert region names to lowercase for matching

## Integration with Nexus Pipeline

### Reconciliation Process
1. **Fetch**: Download latest CSV from intercariforef.org (hourly)
2. **Parse**: Convert CSV to normalized records
3. **Match**: Match with Data Inclusion programs by structure/service IDs
4. **Merge**: Combine data from both sources
5. **Detect**: Identify conflicts between sources
6. **Resolve**: Apply deterministic resolution rules

### Matching Strategy
- Primary key: `id_formation` (Carif-Oref) ↔ `structure_id` + `service_id` (Data Inclusion)
- Fallback: Fuzzy match on program name + city

### Data Precedence
- **Recency Rule**: If Carif-Oref is more recent, use its values
- **Completeness Rule**: If timestamps equal, prefer more complete source
- **Default**: Carif-Oref takes precedence when tied

## Update Frequency

- **Fetch Schedule**: Hourly (top of each hour)
- **Source Update**: Daily from intercariforef.org
- **Latency Target**: <1 hour from source update to Nexus database

## References

- **Source**: https://www.intercariforef.org/dian/
- **Export URL**: https://www.intercariforef.org/dian/?...&excsv=1
- **Documentation**: https://www.intercariforef.org/

## Related Files

- `apps/orchestration/src/services/carif_oref.py` - CSV fetch scheduler
- `apps/orchestration/src/services/reconciliation.py` - Reconciliation logic
- `apps/orchestration/tests/fixtures/test_programs.json` - Test data
