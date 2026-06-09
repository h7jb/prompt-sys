"""Built-in prompt catalog with categorized examples and templates."""

from typing import List, Dict
from .storage import PromptEntry

BUILTIN_PROMPTS: List[dict] = [
    {
        "title": "Code Review Prompt",
        "content": "You are a senior software engineer conducting a code review.\nReview the following code for:\n- Bugs and logic errors\n- Performance issues\n- Security vulnerabilities\n- Code style and best practices\n- Missing edge cases\n\nProvide a structured report with severity levels for each finding.",
        "category": "coding",
        "tags": ["code-review", "programming", "best-practices"],
        "language": "en",
    },
    {
        "title": "Academic Writing Assistant",
        "content": "أنت كاتب أكاديمي محترف. ساعدني في كتابة {type} حول موضوع {topic}.\n\nالمتطلبات:\n- أسلوب أكاديمي رسمي\n- توثيق المراجع بطريقة APA\n- مقدمة وخاتمة واضحتين\n- تقسيم إلى أقسام منطقية\n- لغة عربية فصحى\n\nالجمهور المستهدف: {audience}\nعدد الكلمات التقريبي: {word_count}",
        "category": "writing",
        "tags": ["academic", "writing", "arabic", "research"],
        "language": "ar",
    },
    {
        "title": "Marketing Strategy Generator",
        "content": "You are a senior marketing strategist specializing in {industry}.\n\nCreate a comprehensive marketing strategy for:\nProduct/Service: {product}\nTarget Audience: {audience}\nBudget: {budget}\nTimeline: {timeline}\n\nInclude:\n1. Market analysis (SWOT)\n2. 3 marketing channels with rationale\n3. Content strategy for 30 days\n4. KPIs and success metrics\n5. Budget allocation recommendation\n\nFormat as a structured report with executive summary.",
        "category": "marketing",
        "tags": ["marketing", "strategy", "business"],
        "language": "en",
    },
    {
        "title": "Data Analysis Prompt",
        "content": "You are a data analyst expert. Analyze the following dataset/request:\n{data_description}\n\nProvide:\n1. Summary statistics\n2. Key insights and patterns\n3. Visualizations recommendations\n4. Actionable recommendations\n5. Limitations and caveats\n\nUse plain language suitable for {audience}.",
        "category": "analysis",
        "tags": ["data", "analysis", "analytics"],
        "language": "en",
    },
    {
        "title": "مصمم واجهات المستخدم",
        "content": "أنت مصمم واجهات مستخدم (UI/UX) محترف.\n\nصمم تصوراً كاملاً لـ {project_type} الخاص بـ {project_name}.\n\nالمتطلبات:\n- تحليل المستخدمين المستهدفين\n- هيكل التنقل الرئيسي\n- تصميم 3 شاشات رئيسية على الأقل\n- نظام الألوان والخطوط\n- نقاط التفاعل الرئيسية\n- قائمة التحقق لتجربة المستخدم\n\nالجمهور: {audience}\nالمنصة: {platform}",
        "category": "creative",
        "tags": ["ui-ux", "design", "arabic", "interface"],
        "language": "ar",
    },
    {
        "title": "Lesson Plan Creator",
        "content": "You are an experienced educator creating a lesson plan.\n\nTopic: {topic}\nGrade Level: {grade_level}\nDuration: {duration}\nClass Size: {class_size}\n\nCreate:\n1. Learning objectives (Bloom's taxonomy)\n2. Materials needed\n3. Lesson structure with timing\n4. Activities and assessments\n5. Differentiation strategies\n6. Homework assignment\n\nInclude engagement strategies and assessment criteria.",
        "category": "education",
        "tags": ["education", "teaching", "lesson-plan"],
        "language": "en",
    },
    {
        "title": "Business Plan Generator",
        "content": "You are a business consultant helping a startup create a business plan.\n\nBusiness Idea: {idea}\nIndustry: {industry}\nStage: {stage}\nFunding Goal: {funding_goal}\n\nCreate a professional business plan covering:\n1. Executive Summary\n2. Company Description\n3. Market Analysis\n4. Organization & Management\n5. Products & Services\n6. Marketing & Sales\n7. Financial Projections\n8. Funding Request\n9. Appendix\n\nUse realistic data and industry benchmarks.",
        "category": "business",
        "tags": ["business", "startup", "planning"],
        "language": "en",
    },
    {
        "title": "Technical Documentation Writer",
        "content": "You are a technical writer creating documentation for {project}.\n\nAudience: {audience}\nComplexity Level: {level}\n\nCreate:\n1. Overview and architecture\n2. Setup and installation guide\n3. API reference (with examples)\n4. Configuration options\n5. Troubleshooting guide\n6. FAQ\n\nUse clear, concise language with code examples where applicable.",
        "category": "technical",
        "tags": ["documentation", "technical", "writing"],
        "language": "en",
    },
]


def get_builtin_categories() -> List[str]:
    """Return all available categories from built-in prompts."""
    cats: set = set()
    for p in BUILTIN_PROMPTS:
        cats.add(p["category"])
    return sorted(cats)


def get_builtin_by_category(category: str) -> List[PromptEntry]:
    """Get built-in prompts filtered by category."""
    return [
        PromptEntry.from_dict(p)
        for p in BUILTIN_PROMPTS
        if p["category"] == category
    ]


def seed_library(library: "PromptLibrary") -> None:
    """Seed a library with built-in prompts if it's empty."""
    if library.count == 0:
        for p_data in BUILTIN_PROMPTS:
            entry = PromptEntry.from_dict(p_data)
            library.add(entry)
