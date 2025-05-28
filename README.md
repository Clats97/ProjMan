# ProjMan Project Management Assistant
An easy to use Python tool that turns a plain-language scope / project into a project report with cost forecasting, timelines, contingencies, and more..

---

1. What ProjMan Is

ProjMan is a single-file Python script that behaves like a pocket-sized
consultant.  You describe *what* you want to build or buy, ProjMan crunches
numbers using a built-in price list plus deterministic estimates, and a LLM
writes a full nine-section report that covers cost, timeline,
resources, tasks, risks, and recommendations.  Everything is expressed in
**CAD $** and sized for a Canadian audience, but the logic works anywhere.

---

2. Why It Exists

Traditional project-management software is powerful but has a steep setup
curve, requires lots of manual data entry, and often hides raw assumptions
behind UI widgets.  Consultants charge by the hour.  Spreadsheets grow
chaotic.  ProjMan offers an “instant first pass” so you can:

* sanity-check a budget before seeking quotes;  
* justify a funding request with a structured narrative;  
* identify gaps in scope or resourcing early;  
* iterate quickly as ideas evolve.

It is **not** meant to replace detailed Gantt plans or a professional cost
engineer, but rather to give you a data-backed starting point in minutes.

---

3. Main Features (Expanded)

| Capability                | Details                                                                                         |
|---------------------------|--------------------------------------------------------------------------------------------------|
| Live streaming            | The report arrives in real time—no waiting for a massive JSON blob to finish.                   |
| 3 000-word guarantee      | The prompt enforces a minimum length, ensuring meaningful depth in every section.               |
| CAD currency everywhere   | Symbols, commas, spacing—you get the correct Canadian style (`CAD $ 1 234`).                    |
| Dual cost buffers         | 15 % emergency + 7 % unexpected reserves included automatically, visible in both text and pie.  |
| 450 + item catalogue      | Kitchen, laundry, HVAC, industrial machinery, and more—each with low/high price brackets.       |
| Deterministic fall-back   | Unknown items map SHA-256 bits → a repeatable pseudo-cost, so reruns stay stable.               |
| Rich ASCII summary table  | Quick glance totals with right-aligned numbers for copy-paste into e-mail or chat.              |
| PNG bar & pie charts      | Drop them straight into PowerPoint or Docs—Matplotlib handles the heavy lifting.                |
| Zero external storage     | Data lives only in RAM and the folder you run in; nothing is posted to dashboards or clouds.    |
| Pure Python 3.10+         | Aside from `openai` and `matplotlib`, no extra packages, no compiled extensions.                |

---

4. How the Magic Happens

1. **Input Phase**  
   You run `python projman.py`, type a project name (“Midtown Bakery
   Fit-Out”) and a scope (“commercial pizza oven, walk-in freezer, HVAC
   upgrade”).

2. **Parsing & Costing**  
   `parse_items()` walks the scope, matching four-word phrases down to single
   words against `ITEM_COSTS`.  Each match pulls the midpoint of its
   low/high price.  Misses feed into `deterministic_cost()`, which turns the
   first eight bytes of a SHA-256 digest into a number between 1 000 and
   20 000 CAD—stable yet unpredictable enough for rough planning.

3. **Reserve Calculation**  
   Baseline × 0.15 → emergency fund.  
   Baseline × 0.07 → unexpected fund.  
   Both are rounded to the nearest dollar for readability.

4. **Prompt Assembly**  
   A hidden “ITEM COST BREAKDOWN” context block is added so the LLM reads
   concrete numbers rather than guessing.  Then the system prompt lays out
   nine section headings and the 3 000-word rule.

5. **OpenAI Streaming**  
   The script calls `client.chat.completions.create(stream=True)`.  Each
   delta chunk’s `content` is printed immediately, so you can skim while it
   writes.

6. **Post-Processing**  
   When the stream ends, ProjMan prints a tidy cost table, saves bar and pie
   PNGs with the project name in the filename, writes the full text report
   to `<Project>_REPORT_<timestamp>.txt`, and pauses for *Enter*.

---

5. Installation

Download the ZIP from GitHub and unzip it.
Ensure Python ≥ 3.10

4. Install dependencies:
pip install --upgrade openai matplotlib

5. Add your API key, then run the scripts Python or executable (Windows) version.

6. Using ProjMan Day-to-Day

1. **Describe the scope clearly**.  More nouns → better price matches.
2. **Wait for the stream**.  On a typical broadband link, a 3 000-word
   response takes 15–30 s.
3. **Review the ASCII table** for a sanity check; adjust scope and rerun if a
   number looks off.
4. **Open the text file** in any editor—searchable, portable.
5. **Drag the PNGs** into Slack, e-mails, or slide decks.

---

7. Reading the Report

Every report is divided into:

1. **EXECUTIVE SUMMARY** – one-screen overview, business-friendly.
2. **COST ANALYSIS** – itemised spend, variance bands, reserve maths, ends
   with “OVERALL ESTIMATED COST”.
3. **TIMELINE MANAGEMENT** – Gantt-style narrative (no actual chart yet).
4. **TASK MANAGEMENT** – bullet list of work packages.
5. **RESOURCE ALLOCATION** – staffing, equipment, vendor notes.
6. **RISK ASSESSMENT** – likelihood × impact matrix in prose.
7. **MILESTONES** – critical dates with acceptance criteria.
8. **METRIC DEFINITIONS & ASSUMPTIONS** – how success and cost units are
   measured.
9. **RECOMMENDATIONS** – next steps, alternatives, procurement tips.

Because the LLM sees the price context, dollar figures in the text match the
numbers in the table and charts.

---

8. Deep Dive: Cost Engine

8.1 Item Catalogue

`ITEM_COSTS` is a plain Python dictionary where each key is a human-readable
label and the value is a two-element `(low, high)` CAD tuple:

"Commercial Pizza Oven": (3_000, 10_000)

Midpoint is chosen for baseline because it balances optimism and realism.

8.2 Deterministic Estimation

For items **not** in the catalogue, ProjMan needs a number that:

* is fast to compute (no web calls);
* stays the same across runs for the same label;
* falls into a believable range.

The function:

digest = hashlib.sha256(label.lower().encode()).digest()
value  = struct.unpack(">Q", digest[:8])[0]
return 1_000.0 + (value / 2**64) * 19_000.0

transforms 64 bits of SHA-256 into a float between 1 000 and 20 000.

---

9. Customising Behaviour

| What you want                         | Edit or set                              |
| ------------------------------------- | ---------------------------------------- |
| Use a different OpenAI model          | `MODEL_NAME` constant                    |
| Lower token count (cheaper)           | `max_completion_tokens` parameter        |
| Change emergency or unexpected ratios | `F_EMERGENCY`, `F_UNEXPECTED` constants  |
| Add or tweak price items              | `ITEM_COSTS` dictionary                  |
| Non-English report                    | Append `"Language: French"` to the scope |
| Shorter report                        | Remove the 3 000-word line in the prompt |

---

10. Performance Notes

* **CPU/RAM** – The heavy lifting happens in OpenAI’s cloud.  Local memory
  usage stays under 200 MB even with large scopes.
* **Network** – The script sends one request and receives a stream; total
  payload \~50–80 KB.
* **Matplotlib render** – Chart generation takes < 1 s on a modern laptop.

---

11. Security & Privacy

* The only outbound call is to `api.openai.com`.
* No scope text or cost data is logged elsewhere.
* Reports are saved in your working directory; git-ignore as needed.
* Keep your key out of version control—use environment variables or a
  local `.env`.

---

12. Troubleshooting

| Symptom                              | Likely Cause / Fix                                            |
| ------------------------------------ | ------------------------------------------------------------- |
| `❌ pip install matplotlib` exit     | You skipped the `pip install` step.                           |
| `401 Unauthorized` during streaming  | Bad or missing `OPENAI_API_KEY`.                              |
| ANSI banner shows garbled symbols    | Terminal encoding is not UTF-8; set `PYTHONIOENCODING=UTF-8`. |
| Pie/bar PNGs overwrite previous ones | Run in separate folders or rename the project each time.      |
| Report under 3 000 words             | Model hit length cap—raise `max_completion_tokens`.           |

---

13. License

ProjMan is licensed under the **Apache 2.0 License**.  See `LICENSE` for the full
text.


Copyright 2025 Joshua M Clatney. All Rights Reserved
