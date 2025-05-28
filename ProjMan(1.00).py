from __future__ import annotations
import sys, traceback, re, hashlib, struct, textwrap
from datetime import datetime
from pathlib import Path

_RED   = "\033[31m"
_RESET = "\033[0m"
_ASCII_BANNER = r"""
██████╗ ██████╗  ██████╗      ██╗███╗   ███╗ █████╗ ███╗   ██╗
██╔══██╗██╔══██╗██╔═══██╗     ██║████╗ ████║██╔══██╗████╗  ██║
██████╔╝██████╔╝██║   ██║     ██║██╔████╔██║███████║██╔██╗ ██║
██╔═══╝ ██╔══██╗██║   ██║██   ██║██║╚██╔╝██║██╔══██║██║╚██╗██║
██║     ██║  ██║╚██████╔╝╚█████╔╝██║ ╚═╝ ██║██║  ██║██║ ╚████║
╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
"""
print(f"{_RED}{_ASCII_BANNER}{_RESET}")

try:
    import matplotlib.pyplot as plt
except ImportError:
    sys.exit("❌  pip install matplotlib")

try:
    from openai import OpenAI
except ImportError:
    sys.exit("❌  Run:  pip install --upgrade openai")

API_KEY    = "INSERT API KEY HERE"
MODEL_NAME = "gpt-4.1"
client     = OpenAI(api_key=API_KEY)

ITEM_COSTS: dict[str, tuple[float, float]] = {
    # Kitchen Appliances
    "Blender": (50, 200),
    "Bread Maker": (100, 300),
    "Coffee Maker": (50, 300),
    "Countertop Oven": (100, 300),
    "Deep Fryer": (50, 200),
    "Dishwasher": (800, 1500),
    "Electric Can Opener": (20, 50),
    "Electric Crepe Maker": (30, 100),
    "Electric Donut Maker": (30, 100),
    "Electric Egg Cooker": (20, 50),
    "Electric Egg Roll Maker": (20, 50),
    "Electric Espresso Machine": (100, 1000),
    "Electric Fondue Set": (30, 100),
    "Electric Griddle": (30, 100),
    "Electric Grill": (100, 300),
    "Electric Hot Dog Roller": (30, 100),
    "Electric Hot Plate": (20, 100),
    "Electric Ice Cream Maker": (50, 200),
    "Electric Juicer": (50, 300),
    "Electric Knife": (30, 100),
    "Electric Meat Grinder": (50, 200),
    "Electric Milk Frother": (20, 50),
    "Electric Pasta Maker": (100, 300),
    "Electric Pizza Maker": (50, 150),
    "Electric Popcorn Maker": (20, 100),
    "Electric Pressure Cooker": (80, 200),
    "Electric Quesadilla Maker": (20, 50),
    "Electric Raclette Grill": (50, 200),
    "Electric Sandwich Maker": (20, 50),
    "Electric Skillet": (30, 100),
    "Electric S'mores Maker": (20, 50),
    "Electric Snow Cone Maker": (30, 100),
    "Electric Sous Vide Machine": (100, 300),
    "Electric Steamer": (30, 150),
    "Electric Taco Maker": (20, 50),
    "Electric Toaster Oven": (50, 200),
    "Electric Waffle Maker": (20, 100),
    "Electric Wine Cooler": (200, 1000),
    "Electric Yogurt Maker": (30, 100),
    "Food Dehydrator": (50, 200),
    "Food Processor": (100, 300),
    "Freezer": (500, 1500),
    "Garbage Disposal": (100, 300),
    "Immersion Blender": (20, 100),
    "Juicer": (50, 300),
    "Microwave": (100, 300),
    "Panini Press": (30, 100),
    "Range Hood": (200, 1000),
    "Refrigerator": (1000, 3000),
    "Rice Cooker": (30, 150),
    "Slow Cooker": (50, 150),
    "Stand Mixer": (200, 500),
    "Stove/Range": (800, 2000),
    "Toaster Oven": (50, 200),
    "Wine Cooler": (200, 1000),

    # Laundry Appliances
    "Clothes Dryer": (700, 1500),
    "Washing Machine": (700, 1500),

    # Heating and Cooling Appliances
    "Air Conditioner (Central)": (3000, 7000),
    "Air Conditioner (Window Unit)": (200, 500),
    "Air Purifier": (100, 500),
    "Dehumidifier": (200, 500),
    "Furnace": (2000, 4000),
    "Heater (Portable)": (50, 200),
    "Humidifier": (50, 200),

    # Cleaning Appliances
    "Canister Vacuum": (150, 500),
    "Carpet Cleaner": (100, 300),
    "Handheld Vacuum": (30, 150),
    "Robot Vacuum": (300, 1000),
    "Steam Mop": (50, 200),
    "Stick Vacuum": (100, 400),
    "Upright Vacuum": (100, 400),
    "Vacuum Cleaner": (100, 500),

    # Power and Water Appliances
    "Generator": (500, 3000),
    "Water Heater": (800, 1500),

    # Miscellaneous Appliances
    "Ice Maker": (200, 500),
    "Portable Solar Panel": (100, 500),

    # Clothing Care Appliances
    "Garment Steamer": (30, 150),
    "Iron": (20, 100),
    "Sewing Machine": (100, 500),
    "Steam Iron": (30, 150),

    # Commercial / Industrial Appliances & Equipment
    "Commercial Baking Oven": (5000, 20000),
    "Commercial Bread Proofer": (1000, 5000),
    "Commercial Brewing Equipment": (5000, 20000),
    "Commercial Cappuccino Machine": (2000, 10000),
    "Commercial Chocolate Tempering Machine": (2000, 10000),
    "Commercial Coffee Roaster": (5000, 20000),
    "Commercial Cotton Candy Floss Machine": (500, 2000),
    "Commercial Cotton Candy Machine": (300, 1000),
    "Commercial Crepe Maker": (500, 2000),
    "Commercial Deep Fryer": (1000, 5000),
    "Commercial Dishwasher": (2000, 10000),
    "Commercial Dough Mixer": (1000, 5000),
    "Commercial Espresso Machine": (3000, 10000),
    "Commercial Fondue Set": (300, 1000),
    "Commercial Food Dehydrator": (1000, 5000),
    "Commercial Food Warmer": (500, 2000),
    "Commercial Freezer": (3000, 10000),
    "Commercial Greenhouse": (5000, 20000),
    "Commercial Griddle": (1000, 5000),
    "Commercial Hot Dog Roller": (300, 1000),
    "Commercial Hot Dog Steamer": (500, 2000),
    "Commercial Ice Cream Machine": (2000, 5000),
    "Commercial Ice Machine": (1500, 5000),
    "Commercial Ice Shavers": (500, 2000),
    "Commercial Juice Extractor": (2000, 10000),
    "Commercial Meat Grinder": (1000, 5000),
    "Commercial Meat Slicer": (500, 2000),
    "Commercial Oven": (3000, 15000),
    "Commercial Pasta Cooker": (1000, 5000),
    "Commercial Pasta Extruder": (3000, 10000),
    "Commercial Pizza Box Warmer": (500, 2000),
    "Commercial Pizza Cutter": (20, 100),
    "Commercial Pizza Dough Roller": (1000, 5000),
    "Commercial Pizza Oven": (3000, 10000),
    "Commercial Pizza Oven Brush": (20, 100),
    "Commercial Pizza Peel": (50, 200),
    "Commercial Popcorn Machine": (500, 2000),
    "Commercial Pretzel Maker": (500, 2000),
    "Commercial Quesadilla Maker": (300, 1000),
    "Commercial Refrigerator": (2000, 8000),
    "Commercial Sausage Stuffer": (1000, 5000),
    "Commercial Slush Machine": (1000, 3000),
    "Commercial Soda Fountain": (1000, 3000),
    "Commercial Soft Serve Machine": (2000, 5000),
    "Commercial Sushi Roller": (500, 2000),
    "Commercial Vacuum Sealer": (500, 2000),
    "Commercial Waffle Maker": (500, 2000),
    "Commercial Wine Fermenter": (2000, 10000),
    "Industrial 3D Printer": (2000, 10000),
    "Industrial Air Compressor": (1000, 5000),
    "Industrial Air Dryer": (1000, 3000),
    "Industrial Air Purifier": (1000, 3000),
    "Industrial Band Saw": (2000, 10000),
    "Industrial Boiler": (5000, 20000),
    "Industrial Chiller": (3000, 10000),
    "Industrial Conveyor Belt": (2000, 10000),
    "Industrial Cooling Tower": (5000, 20000),
    "Industrial CNC Machine": (10000, 50000),
    "Industrial Drill Press": (1000, 5000),
    "Industrial Dust Collector": (1000, 5000),
    "Industrial Fan": (200, 1000),
    "Industrial Food Processor": (1000, 5000),
    "Industrial Generator": (5000, 20000),
    "Industrial Heater": (500, 2000),
    "Industrial HVAC System": (5000, 20000),
    "Industrial Hydraulic Press": (5000, 20000),
    "Industrial Laser Cutter": (10000, 50000),
    "Industrial Metal Bender": (2000, 10000),
    "Industrial Metal Cutting Saw": (1000, 5000),
    "Industrial Metal Drilling Machine": (2000, 10000),
    "Industrial Metal Fabrication Equipment": (5000, 20000),
    "Industrial Metal Forming Machine": (5000, 20000),
    "Industrial Metal Lathe": (5000, 20000),
    "Industrial Metal Polisher": (2000, 10000),
    "Industrial Metal Stamping Machine": (5000, 20000),
    "Industrial Milling Machine": (5000, 20000),
    "Industrial Plasma Cutter": (2000, 10000),
    "Industrial Pump": (500, 3000),
    "Industrial Powder Coating System": (5000, 20000),
    "Industrial Pressure Washer": (500, 2000),
    "Industrial Robotic Arm": (10000, 50000),
    "Industrial Sandblaster": (1000, 5000),
    "Industrial Sheet Metal Shear": (2000, 10000),
    "Industrial Steam Cleaner": (1000, 3000),
    "Industrial Tube Bender": (2000, 10000),
    "Industrial Vacuum": (500, 2000),
    "Industrial Water Filtration System": (2000, 10000),
    "Industrial Water Heater": (2000, 5000),
    "Industrial Welder": (500, 3000),
    "Industrial Welding Table": (1000, 5000),
}

F_EMERGENCY  = 0.15   
F_UNEXPECTED = 0.07   

def deterministic_cost(label: str) -> float:
    digest = hashlib.sha256(label.lower().encode()).digest()
    value  = struct.unpack(">Q", digest[:8])[0]
    return 1_000.0 + (value / 2**64) * 19_000.0   # 1k–20k

def parse_items(scope: str) -> list[str]:
    tokens = re.split(r"[^A-Za-z]+", scope)
    words  = [w.title() for w in tokens if w]
    found: list[str] = []
    i = 0
    while i < len(words):
        matched = False
        for n in range(4, 0, -1):
            if i + n > len(words):
                continue
            phrase = " ".join(words[i:i+n])
            if phrase in ITEM_COSTS and phrase not in found:
                found.append(phrase)
                i += n
                matched = True
                break
        if not matched:
            i += 1
    return found

def estimate_cost(items: list[str]) -> tuple[float, dict[str, float]]:
    per_item: dict[str, float] = {}
    for label in items:
        if label in ITEM_COSTS:
            lo, hi = ITEM_COSTS[label]
            per_item[label] = (lo + hi) / 2.0
        else:
            per_item[label] = deterministic_cost(label)
    baseline = sum(per_item.values())
    return baseline, per_item

SYSTEM_PROMPT = """\
You are a senior project-planning analyst in Canada.

Return a *plain-text* report (no JSON or code fences) with these sections \
in **this exact order**:

1. EXECUTIVE SUMMARY
2. COST ANALYSIS
3. TIMELINE MANAGEMENT
4. TASK MANAGEMENT
5. RESOURCE ALLOCATION
6. RISK ASSESSMENT
7. MILESTONES
8. METRIC DEFINITIONS & ASSUMPTIONS
9. RECOMMENDATIONS

Formatting rules
• Headings in ALL CAPS.  
• Use paragraphs, ASCII bullets “•”, or numbered lists as appropriate.  
• Do **not** wrap the whole report in markdown fences.  
• Start output immediately with “EXECUTIVE SUMMARY”.

Currency rules (very important)
• **All monetary values must be expressed in Canadian dollars.**  
• Use the symbol “CAD $” before every amount (e.g., “CAD $ 125 000”).  
• In COST ANALYSIS include: baseline/expected cost, variance bands, \
  emergency reserve, and unexpected reserve.  
• *At the very bottom* of the COST ANALYSIS section add a blank line \
  followed by:

      OVERALL ESTIMATED COST: CAD $ <sum>

  where <sum> = baseline cost + emergency reserve + unexpected reserve.

LENGTH REQUIREMENT
• The finished report **must contain at least 3 000 English words** \
  (≈18 000 characters).  If necessary, expand discussion in each section \
  to satisfy this minimum word count while maintaining relevance and clarity.
"""

def build_estimate_context(scope: str) -> tuple[str, float, float, float, dict[str,float]]:
    items        = parse_items(scope)
    baseline, per_item = estimate_cost(items or ["General Allowance"])
    emergency    = baseline * F_EMERGENCY
    unexpected   = baseline * F_UNEXPECTED

    list_lines = [f"• {lbl}: CAD $ {val:,.0f}" for lbl, val in per_item.items()]
    context = "\n".join([
        "ITEM COST BREAKDOWN (pre-calculated by host script):",
        *list_lines,
        "",
        f"BASELINE COST (sum of above): CAD $ {baseline:,.0f}",
        f"EMERGENCY RESERVE (15 %):   CAD $ {emergency:,.0f}",
        f"UNEXPECTED RESERVE (7 %):   CAD $ {unexpected:,.0f}",
        "",
        "Final baseline cost to respect in COST ANALYSIS section: "
        f"CAD $ {baseline:,.0f}"
    ])
    return context, baseline, emergency, unexpected, per_item

def stream_plain_report(project: str, scope: str) -> str:
    estimate_ctx, baseline, emergency, unexpected, per_item = build_estimate_context(scope)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": f"Project: {project}\nScope: {scope}"},
        {"role": "user",   "content": estimate_ctx}
    ]
    stream = client.chat.completions.create(
        model                   = MODEL_NAME,
        messages                = messages,
        max_completion_tokens   = 32_768,
        stream                  = True
    )

    print("\n── Streaming report ──\n")
    chunks: list[str] = []
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            print(delta.content, end="", flush=True)
            chunks.append(delta.content)
    print("\n── End of report ──\n")
    full_report = "".join(chunks)

    show_metrics_and_graphs(project, baseline, emergency, unexpected, per_item)
    return full_report

def show_metrics_and_graphs(project: str,
                            baseline: float,
                            emergency: float,
                            unexpected: float,
                            per_item: dict[str,float]) -> None:
    print("\nSUMMARY METRICS\n" + "-"*70)
    print(f"{'Item':40} | {'CAD $':>15}")
    print("-"*58)
    for lbl, val in per_item.items():
        print(f"{lbl:40} | {val:15,.0f}")
    print("-"*58)
    print(f"{'BASELINE TOTAL':40} | {baseline:15,.0f}")
    print(f"{'EMERGENCY RESERVE (15%)':40} | {emergency:15,.0f}")
    print(f"{'UNEXPECTED RESERVE (7%)':40} | {unexpected:15,.0f}")
    print(f"{'OVERALL ESTIMATED COST':40} | {baseline+emergency+unexpected:15,.0f}")
    print("-"*70 + "\n")

    fig1, ax1 = plt.subplots(figsize=(10, 6))
    labels = list(per_item.keys())
    costs  = list(per_item.values())
    ax1.bar(labels, costs)
    ax1.set_ylabel("CAD $")
    ax1.set_title(f"Cost Breakdown – {project}")
    ax1.tick_params(axis='x', rotation=90)
    fig1.tight_layout()
    png1 = f"{project.replace(' ','_')}_breakdown.png"
    fig1.savefig(png1, dpi=144)
    print(f"📊  Saved bar chart → {png1}")

    fig2, ax2 = plt.subplots()
    ax2.pie([baseline, emergency, unexpected],
            labels=["Baseline", "Emergency", "Unexpected"],
            autopct="%1.1f%%", startangle=140)
    ax2.axis('equal')
    ax2.set_title("Budget Composition")
    png2 = f"{project.replace(' ','_')}_reserves.png"
    fig2.savefig(png2, dpi=144)
    print(f"📈  Saved reserve pie chart → {png2}")

    plt.show()

def main() -> None:
    print("FULL-SPECTRUM PROJECT ANALYTICS (PLAIN TEXT, CAD)\n" + "-"*70)
    proj_name  = input("Project name  : ").strip() or "Untitled Project"
    proj_scope = input("Scope summary : ").strip()

    report_text = stream_plain_report(proj_name, proj_scope)

    ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{proj_name.replace(' ','_')}_REPORT_{ts}.txt"
    Path(fname).write_text(report_text, encoding="utf-8")
    print(f"\n📄  Report saved → {fname}\n")
    input("Press <Enter> to exit…")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("\n‼️  Unexpected error:\n")
        traceback.print_exc()
        input("\nPress <Enter> to exit…")
        sys.exit(1)