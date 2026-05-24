from __future__ import annotations

import json, logging, os, re
from collections import OrderedDict
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document as SimpleDocument
from langchain_community.chat_message_histories import ChatMessageHistory

from macgen.config import (
    config_to_str,
    EngineConfig,
    EXCLUDE_LSE,
    CSV_PATH,
    CWE_TREE_PATH,
)
from macgen.llm import create_chat_model
from macgen.rag import RAGManager
from macgen.utils.text import to_text, remove_codeblocks, safe_json_loads, format_step
from macgen.utils.logging import setup_logging, attach_pid_log_handler, detach_handler
from macgen.utils.util import load_cwe_table, load_cwe_tree
from macgen.utils.usage import set_current_phase, global_usage_tracker, compute_cost
from macgen.utils.data import load_data
from macgen.utils.code_parse import extract_code, make_parse_list, Parser
from macgen.prompts import (
    # === Phase 1 ===
    cwe_extract_prompt,
    prompt_for_planning,
    prompt_for_simulation,
    prompt_for_plan_refinement,
    code_understand_prompt,
    code_gen_prompt,
    code_gen_for_draft,
    prompt_4_code,
    prompt_4_draft_code,
    prompt_4_se_history,
    prompt_4_se,
    prompt_4_sec_tail_for_gemini,
    prompt_4_se_wo_rag,
    prompt_4_sec_tail,
    sec_guide_prompt,
    sec_guide_else_prompt,
    sec_guide_refine_prompt,
    sec_attack_surface_prompt,
    sec_attack_surface_prompt_mini,
    sec_attack_surface_prompt_gemini_flash,
    sec_attack_surface_with_quick_wins_prompt,
    syntax_fix_prompt,
    code_refine_prompt,
    func_understand_prompt,
    fix_suggestion_after,
    fix_suggestion_after_bax,
    sec_understand_prompt,
    sec_understand_prompt_bax,
    func_answer_prompt,
    _to_chat_prompt_from_legacy,
)


# ===== Conversation memory =====
_shared_memory_dict: Dict[str, ChatMessageHistory] = {}


def get_limited_memory(session_id: str) -> ChatMessageHistory:
    if session_id not in _shared_memory_dict:
        _shared_memory_dict[session_id] = ChatMessageHistory()
    return _shared_memory_dict[session_id]


class MacgenEngine:
    def __init__(
        self,
        cfg: EngineConfig,
        out_dir: Path,
        rag_manager: Optional[RAGManager] = None,
    ):
        self.cfg = cfg
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)

        self.rag_manager = rag_manager or RAGManager(k=cfg.sec_docs_rag_k)
        self.df_cwe = load_cwe_table(CSV_PATH)
        self.cwe_tree = load_cwe_tree(CWE_TREE_PATH)
        self.retriever = None
        self.os_platform = cfg.os_platform

        # LLMs
        self.plan_agent_llm = create_chat_model(
            model_name=cfg.model_name,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            agent_name="planner",
        )
        self.sec_agent_llm = create_chat_model(
            model_name=cfg.model_name,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            agent_name="sec_agent",
        )
        self.code_agent_llm = create_chat_model(
            model_name=cfg.model_name,
            temperature=cfg.temperature,
            coder=True,
            agent_name="code_agent",
        )

        self.shared_session_id_code_agent = "code-agent-session"
        self.shared_session_id_sec_agent = "sec-agent-session"
        self.shared_session_id_plan_agent = "plan-agent-session"
        self.shared_session_id_func_eval_agent = "func-eval-agent-session"
        self.shared_session_id_sec_eval_agent = "sec-eval-agent-session"

        # Phase 2 LLMs
        if "baxbench" in cfg.task.lower() :
            self._fix_suggestion_after = fix_suggestion_after_bax
            self._sec_understand_prompt = sec_understand_prompt_bax
        else:
            self._fix_suggestion_after = fix_suggestion_after
            self._sec_understand_prompt = sec_understand_prompt

        if cfg.enable_phase2:
            self.func_eval_llm = create_chat_model(
                model_name=cfg.model_name,
                temperature=cfg.temperature,
                # max_tokens=cfg.max_tokens,
                agent_name="func_eval",
            )
            self.sec_eval_llm = create_chat_model(
                model_name=cfg.model_name,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
                agent_name="sec_eval",
            )

            self.func_answer_prompt = _to_chat_prompt_from_legacy(func_answer_prompt[0])

            # self.func_understand_chain = func_understand_prompt | self.func_eval_llm
            # self.func_fix_suggestion_chain = fix_suggestion_after | self.func_eval_llm
            # self.sec_fix_suggestion_chain = fix_suggestion_after | self.sec_eval_llm
            # self.sec_code_analyze_chain = sec_understand_prompt | self.sec_eval_llm

            self.func_understand_chain = RunnableWithMessageHistory(
                prompt_4_code | self.func_eval_llm,
                get_session_history=get_limited_memory,
                input_messages_key="input",
                history_messages_key="chat_history",
            )
            self.func_fix_suggestion_chain = RunnableWithMessageHistory(
                prompt_4_code | self.func_eval_llm,
                get_session_history=get_limited_memory,
                input_messages_key="input",
                history_messages_key="chat_history",
            )
            self.sec_fix_suggestion_chain = RunnableWithMessageHistory(
                prompt_4_code | self.sec_eval_llm,
                get_session_history=get_limited_memory,
                input_messages_key="input",
                history_messages_key="chat_history",
            )
            self.func_answer_chain = self.func_answer_prompt | self.func_eval_llm
            self.sec_code_analyze_chain = RunnableWithMessageHistory(
                prompt_4_code | self.sec_eval_llm,
                get_session_history=get_limited_memory,
                input_messages_key="input",
                history_messages_key="chat_history",
            )

        self.prompt_for_planning = (
            prompt_for_planning[1]
            if ("gemini-2.5-flash" == cfg.model_name.lower())
            else (
                prompt_for_planning[3]
                if cfg.model_name.lower().startswith("qwen")
                else prompt_for_planning[0]
            )
        )
        self.plan_for_func_chain = self.prompt_for_planning | self.plan_agent_llm
        self.plan_for_sim_chain = prompt_for_simulation | self.plan_agent_llm
        self.plan_revise = prompt_for_plan_refinement | self.plan_agent_llm
        self.cwe_extract_prompt_for_model = (
            cwe_extract_prompt[1]
            if ("gemini-2.5-flash" in cfg.model_name.lower())
            else cwe_extract_prompt[0]
        )  #
        self.cwe_extract_chain = self.cwe_extract_prompt_for_model | self.sec_agent_llm
        # self.cwe_extract_chain = RunnableWithMessageHistory(
        #     prompt_4_code | self.sec_agent_llm,
        #     get_session_history=get_limited_memory,
        #     input_messages_key="input",
        #     history_messages_key="chat_history",
        # )

        self.code_gen_for_draft = (
            code_gen_for_draft[1]
            if cfg.model_name.lower().startswith("qwen")
            else code_gen_for_draft[0] if not cfg.only_plan else code_gen_for_draft[2]
        )
        # self.code_gen_w_only_plan_chain = self.code_gen_for_draft | self.code_agent_llm
        self.code_gen_w_only_plan_chain = RunnableWithMessageHistory(
            prompt_4_code | self.code_agent_llm,
            get_session_history=get_limited_memory,
            input_messages_key="input",
            history_messages_key="chat_history",
        )
        self.code_gen_prompt = (
            code_gen_prompt[2]
            if cfg.model_name.lower().startswith("qwen")
            else 
            code_gen_prompt[1]
            if cfg.model_name.lower().startswith("gemini")
            else
            code_gen_prompt[0]
        )
        if cfg.only_direct:
            self.code_only_direct_chain = prompt_4_draft_code | self.code_agent_llm
        self.code_gen_chain = RunnableWithMessageHistory(
            prompt_4_code | self.code_agent_llm,
            get_session_history=get_limited_memory,
            input_messages_key="input",
            history_messages_key="chat_history",
        )
        self.code_gen_w_merge_chain = RunnableWithMessageHistory(
            prompt_4_code | self.code_agent_llm,
            get_session_history=get_limited_memory,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

        self.code_refine_chain = RunnableWithMessageHistory(
            prompt_4_code | self.code_agent_llm,
            get_session_history=get_limited_memory,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

        self.sec_draft_analyze_chain = RunnableWithMessageHistory(
            prompt_4_code | self.sec_agent_llm,
            get_session_history=get_limited_memory,
            input_messages_key="input",
            history_messages_key="chat_history",
        )
        self.sec_guide_chain = RunnableWithMessageHistory(
            prompt_4_se_history | self.sec_agent_llm,
            get_session_history=get_limited_memory,
            input_messages_key="input",
            history_messages_key="chat_history",
        )
        self.sec_guide_without_rag_chain = RunnableWithMessageHistory(
            prompt_4_se_wo_rag | self.sec_agent_llm,
            get_session_history=get_limited_memory,
            input_messages_key="input",
            history_messages_key="chat_history",
        )
        self.sec_guide_not_history_chain = prompt_4_se | self.sec_agent_llm
        self.syntax_fixing_chain = syntax_fix_prompt | self.code_agent_llm

        self.preset_data = {}
        if cfg.load_preset:
            if cfg.preset_file:
                preset_path = Path(cfg.preset_file)
            else:
                preset_path = Path(
                    f"data/presets/{cfg.model_name}_{cfg.task}_preset.json"
                )
            print(f"Loading preset data from {preset_path}")
            self.preset_data = self.load_prev(preset_path)

        self.rescue_guide_data: Dict[str, str] = {}
        if cfg.rescue_guide_file:
            rescue_path = Path(cfg.rescue_guide_file)
            print(f"Loading rescue guide data from {rescue_path}")
            rescue_raw = self.load_prev(rescue_path)
            self.rescue_guide_data = {
                pid: item.get("sec_guidelines", item.get("codeguarder_prompt", ""))
                for pid, item in rescue_raw.items()
                if item.get("sec_guidelines") or item.get("codeguarder_prompt")
            }

        self._phase_paths = self._init_phase_paths()
        self.prev_map_phase1: Dict[int, Dict[str, Any]] = {}
        self.prev_map_phase2: Dict[int, Dict[str, Any]] = {}
        if self._phase_paths["phase1"].exists():
            self.prev_map_phase1 = self.load_prev(self._phase_paths["phase1"])
        if self._phase_paths["phase2"].exists():
            self.prev_map_phase2 = self.load_prev(self._phase_paths["phase2"])

    def _norm_model_name(self, name: str) -> str:
        # "gpt-4o-mini" -> "gpt4omini", "gpt4o" -> "gpt4o"
        return re.sub(r"[^a-z0-9]", "", (name or "").lower())

    def _should_dump_usage(self) -> bool:
        m = self._norm_model_name(self.cfg.model_name)
        return m in {"gpt4o", "gpt4omini"}

    # ---------- Helpers ----------
    def _init_phase_paths(self) -> Dict[str, Path]:
        """define paths for each phase"""
        base = f"{self.cfg.model_name}_{self.cfg.task}_{self.cfg.max_cwe_limit}"
        p1 = self.out_dir / f"_{base}.json"
        p2 = self.out_dir / f"_phase2_{base}.json"
        p1_log = self.out_dir / f"_{base}.log"
        p2_log = self.out_dir / f"_phase2_{base}.log"
        return {"phase1": p1, "phase2": p2, "p1_log": p1_log, "p2_log": p2_log}

    def load_prev(self, file_path):
        content: Dict[int, Dict[str, Any]] = {}
        if file_path.exists():
            with file_path.open("r", encoding="utf-8") as f:
                res = json.load(f)
            for item in res:
                pid = item.get("prompt_id", -1)
                if pid != -1:
                    content[pid] = item
        return content

    def _related_with_tree(self, target_cwe: int) -> List[int]:
        related: List[int] = []
        for od in self.cwe_tree:
            for k, v in od.items():
                vals = v if isinstance(v, list) else [v]
                if int(k) == target_cwe:
                    related.extend(vals)
                if target_cwe in vals:
                    related.append(int(k))
        return sorted(set(related))

    def _collect_related(self, target_cwe: int) -> List[int]:
        row = self.df_cwe.loc[self.df_cwe["CWE-ID"] == target_cwe]
        base = [] if row.empty else list(map(int, row["Related Weaknesses"].iloc[0]))
        return sorted(base + self._related_with_tree(target_cwe))

    def _row_meta(self, row: dict, question_key: str) -> tuple[int, str, str, str, int]:
        pid = int(row.get("prompt_id", -1))
        language = str(row.get("language") or row.get("lang") or "python").lower()
        question = row.get(question_key, "") or ""
        target_raw = row.get("cwe_identifier") or row.get("cwe") or "CWE-0"
        m = re.search(r"\d+", str(target_raw))
        target_cwe_num = int(m.group(0)) if m else 0
        return pid, language, question, target_raw, target_cwe_num

    def _normalize_plan_text(self, plan: str) -> str:
        if not plan:
            return ""
        txt = plan.strip().lower()
        markers = [
            "### plan",
            "###plan",
            "##plan",
            "## plan",
            "## new plan",
            "### functional plan",
            "### final plan",
            "functional plan",
            "final plan",
            "## New Plan",
            "### New Plan",
        ]
        anchor = -1
        for m in markers:
            pos = txt.rfind(m)
            if pos > anchor:
                anchor = pos
        if anchor != -1:
            txt = txt[anchor:]
        else:
            fallback_len = 1200  # 700
            txt = txt[-fallback_len:]
            txt = f"### Plan\n\n{txt}"
        txt = re.sub(r"\n+", "\n", txt)
        lines = [ln for ln in txt.splitlines() if ln.strip()]
        return "\n".join(lines)

    def _get_plan(
        self,
        pid: int,
        language: str,
        question: str,
        prev_map: dict,
        max_plan_steps: int = 1,
    ) -> str:
        if not self.cfg.with_plan:
            return "", 0
        plan = ""
        if self.cfg.already_plan:
            plan = (prev_map.get(pid) or {}).get("plan", "")
            return plan, None
        if not plan:
            inputs = {"language": language, "task": question}
            temp = self.plan_for_func_chain.invoke(inputs)

            # logging.info(temp)
            out = to_text(temp)
            plan = out.strip()
            retry = 0
            while not plan and retry < 3:
                retry += 1
                logging.warning("Planning chain returned empty output for pid=%s", pid)
                logging.warning("Re-trying %d...", retry)
                temp = self.plan_for_func_chain.invoke(inputs)
                out = to_text(temp)
                plan = out.strip()
            formatted = self.prompt_for_planning.format(**inputs)
            logging.info("[PLAN] Prompt:\n%s", formatted)
            logging.info("===== Finish Prompt =====")
            logging.info("[PLAN] Output:\n%s\n", plan)
            logging.info("===== Finish Output =====")
            plan = self._normalize_plan_text(plan)
            current_step = 0

        return plan, current_step

    def _extract_from_docs(
        self, rag_json: List[Dict[str, Any]]
    ) -> Tuple[
        List[str], List[str], List[int], Dict[str, str], Dict[str, Dict[str, str]]
    ]:
        extracted_cause: List[str] = []
        extracted_effect: List[str] = []
        cause_ids: List[str] = []
        effect_ids: List[str] = []
        descriptions: Dict[str, str] = {}

        for item in rag_json:
            if "cause_cwes" in item and item["cause_cwes"]:
                extracted_cause.extend(item["cause_cwes"])
                cause_ids.extend(
                    x.split(":")[0].strip().replace("CWE-", "")
                    for x in item["cause_cwes"]
                )
            if "effect_cwes" in item and item["effect_cwes"]:
                extracted_effect.extend(item["effect_cwes"])
                effect_ids.extend(
                    x.split(":")[0].strip().replace("CWE-", "")
                    for x in item["effect_cwes"]
                )
            if "why" in item and item.get("cause_cwes"):
                descriptions[item["cause_cwes"][0]] = (
                    item["why"] or "No description provided"
                )

        extracted_clean: List[int] = []
        for c, e in zip(cause_ids, effect_ids):
            for x in (c, e):
                if x.isdigit():
                    extracted_clean.append(int(x))
                elif ":" in x:
                    success_extract = False
                    parts = x.strip().split(":")
                    for part in parts:
                        part = part.strip()
                        if part.isdigit():
                            extracted_clean.append(int(part))
                            success_extract = True
                            break
                        else:
                            # logging.warning("Non-digit CWE ID found in split: %s", part)
                            continue
                    if not success_extract:
                        logging.warning("No valid CWE ID found in split: %s", x)
                        extracted_clean.append(0)
                else:
                    logging.warning("Non-digit CWE ID found: %s", x)
                    extracted_clean.append(0)

        meta: Dict[str, Dict[str, str]] = {}
        for cid in extracted_clean:
            row = self.df_cwe.loc[self.df_cwe["CWE-ID"] == int(cid)]
            desc = (
                "CWE not found in the database."
                if row.empty
                else row["Description"].iloc[0]
            )
            mitigations = (
                "No mitigations found."
                if row.empty
                else row["Potential Mitigations"].iloc[0]
            )
            # key = f"CWE-{cid}"
            name = "Unknown CWE" if row.empty else row["Name"].iloc[0]
            meta.setdefault(cid, {})["cwe_description"] = desc
            meta.setdefault(cid, {})["potential_mitigations"] = mitigations
            meta.setdefault(cid, {})["name"] = name
        return extracted_cause, extracted_effect, extracted_clean, descriptions, meta

    # ---------- Core steps ----------
    def extract_cwes(
        self, language: str, prompt: str, max_limit: int
    ) -> List[Dict[str, Any]]:
        inputs = {
            "problem_with_planning": (
                prompt
            ),
            "language": language,
            "max_limit": max_limit,
            "max_limit_less": max_limit - 1,
        }
        formatted_prompt = self.cwe_extract_prompt_for_model.format(**inputs)
        logging.info(
            "[CWE_EXTRACT] Prompt:\n%s\n==== END PROMPT ====\n", formatted_prompt
        )
        logging.info(
            "[CWE_EXTRACT] extracting with inputs: lang=%s, max_limit=%s",
            language,
            max_limit,
        )
        out = to_text(self.cwe_extract_chain.invoke(inputs))
        content = out.strip()
        logging.info("[CWE_EXTRACT] Answer:\n%s\n==== END ANSWER ====\n", content)
        for t in range(3):  # retry parsing up to 3 times
            try:
                block = extract_code(content, lr="json")
                data = safe_json_loads(block)
                if isinstance(data, dict) and "Security Requirements" in data:
                    data = data["Security Requirements"]
                if isinstance(data, dict) and "security_requirements" in data:
                    data = data["security_requirements"]
                data = sorted(data, key=lambda x: x.get("likelihood", 0), reverse=True)
                logging.info("[CWE_EXTRACT] Output:\n%s", json.dumps(data, indent=2))
                return data
            except Exception as e:
                logging.exception("Failed to parse CWE extraction output: %s", e)
                continue
        return []

    def _process_draft_code(
        self,
        pid: int,
        row: dict,
        language: str,
        question: str,
        problem_with_planning: str,
        action_header: str,
        task: str,
        plan: str,
        target_cwe_num: int,
        entrypoint_code: Optional[str] = None,
        is_multi_file: bool = False
    ) -> Tuple[Optional[str], Optional[OrderedDict], bool, Optional[str]]:

        if not getattr(self.cfg, "make_draft_code", False):
            return None, None, False, None

        draft_code = None
        draft_pass = False

        # 1) preset draft
        if getattr(self.cfg, "already_draft_code", False) and pid in self.preset_data:
            preset = self.preset_data.get(pid, {}) or {}
            draft_code = str(preset.get("draft_code", "") or "")
            draft_pass = bool(preset.get("draft_pass", False))
            if draft_pass and getattr(self.cfg, "with_analyze_draft_surface", False):
                logging.info(
                    "\n[DRAFT] attack-surface pre-pass found in preset (pid=%s)", pid
                )
            temp_cwe_output = (
                (self.preset_data.get(pid, {}) or {}).get("cwe_output", [])
                if pid in self.preset_data
                else []
            )
            _, _, extracted_clean, _, _ = self._extract_from_docs(temp_cwe_output)
            stat = OrderedDict(
                target_cwe=target_cwe_num,
                extracted_cwes=extracted_clean,
                cwe_output=temp_cwe_output,
                plan=plan,
                sec_guidelines=[],
                response=draft_code,
                draft_code=draft_code,
            )
            if draft_pass:
                stat["draft_pass"] = True
            # Seed coder-agent history so the main generate_code call has draft context
            if draft_code:
                draft_prompts, draft_outs, _ = self.generate_code(
                    row, language, self.os_platform, problem_with_planning,
                    action_header, task, security_requirements="",
                    not_invoke=True, is_multi_file=is_multi_file,
                )
                for dp, da in zip(draft_prompts, draft_outs):
                    h = get_limited_memory(self.shared_session_id_code_agent)
                    h.add_message(HumanMessage(content=dp))
                    h.add_message(AIMessage(content=draft_code if not da else da))
            return draft_code, stat, draft_pass, None

        prompt, answer, draft_code = self.generate_code(
            row,
            language,
            self.os_platform,
            problem_with_planning,
            action_header,
            task,
            security_requirements="",
            is_multi_file=is_multi_file
        )
        logging.info(
            "==============\n[DRAFT] Prompt:\n%s\n==== END PROMPT ====\n", prompt
        )
        logging.info("[DRAFT] Answer:\n%s\n==== END ANSWER ====\n", answer)

        if getattr(self.cfg, "with_analyze_draft_surface", False):
            attack_result = self.run_attack_surface_check(question, draft_code)

            has_surface = bool(attack_result.get("has_attack_surface", False))
            quick_wins: Optional[str] = attack_result.get("quick_wins", None)
            logging.info("[DRAFT] attack-surface=%s (pid=%s)", has_surface, pid)

            if not has_surface:
                logging.info(
                    "[SKIP] No attack surface detected → early exit (pid=%s)", pid
                )
                temp_cwe_output = (
                    (self.preset_data.get(pid, {}) or {}).get("cwe_output", [])
                    if pid in self.preset_data
                    else []
                )
                _, _, extracted_clean, _, _ = self._extract_from_docs(temp_cwe_output)
                if draft_code and language.lower() not in ["go", "javascript", "php", "rust", "ruby"]:
                    draft_code, _ = self.compilation_check_and_repair(
                        draft_code,
                        task,
                        language,
                        question,
                        row,
                        entrypoint_code=entrypoint_code,
                    )

                stat = OrderedDict(
                    target_cwe=target_cwe_num,
                    extracted_cwes=extracted_clean,
                    cwe_output=temp_cwe_output,
                    plan=plan,
                    sec_guidelines=[],
                    response=draft_code,
                    draft_pass=True,
                    draft_code=draft_code,
                )
                return draft_code, stat, True, None

            # HAS_ATTACK_SURFACE: pass quick_wins downstream
            return draft_code, None, False, quick_wins

        return draft_code, None, False, None

    def generate_code(
        self,
        total_info: dict,
        language: str,
        os_platform: str,
        task_description: str,
        action_header: str,
        task: str,
        security_requirements: str,
        plan: str = "",
        not_invoke: bool = False,
        is_multi_file: bool = False,
    ) -> Tuple[str, Optional[str], Optional[str]]:
        answer, code = None, None
        prompts = []
        outs = []
        inputs = {
            "task_description": task_description,
            "language": language,
            "action_prompt_header": action_header,
            "os_platform": os_platform,
            "security_requirements": security_requirements,
            "implementation_plan": plan,
        }
        if not_invoke:
            if security_requirements.strip() == "":
                formatted_prompt = self.code_gen_for_draft.format(**inputs)
            else:
                formatted_prompt = self.code_gen_prompt.format(**inputs)
            prompts.append(str(formatted_prompt))
            outs.append("")
            return prompts, outs, None

        if self.cfg.only_direct:
            inputs = {"input": task_description, "language": language}
            formatted_prompt = prompt_4_draft_code.format(**inputs)
            logging.info("[CODE_GEN] Direct Prompt:\n%s", formatted_prompt)
            logging.info("===== Finish Prompt =====")
            out = to_text(self.code_only_direct_chain.invoke(inputs)).strip()
        elif security_requirements.strip() == "":
            formatted_prompt = self.code_gen_for_draft.format(**inputs)
            inputs = {"input": formatted_prompt}
            logging.info("[CODE_GEN] w/o security guide Prompt:\n%s", formatted_prompt)
            out = to_text( self.code_gen_w_only_plan_chain.invoke(inputs, config={"configurable": {"session_id": self.shared_session_id_code_agent}}) )
        else:
            formatted_prompt = self.code_gen_prompt.format(**inputs)
            inputs = {"input": formatted_prompt}
            out = to_text(
                self.code_gen_chain.invoke(
                    inputs,
                    config={
                        "configurable": {
                            "session_id": self.shared_session_id_code_agent
                        }
                    },
                )
            )
        if isinstance(out, str):
            answer = out.strip()
        elif isinstance(out, list):
            answer = out[-1].strip()
        answer = format_step(answer)
        if not is_multi_file:
            code = self.extract_code(answer, task, total_info)
        else:
            code = answer
        return formatted_prompt, answer, code

    def _run_phase2_pipeline(
        self,
        row: dict,
        pid: int,
        language: str,
        question: str,
        code: str,
        action_header: str,
        task: str,
        security_req: Dict,
        draft_code: str,
        rag_json=None,
        is_multi_file: bool = False,
    ):
        """
        Phase 2: Code Evaluation and Refinement Pipeline
        """
        flow = []
        security_req = remove_codeblocks(security_req).strip()
        security_req = re.sub(r"\n\s*\n+", "\n", security_req)
        logging.info(f"[PHASE2] Starting code evaluation================")
        current_attempt = 1
        current_code = code

        while current_attempt <= self.cfg.max_refinement_attempts:
            logging.info(
                f"[PHASE2] Attempt {current_attempt}/{self.cfg.max_refinement_attempts}"
            )
            # Step 1: Functionality Evaluation
            func_result = {}
            sec_result = {}
            if self.cfg.enable_functionality_check:
                get_limited_memory(self.shared_session_id_func_eval_agent).clear()
                func_result = self._evaluate_functionality(
                    current_code,
                    question,
                    language,
                    security_req,
                    draft_code,
                    action_header,
                )
                func_analysis = func_result["feedback"].strip()

            func_pass = func_result.get("passed", True)
            func_analysis = func_result.get("feedback", "")
            sec_llm_pass = True

            if True:
                # Step 2: Security Evaluation
                if self.cfg.enable_security_check:
                    get_limited_memory(self.shared_session_id_sec_eval_agent).clear()
                    sec_result = self._evaluate_security(
                        code=current_code,
                        language=language,
                        question=question,
                        security_req=security_req,
                        action_header=action_header,
                    )
                    logging.info("===========Finish Security Feedback===========\n")

                llm_part = sec_result #.get("llm", {})
                sec_llm_pass = llm_part.get("passed", True)
                sec_feedback = llm_part.get("feedback", "")

            if not func_pass or not sec_llm_pass:
                final_feedback = f"Functionality: {'Passed' if func_pass else 'Failed'}, Security: {'Passed' if sec_llm_pass else 'Failed'}"  
                final_feedback += (
                    f"\n\nFunctionality Feedback:\n{func_analysis}"
                    if not func_pass
                    else ""
                )
                final_feedback += (
                    f"\n\nSecurity Feedback:\n{sec_feedback}"
                    if not sec_llm_pass
                    else ""
                )
                current_code = self._refine_code_with_analysis(
                    row,
                    code=current_code,
                    feedback=final_feedback,
                    problem_with_planning=question,
                    action_prompt_header=action_header,
                    task=task,
                    language=language,
                    sec_req="",
                    is_multi_file=is_multi_file,
                )  
            else:
                logging.info(
                    f"[PHASE2] Both Functionality and Security checks passed. Exiting refinement loop.\n"
                )
                break

            flow.append(
                {
                    "attempt": current_attempt,
                    "func_result": func_result,
                    "sec_result": sec_result,
                }
            )

            current_attempt = current_attempt + 1

        # final compilation check
        if (
            current_code
            and current_code.strip() != code.strip()
            and language.lower() not in ["go", "javascript", "php", "rust", "ruby"]
            and not row.get("is_multi_file", False)
        ):
            current_code, _ = self.compilation_check_and_repair(
                current_code, self.cfg.task, language, question, row
            )
        logging.info(
            f"\n==========[PHASE2] Final code for prompt_id={pid} \n{current_code}\n"
        )
        return current_code, current_code != code, flow

    def extract_section(self, text, start_pattern, end_pattern=None):
        if end_pattern:
            pattern = f"{start_pattern}(.*?){end_pattern}"
        else:
            pattern = f"{start_pattern}(.*)"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(0).strip() if match else text

    def _evaluate_functionality(
        self,
        code: str,
        question: str,
        language: str,
        security_req: str,
        draft_code: str,
        action_header: str,
    ) -> Dict[str, Any]:

        sec_req = remove_codeblocks(security_req).strip()
        sec_req = re.sub(r"\n\s*\n+", "\n", sec_req)

        inputs = {
            "task_description": question, 
            "security_requirements": sec_req,
            "language": language.lower(),
            "current_code": code,
            "draft_code": draft_code,
            "action_header": action_header,
        }

        prompt = func_understand_prompt.format(**inputs)
        logging.info(f"[PHASE2] Functionality understanding prompt:\n{prompt}\n")
        logging.info("========Finish Functionality Understanding Prompt========\n")
        inputs = {"input": prompt}
        under_res = to_text(
                self.func_understand_chain.invoke(
                    inputs,
                    config={
                        "configurable": {
                            "session_id": self.shared_session_id_func_eval_agent
                        }
                    },
                )
            )

        logging.info(f"[PHASE2] Functionality understanding:\n{under_res}\n")
        logging.info("========Finish Functionality Understanding========\n")
        analysis = under_res

        if "THE CODE IS FUNCTIONAL".lower() in under_res.lower():
            passed = True
        else:
            answer = to_text(
                self.func_answer_chain.invoke(
                    {
                        "MISTAKES": under_res,
                        "PROBLEM": question,
                    }
                )
            ).strip()

            logging.info(f"[PHASE2] Functionality evaluation result: {answer}")
            passed = (
                "yes".lower() in answer.lower() and "no".lower() not in answer.lower()
            )
        logging.info(f"[PHASE2] Functionality evaluation passed: {passed}\n")
        markers = {
                "current_code": {
                    "title": "Current Code",
                    "start_pattern": r"(?:^|\n)###\s*Current Code Analysis.*?",
                    # "end_pattern": r"###\s*5\."
                },
            }
        functional_gaps_text = self.extract_section(
            under_res,
            markers["current_code"]["start_pattern"],
        )
        functional_gaps_text = re.sub(r'\n{2,}', '\n', functional_gaps_text.strip())
        analysis = functional_gaps_text
        if not passed:
            fix_suggestion = ""
            inputs = {
                "problem": question,
                "feedback": functional_gaps_text,
                "language": language.lower(),
                "func_analysis": "",
                "current_code": code,
                "action_header": action_header,
            }
            prompt = self._fix_suggestion_after.format(**inputs)
            logging.info(
                f"[PHASE2] Functionality understanding fix suggestion prompt:\n{prompt}\n"
            )
            logging.info(
                "========Finish Functionality Understanding Fix Suggestion Prompt========\n"
            )

            inputs = {"input": prompt}
            fix_suggestion = to_text(
                    self.func_fix_suggestion_chain.invoke(
                        inputs,
                        config={
                            "configurable": {
                                "session_id": self.shared_session_id_func_eval_agent
                            }
                        },
                    )
                )

            total_opinion = (
                fix_suggestion  
            )
            total_opinion = re.sub(r"\n\s*\n+", "\n", total_opinion).strip()
            analysis = total_opinion
            logging.info(
                f"[PHASE2] Functionality understanding extracted analysis:\n{total_opinion}\n"
            )
            logging.info(
                "========Finish Functionality Understanding Extraction========\n"
            )

        if not passed and "no actionable fix" in analysis.lower():
            passed = True
        return {"passed": passed, "feedback": analysis, "func_req": ""}

    def _evaluate_security(
        self,
        code: str,
        language: str,
        question: str = "",
        security_req: str = "",
        action_header: str = "",
    ) -> Dict[str, Any]:
        evaluation_notes = {}
        ## evaluate the code with sec guidelines
        logging.info("\n[SEC_ANALYZE] Start Security Analyze\n")
        inputs = {
            "current_code": code,
            "language": language,
            "task_description": question,  
            "security_requirements": security_req,
            "action_header": action_header,
        }
        prompt = self._sec_understand_prompt.format(**inputs)
        inputs = {"input": prompt}
        und_output = to_text(
                    self.sec_code_analyze_chain.invoke(
                        inputs,
                        config={
                            "configurable": {
                                "session_id": self.shared_session_id_sec_eval_agent
                            }
                        },
                    )
                )
        logging.info("\n[SEC_ANALYZE] Prompt:\n%s", prompt)
        logging.info("========Finish Security Analyze Prompt========\n")
        logging.info("\n[SEC_ANALYZE] Output:\n%s\n", und_output)
        logging.info("========Finish Security Analyze========\n")

        if "THE CODE IS SAFE".lower() in und_output.lower():
            passed = True
        else:
            answer = to_text(
                self.func_answer_chain.invoke(
                    {
                        "MISTAKES": und_output,
                        "PROBLEM": question,
                    }
                )
            ).strip()
            logging.info(f"[PHASE2] Security evaluation result: {answer}")
            passed = "yes" in answer.lower()  #
        logging.info(f"[PHASE2] Security evaluation passed: {passed}\n")

        if passed:
            evaluation_notes["llm"] = {"passed": True, "feedback": und_output}
        else:
            markers = {
                "example_scenario": {
                    "title": "Attack Scenario",
                    "start_pattern": r"(?:^|\n)###\s*Attack Scenarios\s*\n",
                },
                "current_code": {
                    "title": "Current Code",
                    "start_pattern": r"(?:^|\n)###\s*Current Code Analysis.*?",
                    # "end_pattern": r"###\s*5\."
                },
            }
            sec_gaps_text = self.extract_section(
                und_output,
                markers["current_code"]["start_pattern"],
            )
            inputs = {
                "problem": question,
                "feedback": sec_gaps_text,
                "language": language.lower(),
                "current_code": code,
                "action_header": action_header,
            }
            prompt = self._fix_suggestion_after.format(**inputs)
            logging.info(
                f"[PHASE2] Security understanding fix suggestion prompt:\n{prompt}\n"
            )
            logging.info(
                "========Finish Security Understanding Fix Suggestion Prompt========\n"
            )
            # fix_suggestion = to_text(self.sec_fix_suggestion_chain.invoke(inputs))
            inputs = {"input": prompt}
            fix_suggestion = to_text(
                        self.sec_fix_suggestion_chain.invoke(
                            inputs,
                            config={
                                "configurable": {
                                    "session_id": self.shared_session_id_sec_eval_agent
                                }
                            },
                        )
                    )
            total_opinion = fix_suggestion
            logging.info(
                f"[PHASE2] Security understanding extracted analysis:\n{total_opinion}\n"
            )
            fix_approaches_match = re.search(r"(### Fix Approaches.*)", total_opinion, re.DOTALL)
            if fix_approaches_match:
                total_opinion = fix_approaches_match.group(1)
            total_opinion = re.sub(r"\n\s*\n+", "\n", total_opinion).strip()
            
            logging.info(
                "========Finish Security Understanding Extraction========\n"
            )
            
            no_fix = "no actionable fix" in total_opinion.lower()
            evaluation_notes = {"passed": no_fix, "feedback": total_opinion}

        return evaluation_notes

    def _refine_code_with_analysis(
        self,
        total_info: dict,
        code: str,
        feedback: str,
        problem_with_planning: str,
        action_prompt_header: str,
        task: str,
        language: str,
        sec_req: str,
        is_multi_file: bool = False,
    ) -> Optional[str]:
        """
        Refine code based on functionality feedback
        """
        try:
            inputs = {
                "problem_with_planning": problem_with_planning,
                "code": code,
                "feedback": feedback,
                "action_prompt_header": action_prompt_header.format(language=language),
                "language": language,
                "security_req": sec_req,
                "os_platform": getattr(
                    self, "os_platform", getattr(self.cfg, "os_platform", "linux")
                ),
            }

            formatted_prompt = code_refine_prompt.format(**inputs)
            logging.info("[CODE_REFINE] Prompt:\n%s", formatted_prompt)
            logging.info("===== Finish Prompt =====")
            inputs = {"input": formatted_prompt}
            response = to_text(
                self.code_refine_chain.invoke(
                    inputs,
                    config={
                        "configurable": {
                            "session_id": self.shared_session_id_code_agent
                        }
                    },
                )
            )
            if is_multi_file:
                parser = Parser()
                refined_parsed = parser._parse_multi_file_response(response)
                if isinstance(refined_parsed, dict) and refined_parsed:
                    original_parsed = parser._parse_multi_file_response(code)
                    if isinstance(original_parsed, dict) and original_parsed:
                        original_parsed.update(refined_parsed)
                        refined_code = "".join(
                            f"<FILEPATH>\n{fp}\n</FILEPATH>\n<CODE>\n{content}\n</CODE>\n\n"
                            for fp, content in original_parsed.items()
                        )
                    else:
                        refined_code = response
                else:
                    refined_code = response
            else:
                refined_code = self.extract_code(response, task=task, total_info=total_info)
            logging.info(f"Refined code:\n{refined_code}")
            logging.info("===========Finish Code Refinement===========\n")
            return refined_code if refined_code else code

        except Exception as e:
            logging.error(f"Error in functionality code refinement: {str(e)}")
            return code

    def _build_rag_queries(self, group: dict) -> List[str]:
        topics = []
        for g in group:
            topic = " ".join(
                [
                    (g.get("group_name", "") or "").strip(),
                    (g.get("why", "") or "").strip(),
                ]
            ).strip()
            topics.append(topic)
        return topics

    def _format_docs_for_prompt(self, docs: List[Any], max_chars: int = 2500):
        chunks = []
        seen = set()
        for d in docs:
            src = getattr(d, "metadata", {})
            txt = (d.page_content or "").strip()
            key = (str(src) or "") + "||" + txt[:100]
            if len(txt) < 50 or key in seen:
                continue
            seen.add(key)
            chunks.append(txt.strip())
            if sum(len(c) for c in chunks) > max_chars:
                break
        if not chunks:
            return "- (no high-quality practices found)", chunks
        return "\n\n".join(f"- {c}" for c in chunks), chunks

    def extract_content_after_marker(
        self,
        text: str,
        markers: list,
        remove_next: bool = False,
        section_marker: str = "###",
    ) -> str:
        """
        Extracts content after the first occurrence of a marker in the text.
        If the marker is not found, returns the original text.
        """
        for marker in markers:
            idx = text.lower().find(marker.lower())
            if idx != -1:
                section = text[idx + len(marker) :].strip()
                if remove_next:
                    next_marker_idx = section.find(section_marker)
                    if next_marker_idx != -1:
                        section = section[:next_marker_idx].strip()
                return section
        fallback_len = 700
        text = text[-fallback_len:]
        return text.strip()

    def run_attack_surface_check(self, problem: str, draft_code: str):
        try:
            inputs = dict(
                problem=problem,
                draft_code=draft_code,
            )
            prompt = (
                sec_attack_surface_prompt_mini.format(**inputs)
                if self.cfg.model_name.lower() in ["gpt4o-mini"]
                else sec_attack_surface_prompt_gemini_flash.format(**inputs)
                if self.cfg.model_name.lower() in ["gemini-2.5-flash"]
                else sec_attack_surface_prompt.format(**inputs)
            )

            out = to_text(
                self.sec_draft_analyze_chain.invoke(
                    {"input": prompt}, config={"configurable": {"session_id": self.shared_session_id_sec_agent}}
                )
            )

            result_text = out.strip()
            parsed = {
                "has_attack_surface": True,
                "categories": [],
                "raw_output": result_text,
            }
            logging.info("===========Start Attack Surface Check===========")
            logging.info(f"[ATTACK_SURFACE] Prompt:\n{prompt}\n")
            logging.info(f"[ATTACK_SURFACE] Output:\n{result_text}\n")
            logging.info("===========Finish Attack Surface Check===========\n")
            # NO ATTACK SURFACE DETECTED → flag False
            if (
                "NO ATTACK SURFACE".lower() in result_text.lower()
                or "NO_ATTACK_SURFACE".lower() in result_text.lower()
            ):
                parsed["has_attack_surface"] = False

            return parsed

        except Exception as e:
            logging.error(f"Error in attack surface check: {str(e)}")
            return {
                "has_attack_surface": True,
                "categories": [],
                "raw_output": f"Evaluation error: {str(e)}",
            }

    def make_security_guidelines_with_rag(
        self,
        language: str,
        problem_with_planning: str,
        rag_json: List[Dict[str, Any]],
        retriever: RAGManager = None,
        os_platform: str = "linux",
        sec_guidelines: List[Dict[str, Any]] = None,
        draft_code: str = None,
        task: str = "",
        precomputed_else: Optional[str] = None,
        precomputed_snippets: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        results = []

        loop_items = rag_json if rag_json else ([{}] if precomputed_snippets is not None else [])
        for i, group in enumerate(loop_items):
            queries = self._build_rag_queries(rag_json)
            if self.cfg.with_rag:
                if precomputed_snippets is not None:
                    snippets = precomputed_snippets
                    gathered_docs = []
                    logging.info("[RAG %d] using precomputed snippets (%d chars)", i, len(snippets))
                elif not self.cfg.already_rag and sec_guidelines is None:

                    logging.info("[RAG] Queries: %s", queries)
                    gathered_docs: List[Any] = []

                    for qi, q in enumerate(queries):
                        docs = retriever.invoke(q)
                        logging.info("[RAG %d.%d] %s", i, qi, q)
                        gathered_docs.extend(docs)
                else:
                    gathered_docs = []
                    for doc in sec_guidelines[i].get("supporting_docs", []):
                        if doc.get("excerpt"):
                            gathered_docs.append(
                                SimpleDocument(
                                    page_content=doc["excerpt"],
                                    metadata={"source": doc["source"] or None},
                                )
                            )

                if precomputed_snippets is None:
                    snippets, chunks = self._format_docs_for_prompt(
                        gathered_docs, max_chars=7000 #5000
                    )
                else:
                    chunks = []
                logging.info(
                    "[RAG %d] gathered %d docs, formatted to %d chars, %d chunks",
                    i,
                    len(gathered_docs),
                    len(snippets),
                    len(chunks),
                )
            else:
                snippets = ""
                gathered_docs = []
                # queries = []
                logging.info("[RAG] Skipping RAG as per configuration")

            if self.cfg.only_rag:
                results.append(
                    {
                        "group_name": "Reviewed",
                        "guidelines": snippets,
                        "supporting_docs": [
                            {
                                "source": getattr(d, "metadata", {}).get("source")
                                or getattr(d, "metadata", {}).get("path"),
                                "excerpt": (d.page_content or "").strip(),
                            }
                            for d in gathered_docs
                        ],
                    }
                )
                return results
            inputs = dict(
                language=language,
                os_platform=os_platform,
                problem_with_planning=problem_with_planning,
                group_name=group.get("group_name", ""),
                cause_cwes=", ".join(group.get("cause_cwes", [])),
                effect_cwes=", ".join(group.get("effect_cwes", [])),
                why=group.get("why", ""),
                red_flags=", ".join(group.get("red_flags", [])),
                cwe_limit=self.cfg.max_cwe_limit if self.cfg.max_cwe_limit!=1 else 2,
                cwe_list=", ".join(
                    queries
                ),  
            )
            prompt = sec_guide_prompt.format(**inputs)
            tail = (
                prompt_4_sec_tail_for_gemini.format(**inputs)
                if "gemini" in self.cfg.model_name.lower()
                or "deepseek" in self.cfg.model_name.lower()
                else prompt_4_sec_tail.format(**inputs)
            )
            if self.cfg.with_rag:
                formatted_prompt = prompt_4_se.format_prompt(
                    input=prompt,
                    retrieved_snippets=snippets,
                    chat_history=[""],
                    language=language,
                    os_platform=os_platform,
                    problem_with_planning=problem_with_planning,
                    prompt_4_sec_tail=tail,
                ).to_string()
            else:
                formatted_prompt = prompt_4_se_wo_rag.format_prompt(
                    input=prompt,
                    chat_history=[""],
                    language=language,
                    os_platform=os_platform,
                    problem_with_planning=problem_with_planning,
                    prompt_4_sec_tail=tail,
                ).to_string()

            if not self.cfg.with_sec_all_history:
                out = to_text(
                    self.sec_guide_not_history_chain.invoke(
                        {
                            "input": prompt,
                            "retrieved_snippets": snippets,
                            "language": language,
                            "os_platform": os_platform,
                            "problem_with_planning": problem_with_planning,
                            "prompt_4_sec_tail": tail,
                        },
                    )
                )
            else:
                if self.cfg.with_rag:
                    out = to_text(
                        self.sec_guide_chain.invoke(
                            {
                                "input": prompt,
                                "retrieved_snippets": snippets,
                                "language": language,
                                "os_platform": os_platform,
                                "problem_with_planning": problem_with_planning,
                                "prompt_4_sec_tail": tail,
                            },
                            config={
                                "configurable": {
                                    "session_id": self.shared_session_id_sec_agent
                                }
                            },
                        )
                    )
                else:
                    out = to_text(
                        self.sec_guide_without_rag_chain.invoke(
                            {
                                "input": prompt,
                                "retrieved_snippets": "",
                                "language": language,
                                "os_platform": os_platform,
                                "problem_with_planning": problem_with_planning,
                                "prompt_4_sec_tail": tail,
                            },
                            config={
                                "configurable": {
                                    "session_id": self.shared_session_id_sec_agent
                                }
                            },
                        )
                    )
            # out = ""
            markers = [
                "### security guidelines",
                "### security_guidelines",
                "### security guideline",
                "### security_guideline",
                "security guidelines",
                "security_guidelines",
            ]
            guidelines_section = out.strip()
            guidelines_section = self.extract_content_after_marker(out, markers)
            guidelines_section = re.sub(r"\n\s*\n+", "\n", guidelines_section)

            logging.info("\n[SEC_GUIDE %d] Prompt:\n%s", i, formatted_prompt)
            logging.info("\n[SEC_GUIDE %d] Output:\n%s\n", i, out)

            results.append(
                {
                    "group_name": group.get("group_name", f"group_{i}"),
                    "guidelines": guidelines_section,
                    "supporting_docs": [
                        {
                            "source": getattr(d, "metadata", {}).get("source")
                            or getattr(d, "metadata", {}).get("path"),
                            "excerpt": (d.page_content or "").strip(),
                        }
                        for d in gathered_docs
                    ],
                }
            )
            break

        if self.cfg.with_sec_else_draft and draft_code:
            if precomputed_else is not None:
                # Already computed in combined attack surface call — no extra inference needed
                logging.info("\n[SEC_GUIDE ELSE] Using precomputed quick wins:\n%s\n", precomputed_else)
                sec_else = precomputed_else
            else:
                prompt = sec_guide_else_prompt.format(draft_code=draft_code)
                out = to_text(
                    self.sec_guide_chain.invoke(
                        {
                            "input": prompt,
                            "retrieved_snippets": "",
                            "language": language,
                            "os_platform": os_platform,
                            "problem_with_planning": problem_with_planning,
                            "prompt_4_sec_tail": "",
                        },
                        config={
                            "configurable": {"session_id": self.shared_session_id_sec_agent}
                        },
                    )
                )
                logging.info("\n[SEC_GUIDE ELSE] Prompt:\n%s", prompt)
                logging.info("\n[SEC_GUIDE ELSE] Output:\n%s\n", out)
                sec_else = out.strip()

            if "No additional guideline needed".lower() not in sec_else.lower():
                sec_else = re.sub(r"\n\s*\n+", "\n", sec_else)
                results.append(
                    {
                        "group_name": "others",
                        "guidelines": sec_else,
                        "supporting_docs": [],
                    }
                )
        return results

    def validate_security_guidelines(
        self,
        pid: int,
        language: str,
        question: str,
        rag_json: List[Dict[str, Any]],
        sec_guidelines: List[Dict[str, Any]],
        valid_with_rag_raq=False,
    ) -> Tuple[List[Dict[str, Any]], str]:
        if not (getattr(self.cfg, "with_sec_guide_validate", False)):
            return sec_guidelines, ""

        logging.info("[GUIDE] Validating security guidelines for prompt_id=%s", pid)
        sec_guide_review = sec_guide_refine_prompt | self.sec_agent_llm
        if not valid_with_rag_raq:
            # summarized = '\n'.join([sec['guidelines'] for sec in sec_guidelines])
            summarized = "\n".join(
                sec["guidelines"]
                for sec in sec_guidelines
                if sec.get("group_name") != "Reviewed"
            )

        else:
            summarized = "\n".join(
                (
                    "\n".join(
                        doc["excerpt"]
                        for doc in sec.get("supporting_docs", [])
                        if doc.get("excerpt")
                    )
                    if sec.get("supporting_docs")
                    else sec.get("guidelines", "")
                )
                for sec in sec_guidelines
                if sec.get("group_name") != "Reviewed"
            )

        inputs = {
            "language": language,
            "os_platform": getattr(self, "os_platform", "Linux"),
            "question": question ,
            "security_guidelines": summarized,
            "cwe_groups": rag_json,
        }
        try:
            logging.info(
                "[GUIDE] Review prompt:\n%s", sec_guide_refine_prompt.format(**inputs)
            )
            logging.info("===== Finish Review Prompt =====\n")
            out = to_text(sec_guide_review.invoke(inputs)).strip()
            if not out:
                return sec_guidelines, ""
            logging.info("[GUIDE] Review output:\n%s", out)
            logging.info("===== Finish Review Output =====\n")

            markers = [
                "### security guidelines",
                "### security_guidelines",
                "### security guideline",
                "### security_guideline",
                "security guidelines",
                "security_guidelines",
            ]
            guidelines_section = self.extract_content_after_marker(out.strip(), markers)
            guidelines_section = re.sub(r"\n\s*\n+", "\n", guidelines_section).strip()

            if guidelines_section:
                sec_guidelines.append(
                    {"group_name": "Reviewed", "guidelines": guidelines_section}
                )
            else:
                logging.warning(
                    "[GUIDE] No 'Reviewed' guidelines found after validation."
                )
                sec_guidelines.append(
                    {"group_name": "Reviewed", "guidelines": summarized}
                )
            return sec_guidelines, out

        except Exception as e:
            logging.error("[GUIDE] Review error (pid=%s): %s", pid, e)
            return sec_guidelines, f"ERROR: {e}"

    def build_security_requirements(
        self, sec_guidelines: List[Dict[str, Any]]
    ) -> Tuple[str, bool]:
        if getattr(self.cfg, "only_plan", False):
            return ""
        sg = sec_guidelines or []

        if getattr(self.cfg, "only_rag", False) or (
            not getattr(self.cfg, "with_sec_guide_validate", False)
            and len(sg) == 1
            and sg[0].get("group_name", "") == "Reviewed"
        ):
            reviewed = next(
                (
                    g.get("guidelines", "").strip()
                    for g in sg
                    if g.get("group_name") == "Reviewed" and g.get("guidelines")
                ),
                "",
            )
            if reviewed:
                return reviewed
            logging.warning("[GUIDE] No 'Reviewed' guidelines found in only_rag mode.")
            return ""
        if getattr(self.cfg, "with_sec_guide_validate", False):
            reviewed = next(
                (
                    g.get("guidelines", "").strip()
                    for g in sg
                    if g.get("group_name") == "Reviewed" and g.get("guidelines")
                ),
                "",
            )
            if reviewed:
                return reviewed
            logging.warning("[GUIDE] No 'Reviewed' guidelines found after validation.")
            # raise ValueError("No 'Reviewed' guidelines found after validation.")
            return "\n".join(
                sec["group_name"] + "\n" + sec["guidelines"]
                for sec in sec_guidelines
                if sec["group_name"].strip() not in ("Reviewed", "others")
            )

        if not self.cfg.with_sec_else_draft:
            return "\n".join(
                sec["group_name"] + "\n" + sec["guidelines"]
                for sec in sec_guidelines
                if sec["group_name"].strip() not in ("Reviewed", "others")
            )
        else:
            return "\n".join(
                sec["group_name"] + "\n" + sec["guidelines"]
                for sec in sec_guidelines
                if sec["group_name"].strip() != "Reviewed"
            )

    def extract_code(
        self, content: str, task: str, total_info: dict, entrypoint_code=None
    ) -> str:
        content = format_step(content)
        if "safecoder_autocomplete" in task:
            code = extract_code(
                content,
                lr=total_info["language"],
                task=task,
                file_context=total_info["file_context"],
                func_context=total_info["func_context"],
            )
        elif "cweval" in task:
            code = extract_code(
                content,
                lr=total_info["language"],
                task=task,
                file_context=None,
                func_context=entrypoint_code,
            )
        elif "baxbench" in task:
            code = extract_code(content, lr=total_info["language"])
            m = re.search(r"<CODE>(.+?)</CODE>", code, re.DOTALL)
            code = m.group(1).strip() if m else code
        else:
            code = extract_code(content, lr=total_info["language"])
        return code

    def compilation_check_and_repair(
        self,
        code: str,
        task: str,
        language: str,
        question: str,
        total_info: dict,
        max_iter=2,
        entrypoint_code=None,
    ) -> Tuple[str, bool]:
        if language.lower() in ["go", "javascript"]:
            return code, True
        if language.lower() in ["go"]:
            temp = """package main 
    import (
	"fmt"
	"io/ioutil"
	"os")"""
            parse_for_code = [
                (
                    temp
                    + "\n"
                    + code.replace("package main", "")
                    + "\n"
                    + entrypoint_code
                    if entrypoint_code
                    else code
                )
            ]
        else:
            parse_for_code = [code]
        logging.info("\n=======Starting compilation Check=======")
        _, non_parsed_srcs, feedbacks = make_parse_list(
            parse_for_code, total_info, get_feedback=True
        )
        compile_success = len(non_parsed_srcs) == 0
        curr_iter = 0
        logging.info("Compilation success: %s\n", compile_success)
        while not compile_success and curr_iter < max_iter:
            logging.info("\n=======Starting compilation Fixing=======")
            curr_iter += 1
            stdout = feedbacks[0]["stdout"]
            stderr = feedbacks[0]["stderr"]
            inputs = {
                "question": question,
                "language": language,
                "code": code,
                "compiler_feedback": (stdout + "\n" + stderr)[:1000],
            }
            temp = (stdout + "\n" + stderr)[:1000]
            formatted_prompt = syntax_fix_prompt.format(**inputs)
            logging.info(f"error : {temp}")
            logging.info(
                "\n🔍 [Prompt FOR Syntax Fixing - Iteration %d]:\n%s\n",
                curr_iter,
                formatted_prompt,
            )
            code = to_text(self.syntax_fixing_chain.invoke(inputs)).strip()
            code = self.extract_code(code, task, total_info)

            # logging.info("\n🔍 [Fixed Code - Iteration %d]:\n%s\n", curr_iter, code)
            _, non_parsed_srcs, feedbacks = make_parse_list(
                [code], total_info, get_feedback=True
            )
            compile_success = len(non_parsed_srcs) == 0
            logging.info(
                "Iteration %d compilation success: %s\n", curr_iter, compile_success
            )
        return code, compile_success

    def reset_history(self):
        get_limited_memory(self.shared_session_id_code_agent).clear()
        get_limited_memory(self.shared_session_id_sec_agent).clear()
        get_limited_memory(self.shared_session_id_plan_agent).clear()
        get_limited_memory(self.shared_session_id_func_eval_agent).clear()
        get_limited_memory(self.shared_session_id_sec_eval_agent).clear()
        get_limited_memory("").clear()  # draft code session
        logging.info("Cleared conversation history for all agents.")

    def _pre_understand_code(self, task_description: str, security_requirements: str) -> str:
        messages = code_understand_prompt.format_messages(
            task_description=task_description,
            security_requirements=security_requirements,
        )
        response = to_text(self.code_agent_llm.invoke(messages))
        history = get_limited_memory(self.shared_session_id_code_agent)
        history.add_message(messages[-1])
        history.add_message(AIMessage(content=response))
        logging.info("[PRE_UNDERSTAND] Prompt:\n%s", str(messages[0].content))
        logging.info("[PRE_UNDERSTAND] Summary:\n%s", response)
        return response

    # ---------- Orchestration ----------
    def run_phase1(self) -> None:
        start_time = time.time()
        set_current_phase("phase1")
        task = self.cfg.task
        data, action_prompt_header, question_key = load_data(task, "none")
        data.sort(key=lambda x: x["prompt_id"])
        log_path = self._phase_paths["p1_log"]
        output_path = self._phase_paths["phase1"]
        setup_logging(log_path)
        logging.info("\n[EngineConfig]\n%s", config_to_str(self.cfg))
        logging.info("Output: %s", output_path)
        total_results: List[Dict[str, Any]] = []

        cwe_hits = 0
        cwe_rel_hits = 0
        cwe_total = 0
        rows_used = set()

        # Cache for existing plan and results
        prev_map = self.prev_map_phase1
        for row in data:
            pid, language, question, _, target_cwe_num = self._row_meta(
                row, question_key
            )

            row_start_time = time.time()
            pid_handler = attach_pid_log_handler(self.out_dir, pid, phase="phase1")
            try:
                related_list = self._collect_related(target_cwe_num)
                current_code = None
                plan = None
                sec_guidelines = None
                question_ori = None
                action_header_ori = None
                is_multi_file = row.get("is_multi_file", False)
                if isinstance(action_prompt_header, list):
                        action_header = action_prompt_header[1] if is_multi_file else action_prompt_header[0]
                        if "baxbench" in self.cfg.task :
                            if is_multi_file:
                                question_ori = question
                                question = question.replace(action_prompt_header[3], "")
                            else:
                                action_header_ori = action_header
                                action_header = action_header.replace(action_prompt_header[2], "")
                else:
                    action_header = action_prompt_header.format(language=language)
                if pid in prev_map:
                    row.update(prev_map[pid])
                    current_code = str(prev_map[pid].get("response", None))
                    plan = (prev_map.get(pid) or {}).get("plan", "")
                    rag_json = (prev_map.get(pid, {}) or {}).get("cwe_output", [])
                    
                    
                    sec_guidelines = (prev_map.get(pid, {}) or {}).get(
                        "sec_guidelines", []
                    )
                    draft_code = (prev_map.get(pid, {}) or {}).get("draft_code", "")
                    # continue
                else:
                    ### 1) PLANNING PHASE
                    logging.info(
                        "\n=== Start prompt_id=%s (target CWE=%s) (lang=%s)",
                        pid,
                        target_cwe_num,
                        language,
                    )
                    self.reset_history()
                    entrypoint_code = None
                    if (
                        self.cfg.task == "cweval"
                        and "entrypoint_code" in row
                        and row["entrypoint_code"]
                    ):
                        entrypoint_code = row["entrypoint_code"]
                        question += (
                            f"\n\n### Reference Entrypoint (read-only)\nUse this to understand how your solution will be invoked. Do not make the entry\n```\n{entrypoint_code}\n```"
                            if entrypoint_code
                            else ""
                        )
                    temp = '\n'.join(action_header.split('\n')[:-1]) if "baxbench" not in self.cfg.task else ""
                    plan, plan_loop_step = self._get_plan(
                        pid, language, question + f"{temp}", self.preset_data
                    )
                    
                    row["plan_loop_step"] = plan_loop_step if plan_loop_step else 0
                    row["plan"] = plan if plan else ""
                    temp = question if question_ori is None else question_ori
                    problem_with_planning = (
                        f"{temp}\n\n{plan}\n" if self.cfg.with_plan else f"{temp}"
                    )
                    
                    ### Make Draft Code
                    draft_code = None
                    draft_code, early_stat, early_exit, precomputed_else = self._process_draft_code(
                        pid=pid,
                        row=row,
                        language=language,
                        question=question if question_ori is None else question_ori,
                        problem_with_planning=problem_with_planning,
                        action_header=action_header if action_header_ori is None else action_header_ori,
                        task=task,
                        plan=plan,
                        target_cwe_num=target_cwe_num,
                        entrypoint_code=entrypoint_code,
                        is_multi_file=is_multi_file
                    )
                    if self.cfg.with_analyze_draft_surface and early_exit:
                        row.update(early_stat)
                        total_results.append(row)
                        json.dump(
                            total_results,
                            open(os.path.join(output_path), "w"),
                            indent=4,
                        )
                        continue
                    
                    problem_with_planning = (
                        f"{question}\n\n{plan}\n" if self.cfg.with_plan else f"{question}"
                    )
                    ### Extract of CWE Groups
                    rag_json = []
                    if not self.cfg.only_plan and self.cfg.cwe_extract and pid not in self.rescue_guide_data:
                        if self.cfg.already_cwe and pid in self.preset_data:
                            rag_json = (self.preset_data.get(pid, {}) or {}).get(
                                "cwe_output", []
                            )
                            if len(rag_json) ==0:
                                logging.warning(
                                    "[GUIDE] No cwes found for prompt_id=%s",
                                    pid,
                                )
                                continue
                        else:
                            rag_json = self.extract_cwes(
                                language,
                                problem_with_planning,
                                self.cfg.max_cwe_limit,
                            )
                        if not rag_json:
                            rag_json = self.extract_cwes(
                                language,
                                problem_with_planning,
                                self.cfg.max_cwe_limit,
                            )

                c_cause, c_effect, extracted_clean, _, _ = self._extract_from_docs(
                    rag_json
                )
                idx_target = next(
                    (i for i, v in enumerate(extracted_clean) if v == target_cwe_num),
                    -1,
                )
                idx_related = next(
                    (i for i, v in enumerate(extracted_clean) if v in related_list), -1
                )
                if ("llmseceval" in task and pid not in EXCLUDE_LSE) or (
                    "llmseceval" not in task
                ):
                    cwe_total += 1
                    if idx_target >= 0:
                        cwe_hits += 1
                        cwe_rel_hits += 1
                    elif idx_related >= 0:
                        cwe_rel_hits += 1

                stat = OrderedDict(
                    target_cwe=target_cwe_num,
                    extracted_cwes=extracted_clean,
                    cwe_count=len(extracted_clean),
                    cwe_output=rag_json,
                    plan=plan,
                    sec_guidelines=sec_guidelines,
                    response=current_code,
                    draft_code=draft_code,
                )

                if current_code is None and not self.cfg.already_code:
                    if pid == -1:
                        logging.warning("Invalid prompt_id=%s, skipping", pid)
                        continue

                    ## Make security guidelines with RAG
                    already_validate_done = False
                    if self.cfg.with_sec_guide:
                        if self.cfg.already_sec_guide and pid in self.preset_data:
                            sec_guidelines = (self.preset_data.get(pid, {}) or {}).get(
                                "sec_guidelines", []
                            )
                            if len(sec_guidelines) == 0:
                                logging.warning(
                                    "[GUIDE] No security guidelines found for prompt_id=%s",
                                    pid,
                                )
                                continue
                            stat["sec_guidelines"] = sec_guidelines
                            
                            for _, sec in enumerate(sec_guidelines):
                                gr = sec.get("group_name")
                                if gr == "Reviewed":
                                    logging.warning(
                                        "[GUIDE] Found 'Reviewed' group in preset data for prompt_id=%s, skipping",
                                        pid,
                                    )
                                    already_validate_done = True
                                    break
                        else:
                            if self.cfg.already_rag and pid in self.preset_data:
                                sec_guidelines = (
                                    self.preset_data.get(pid, {}) or {}
                                ).get("sec_guidelines", [])
                            self.retriever = self.rag_manager.get_retriever(language)
                            temp = '\n'.join(action_header.split('\n')[:-1])
                            problem_with_planning = (
                                        f"{question}\n{temp}\n{plan}"
                                        if self.cfg.with_plan and plan
                                        else f"{question}"
                                    )
                            precomputed_snippets = None
                            if self.cfg.task == "cweval" and self.rescue_guide_data :
                                precomputed_snippets = self.rescue_guide_data.get(row["scenario"]+"_s0")
                                if precomputed_snippets is None:
                                    precomputed_snippets = self.rescue_guide_data.get(pid) or self.rescue_guide_data.get(int(pid)) or None
                                    if precomputed_snippets and "### Task:" in precomputed_snippets:
                                        precomputed_snippets = precomputed_snippets[precomputed_snippets.index("### Security Knowledge:"):precomputed_snippets.index("### Task:")]
                            sec_guidelines = self.make_security_guidelines_with_rag(
                                language=language,
                                problem_with_planning=problem_with_planning,
                                rag_json=rag_json,
                                retriever=self.retriever,
                                os_platform=self.os_platform,
                                sec_guidelines=sec_guidelines,
                                draft_code=draft_code,
                                task=task,
                                precomputed_else=None,
                                precomputed_snippets=precomputed_snippets,
                            )

                            logging.info(
                                "\n[GUIDE] built %d guideline groups",
                                len(sec_guidelines),
                            )
                            stat["sec_guidelines"] = sec_guidelines

                        ## Validate security guidelines
                        if (
                            not already_validate_done
                            and self.cfg.with_sec_guide_validate
                        ):
                            sec_guidelines, review_raw = (
                                self.validate_security_guidelines(
                                    pid=pid,
                                    language=language,
                                    question=question + f"\n{temp}",
                                    rag_json=rag_json,
                                    sec_guidelines=sec_guidelines,
                                    valid_with_rag_raq=False,
                                )
                            )
                            stat["sec_guidelines"] = sec_guidelines
                    else:
                        ## using rag_json (CWE extraction) to build basic security guidelines
                        sec_guidelines = [
                            {
                                "group_name": "Reviewed",
                                "guidelines": ", ".join(
                                    self._build_rag_queries(rag_json)
                                ),
                            }
                        ]
                ## Make Code
                if question_ori is not None : question = question_ori
                if action_header_ori is not None : action_header = action_header_ori
                if (self.cfg.only_direct or self.cfg.only_plan) and current_code is None:
                    problem_with_planning = f"{question}" if self.cfg.only_direct else f"{question}\n\n{plan}\n"
                    prompt, _, current_code = self.generate_code(
                        row,
                        language,
                        self.os_platform,
                        problem_with_planning,
                        action_header,
                        task,
                        "",
                        plan="",
                        is_multi_file=is_multi_file
                    )
                    stat["response"] = current_code
                    logging.info(f"\n[CODE_GEN] Generated code for prompt_id={pid} ")
                    logging.info(
                        f"\n[CODE_GEN] Code:\n{current_code}\n==== Finish Code Generation ===="
                    )

                elif not self.cfg.already_code and current_code is None:
                    security_req = self.build_security_requirements(sec_guidelines)
                    problem_with_planning = (
                        f"{question}\n\n{plan}" if self.cfg.with_plan else f"{question}"
                    )
                    if getattr(self.cfg, "with_pre_understand", False):
                        # self.reset_history()
                        self._pre_understand_code(
                            task_description=problem_with_planning,
                            security_requirements=security_req,
                        )
                    prompt, _, current_code = self.generate_code(
                        row,
                        language,
                        self.os_platform,
                        question,
                        action_header,
                        task,
                        security_req,
                        plan=plan,
                        is_multi_file=is_multi_file
                    )
                    logging.info(
                        f"\n[CODE_GEN] Prompt Start\n{prompt}\n==== FINISH CODE GEN PROMPT ===="
                    )
                    if not current_code:
                        current_code = ""
                    logging.info(f"\n[CODE_GEN] Generated code for prompt_id={pid} ")
                    logging.info(
                        f"\n[CODE_GEN] Code:\n{current_code}\n==== Finish Code Generation ===="
                    )
                elif self.cfg.already_code and current_code is None:
                    logging.info(f"\n[CODE_GEN] Using preset code for prompt_id={pid}")
                    current_code = str(
                        (self.preset_data.get(pid, {}) or {}).get("response", "")
                    )

                ### syntax error check
                if current_code:
                    stat["response"] = current_code
                elif draft_code:
                    stat["response"] = draft_code

                if (
                    not self.cfg.only_direct
                    and not self.cfg.only_plan
                    and current_code
                    and pid not in prev_map
                    and language.lower() not in ["go", "javascript", "php", "rust", "ruby"]
                    and not is_multi_file
                ):
                    current_code, compile_success = self.compilation_check_and_repair(
                        current_code,
                        task,
                        language,
                        question,
                        row,
                        entrypoint_code=entrypoint_code,
                    )
                    stat["response"] = current_code

                rows_used.add(pid)
                row.update(stat)
                total_results.append(row)
                json.dump(
                    total_results, open(os.path.join(output_path), "w"), indent=4
                )
                # break
            finally:
                if pid not in prev_map:
                    logging.info(
                        "[PHASE1] Task time: %.2f minutes | Total elapsed: %.2f minutes",
                        (time.time() - row_start_time) / 60,
                        (time.time() - start_time) / 60,
                    )
                detach_handler(pid_handler)

        json.dump(total_results, open(os.path.join(output_path), "w"), indent=4)
        if self.cfg.task.lower() == "humaneval":
            # Save as JSONL for human evaluation
            jsonl_path = os.path.splitext(str(output_path))[0] + ".jsonl"
            with open(jsonl_path, "w", encoding="utf-8") as f_jsonl:
                for item in total_results:
                    item["completion"] = item.get("response", "")
                    f_jsonl.write(json.dumps(item, ensure_ascii=False) + "\n")
            logging.info(f"[PHASE1] Also saved results as JSONL: {jsonl_path}")
        logging.info("\n[PHASE1] Done. saved: %s", output_path)
        logging.info(
            "[PHASE1] Total Time taken: %.2f minutes", (time.time() - start_time) / 60
        )
        if self._should_dump_usage():
            usage_path = self.out_dir / "_usage_phase1.json"
            summary_path = self.out_dir / "_total_usage_phase1.json"
            global_usage_tracker.to_json(usage_path)
            logging.info("[USAGE] Phase1 summary: %s", global_usage_tracker.summary())
            total_p1_cost = compute_cost(usage_path)
            with summary_path.open("w", encoding="utf-8") as f:
                # temp = global_usage_tracker.summary()
                summary = global_usage_tracker.summary()
                totals = {
                    "total_prompt_tokens": sum(
                        v.get("prompt_tokens", 0) for v in summary.values()
                    ),
                    "total_completion_tokens": sum(
                        v.get("completion_tokens", 0) for v in summary.values()
                    ),
                    "total_cached_prompt_tokens": sum(
                        v.get("cached_prompt_tokens", 0) for v in summary.values()
                    ),
                    "total_total_tokens": sum(
                        v.get("total_tokens", 0) for v in summary.values()
                    ),
                    "total_cost": total_p1_cost,
                }
                summary.update(totals)
                json.dump(summary, f, indent=2, ensure_ascii=False)

    def run_phase2(self) -> None:
        start_time = time.time()
        set_current_phase("phase2")
        task = self.cfg.task
        data, action_prompt_header, question_key = load_data(task, "none")
        data.sort(key=lambda x: x["prompt_id"])
        log_path = self._phase_paths["p2_log"]
        output_path = self._phase_paths["phase2"]
        setup_logging(log_path)
        logging.info("\n[EngineConfig]\n%s", config_to_str(self.cfg))
        logging.info("\nOutput: %s", output_path)
        total_results: List[Dict[str, Any]] = []

        rows_used = set()
        prev_map = self.prev_map_phase2
        base_rows = (
            self.prev_map_phase1 if not self.cfg.load_preset else self.preset_data
        )
        if not base_rows:
            logging.error("[PHASE2] No phase1 data. Abort.")
            return

        for row in data:
            pid, language, question, _, target_cwe_num = self._row_meta(
                row, question_key
            )
            pid_handler = attach_pid_log_handler(self.out_dir, pid, phase="phase2")

            is_multi_file = row.get("is_multi_file", False)
            if isinstance(action_prompt_header, list):
                action_header = action_prompt_header[1] if is_multi_file else action_prompt_header[0]
            else:
                action_header = action_prompt_header.format(language=language)
            task_start_time = time.time()
            try:
                entrypoint_code = None
                if (
                    self.cfg.task == "cweval"
                    and "entrypoint_code" in row
                    and row["entrypoint_code"]
                ):
                    entrypoint_code = row["entrypoint_code"]
                question = (
                    f"\n### Reference Entrypoint (read-only)\nUse this to understand how your solution will be invoked. Do not make the entry\n```\n{entrypoint_code}\n\n ###Problem \n{question}```"
                    if entrypoint_code
                    else question
                )

                current_code = None
                plan = None
                sec_guidelines = None
                if "task_file_path" in row:
                    logging.info(f"\n====Task file path: {row['task_file_path']}")
                if pid in prev_map:
                    row.update(prev_map[pid])
                    total_results.append(row)
                    logging.info("load previous data for prompt %s", pid)
                    current_code = prev_map[pid].get("response", None)
                    if current_code is not None:
                        continue

                base_row = base_rows.get(pid, {})
                current_code = base_row.get("response", None)
                draft_pass = base_row.get("draft_pass", False)
                draft_code = base_row.get("draft_code", "")
                if not current_code:
                    logging.warning("[PHASE2] pid=%s has no code; skip.", pid)
                    continue
                if draft_pass:
                    row["draft_pass"] = True
                    row["phase2_flow"] = []
                    row["response"] = current_code
                    total_results.append(row)
                    continue

                row["response"] = current_code
                rag_json = base_row.get("cwe_output", [])
                sec_guidelines = base_row.get("sec_guidelines", [])
                problem_with_planning = f"{question}\n\n{plan}".strip()
                logging.info(
                    "\n=== Start prompt_id=%s (target CWE=%s) (lang=%s)",
                    pid,
                    target_cwe_num,
                    language,
                )

                security_req = ""
                if not self.cfg.only_plan and self.cfg.with_sec_guide:
                    security_req = self.build_security_requirements(sec_guidelines)
                self.reset_history()
                prompts, outs, _ = self.generate_code(
                    row,
                    language,
                    self.os_platform,
                    problem_with_planning,
                    action_header,
                    task,
                    security_req,
                    not_invoke=True,
                    is_multi_file=is_multi_file
                )
                if not prompts or not outs:
                    logging.warning("[PHASE2] pid=%s has no valid history;", pid)
                else:
                    for step, (prompt, answer) in enumerate(zip(prompts, outs)):
                        history = get_limited_memory(self.shared_session_id_code_agent)
                        history.add_message(HumanMessage(content=prompt))
                        if not answer == "":
                            history.add_message(AIMessage(content=answer))
                        else:
                            if current_code is not None:
                                history.add_message(AIMessage(content=current_code))
                            else:
                                current_code = ""
                refined_code, did_refine, flow = self._run_phase2_pipeline(
                    row=row,
                    pid=pid,
                    language=language,
                    question=question,
                    code=current_code,
                    action_header=action_header,
                    task=task,
                    rag_json=rag_json,
                    security_req=security_req,
                    draft_code=draft_code,
                    is_multi_file=is_multi_file,
                )
                rows_used.add(pid)
                row["response"] = refined_code.strip()
                row["did_refine"] = did_refine
                row["phase2_flow"] = flow
                total_results.append(row)
                json.dump(
                    total_results, open(os.path.join(output_path), "w"), indent=4
                )
                logging.info(
                    f"\n==========[PHASE2] Finished prompt_id={pid}, saved intermediate results.============="
                )
            finally:
                logging.info(
                    "[PHASE2] Task time: %.2f minutes | Total elapsed: %.2f minutes",
                    (time.time() - task_start_time) / 60,
                    (time.time() - start_time) / 60,
                )
                detach_handler(pid_handler)

        json.dump(total_results, open(os.path.join(output_path), "w"), indent=4)
        if self.cfg.task.lower() == "humaneval":
            jsonl_path = os.path.splitext(str(output_path))[0] + ".jsonl"
            with open(jsonl_path, "w", encoding="utf-8") as f_jsonl:
                for item in total_results:
                    item["completion"] = item.get("response", "")
                    f_jsonl.write(json.dumps(item, ensure_ascii=False) + "\n")
        logging.info("\n[PHASE2] Done. saved: %s", output_path)

        if self._should_dump_usage():
            usage_path = self.out_dir / "_usage_phase2.json"
            summary_path = self.out_dir / "_total_usage_phase2.json"
            global_usage_tracker.to_json(usage_path)
            logging.info("[USAGE] Phase1 summary: %s", global_usage_tracker.summary())
            total_p1_cost = compute_cost(usage_path)
            with summary_path.open("w", encoding="utf-8") as f:
                # temp = global_usage_tracker.summary()
                summary = global_usage_tracker.summary()
                totals = {
                    "total_prompt_tokens": sum(
                        v.get("prompt_tokens", 0) for v in summary.values()
                    ),
                    "total_completion_tokens": sum(
                        v.get("completion_tokens", 0) for v in summary.values()
                    ),
                    "total_cached_prompt_tokens": sum(
                        v.get("cached_prompt_tokens", 0) for v in summary.values()
                    ),
                    "total_total_tokens": sum(
                        v.get("total_tokens", 0) for v in summary.values()
                    ),
                    "total_cost": total_p1_cost,
                }
                summary.update(totals)
                json.dump(summary, f, indent=2, ensure_ascii=False)