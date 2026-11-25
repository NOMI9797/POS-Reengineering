# Risk Register

**Owner (maintainer):** Member A. All members add risks, and each risk has its own owner.
**Scale:**
* Likelihood (L) and Impact (I) are each rated 1–5. 1 = very low, 5 = very high.
* **Score = L × I.** 1–6 = Low, 8–12 = Medium, 15–25 = High.

**Review points:** end of each phase and before submission (1 Dec 2026).

| ID | Phase | Risk description | Category | L | I | Score | Mitigation / response | Owner | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-01 | All | **Schedule:** only 6 days remain before the deadline, so phases may overlap or be rushed | Project | 4 | 5 | **20 High** | Daily plan with owners; run phases 1–3 in parallel; freeze scope (no new features); keep a "minimum complete" version by 30 Nov | All (A tracks) | Open |
| R-02 | 3, 6 | **Lost behaviour:** the new system might not reproduce a legacy business rule (discount choice, point maths, stock checks) | Technical | 3 | 5 | **15 High** | Business-rule catalogue BR-01…18 (Phase 2); one regression test per rule; reuse the 45 legacy test assertions as the specification | C | Open |
| R-03 | 5 | **Data corruption during migration**: the legacy `Transactions.dat` may already be damaged by defect L-01, and the comma problem L-02 can split fields | Data | 4 | 4 | **16 High** | Migrate from `data-sample/` (original, untouched); validate row counts and foreign keys after migration; log rejected rows instead of dropping them silently | B | Open |
| R-04 | 3, 6 | **Preserving defects vs fixing them:** the rule "preserve functionality" conflicts with known bugs (L-01…L-06) | Requirements | 4 | 3 | **12 Medium** | Fix only defects that break the documented intent. Record each one as "intentional deviation" with a before/after test. Keep all business rules unchanged. | A + C | Open |
| R-05 | 6 | **Technology learning curve:** the chosen stack is unfamiliar to some members | People | 3 | 4 | **12 Medium** | Choose the stack the team knows best; spike a "hello CRUD" on day 1; pair programming | All | Open |
| R-06 | 6 | **Integration problems** between layers built by different members (API names, DTOs) | Technical | 3 | 4 | **12 Medium** | Agree interfaces first (repository and service signatures); integrate daily; one shared `main` branch with small PRs | C | Open |
| R-07 | All | **Uneven contribution or missing commits:** a member's work may not appear in git history (graded) | Process | 3 | 4 | **12 Medium** | Each member commits their own work under their own name; check `git shortlog -sn` daily | A | Open |
| R-08 | All | **Similarity check:** text or code too close to online sources gets zero | Compliance | 2 | 5 | **10 Medium** | Write all text in our own words; cite the legacy repository; do not copy published reengineering of this repo | All | Open |
| R-09 | 5, 6 | **Security:** plain-text passwords (DAT-06) carried into the database | Security | 3 | 3 | 9 Medium | Hash passwords (e.g. bcrypt) during migration; never log credentials | B | Open |
| R-10 | 5 | **Money precision:** `double` arithmetic causes cent differences (e.g. 66.28500000000001) | Technical | 4 | 2 | 8 Medium | Use a decimal type in code (Money value object, refactoring A3) and `DECIMAL(10,2)` in the schema; round half-up in one place | A + B | Open |
| R-11 | 6 | **Date-dependent behaviour:** discount validity depends on "today", so tests may pass today and fail later | Testing | 4 | 2 | 8 Medium | Inject a clock (time provider) into the discount service; use fixed dates in tests | C | Open |
| R-12 | 3 | **Incomplete understanding** of undocumented legacy behaviour | Technical | 2 | 4 | 8 Medium | Characterisation probes run against the legacy code (`analysis/legacy-bug-probe`); 45 legacy tests re-run (all pass) | A | Mitigated |
| R-13 | 5 | **Encoding problems:** curly apostrophes (`’`) in data files may break if read with the wrong charset | Data | 2 | 2 | 4 Low | Read as UTF-8 explicitly; DB uses UTF-8 (`utf8mb4` if MySQL) | B | Open |
| R-14 | 6 | **Environment differences:** the legacy build only works on Windows with JDK 1.8; Django 5.2 does not yet support the newest Python (3.15) | Technical | 3 | 3 | 9 Medium | Pin Python 3.12/3.13 in a virtual environment; `requirements.txt` with exact versions; README with setup steps | C | Open |
| R-15 | All | **Documentation drift:** code changes are not reflected in the report and diagrams | Process | 3 | 3 | 9 Medium | Every refactoring entry links to its commit; final consistency review on 30 Nov | A | Open |
| R-16 | Presentation | A member **cannot explain** their own work in the presentation (no marks) | People | 2 | 4 | 8 Medium | Each member presents only their own parts; dry run on 1 Dec | All | Open |
| R-17 | 6 | **Scope creep:** adding update/delete, vendor UI and other new features beyond the legacy scope | Project | 3 | 3 | 9 Medium | Guideline: "no new features". Any extra must be justified as required by the architecture (e.g. a repository `delete` method only for tests) | A | Open |

## Risk heat map (current)

| Impact ↓ / Likelihood → | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **5** | | R-08 | R-02 | R-01 | |
| **4** | | R-12, R-16 | R-05, R-06, R-07 | R-03 | |
| **3** | | | R-09, R-14, R-15, R-17 | R-04 | |
| **2** | | R-13 | | R-10, R-11 | |
| **1** | | | | | |

## Change log
| Date | Change | By |
|---|---|---|
| 25 Nov 2026 | Register created after inventory and legacy analysis (R-01…R-17); R-12 marked mitigated after probes ran | Member A |
