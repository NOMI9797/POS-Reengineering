# Live Demo – Inventory Analysis (SonarQube + inventory script)

About 4 minutes. SonarQube shows code size and smells in a web dashboard; the inventory
script covers what SonarQube cannot: obsolete classes, dependencies, tests and defects.

## Before the class (5 minutes, not shown)

```bash
cd ~/Desktop/RE_Project
./analysis/sonarqube/start-sonarqube.sh      # starts Docker + SonarQube, waits until ready
```

Open http://localhost:9000 and log in as `admin` (password: the one set during setup, kept in your own notes).
Open a Terminal in `~/Desktop/RE_Project`, text enlarged (Cmd +).

## Live part

### 1. Run the analysis (SonarQube) – about 20 seconds

```bash
./analysis/sonarqube/run-sonar-scan.sh
```

Say: "SonarScanner compiles and analyses the unmodified legacy code and uploads the results to SonarQube."
Wait for `ANALYSIS SUCCESSFUL`, then click the link or refresh http://localhost:9000/dashboard?id=legacy-pos.

### 2. Identify the code assets – Overview and Code tabs

| Click | Point at | Say |
|---|---|---|
| Overview | Lines of code, issues, duplications | "This is the size and health of the legacy system." |
| Code tab | The package folders and the lines per file | "Every Java asset is identified: 40 files, 40 classes, 13 packages." |
| Measures → Size | Lines 3,901, Classes 40, Functions 219 | "SonarQube counts 3,901 lines; our inventory counts 3,883 because SonarQube adds the empty line after a final newline in 18 files." |
| Measures → Complexity | Cyclomatic complexity 541 | "The largest classes are the checkout dialogs and the Managers – the same ones our inventory marks Rework." |
| Measures → Duplications | 6 duplicated blocks | "Duplicated code in the Managers – smell S-02." |

### 3. Smell indicators – Issues tab (filter by Rule)

| Rule in SonarQube | Count | Our inventory finding |
|---|---|---|
| Track uses of "TODO" tags (S1135) | 13 | 12 TODO comments in production code + 1 in a test |
| Debug features in production / printStackTrace (S4507) | 16 | 16 swallowed errors (S-09) |
| Sections of code should not be commented out (S125) | 6 blocks | ≈ 62 commented-out lines (S-08) |
| Unused imports (S1128) | 6 | Dead code (S-08), e.g. `ProductPanel` |
| Methods should not have too many lines (S138) | 4 | Long methods (S-03), `ConfirmPaymentDialog` |
| Cognitive complexity (S3776) / class coupling (S1200) | 2 / 2 | God classes and coupling (S-01) |
| Non-thread-safe fields should not be static (S2885, bug) | 1 | Shared `SimpleDateFormat` (S-13) |

Say: "SonarQube confirms the smell indicators we measured: 12 TODOs, 16 swallowed exceptions, commented-out code and long methods."

### 4. What SonarQube cannot do – switch to the Terminal

Say: "SonarQube only analyses code quality. The rest of the inventory – classifying obsolete assets, mapping dependencies, running the tests and proving the defects – is done by our script and jdeps."

```bash
./analysis/inventory/inventory.sh
```

Scroll to and point at:

| Section of the output | Say |
|---|---|
| 1. Asset counts | "All assets, including the 11 data files, configs and scripts SonarQube ignores." |
| 4. Obsolete check | "`AdhesiveLabelPrinter` has 0 references – obsolete. SonarQube does not flag it because it is a public class." |
| 6. Package dependencies (jdeps) | "jdeps maps 39 package dependencies; 5 business packages depend on the Swing GUI library – a layer violation." |

Then the evidence from running the legacy code:

```bash
./analysis/legacy-bug-probe/run-probe.sh
```

Say: "P1: after one new sale, every member sale is rewritten as PUBLIC – data loss found by running the code, which static tools cannot see."

### 5. After the class

```bash
./analysis/sonarqube/stop-sonarqube.sh       # frees memory; results stay saved
```

## If something goes wrong

| Problem | Fix |
|---|---|
| Dashboard does not open | Run `./analysis/sonarqube/start-sonarqube.sh` again and wait for "ready" |
| Scan says "Not authorized" | The token in `~/.sonarqube-pos-token` was deleted; create a new one in SonarQube → My Account → Security |
| Very slow Mac | Close other apps; SonarQube uses about 2–3 GB of memory |
| No time | Show the saved screenshots in the report (Section 2 and 7) instead |
