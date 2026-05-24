#!/usr/bin/env python3
"""
Parse SEI CERT C++ Coding Standard PDF to extract CERT rule to CWE mappings.

Extracts "Related Guidelines" sections from the PDF and builds a dictionary
mapping CERT C++ rules to their associated MITRE CWE identifiers.

Usage:
    python parse_cert_cpp_cwe_mapping.py

Outputs:
    - cert_cpp_to_cwe_mapping.json: CERT rule -> CWE mapping
    - cwe_to_cert_cpp_mapping.json: CWE -> CERT rule reverse mapping
"""

from pypdf import PdfReader
import re
import json
from collections import defaultdict
from pathlib import Path


def parse_cert_cpp_cwe_mapping(pdf_path: str) -> tuple[dict, dict]:
    """
    Parse CERT C++ PDF and extract CWE mappings.
    
    Args:
        pdf_path: Path to the SEI CERT C++ Coding Standard PDF
        
    Returns:
        Tuple of (cert_to_cwe, cwe_to_cert) dictionaries
    """
    # Load PDF
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    
    # Pattern to find CERT C++ rule sections
    # Format: "x.x RULE_ID. Title"
    rule_pattern = re.compile(
        r'^(\d+\.\d+)\s+([A-Z]{3}\d{2}-CPP)\.\s+(.+?)$',
        re.MULTILINE
    )
    
    # Extract all rules and their positions
    rules = []
    for m in rule_pattern.finditer(full_text):
        rules.append({
            'section': m.group(1),
            'rule_id': m.group(2),
            'title': m.group(3).strip(),
            'pos': m.start()
        })
    
    # Map section number to rule
    section_to_rule = {r['section']: r for r in rules}
    
    # Pattern to find Related Guidelines sections
    # Format: "x.x.x Related Guidelines ... MITRE CWE ..."
    related_pattern = re.compile(
        r'(\d+\.\d+)\.(\d+)\s+Related\s+Guidelines(.*?)'
        r'(?=\d+\.\d+\.\d+\s+[A-Z]|\n\d+\.\d+\s+[A-Z]|\Z)',
        re.DOTALL | re.IGNORECASE
    )
    
    # CWE pattern: "CWE XXX, Description" or "CWE-XXX, Description"
    cwe_pattern = re.compile(
        r'CWE[-\s]?(\d+)[,\s]+([A-Z][^\n]+)',
        re.IGNORECASE
    )
    
    # Extract CWEs for each rule from Related Guidelines sections
    cert_to_cwe = {}
    
    for m in related_pattern.finditer(full_text):
        main_section = m.group(1)  # e.g., "5.1"
        content = m.group(3)
        
        if main_section in section_to_rule:
            rule = section_to_rule[main_section]
            rule_id = rule['rule_id']
            
            # Find CWEs in this section
            cwes = []
            for cwe_m in cwe_pattern.finditer(content):
                cwe_id = cwe_m.group(1)
                desc = cwe_m.group(2).strip()
                # Clean up description
                desc = re.sub(r'\s+', ' ', desc)
                desc = desc.split('\n')[0][:100]
                cwes.append({
                    'cwe_id': f"CWE-{cwe_id}",
                    'description': desc
                })
            
            if cwes:
                if rule_id not in cert_to_cwe:
                    cert_to_cwe[rule_id] = {
                        'title': rule['title'],
                        'section': main_section,
                        'related_cwes': []
                    }
                # Add CWEs without duplicates
                existing_cwe_ids = {c['cwe_id'] for c in cert_to_cwe[rule_id]['related_cwes']}
                for cwe in cwes:
                    if cwe['cwe_id'] not in existing_cwe_ids:
                        cert_to_cwe[rule_id]['related_cwes'].append(cwe)
                        existing_cwe_ids.add(cwe['cwe_id'])
    
    # Build reverse mapping: CWE -> CERT rules
    cwe_to_cert = defaultdict(list)
    for rule_id, info in cert_to_cwe.items():
        for cwe in info['related_cwes']:
            if rule_id not in cwe_to_cert[cwe['cwe_id']]:
                cwe_to_cert[cwe['cwe_id']].append(rule_id)
    
    # Sort the rules in reverse mapping
    cwe_to_cert = {k: sorted(v) for k, v in cwe_to_cert.items()}
    
    return cert_to_cwe, dict(cwe_to_cert), rules


def main():
    # Get script directory
    script_dir = Path(__file__).parent
    pdf_path = script_dir / "SEI CERT CPP Coding Standard.pdf"
    
    if not pdf_path.exists():
        print(f"Error: PDF not found at {pdf_path}")
        return
    
    print(f"Parsing: {pdf_path}")
    cert_to_cwe, cwe_to_cert, rules = parse_cert_cpp_cwe_mapping(str(pdf_path))
    
    # Print summary
    print(f"\n{'='*60}")
    print("Summary")
    print('='*60)
    print(f"Total CERT C++ rules found: {len(rules)}")
    print(f"Rules with CWE mapping: {len(cert_to_cwe)}")
    print(f"Unique CWEs: {len(cwe_to_cert)}")
    
    # Print CERT to CWE mapping
    print(f"\n{'='*60}")
    print("CERT C++ -> CWE Mapping")
    print('='*60)
    for rule_id in sorted(cert_to_cwe.keys()):
        info = cert_to_cwe[rule_id]
        print(f"\n{rule_id}: {info['title'][:60]}")
        for cwe in info['related_cwes']:
            print(f"  └─ {cwe['cwe_id']}: {cwe['description'][:55]}...")
    
    # Print CWE to CERT mapping
    print(f"\n{'='*60}")
    print(f"CWE -> CERT C++ Mapping ({len(cwe_to_cert)} unique CWEs)")
    print('='*60)
    for cwe_id in sorted(cwe_to_cert.keys(), key=lambda x: int(x.split('-')[1])):
        rules = cwe_to_cert[cwe_id]
        print(f"{cwe_id}: {', '.join(rules)}")
    
    # Save JSON files
    output_dir = script_dir
    
    cert_output = output_dir / "cert_cpp_to_cwe_mapping.json"
    with open(cert_output, 'w', encoding='utf-8') as f:
        json.dump(cert_to_cwe, f, indent=2, ensure_ascii=False)
    print(f"\nCERT->CWE mapping saved to: {cert_output}")
    
    cwe_output = output_dir / "cwe_to_cert_cpp_mapping.json"
    with open(cwe_output, 'w', encoding='utf-8') as f:
        json.dump(cwe_to_cert, f, indent=2, ensure_ascii=False)
    print(f"CWE->CERT mapping saved to: {cwe_output}")


if __name__ == "__main__":
    main()
