from langchain_core.prompts import (
  ChatPromptTemplate, 
  HumanMessagePromptTemplate, 
  SystemMessagePromptTemplate,
  PromptTemplate, 
  MessagesPlaceholder)
import re

def _fix_double_braces(s: str) -> str:
    return re.sub(r"\{\{(\w+)\}\}", r"{\1}", s)
def _to_chat_prompt_from_legacy(messages: list[dict]) -> ChatPromptTemplate:
    """legacy [{role, content}] → ChatPromptTemplate.}"""
    normalized = []
    for m in messages:
        role = m.get("role", "user")
        content = _fix_double_braces(m.get("content", ""))
        normalized.append((role, content))
    return ChatPromptTemplate.from_messages(normalized)



# ==============Phase 1 Prompts===============

# =============================
# PLAN AGENT : Make Plan Prompt
# =============================

prompt_4_planning =  PromptTemplate.from_template("""{input}""")
prompt_for_planning = [PromptTemplate.from_template("""{task}
You are a programmer tasked with generating appropriate plan to solve a given problem using the **{language}** programming language.
        
**Expected Output:**
Your response must be structured as follows:

### Problem Understanding
- Think about the original problem. Develop an initial understanding about the problem.
                                                    
### Recall Example Problem
Recall a relevant and distinct problems (different from problem mentioned above) and
- Describe it
- Generate {language} code step by step to solve that problem
- Discuss the algorithm to solve this problem
 within 5 bullet points
                                                    
### Algorithm to solve the original problem
- Write down the algorithm that is well suited for the original problem
- Give some tutorials to about the algorithm for example:
    - How to approach this type of algorithm
    - Important things to consider

### Plan
- Write down a step-by-step plan to solve the original problem with bullet points.
- Do not consider testing, deployment, document and future maintenance in your plan.

--------
**Important Instruction:**
- Strictly follow the instructions.
- Do not generate code.
"""),

PromptTemplate.from_template("""{task}
You are an expert software architect specializing in the **{language}** programming language. Your goal is to create a clear, step-by-step plan to solve the given problem.
                             
**Expected Output:**
Your response must be structured as follows:

### Problem Analysis
- **Core Requirement:** State the main goal of the problem in one sentence.
- **Inputs:** Describe the expected inputs (e.g., data types, formats, constraints).
- **Outputs:** Describe the expected outputs (e.g., data types, formats).
- **Edge Cases:** List potential edge cases to consider (e.g., empty inputs, invalid data).

### Proposed Algorithm
- **Name:** Name the algorithm or approach (e.g., "Sliding Window," "Two Pointers," "Depth-First Search").
- **Description:** Briefly explain how the algorithm works in the context of this specific problem.

### Plan
Provide a step-by-step plan to solve the **original problem**. Each step should be a clear action for a programmer to take. Do not include code in this section.

--------
**Important Instructions:**
- Adhere strictly to the 3-part structure provided above.
- Do not write any code, tests, or documentation. Focus only on the analysis and the plan.
"""),

PromptTemplate.from_template("""
You are a programmer tasked with generating appropriate plan to solve a the **{language}** programming language problem .
Make a plan to solve the following problem.
--------
**Important Instruction:**
- Just write the plan.
- Do not generate code.

### Example
Input:
- task: "Given a list of integers, return the sum in {language}."
Output:
### Plan
- Read the list of integers.
- Accumulate a running total.
- Return the total.

Input:          
## Problem Statement for {language}:
{task}
Output:
### Plan
"""),

PromptTemplate.from_template("""
You are a planning engine.

STRICT OUTPUT RULES:
- Output ONLY the plan list items.
- Output MUST start with: "### Plan"
- After that, output ONLY lines that start with "- ".
- Do NOT output code blocks, backticks, examples, headings, emojis, or explanations.
- If you are about to output anything else, stop and only output plan bullets.

### Problem Statement for {language} language:
{task}
                             
### Plan
 
""")



]
# - Do not consider testing, deployment, document and future maintenance in your plan.
prompt_for_simulation = PromptTemplate.from_template("""{problem_with_planning}

You are a programmer tasked with verifying the plan to solve a given problem using the **{language}** programming language.

**Expected Output:**

Your response must be structured as follows:

### Simulation

- Take a sample input and apply plan step by step to get the output. Do not generate code do it manually by applying reasoning.
- Compare the generated output with the sample output to verify if your plan works as expected.

### Plan Evaluation

- If the simulation is successful write **No Need to Modify Plan**.
- Otherwise write **Plan Modification Needed**.
""")

prompt_for_plan_refinement = PromptTemplate.from_template("""{problem_with_planning}
You are a programmer in the **{language}** programming language.  You already have a wrong plan. Correct it so that it can generate correct plan.

## Plan Critique
{critique}

**Expected Output:**

Your response must be structured as follows:

## New Plan

- Write down a step-by-step modified plan to solve the **original problem**.
- Ensure each step logically follows from the previous one.

--------
**Important Instruction:**
- Your response must contain only the plan.
- Do not add any explanation.
- Do not generate code.
- You MUST strictly follow the function signature specified in the problem. (e.g. do not change function name, its arguments and return type)
- Do not include anything about deployment, or future maintenance.
""")


# =============================
# CODE AGENT : Make Draft Code
# =============================
prompt_4_draft_code =  PromptTemplate.from_template("""{input}\nHere's the code in a single code block (wrap in ```{language})""")

code_gen_for_draft = [ 
    PromptTemplate.from_template("""{task_description}
{action_prompt_header}

 **Important Instructions:**
- Do not add any explanation.
- Write secure code.
- You MUST strictly follow the function signature specified in the problem."""),


    PromptTemplate.from_template("""
You are a code generator.

STRICT OUTPUT RULES:
- Output ONLY {language} code.
- Output ONLY the function with the exact signature provided.
- Do NOT output main/tests/examples/comments/explanations/markdown.

REQUIREMENTS:
{task_description}

{action_prompt_header}
"""),

 PromptTemplate.from_template("""{task_description}
{action_prompt_header}

 **Important Instructions:**
- You MUST strictly follow the function signature specified in the problem."""),
]


# =============================
# SECURITY AGENT : Judge Attack-Surface Prompt
# Your response should include all dependencies, headers and function declaration to be directly usable. 
# - Only flag when there is an attack surface AND it is not clearly handled safely.
# - Skip simple code with no explicit attack surface.
# =============================
sec_attack_surface_prompt = """
You are a security engineer. You will be given a problem statement and draft code.

Goal:
- Skip simple code with no external interaction.
- Only flag code that clearly exposes an attack surface.

Decision rules (IMPORTANT):
- Judge based on the **Draft Code only**.
- If the code is simple logic, or uses only constants → NO_ATTACK_SURFACE.
- If there is an attack surface BUT it appears already safely handled → NO_ATTACK_SURFACE.
- Only flag when there is an attack surface AND it is not clearly handled safely.

Categories (ONLY IF the code includes one of):
- Untrusted Input (user, request, file, env)
- Network/API (HTTP, sockets)
- Database/Storage (SQL, queries)
- File System (open, write, path join)
- Exec/Deserialization/rendering (subprocess, eval, pickle, yaml)
- Auth/Session/Secrets (hard-coded keys, debug flags, session, logging)
- Memory/Resources (buffers, unsafe ops, regax, DoS)
- Crypto (hash, verify flags, random generators)

Output format:
### Attack Surface
- [Category] Evidence: ... — Candidate: ...

### Overall
HAS_ATTACK_SURFACE | NO_ATTACK_SURFACE
---

## Problem:
{problem}

## Draft Code:
{draft_code}
"""

sec_attack_surface_prompt_mini = """
You are a security engineer. You will be given a problem statement and draft code.

Goal:
- Skip simple code with no external interaction.
- Only flag code that clearly exposes an attack surface.

Decision rules (IMPORTANT):
- Judge based on the **Draft Code only**.
- If the code is simple logic, or uses only constants → NO_ATTACK_SURFACE.
- If there is an attack surface BUT it appears already safely handled → NO_ATTACK_SURFACE.
- Only flag when there is an attack surface AND it is not clearly handled safely.

Categories (ONLY IF the code includes one of):
- Untrusted Input (user, request, file, env)
- Network/API/rendering (HTTP, sockets, RPC)
- Database/Storage (SQL, queries)
- File System (open, write, path join)
- Exec/Deserialization/rendering (subprocess, eval, pickle, yaml)
- Auth/Session/Secrets (hard-coded keys, debug flags, session, logging)
- Memory/Resources (buffers, unsafe ops, regax, DoS)
- Crypto (hash, verify flags)

Output format:
### Attack Surface
- [Category] Evidence: ... — Candidate: ...

### Overall
HAS_ATTACK_SURFACE | NO_ATTACK_SURFACE

If nothing is found, return exactly:
NO_ATTACK_SURFACE

## Problem:
{problem}

## Draft Code:
{draft_code}
"""

sec_attack_surface_prompt_gemini_flash = """
You are a security engineer. You will be given a problem statement and draft code.

Goal:
Only flag code that clearly exposes an attack surface AND appears to have a security concern.
Judge based only on the draft code. Classify NO_ATTACK_SURFACE if:
- The code is trivial or constants-only, OR
- The code already handles the attack surface safely.

Categories (flag ONLY if present in code):
- Untrusted Input (user, request, env)
- Network/API (HTTP, sockets)
- Database/Storage (SQL, queries)
- File System (open, write, path join)
- Exec/Deserialization/rendering (subprocess, eval, pickle, yaml)
- Auth/Session/Secrets (hard-coded keys, debug flags, session)
- Memory/Resources (buffers, unsafe ops, regex, DoS)
- Crypto (hash, verify flags, random generators)

Output format:
### Attack Surface
- [Category] Evidence: ... — Candidate: ...

### Overall
HAS_ATTACK_SURFACE | NO_ATTACK_SURFACE
---

## Problem:
{problem}

## Draft Code:
{draft_code}
"""
# — Candidate: ...

# You are a senior security engineer. You will be given a problem statement and draft code.

# Goal:
# - Skip simple code with no external interaction.
# - Only flag code that clearly exposes an attack surface.

# Decision rules (IMPORTANT):
# - Judge based on the **Draft Code only**.
# - If the code is simple logic, or uses only constants → NO_ATTACK_SURFACE.
# - If there is an attack surface BUT it appears already safely handled → NO_ATTACK_SURFACE.
# - Only flag when there is an attack surface AND it is not clearly handled safely.


sec_attack_surface_with_quick_wins_prompt = """You are a security engineer. Given a problem and draft code, complete two tasks in order.

### Task 1 — Attack Surface Classification
Only flag code that clearly exposes an attack surface AND appears to have a security concern.
Judge based only on the draft code. Classify NO_ATTACK_SURFACE if:
- The code is trivial or constants-only, OR
- The code already handles the attack surface safely with no obvious remaining risk.

Categories (flag ONLY if present in code):
- Untrusted Input (user, request, env)
- Network/API (HTTP, sockets)
- Database/Storage (SQL, queries)
- File System (open, write, path join)
- Exec/Deserialization/rendering (subprocess, eval, pickle, yaml)
- Auth/Session/Secrets (hard-coded keys, debug flags, session)
- Memory/Resources (buffers, unsafe ops, regex, DoS)
- Crypto (hash, verify flags, random generators)

Output format:
### Attack Surface
- [Category] Evidence: ... 
### Overall
HAS_ATTACK_SURFACE | NO_ATTACK_SURFACE

---

### Task 2 — Quick Wins (run only if HAS_ATTACK_SURFACE above)
Identify up to 2 lightweight, one-line security advices *directly visible* in the code and not covered by CWE analysis.

Priorities:
P0: Hard-coded credentials/keys → use env vars or secret manager. Debug/test flags in prod path (e.g., `debug=True`) → disable.
P1: API call options that need safe defaults observable in code (e.g. unsafe API choices, missing safe flags).

Constraints: no logging/auditing/compliance/large refactors. No infra advice unless evidenced in code.

Output format (or "No additional guideline needed." if none apply):
### Quick Wins
- Advice 1: <one-line advice>
- Advice 2: <one-line advice>

---

## Draft Code:
{draft_code}
"""




# =============================
# SECURITY AGENT : CWEs Extraction Prompts
# =============================
SEC_AGENT_SYSTEM = (
    "You are a senior security engineer."
    "Your task is to identify the most likely CWE vulnerabilities that the following function might introduce."
)

cwe_extract_prompt = [
    ChatPromptTemplate.from_messages(
    [
        SEC_AGENT_SYSTEM,
        HumanMessagePromptTemplate.from_template(
            """Use the provided context and guidelines to output a list of group of probable cause-effect CWE(s) pair(s). For each, provide a concise explanation, a likelihood score in [0, 1].
Reasoning levels:
1. **Cause (fine-grained CWE(s))**: the direct insecure practice or action(s).
2. **Effect (broad CWE(s))**: all higher-level security consequence(s).

## Context
- Language: {language}
- Problem: {problem_with_planning}

### Guidelines
1. Read the problem and plan carefully.
2. Define rules for identifying vulnerabilities groups.
3. For each vulnerability:
   - Map to cause CWE(s).
   - Map to effect CWEs.
   - Group similar categories.
4. Rank and return AT MOST {max_limit} groups. (Do NOT pad to {max_limit})

Output format:
* plan understanding: a short summary of the plan
* extract keywords: APIs, inputs(trust level), credential info, auth/cryptography(for what), memory/logic (include only if present, few lines).
* JSON array of objects. Each object must contain: (in wrap ```json)
  - `group_name` : string, <group_name>
  - `why`: short rationale (1-2 sentences)
  - `cause_cwes`: ["CWE-###", ...],
  - `effect_cwes`: ["CWE-###", ...],
  - `likelihood`: float ∈ [0, 1]
"""     ),
    ]
) ,
#   - `red_flags`: list of strings
## For Gemini-Flash Model
ChatPromptTemplate.from_messages(
    [
        SEC_AGENT_SYSTEM,
        HumanMessagePromptTemplate.from_template(
            """Use the provided context and guidelines to output a list of group of probable cause-effect CWE(s) pair(s). For each, provide a concise explanation, a likelihood score in [0, 1].
Reasoning levels:
1. **Cause (fine-grained CWE(s))**: the direct insecure practice or action(s).
2. **Effect (broad CWE(s))**: all higher-level security consequence(s).

## Context
- Language: {language}
- Problem: {problem_with_planning}

### Guidelines
1. Read the problem and plan carefully.
2. Define rules for identifying vulnerabilities groups.
3. For each vulnerability:
   - Map to cause CWE(s).
   - Map to effect CWEs.
   - Group similar categories.
4. Rank and return ≤ {max_limit} group (not padded).

Output format:
* plan understanding: a short summary of the plan
* extract keywords: APIs, inputs(trust level), info, auth/cryptography(for what), memory safe (include only if present, few lines).
* JSON array of objects. Each object must contain: (in wrap ```json)
  - `group_name` : string, <group_name>
  - `why`: short rationale (1-2 sentences)
  - `cause_cwes`: ["CWE-###"],
  - `effect_cwes`: ["CWE-###"]
"""     ),
    ]
)

]


# =============================
# SECURITY AGENT : Security Guidelines Prompts
# =============================
prompt_4_se = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are a security agent. "
        "Using the retrieved secure-coding practices as reference, write concise, actionable "
        "security guidelines tailored to THIS problem and language."
    ),
    HumanMessagePromptTemplate.from_template(
"""
---
Context:
- Language/Os: {language}, {os_platform}
- Problem (with plan): {problem_with_planning}\n
- Retrieved practices:\n{retrieved_snippets}\n\n\

{input}

{prompt_4_sec_tail}"""
    ),
])


prompt_4_se_wo_rag = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are a security agent. "
        "Write concise, actionable "
        "security guidelines tailored to THIS problem and language."
    ),
    HumanMessagePromptTemplate.from_template(
"""
---
Context:
- Language/Os: {language}, {os_platform}
- Problem (with plan): {problem_with_planning}\n

{input}

{prompt_4_sec_tail}"""
    ),
])



prompt_4_se_history = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are a security agent."
        "Using the retrieved secure-coding practices, write concise, actionable "
        "security guidelines tailored to THIS problem."
    ),
    # history
    MessagesPlaceholder("chat_history"),
    HumanMessagePromptTemplate.from_template(
"""Retrieved practices (ranked, deduplicated):\n{retrieved_snippets}\n\n\
---
Context:
- Language/Os: {language}, {os_platform}
- Problem (with plan): {problem_with_planning}
{input}

{prompt_4_sec_tail}"""),
])

prompt_4_sec_tail = """Output format:.
### security guidelines
- Provide 1-{cwe_limit} clear guidelines that leave no room for error. (if needed, with at most one minimal code line as an example).
- Keep it precise; no fluff, no generic advice.
- Preserving functionality.
- Do NOT include (logging, audit trail) unless the problem explicitly asks for it.
""" 
# - Do Not make full code.
# - Preserving functionality.
# - Do Not make code.

prompt_4_sec_tail_for_gemini = """Output format:
### security guidelines
- Provide a few clear guidelines that leave no room for error. (if needed, with at most one minimal code line as an example).
- Keep it precise; no fluff, no generic advice.
- Preserving functionality.
- Do NOT include (logging, audit trail) unless the problem explicitly asks for it.
- Do Not make full code.
"""

sec_guide_prompt_per =   """
Findings (CWE group):
- Group: {group_name}
- Why: {why}
- Red flags: {red_flags}"""

sec_guide_prompt =   """
Findings (CWE groups):
{cwe_list}"""

sec_guide_else_prompt = """Your task is to:
- Review the draft code and identify up to **2 small, lightweight security analysis and one-line advices** that are *not already covered*.
- Focus on **direct, code-evident quick wins** (single-line changes or flags).
- If there are no new lightweight guidelines, return exactly: "No additional guideline needed."

Evidence-first rule:
- Prefer findings that are **directly visible in the draft code** (e.g., hard-coded secrets, debug/dev flags, unsafe API options).
- Deprioritize infrastructure-only guidance (e.g., “use HTTPS”) unless the code explicitly sets/assumes insecure behavior.

Priorities (apply in order; only include items that actually appear in code):
P0 (must-check quick wins):
  - Hard-coded credentials/secrets/keys (e.g., API keys in literals) → advise using environment variables or secret manager.
  - Development/test toggles in production path (e.g., `debug=True`) → advise disabling (`debug=False`) for production.
P1:
  - API call flags that need safe defaults
P2:
  - Other one-line configuration hardening directly observable in the code. (unsafe API usage, missing safe flags, etc.)

Constraints:
- Suggestions must be **minimal and actionable with a single line** of advice or configuration.
- Do NOT suggest heavy-weight practices (logging/auditing/compliance frameworks/large refactors).
- Do NOT include broad infra advice unless **explicitly evidenced in code**.

Output format (exactly):
- Advice 1: <one-line advice> 
- Advice 2: <one-line advice>

## Code (draft):
{draft_code}"""

# =============================
# SECURITY AGENT : Security Guidelines Validation Prompts
# =============================
sec_guide_refine_prompt = ChatPromptTemplate.from_template("""You are a security agent. Your task is to carefully review and refine the provided Security Guidelines for the given problem.

Steps:
1. Think about the original problem and functional requirements which must be preserved.
2. Check if any security guideline conflicts with the functional constraints (e.g., removing an argument when signature must be preserved).  
   - If conflict exists, modify or drop the guideline so that functional constraints are preserved.
   - If there are over-engineering which destroy functionality, modify or drop them.
3. If duplicate or overlapping guidelines exist, merge them into a single, coherent detailed guideline.

## Language/Os: {language}, {os_platform}
## Problem:
{question}

## Security Guidelines (draft):
{security_guidelines}

Output format:
### Functional Requirements
- Summarize must have to keep from the problem.
### Conflicting Identified
- List any security guidelines that conflict with functional constraints, and how you modified them to preserve Functional Requirements.
### Security Guidelines
- Provide improved guidelines for code engineers.
- Keep it ultra concise; include only essentials; no filler.
- Do NOT include (logging, audit trail) unless the problem explicitly asks for it.""")

# - Keep it ultra concise; include only essentials; no filler.
# =============================
# CODE AGENT : Code Generation Prompts
# =============================
prompt_4_code = ChatPromptTemplate.from_messages([
    MessagesPlaceholder("chat_history"),    
    HumanMessagePromptTemplate.from_template("{input}")
])

code_gen_prompt = [ChatPromptTemplate.from_template(
    """Your task is to write secure and functional code **for the following problem** in {language}.
### Problem Statement:
{task_description}

{implementation_plan}
### Security Guidelines:
{security_requirements}

Requirements:
- You MUST strictly follow the function signature specified in the problem. (e.g. do not change function name, its arguments and return type)
- Keep it simple. Avoid unnecessary complexity or over-engineering.

### Output format:
{action_prompt_header}"""
),

ChatPromptTemplate.from_template(
    """Your task is to write secure and functional code for the problem in {language}.
### Problem Statement:
{task_description}

{implementation_plan}
### Security Guidelines:
{security_requirements}

Requirements:
- You MUST strictly follow the function signature specified in the problem. (e.g. do not change function name, its arguments and return type)
- Avoid unnecessary complexity or over-engineering.

### Output format:
{action_prompt_header}"""
),

ChatPromptTemplate.from_template(
"""You are a senior software engineer. Write ONLY code in {language}.

ABSOLUTE RULES (must follow):
1) Output ONLY one code block. No explanations.
2) Do NOT change the required function signature (name/args/return).
3) Must be secure + functionally correct code.

Problem:
{task_description}

Implementation Plan:
{implementation_plan}

### Security Guidelines:
{security_requirements}

Output:
{action_prompt_header}

"""
),


ChatPromptTemplate.from_template(
    """Your task is to write a secure and functional code **to the following problem** in {language}.
### Problem Statement:
{task_description}

### Security Guidelines:
{security_requirements}

### Output format:
{action_prompt_header}"""
),]

code_understand_prompt = ChatPromptTemplate.from_template(
    """You are a coding engineer. You are given a problem statement with plan and security guidelines. 
    Your task is to analyze the problem, plan, and security guideline to produce a concise summary of the key functional and security aspects that must be considered during implementation.

### Problem Statement (with plan):
{task_description}

### Security Guidelines:
{security_requirements}

### Output format:
- problem understanding: a short summary of the problem
- summary of the plan: a short summary of the plan
- summary of security guidelines : a short summary of the security guidelines (check detail whether it is also functional like regex, input validation, auth, cryptography, memory safe, etc.)
- conflicts between functional requirements and security guidelines if any: a short summary of the conflicts (not related to efficiency)
- your plan to implement the problem: a short summary of your plan to implement the problem considering both functional and security aspects
"""
)

### Other options for code generation prompt
code_gen_w_only_plan_prompt = ChatPromptTemplate.from_template(
    """You are a coding engineer. You are given a problem statement and implementation guidelines.
Write a solution in {language}, targeting the {os_platform} platform.

Problem Statement:
{task_description}

Requirements:
- Do Not include any comments, explanations.
- You MUST strictly follow the function signature specified in the problem. (e.g. do not change function name, its arguments and return type)

Output format:
{action_prompt_header}"""
)

code_gen_w_merge_prompt = ChatPromptTemplate.from_template(
    """You are a coding engineer. You are given a problem statement and implementation guidelines.
Write a solution in {language}, targeting the {os_platform} platform for a functional and secure code.

Problem Statement:
{task_description}

Requirements:
- Do not add any explanation.
- You MUST strictly follow the function signature specified in the problem. (e.g. do not change function name, its arguments and return type)

Output format:
{action_prompt_header}"""
)


# =============================
# CODE AGENT : Syntax Fix Prompts
# =============================
syntax_fix_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are given a programming task, a code snippet containing syntax errors, and compiler feedback. Your task is to correct the code strictly according to the compiler feedback. Respond only with the corrected code, nothing else."
    ),
    HumanMessagePromptTemplate.from_template(
        """## Task : {question}
## The code is 
```{language}
{code}
```
## The feedback from compiler is
{compiler_feedback}

Your solution should be in the form of a code snippet with prefix code.
Wrap the code snippet in (wrap in ```{language}). """ ),
])




# ==============Phase 2 Prompts===============
prompt_4_fe =  PromptTemplate.from_template("""{input}""")

fix_suggestion_after_bax = ChatPromptTemplate.from_template(
    """Given the Problem, Current Code, and Feedback, produce the SMALLEST possible code change as ONE line (prefer 1 line; max 3 lines).
First, think step-by-step about the root cause and the minimal fix.

**Core Priority: Functionality must NOT be broken. If a fix risks breaking functionality, drop it entirely — a dropped fix is better than a broken one.**

Constraints:
- Strictly follow the provided docstring and function signature; do not alter names, order, types, headers, or imports.
- No refactors, no scaffolding, no placeholders.
- If the Feedback asks to change the prefix/header, function signature, return type, DROP and ignore those parts and proceed with an in-scope fix only.
- **Reproducer check**: Before flagging any issue, verify step-by-step that the claimed attack input actually bypasses the CURRENT CODE's existing validation.
- **No invented fixes**: A dropped item means NO fix for that issue — do not substitute with a different approach.

Inputs:
[Problem]
{problem}

[Current Code]
```{language}
{current_code}
```

[Feedback]
{feedback}

Output (STRICT):
### Conflicts Identified
- List any Feedback items that fall into the following out-of-scope categories, and briefly explain why each is excluded and drop the fix:
  (a) conflicts with the Problem/docstring/signature (e.g., prefix/header changes),
  (b) would break Functional Requirements,
  (c) requires large-scale code restructuring (e.g., replacing the entire logic),
  (d) an attack already blocked by the Current Code's existing validation
  (e) involves changing decorators, middleware, or access-control mechanisms,
If ALL items are dropped, output "No actionable fix." and stop.
### Fix Approaches
- If ALL feedback items are dropped, output "No actionable fix." and skip the Fix Approaches section entirely.
- For **each identified issue**:
    - IdentifiedIssue: <max 1 sentence describing what the feedback flags (after dropping out-of-scope items)>
    - Cautions: <max 1 sentence on what to watch out for in functionality (e.g., return values) and syntax>
    - FixApproach: <max 1 sentences explaining how we will fix the issues>
    - CodeExampleLines({language}):
        <line 1>
        <line 2> (optional)
        <line 3> (optional)

Rules:
- Maximum 3 lines.
- Functionality is the top priority; if in doubt, drop the fix.
- If the fix requires rewriting major logic or restructuring the code significantly, drop it.
- CodeExampleLines must be the final section and compile/parse correctly in {language}."""
)

code_refine_prompt = ChatPromptTemplate.from_template(
                """You are a S/W engineer. Improve the code into a functional and secure implementation.

Problem: 
{problem_with_planning}

Original Code: 
```{language}
{code}
```

Feedback from Evaluation: 
{feedback}

-----
Requirements:
1. Review the feedback carefully. Use it as a reference—not a rule—and adopt only what aligns with the problem logic and intended behavior.
2. Make the SMALLEST possible change: touch only the exact lines the feedback targets. Do NOT rewrite, restructure, or replace logic that already works.
3. Do NOT change function name, params, return type, prefix/header, or imports. Drop feedback that asks for these.
4. Ensure the final code is both functionally correct.
5. Keep it simple. Avoid unnecessary complexity or over-engineering.
6. If the feedback suggests replacing a working implementation with a completely different approach, ignore that suggestion.

{action_prompt_header}""")


sys_prompt_4_sec_req = SystemMessagePromptTemplate.from_template("""

""")

prompt_4_sec_req = HumanMessagePromptTemplate.from_template(
"""{language} coding task.
Problem Statement (PS):
{question}

Security Guideline (SB):
{security_requirements}
""")
chat_prompt = ChatPromptTemplate.from_messages([sys_prompt_4_sec_req, prompt_4_sec_req])


func_understand_prompt = ChatPromptTemplate.from_template(
    """### Problem Statement:
{task_description}
{action_header}

### Current Code:
```{language}
{current_code}
```
---
You are a software engineer. You are given a problem statement and a implementation called the current code.
Goal: Decide whether the Current Code correctly implements the REQUIRED core functionalities in the Problem Statement.

Output format:
### Problem Understanding
Summarize the core task and goals of the problem.
Keywords and definitions that are critical to the problem and test case inputs. (what is it, specific things to consider)

### Example Scenarios
Describe a concrete example user-scenario that illustrates the problem requirements and expected behavior.
Describe how to handle these scenarios on the code.

### Current Code Analysis
For each core function or block:
Step-by-step explanation of logic
Highlight any missing logic or unclear behavior (e.g., return type, format, false positive/negative on edge cases etc.)
Your opinion on whether it fulfills the requirements correctly from the the scenario

### Final Opinion
- Provide your overall assessment of the current code’s functional completeness.
- If you find no issue, output ONLY the 'THE CODE IS FUNCTIONAL'.
"""
) 

sec_understand_prompt_bax =  ChatPromptTemplate.from_template(
    """You are a security engineer. You are given a problem statement and a implementation called the **current code**.
Goal: Decide whether the code is safe related to the security guidelines.

Rules for reporting:
 - Do NOT modify the provided function signature (including prefix/header, parameter names, order, or types).
 - If you cannot provide a concrete reproducer (input/test-case) for an issue, do NOT report it as a concern.
 - If fixing an issue would require large-scale restructuring (e.g., replacing the entire logic, rewriting major components), do NOT report it as a concern.
 - DO report an issue if ALL of the following hold: (1) you can provide a concrete reproducer, (2) applying the fix would not cause a standard programmatic API client to receive a non-2xx response for a valid request.
---
### Problem Statement:
{task_description}
{action_header}

### Current Code:
```{language}
{current_code}
```

### Referenced Security guidelines:
{security_requirements}
- other security issues when the code touches predefined risk categories (e.g. input, storage, File, auth, memory, crypto).

Output format:
### Problem Understanding
Summarize the core task and goals of the problem.
### Current Code Analysis
Step-by-step explanation of functional logic and security mechanisms.
### Final Opinion
- Provide your overall assessment of the current code’s **security concerns**.
- If you find no issue, output ONLY the ‘THE CODE IS SAFE’.""")


# === Default (non-baxbench) phase2 variants ===
fix_suggestion_after = ChatPromptTemplate.from_template(
    """You are a senior software engineer. Given the Problem and Feedback, produce the SMALLEST possible code change as ONE line (prefer 1 line; max 3 lines).
First, think step-by-step about the root cause and the minimal fix.

Constraints:
- Strictly follow the provided docstring and function signature; do not alter names, order, types, headers, or imports.
- No refactors, no scaffolding, no placeholders.
- If the Feedback asks to change the prefix/header, function signature, parameter list/order/types, return type, DROP and ignore those parts and proceed with an in-scope fix only.

Inputs:
[Problem]
{problem}

[Feedback]
{feedback}

Output (STRICT):
### Conflicts Identified
- Enumerate any Feedback items that (a) conflict with the Problem/docstring/signature (e.g., prefix/header/signature/import changes) or (b) would break Functional Requirements.
- State how you modified or dropped them to preserve functionality and constraints.
### Fix Approaches
- For **each identified issue**:
    - IdentifiedIssue: <max 2 sentences describing what the feedback flags (after dropping out-of-scope items)>
    - FixApproach: <max 2 sentences explaining how we will fix the issues>
    - CodeExampleLines({language}):
        <line 1>
        <line 2> (optional)
        <line 3> (optional)

Rules:
- Maximum 3 lines.
- Functionality is the top priority; do not break it.
- CodeExampleLines must be the final section and compile/parse correctly in {language}.
"""
)

sec_understand_prompt = ChatPromptTemplate.from_template(
    """You are a security engineer. You are given a problem statement and a implementation called the **current code**.
Goal: Decide whether the code is safe related to the security guidelines.
Minimize false positives:
- Do NOT modify the provided function signature (including prefix/header, parameter names, order, or types).
- If you cannot provide a minimal concrete reproducer (input/test-case) for an issue, do NOT report it as a concern.
---
### Problem Statement:
{task_description}
{action_header}

### Current Code:
```{language}
{current_code}
```

### Security guidelines:
{security_requirements}
- other security issues when the code touches predefined risk categories (input, network, storage, FS, exec, auth, memory, crypto).

Output format:
### Current Code Analysis
Step-by-step explanation of logic and security mechanisms
### Final Opinion
- Provide your overall assessment of the current code’s **security concerns**.
- If you find no issue, output ONLY the ‘THE CODE IS SAFE’.
""")


func_answer_prompt =  [
        [
            {
                "role": "system",
                "content": """\
You will be provided with an analysis result of a code snippet.
If the analysis confirms that the code snippet correctly implements the **core functionalities** as required by the problem statement, output: "Yes". Otherwise, output: "No".
""",
            },
            {
                "role": "user",
                "content": """\
Analysis Result:\"\"\"
{{MISTAKES}}
\"\"\"
"""
            },
            {
                "role": "assistant",
                "content": """\
Final Answer (Yes or No):
"""
            }
        ]
    ]
