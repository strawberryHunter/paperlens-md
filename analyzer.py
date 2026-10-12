"""Evidence-first candidate extraction; findings require manual validation."""
import re
from dataclasses import dataclass, asdict

@dataclass
class Evidence:
    field: str
    value: str
    page: int
    excerpt: str

PATTERNS = {
    "MD engine": r"\b(?:GROMACS(?:\s*\d{4}(?:\.\d+)?)?|OpenMM(?:\s*\d+(?:\.\d+)*)?|NAMD|AMBER|Desmond|LAMMPS)\b",
    "Force field": r"\b(?:CHARMM\s*36m?|AMBER\s*(?:ff\s*)?(?:14SB|19SB|99SB(?:-ILDN)?)|OPLS[- ]?AA|GAFF\s*2?|CGenFF|MARTINI\s*[23]?)\b",
    "Water model": r"\b(?:TIP3P|TIP4P(?:/\d+)?|SPC/E|SPC|OPC|TIP5P)\b",
    "Ensemble": r"\b(?:NVT|NPT|NVE)\b",
    "Temperature": r"\b\d{2,3}(?:\.\d+)?\s*(?:K|kelvin)\b",
    "Pressure": r"\b\d+(?:\.\d+)?\s*(?:bar|atm)\b",
    "Time step": r"\b(?:(?:time\s*step|timestep|integration\s*step)\s*(?:of|was|=|:)?\s*\d+(?:\.\d+)?\s*(?:fs|ps)|\d+(?:\.\d+)?\s*(?:fs|ps)\s*(?:time\s*step|timestep|integration\s*step))\b",
    "Simulation duration": r"\b\d+(?:\.\d+)?\s*(?:ns|microseconds?|nanoseconds?|µs|μs)\b",
    "Replicas": r"\b\d+\s*(?:independent\s*)?(?:replicas?|replicates?|independent\s+runs?)\b",
    "Thermostat": r"\b(?:Nos[eé][– -]?Hoover|v-rescale|Langevin|Berendsen|Andersen)\b",
    "Barostat": r"\b(?:Parrinello[– -]?Rahman|Monte\s*Carlo\s*barostat|C-rescale|Berendsen)\b",
    "Electrostatics": r"\b(?:particle[– -]mesh\s*Ewald|PME|Ewald\s*summation)\b",
    "Constraints / HMR": r"\b(?:LINCS|SHAKE|SETTLE|HMR|hydrogen\s*mass\s*repartitioning)\b",
    "Enhanced sampling": r"\b(?:umbrella\s*sampling|metadynamics|replica\s*exchange|steered\s*(?:molecular\s*dynamics|MD))\b",
}
REGEX = {k: re.compile(v,re.I) for k,v in PATTERNS.items()}

def analyze_pages(pages):
    found=[]; seen=set()
    for page_number,text in enumerate(pages,1):
        clean=" ".join(text.split())
        for field,rx in REGEX.items():
            for match in rx.finditer(clean):
                key=(field,page_number,match.group().lower())
                if key in seen: continue
                seen.add(key)
                found.append(Evidence(field,match.group(),page_number,clean[max(0,match.start()-110):match.end()+130]))
                if len(found)>=500: return found
    return found

def checklist(records):
    present={r.field for r in records}
    return [{"Parameter":x,"Detection":"Candidate found" if x in present else "Not detected","Reviewer action":"Verify PDF and supplementary information"} for x in PATTERNS]

def advisory(records):
    vals=" ".join(r.value.lower() for r in records)
    notes=[]
    if any(f"{n} fs" in vals for n in (4,5)):
        notes.append("4–5 fs timestep candidate: check HMR, constraints, integrator and stability; not an error verdict.")
    if "npt" in vals and not any(r.field=="Barostat" for r in records):
        notes.append("NPT found but barostat not detected; check Methods and SI.")
    if any(r.field=="Enhanced sampling" for r in records):
        notes.append("Enhanced sampling found: verify CVs, bias configuration and convergence.")
    notes.append("Missing matches do not prove methods were unreported; inspect sources and supplementary files.")
    return notes

def export_records(records):
    return [asdict(r) for r in records]
