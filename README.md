# PlantCare Expert

A Python rule-based expert system for common indoor potted plants. Includes
20 source-linked rules, forward chaining, a local browser interface, reasoning
traces and automated tests. It suggests possible causes and care actions.

## Run

1. Install Python 3.10 or newer if needed.
2. Extract the ZIP. Open a terminal inside the `plantcare` folder.
3. Run `python app.py` (Windows) or `python3 app.py` (macOS/Linux).
4. Open **http://127.0.0.1:8000** in your browser.
5. Stop the server with Ctrl+C in the terminal.

No pip packages, accounts, API keys, database or internet connection are
needed to run the system. External reference links require internet access.
If port 8000 is occupied, run `python app.py --port 8001` and open port 8001.
This server is intended for a local classroom demonstration, not public hosting.

## Use

Answer observations across four sections. Unknown answers may remain **Not sure**.
Select **Analyse my plant**. Read the matched rules and explanation. Multiple
findings may coexist. Use **See the reasoning step by step** for the full trace.
Changing an answer clears the old result; analyse again to update it.
Use **Start again** to reset all answers or **Download consultation** to save
your current inputs and result as JSON. Consultations are not stored by the server.

**Example demonstration:** Open Visible pests. Set pale speckles and delicate
webbing to Yes. Analyse. R16 should fire in round 1 and R20 in round 2. Open the
reasoning trace and then the 20 rules and sources tab.

## Tests

From the project folder run:

```sh
python -m unittest discover -s tests -v
```

There are 30 explicit rule scenarios plus engine and HTTP tests. Running them
updates `test_results.json`. The supplied `test_run.txt` records the author's
execution environment and observed test run; it is not a claim of testing on
every operating system. Live browser testing could not be completed in the preparation environment.
The report labels its interface figures as illustrations, not screenshots.

## Files

- `app.py`: local HTTP server, static file whitelist and API validation.
- `knowledge_base.py`: 28 questions, exactly 20 rules and 5 references.
- `engine.py`: validation and snapshot-based forward chaining.
- `static/`: HTML, CSS and JavaScript presentation layer; no inference in JS.
- `tests/test_system.py`: independently specified scenarios and integration tests.
- `test_results.json`, `test_run.txt`: executed test evidence.
- `browser_review.json`: pending local browser checks and the environment limitation.
- `RULES_AND_SOURCES.md`: readable rule catalogue generated from the implementation.

## Reasoning and limitations

All required conditions must match; an optional OR group needs one match.
Omitted values become `unknown`, not `no`. Each round evaluates a snapshot of
facts. Matched rules add derived facts for the next round. Each rule fires at
most once. R14–R19 derive `pest_suspected`; R20 consumes it next round.

Results are possible findings, not confirmed diagnoses or probabilities.
No match does not establish plant health. The rules are a bounded educational
interpretation of university extension guidance, not validation on real plants.
They do not identify plants from photographs, cover all species or prescribe
chemical treatments. Adapt care to the plant species. Specialty growing
systems, cacti, aquatic plants and crop diagnosis are outside the intended scope.

## Assignment preparation

The accompanying report contains the architecture diagram, labelled interface
illustrations, knowledge base, inference explanation, rule references and test
cases. Add your name, student ID, lecturer and submission date before submitting.
Read the source code and practise the example so you can explain the work.
