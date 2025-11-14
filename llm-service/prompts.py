"""Prompt templates for LLM tasks."""

REPO_SUMMARY_PROMPT = """Analyze the following GitHub repository and provide a comprehensive summary.

Repository Information:
- Name: {name}
- Owner: {owner}
- Description: {description}
- Languages: {languages}
- Topics: {topics}
- Stars: {stars}
- README (first 2000 chars): {readme_preview}

Please provide a JSON response with the following structure:
{{
    "summary": "A 100-200 word summary of what this repository does, its purpose, and key features.",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8"],
    "category": "One primary category (e.g., 'Machine Learning', 'Web Framework', 'Developer Tools', 'Data Science', 'Game Engine', etc.)",
    "skill_level": "beginner|intermediate|advanced|expert",
    "skill_level_numeric": 1-10,
    "project_health": "excellent|good|moderate|poor|abandoned",
    "project_health_score": 0.0-1.0,
    "use_cases": ["use case 1", "use case 2", "use case 3"]
}}

Guidelines:
- Tags should be specific, relevant, and diverse (5-12 tags)
- Category should be a single, clear category
- Skill level should reflect the complexity of understanding/contributing to the project
- Project health should consider: recent activity, documentation quality, community engagement, issue resolution
- Use cases should be practical, real-world applications
- Be objective and accurate based on the provided information
"""

BOARD_NAME_PROMPT = """Given a cluster of GitHub repositories with the following characteristics:

Repositories: {repo_names}
Categories: {categories}
Tags: {common_tags}
Average Stars: {avg_stars}

Generate a concise, descriptive board name (2-5 words) and description (1-2 sentences) for this curated collection.

Return JSON:
{{
    "name": "Board Name",
    "description": "A brief description of what this board contains and why these repos are grouped together."
}}
"""

CLUSTER_ANALYSIS_PROMPT = """Analyze the following cluster of repositories and provide insights:

Repositories: {repo_list}

Provide:
1. Common themes
2. Shared technologies
3. Target audience
4. Recommended board name
5. Board description

Return as JSON with the above fields.
"""

