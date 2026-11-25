# POS Reengineering

Semester project: software reengineering of a legacy Point-of-Sale system.

The legacy **University Souvenir Store** application (Java 8 + Swing, CSV files) is taken through all six phases of the Software Reengineering Process Model:
1. inventory analysis
2. document restructuring
3. reverse engineering
4. code restructuring
5. data restructuring
6. forward engineering

The result is a layered **Python + Django** application backed by a relational database.

## Repository layout

| Folder | Contents |
|---|---|
| [`legacy-pos/`](legacy-pos/) | Original legacy system, **unmodified** baseline (source: `github.com/yangzai/unit1-ca`, commit `87bee5f`). Git tag `legacy-baseline`. |
| [`reengineered/`](reengineered/) | Reengineered Django application *(in progress; see its [README](reengineered/README.md))* |
| [`docs/`](docs/) | Technical report sources: inventory, legacy documentation, risk register, refactoring logs ([index](docs/README.md)) |
| [`analysis/`](analysis/) | Executable evidence from analysing the legacy code (defect probes P1–P8) |
| `presentation/` | Slides *(to be added)* |

## Running the legacy system (reference only)

Requires JDK 11 or later.

```bash
cd legacy-pos
mkdir -p /tmp/legacy-out
javac -encoding UTF-8 -d /tmp/legacy-out $(find src -name '*.java')
cp -r data-sample data
java -cp /tmp/legacy-out sg.edu.nus.iss.se24_2ft.unit1.ca.StoreApplication   # login: Stacy / Dean56s
```

Reproduce the legacy defects:

```bash
./analysis/legacy-bug-probe/run-probe.sh
```

## Running the reengineered system

Requires Python 3.12 or 3.13 (Django 5.2 LTS).

```bash
cd reengineered
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py test        # 44 tests
```

## Team and work distribution

| Member | Phases owned | Refactorings | Deliverables |
|---|---|---|---|
| Member A: Malik Nouman Ahmed | 1 Inventory Analysis, 2 Document Restructuring, legacy documentation, risk register | A1–A3 (domain model) | `docs/01`–`05`, `analysis/`, Django skeleton, `core/money.py`, `members/`, `inventory/` (Category) |
| Member B | 3 Reverse Engineering, 5 Data Restructuring | B1–B3 (persistence) | *tbd* |
| Member C | 6 Forward Engineering, testing | C1–C3 (service/UI) | *tbd* |
