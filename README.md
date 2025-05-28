# ProjMan Project Management Assistant
An easy to use Python tool that turns a plain-language scope / project into a project report with cost forecasting, timelines, contingencies, and more. An example output is at the end of this readme.

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

5. Add your API key, then run the script.

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

13. Example Output
── Streaming report ──

EXECUTIVE SUMMARY

This report provides a comprehensive project plan for the renovation of a 250 square foot bedroom, encompassing the installation of wood floors, a dedicated desk area, a double-sized bed, a new closet, and the addition of a bathroom with a shower and bathtub. The project scope is defined according to the outlined requirements and leverages best practices for residential renovation planning in Canada. Special emphasis is placed on cost monitoring, timeline management, resource allocation, risk assessment, and milestone setting to ensure the seamless execution of the renovation while respecting budgetary and scheduling constraints. The documented costs include a general allowance, as well as calculated reserves for emergencies and unforeseen expenses, ensuring preparedness for contingencies. This report aims to equip stakeholders with a strategic, clear, and actionable roadmap for delivering a quality bedroom and en-suite renovation that meets both aesthetic and functional objectives.

COST ANALYSIS

The cost projection for this bedroom renovation is grounded in a systematic evaluation of both direct costs (labour, materials, fixtures, finishes) and indirect or contingency-related costs. The project’s cost structure is built as follows:

• Baseline (Expected) Cost: CAD $ 6,637  
  The baseline includes the anticipated expenses for demolition, material procurement (hardwood flooring, bathroom fixtures, cabinetry), labour charges (carpentry, plumbing, electrical, painting), and the acquisition/installation of major furnishings (desk, bed, closet).

• Variance Bands:  
  Cost overruns in residential renovation are common, particularly in older homes or scenarios involving the addition of new plumbing and electrical fixtures. Therefore, variance bands have been considered to cover expected fluctuations arising from supplier delivery timing, unforeseen subfloor issues, the complexity of bathroom integration, and other routine variables.

  - Moderate Overrun (Up to +10%): CAD $ 664  
  - High Overrun (Up to +20%): CAD $ 1,327

• Emergency Reserve (15%): CAD $ 995  
  This reserve is earmarked for significant but predictable risks such as minor structural repairs, unexpected code-related upgrades, or rapid material replacements if items arrive damaged.

• Unexpected Reserve (7%): CAD $ 465  
  This smaller, flexible reserve addresses rare and highly unpredictable risks including abrupt labour or supplier shortages, accidental breakage of unique imported items, or sudden regulatory changes influencing material use or accessibility.

In summary, the cost management strategy is designed to uphold financial discipline while affording the flexibility to address emerging challenges without project delays or scope compromise.

OVERALL ESTIMATED COST: CAD $ 8,097

TIMELINE MANAGEMENT

Delivering the project on time demands an integrated approach to schedule planning, with clearly identified phases, dependencies, and milestone checkpoints. The recommended project duration for a bedroom renovation of this scope (including the construction of a full bathroom) is approximately 8–10 weeks from initiation to final inspection, assuming regulatory and supply-chain stability.

Key phases and their estimated durations include:

1. Design & Permitting (Week 1–2)
   • Finalize plans, conduct site assessment, and secure necessary municipal construction permits, especially for plumbing and drainage.
   • Parallel procurement of long-lead items (bathtub, custom closet kits) to prevent mid-project delays.

2. Demolition & Initial Prep (Week 2–3)
   • Strip existing flooring, prepare subfloor, and erect new structural framing for bathroom partitions.
   • Remove or reroute electrical and plumbing lines as per new layouts.

3. Core Construction (Week 3–6)
   • Rough-in plumbing and electrical for bathroom addition.
   • Framing and drywall installation, bathroom waterproofing, and floor leveling.
   • Begin bathroom tiling, bathtub, and shower base installation.
   • Simultaneous progress on new closet framing and desk nook cabinetry.

4. Finishes & Installation (Week 7–8)
   • Install wood flooring, door hardware, lighting fixtures, and final backsplash/floor tiling.
   • Set up major furnishings: double bed, built-in desk, closet systems.
   • Install, test, and commission bathroom fixtures (vanity, toilet, shower door).

5. Inspection & Punch List (Week 9–10)
   • Conduct municipal or third-party inspections for plumbing and electrics.
   • Address punch-list deficiencies (e.g., paint touch-ups, caulking, fixture adjustments).

To remain on schedule:
   • Weekly check-ins and daily progress logs should be maintained.
   • Suppliers should be briefed with clear, non-negotiable deadlines.
   • Contractor schedules should be cross-referenced to prevent subcontractor roadblocks.
   • Overlaps are encouraged in finish and furnishing installation to compress the timeline without compromising sequencing integrity.

Slack time (buffer days for weather, delivery, or permit delay) totaling 1 week is built into the project, principally between rough-in and finishes phases.

TASK MANAGEMENT

Successful delivery requires granular task breakdown, robust sequencing, and clear assignment of responsibility. Major tasks and subtasks are as follows:

1. Pre-Construction
   • Conduct client requirements survey.
   • Engage architect/designer.
   • Complete site measurement and digital modeling.
   • Review and finalize choice of flooring, fixtures, and finishes.

2. Permits & Procurement
   • Submit building permit applications.
   • Order primary construction materials, wood flooring, tiles, bathroom fixtures, and lighting.

3. Demolition
   • Remove existing flooring, baseboards, and fixtures.
   • Box off and protect non-renovation areas.

4. Carpentry and Structural
   • Frame new bathroom enclosure and utility chases.
   • Build closet and integrated desk support structures.
   • Reposition entry or closet doors (as necessary).

5. Mechanical (Plumbing & Electrical)
   • Rough-in hot/cold water supply and drain lines.
   • Rewire or extend circuits for lighting, outlets, and underfloor heating (if specified).

6. Wall & Floor Prep
   • Drywall hanging, taping, and mudding.
   • Apply waterproofing membrane to bathroom walls and floors.
   • Level and repair subfloor as required.

7. Finishes/Installations
   • Lay wood flooring in main bedroom.
   • Tile bathroom floors and lower walls.
   • Install bath, shower controls, toilet, vanity, mirror, and towel bars.
   • Mount closet hardware and shelving.
   • Assemble desk and install task lighting.

8. Finalization
   • Paint and touch-up all surfaces.
   • Clean entire suite, conduct final walkthrough with client and contractor.
   • Schedule and receive city inspector signoff.

Task allocation should place key responsibilities with the prime contractor, while specialty trades (licensed plumber and electrician) perform code-sensitive work. Progress tracking should employ Gantt charting or digital project management tools to enable timely intervention on slippages or bottlenecks.

RESOURCE ALLOCATION

Effective resource allocation is critical in ensuring both quality and adherence to schedule. Human resources, equipment, and material resources must be precisely mapped to the project calendar and sequence.

• Human Resources:
   - Project Manager: Oversees schedule, financial controls, and quality assurance.
   - Subcontractors: Expert carpenters for framing, finishers for flooring and cabinetry, licensed plumber and electrician for wet and powered work, specialized tiler for bathroom surfaces.
   - Interior Designer (part-time): Consults on layout and finish selection, ensures fusion of aesthetic with functionality.
   - Labourers: Perform demolition, materials handling, and site cleaning.

• Material Resources:
   - Wood flooring (select Canadian maple or equivalent for durability).
   - Moisture-resistant drywall and cement board for bathroom.
   - High-quality plumbing fixtures, eco-friendly ventilation, dual-flush toilet.
   - Double-bed frame and mattress, ergonomic desk system, closet hardware.
   - Paints/finishes with low-VOC content for indoor air quality.

• Equipment and Tools:
   - Power saws, nail guns, drills, tile cutters, and finish sanders.
   - Personal protective equipment (PPE) for all workers.
   - Dehumidifiers or fans to ensure drying between phases.

Resource sequencing is optimized by pre-staging materials, avoiding on-site congestion, and ensuring high-value trades (licensed plumber/electrician) are deployed only when the site is prepared, avoiding idle time and billing discrepancies. Supplier agreements should stipulate firm delivery schedules and penalty clauses for late shipments on critical path items.

RISK ASSESSMENT

Residential renovations, particularly those introducing new plumbing systems or significant built-ins, are affected by a range of project risks. These should be proactively managed through early identification, contingency planning, and ongoing supervision.

Major risk categories include:

1. Regulatory/Permitting Risk
   • Permits may require multiple resubmissions or have unexpected approval lags.
   • Mitigation: Early engagement with municipal building officials, ensure applications are detailed and error-free.

2. Design Scope Creep
   • Late changes requested by homeowner can disrupt sequencing and add costs.
   • Mitigation: Formal sign-off on design documents. Change requests after approval to be priced and time-assessed before acceptance.

3. Supply Chain Volatility
   • Delays in materials (flooring, tiles, fixtures) can arrest on-site progress.
   • Mitigation: Dual sourcing for high-risk supplies, maintain ‘buffer stock’ of universally-used components.

4. Subsurface Surprises
   • Discovery of uneven subfloor, mold, or hidden water damage during demolition.
   • Mitigation: Include a demolition/assessment phase with short schedule buffer for contingency repair.

5. Trades Coordination
   • Poor handoff between trades (e.g., late completion of plumbing rough-in holding up drywall) leads to compounded delays.
   • Mitigation: Weekly cross-trade coordination meetings, transparent task completion checklists.

6. Financial Overruns
   • Unexpected finds or extended timelines deplete baseline funds.
   • Mitigation: Maintain strict budget monitoring, ready access to reserves, and client pre-approval on emergent costs.

7. Health and Safety
   • Tight spaces, dust, or tool mishandling can endanger trades.
   • Mitigation: Frequent toolbox safety talks, proper PPE, and strict adherence to provincial OHS standards.

8. Weather Dependencies
   • If any exterior wall work is required, weather may introduce delays or additional protection costs.
   • Mitigation: Schedule critical external works for best-forecast weeks, plan weather-resistant site protection.

Continuous risks monitoring, paired with a well-communicated escalation path (from site foreman to client), is indispensable in shrinking reaction times and minimizing impact.

MILESTONES

The following are major progress markers to guide the renovation:

1. Design & Permit Milestone
   • Approved architectural/design drawings and city-issued renovation permits.

2. Demolition Completion
   • All targeted demolition and tear-out work completed, site prepped for construction.

3. Framing & Utility Completion
   • Erection of new bathroom and closet structural elements, finalization of plumbing and electrical rough-in.

4. Closed-in Inspection Pass
   • Successful municipal inspection of hidden plumbing and electrics, allowing wall/floor closure.

5. Main Flooring & Bathroom Tile Completion
   • Wood flooring and all bathroom tiling complete, surfaces ready for fixture install.

6. Fixture and Finish Install Complete
   • Bathtub, shower, vanity, toilet, closet interiors, bed and desk installation executed.

7. Final Inspection Milestone
   • City inspection passed on all applicable systems (plumbing, electrical), with a fully code-compliant result.

8. Client Walkthrough & Handover
   • Final cleaning and snag list addressed. Room ready for immediate use.

Each milestone is accompanied by a review meeting (with onsite inspection and checklist validation) to ensure all parties (client, project manager, key contractors) agree on quality and completion prior to advancing. Milestone documentation is crucial for clear payment schedule adherence.

METRIC DEFINITIONS & ASSUMPTIONS

This section outlines the metrics and baseline assumptions steering this project plan:

• ROOM AREA: 250 sq. ft. (inclusive of new bathroom)
• FLOORING TYPE: Quality pre-finished Canadian hardwood (cost averaged for mid-market supply)
• BED: Standard double-size (54” x 74”), cost includes frame and mid-range mattress
• DESK: Integrated or free-standing, with standard power/data outlet nearby
• CLOSET: Custom or semi-custom (6’ width), shelf and hanging rod system
• BATHROOM:
   - Shower Stall: 32” x 48”, waterproofed, with 3-piece fixture set
   - Bathtub: 60” soaker, acrylic or enamelled steel construction
   - Vanity: 30” with integrated sink and storage
   - Toilet: Dual-flush, WaterSense certified
• PERMITTING: Required for plumbing addition, included in schedule and cost estimates
• CONTRACTOR RATES: Assumed prevailing rates for Toronto/Vancouver average (adjust as necessary for regional variance)
• MATERIAL AVAILABILITY: All standard materials expected to be locally sourced – imported lead times are excluded unless client-specified
• CONTINGENCY: Emergency reserve = 15% of baseline; unexpected reserve = 7%
• INSPECTIONS: One pre-drywall (mechanicals), one final (occupancy)
• SCHEDULE: Full project duration assumed at 8–10 weeks, with built-in slack
• CLIENT DECISION WINDOWS: All client-input choices (finish, paint, hardware) required two weeks pre-installation to preserve schedule integrity

RECOMMENDATIONS

To ensure a successful renovation and minimize disruption, the following recommendations are made to the homeowner and/or project sponsor:

1. Commit to Final Design Early
   • The most common source of overruns is late-stage design alterations. Finalize all selections (from flooring to fixtures) before mobilization and enforce a formal change process for any post-approval modifications.

2. Stage Materials in Advance
   • For all critical-path components (flooring, plumbing kits, cabinetry), confirm availability and delivery dates prior to demolition. Consider local warehouse temporary storage if space is insufficient onsite.

3. Insist on Contractual Clarity
   • Employ clear and thorough contracts with all trades and suppliers, including scope of work, fixed pricing where possible, and defined penalty/bonus clauses for late/early completion.

4. Monitor, Communicate, Document
   • Establish weekly update meetings (virtual or onsite) to review progress, address issues, and adjust plans as required. Insist on written daily job logs, including photographs and supervisor sign-offs at each phase.

5. Leverage Technology
   • Utilize digital project management platforms to track tasks, share documents, and record milestone completion dates, ensuring all stakeholders maintain visibility.

6. Set Aside Disruption Mitigation Resources
   • With work occurring in a single room, dust, noise, and temporary water/electric shutoffs may impact adjoining spaces. Budget for protective barriers, air scrubbing, and ‘quiet hours’ to reduce stakeholder friction.

7. Hold Regular Cross-Trade Meetings
   • Effective coordination between trades (plumbing, electrical, finishing) prevents sequencing breakdowns. Facilitate weekly coordination huddles and maintain a shared site schedule accessible to all subcontractors.

8. Rigorously Enforce Health & Safety
   • Demand compliance with all OHS protocols. Clearly communicate emergency contacts and maintain stocked first-aid kits onsite.

9. Review Contingency Plans Monthly
   • Hold formal contingency/budget reviews at set milestones, adjusting reserves and timelines as project unfolds, to prevent surprises and preserve financial control.

10. Prioritize Code Compliance
   • Insist that all work is completed to Provincial and Municipal standards, with full inspection and approval at the relevant stages. This mitigates long-term risk and ensures the safety, value, and legality of the renovated space.

Through adherence to these recommendations, the renovation is well-positioned to achieve a high-quality, on-budget, and on-schedule result, transforming the targeted bedroom into a modern, comfortable, and fully functional personal suite. The structured plan presented herein will serve as an indispensable reference throughout project execution, supporting stakeholder alignment, informed decision-making, and robust project governance.
── End of report ──


SUMMARY METRICS
----------------------------------------------------------------------
Item                                     |           CAD $
----------------------------------------------------------
General Allowance                        |           6,637
----------------------------------------------------------
BASELINE TOTAL                           |           6,637
EMERGENCY RESERVE (15%)                  |             995
UNEXPECTED RESERVE (7%)                  |             465
OVERALL ESTIMATED COST                   |           8,097
----------------------------------------------------------------------

📊  Saved bar chart → room_breakdown.png
📈  Saved reserve pie chart → room_reserves.png

---

15. License

ProjMan is licensed under the **Apache 2.0 License**.  See `LICENSE` for the full
text.


Copyright 2025 Joshua M Clatney. All Rights Reserved
