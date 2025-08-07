from datetime import datetime
from loguru import logger
from models.types import CodeReviewState
from core.llm_service import LLMService
from core.prompt_service import PromptService
import json
from langgraph.graph import StateGraph, END

class CodeReviewAgent:
    """Agent class for managing code reviews with RAG support using agent architecture."""

    def __init__(self, llm_service: LLMService = None, prompt_service: PromptService = None):
        logger.info("Initializing Code Review Service")
        self.llm_service = llm_service or LLMService()
        self.prompt_service = prompt_service or PromptService()
        logger.success("Code Review Service initialized successfully")

    async def parse_code_input(self, state: CodeReviewState) -> CodeReviewState:
        logger.info(f"Parsing code input - Language: {state.get('language')}, File type: {state.get('file_type')}")
        start_time = datetime.now()
        
        code = state["code"]
        language = state["language"]
        file_type = state["file_type"]

        logger.debug(f"Code length: {len(code)} characters")

        if not code or len(code) > 50000:
            logger.error(f"Invalid code input: length={len(code)}")
            raise ValueError("Invalid code input: empty or too large (max 50,000 characters).")
        if language not in ["python", "javascript"]:
            logger.error(f"Unsupported language: {language}")
            raise ValueError("Unsupported programming language.")
        if file_type not in ["py", "js"]:
            logger.error(f"Unsupported file type: {file_type}")
            raise ValueError("Unsupported file type.")

        processing_time = (datetime.now() - start_time).total_seconds()
        state["processing_time"] = processing_time
        logger.success(f"Code input parsed successfully in {processing_time:.3f}s")
        return state

    async def analyze_syntax_style(self, state: CodeReviewState) -> CodeReviewState:
        logger.info("Starting syntax and style analysis")
        try:
            # Syntax analysis
            syntax_prompt_str = self.prompt_service.get_syntax_prompt(state["code"], state["language"])
            syntax_response = await self.llm_service.model.ainvoke(syntax_prompt_str)
            
            syntax_content = syntax_response.content if hasattr(syntax_response, 'content') else str(syntax_response)
            syntax_result = self.llm_service.extract_json_from_response(syntax_content)
            state["syntax_issues"] = syntax_result.get("issues", [])

            # Style analysis
            format_prompt_str = self.prompt_service.get_style_prompt(state["code"], state["language"])
            format_response = await self.llm_service.model.ainvoke(format_prompt_str)
            
            format_content = format_response.content if hasattr(format_response, 'content') else str(format_response)
            format_result = self.llm_service.extract_json_from_response(format_content)
            state["style_violations"] = format_result.get("issues", [])

            # Comment quality analysis
            comment_prompt_str = self.prompt_service.get_comment_quality_prompt(state["code"], state["language"])
            comment_response = await self.llm_service.model.ainvoke(comment_prompt_str)
            
            comment_content = comment_response.content if hasattr(comment_response, 'content') else str(comment_response)
            comment_result = self.llm_service.extract_json_from_response(comment_content)
            
            if state.get("style_violations") is None:
                state["style_violations"] = []
            state["style_violations"].extend(comment_result.get("issues", []))

        except Exception as e:
            logger.error(f"Error in syntax/style analysis: {e}", exc_info=True)
            state["syntax_issues"] = [{"error": f"Syntax analysis failed: {str(e)}"}]
            state["style_violations"] = [{"error": f"Style analysis failed: {str(e)}"}]
        
        return state

    async def security_scan(self, state: CodeReviewState) -> CodeReviewState:
        logger.info("Starting security vulnerability scan")
        try:
            prompt_str = self.prompt_service.get_security_prompt(state["code"], state["language"])
            response = await self.llm_service.model.ainvoke(prompt_str)
            
            content = response.content if hasattr(response, 'content') else str(response)
            result = self.llm_service.extract_json_from_response(content)
            state["security_vulnerabilities"] = result.get("vulnerabilities", [])
            
        except Exception as e:
            logger.error(f"Error in security scan: {e}", exc_info=True)
            state["security_vulnerabilities"] = [{"error": f"Security scan failed: {str(e)}"}]
        
        return state

    async def performance_analysis(self, state: CodeReviewState) -> CodeReviewState:
        logger.info("Starting performance analysis")
        state["performance_issues"] = []
        
        try:
            prompt_str = self.prompt_service.get_performance_prompt(state["code"], state["language"])
            response = await self.llm_service.model.ainvoke(prompt_str)
            
            content = response.content if hasattr(response, 'content') else str(response)
            result = self.llm_service.extract_json_from_response(content)
            
            issues = result.get("issues", [])
            state["performance_issues"] = issues
                    
        except Exception as e:
            logger.error(f"Error in performance analysis: {e}", exc_info=True)
            state["performance_issues"] = [{"error": f"Performance analysis failed: {str(e)}"}]
        
        return state

    async def best_practices_check(self, state: CodeReviewState) -> CodeReviewState:
        logger.info("Starting best practices check")
        try:
            prompt_str = self.prompt_service.get_best_practices_prompt(state["code"], state["language"])
            response = await self.llm_service.model.ainvoke(prompt_str)
            
            content = response.content if hasattr(response, 'content') else str(response)
            result = self.llm_service.extract_json_from_response(content)
            state["best_practice_violations"] = result.get("issues", [])
            
        except Exception as e:
            logger.error(f"Error in best practices check: {e}", exc_info=True)
            state["best_practice_violations"] = [{"error": f"Best practices check failed: {str(e)}"}]
        
        # Calculate severity level
        total_issues = (
            len([x for x in (state.get("syntax_issues") or []) if not x.get("error")]) +
            len([x for x in (state.get("security_vulnerabilities") or []) if not x.get("error")]) +
            len([x for x in (state.get("performance_issues") or []) if not x.get("error")]) +
            len([x for x in (state.get("style_violations") or []) if not x.get("error")]) +
            len([x for x in (state.get("best_practice_violations") or []) if not x.get("error")])
        )
        
        if total_issues >= 10:
            state["severity_level"] = "critical"
        elif total_issues >= 5:
            state["severity_level"] = "high"
        elif total_issues >= 2:
            state["severity_level"] = "medium"
        else:
            state["severity_level"] = "low"
            
        return state

    async def generate_explanations(self, state: CodeReviewState) -> CodeReviewState:
        logger.info("Generating explanations and suggestions")
        try:
            issues = json.dumps({
                "syntax": state.get("syntax_issues", []),
                "security": state.get("security_vulnerabilities", []),
                "performance": state.get("performance_issues", []),
                "style": state.get("style_violations", []),
                "best_practices": state.get("best_practice_violations", [])
            })

            prompt_str = self.prompt_service.get_explanation_prompt(state["code"][:500], state["language"])

            response = await self.llm_service.model.ainvoke(prompt_str)
            content = response.content if hasattr(response, 'content') else str(response)
            result = self.llm_service.extract_json_from_response(content)
            
            state["explanations"] = result.get("explanations", [])
            state["improvement_suggestions"] = result.get("suggestions", [])
            state["learning_resources"] = result.get("resources", [])
            
        except Exception as e:
            logger.error(f"Error generating explanations: {e}", exc_info=True)
            state["explanations"] = [{"error": str(e)}]
            state["improvement_suggestions"] = []
            state["learning_resources"] = []
        
        return state

    async def generate_final_report(self, state: CodeReviewState) -> CodeReviewState:
        state["requires_human_review"] = state.get("severity_level") in ["high", "critical"]
        state["analysis_complete"] = True
        return state

    async def human_escalation(self, state: CodeReviewState) -> CodeReviewState:
        state["requires_human_review"] = True
        return state

    async def detailed_analysis(self, state: CodeReviewState) -> CodeReviewState:
        return state

    async def route_by_severity(self, state: CodeReviewState) -> str:
        severity = state.get("severity_level", "low")
        if severity == "critical":
            return "human_escalation"
        elif severity == "high":
            return "detailed_analysis"
        else:
            return "educational_content"

    async def build_agent(self):
        logger.info("Building code review workflow graph")
        workflow = StateGraph(CodeReviewState)
        workflow.add_node("parse_input", self.parse_code_input)
        workflow.add_node("syntax_analysis", self.analyze_syntax_style)
        workflow.add_node("security_scan", self.security_scan)
        workflow.add_node("performance_check", self.performance_analysis)
        workflow.add_node("best_practices", self.best_practices_check)
        workflow.add_node("generate_report", self.generate_final_report)
        workflow.add_node("educational_content", self.generate_explanations)
        workflow.add_node("human_escalation", self.human_escalation)
        workflow.add_node("detailed_analysis", self.detailed_analysis)

        workflow.add_edge("parse_input", "syntax_analysis")
        workflow.add_edge("syntax_analysis", "security_scan")
        workflow.add_edge("security_scan", "performance_check")
        workflow.add_edge("performance_check", "best_practices")

        workflow.add_conditional_edges(
            "best_practices",
            self.route_by_severity,
            {
                "human_escalation": "human_escalation",
                "detailed_analysis": "detailed_analysis", 
                "educational_content": "educational_content"
            }
        )

        workflow.add_edge("detailed_analysis", "educational_content")
        workflow.add_edge("human_escalation", "educational_content")
        workflow.add_edge("educational_content", "generate_report")
        workflow.add_edge("generate_report", END)

        workflow.set_entry_point("parse_input")
        compiled_workflow = workflow.compile()
        logger.success("Code review workflow compiled successfully")
        return compiled_workflow

    async def invoke(self, state: CodeReviewState) -> CodeReviewState:
        """Public method to analyze code using the agent workflow."""
        logger.info("Starting code analysis")
        try:
            # Build and execute the workflow
            workflow = await self.build_agent()
            result = await workflow.ainvoke(state)
            logger.success("Code analysis completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error in code analysis: {e}", exc_info=True)
            # Return error state
            return {
                **state,
                "analysis_complete": True,
                "severity_level": "error",
                "requires_human_review": True,
                "syntax_issues": [{"error": f"Analysis failed: {str(e)}"}],
                "security_vulnerabilities": [],
                "performance_issues": [],
                "style_violations": [],
                "best_practice_violations": [],
                "explanations": [],
                "improvement_suggestions": [],
                "learning_resources": []
            }
