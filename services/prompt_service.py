from langchain.prompts import PromptTemplate


class PromptService:
    def __init__(self):
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Initialize all prompt templates."""
        self.syntax_prompt = PromptTemplate.from_template(
            """You are a code analysis expert. Analyze the following {language} code for syntax errors.

Code to analyze:
```{language}
{code}
```

Return your response as a valid JSON object in this exact format:
{{"errors": [{{"line": <int>, "error": "<string>", "severity": "<string>"}}]}}

If no syntax errors are found, return: {{"errors": []}}

JSON Response:"""
        )

        self.format_prompt = PromptTemplate.from_template(
            """You are a code style expert. Check the following {language} code for style violations.

Code to analyze:
```{language}
{code}
```

Return your response as a valid JSON object in this exact format:
{{"style_violations": [{{"line": <int>, "violation": "<string>", "suggestion": "<string>"}}]}}

If no style violations are found, return: {{"style_violations": []}}

JSON Response:"""
        )

        self.comment_quality_prompt = PromptTemplate.from_template(
            """You are a code documentation expert. Evaluate the comment quality in this {language} code.

Code to analyze:
```{language}
{code}
```

Return your response as a valid JSON object in this exact format:
{{"issues": [{{"line": <int>, "issue": "<string>", "suggestion": "<string>"}}]}}

If no comment issues are found, return: {{"issues": []}}

JSON Response:"""
        )

        self.security_scan_prompt = PromptTemplate.from_template(
            """You are a security expert. Perform a security scan on the following {language} code.

Code to analyze:
```{language}
{code}
```

Return your response as a valid JSON object in this exact format:
{{"issues": [{{"line": <int>, "vulnerability": "<string>", "severity": "<string>", "recommendation": "<string>"}}]}}

If no security issues are found, return: {{"issues": []}}

JSON Response:"""
        )

        self.performance_prompt = PromptTemplate.from_template(
            """You are a performance optimization expert. Analyze this {language} code for performance issues related to {aspect}.

Code to analyze:
```{language}
{code}
```

Return your response as a valid JSON object in this exact format:
{{"issues": [{{"line": <int>, "issue": "<string>", "impact": "<string>", "solution": "<string>"}}]}}

If no performance issues are found, return: {{"issues": []}}

JSON Response:"""
        )

        self.best_practices_prompt = PromptTemplate.from_template(
            """You are a software engineering expert. Check the following {language} code for violations of best practices.

Code to analyze:
```{language}
{code}
```

Return your response as a valid JSON object in this exact format:
{{"violations": [{{"line": <int>, "violation": "<string>", "principle": "<string>", "improvement": "<string>"}}]}}

If no best practice violations are found, return: {{"violations": []}}

JSON Response:"""
        )

        self.explanation_prompt = PromptTemplate.from_template(
            """You are a code education expert. Based on the code review findings, provide educational explanations and improvement suggestions.

Language: {language}
Code: {code}
Issues found: {issues}

Return your response as a valid JSON object in this exact format:
{{
    "explanations": [{{"topic": "<string>", "explanation": "<string>"}}],
    "suggestions": [{{"priority": "<string>", "suggestion": "<string>", "rationale": "<string>"}}],
    "resources": ["<string>"]
}}

If no explanations needed, return: {{"explanations": [], "suggestions": [], "resources": []}}

JSON Response:"""
        )