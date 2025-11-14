"""LLM client for generating summaries and analysis."""

import sys
import os
import json
from typing import Dict, Any, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import settings
from llm_service.prompts import REPO_SUMMARY_PROMPT, BOARD_NAME_PROMPT


class LLMClient:
    """Client for LLM operations."""
    
    def __init__(self):
        self.provider = settings.llm_provider
        
        if self.provider == "openai":
            try:
                import openai
                self.client = openai.OpenAI(api_key=settings.openai_api_key)
                self.model = "gpt-4o-mini"
            except ImportError:
                raise ImportError("openai package required. Install with: pip install openai")
        elif self.provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
                self.model = "claude-3-haiku-20240307"
            except ImportError:
                raise ImportError("anthropic package required. Install with: pip install anthropic")
        elif self.provider == "ollama":
            self.base_url = settings.ollama_base_url
            self.model = "llama3"
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _call_openai(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call OpenAI API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content
    
    def _call_anthropic(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call Anthropic API."""
        system = system_prompt or "You are a helpful assistant that analyzes GitHub repositories."
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=system,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def _call_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call Ollama API."""
        import requests
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()["response"]
    
    def _call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call the configured LLM provider."""
        if self.provider == "openai":
            return self._call_openai(prompt, system_prompt)
        elif self.provider == "anthropic":
            return self._call_anthropic(prompt, system_prompt)
        elif self.provider == "ollama":
            return self._call_ollama(prompt, system_prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def generate_repo_summary(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary, tags, and analysis for a repository."""
        prompt = REPO_SUMMARY_PROMPT.format(
            name=repo_data.get("name", ""),
            owner=repo_data.get("owner", ""),
            description=repo_data.get("description", "No description"),
            languages=", ".join(list(repo_data.get("languages", {}).keys())[:5]),
            topics=", ".join(repo_data.get("topics", [])[:10]),
            stars=repo_data.get("stars", 0),
            readme_preview=(repo_data.get("readme", "") or "")[:2000]
        )
        
        system_prompt = "You are an expert at analyzing GitHub repositories. Provide accurate, objective analysis in JSON format."
        
        try:
            response = self._call_llm(prompt, system_prompt)
            # Try to extract JSON from response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            result = json.loads(response)
            return result
        except Exception as e:
            print(f"Error generating summary: {e}")
            # Return default values
            return {
                "summary": f"{repo_data.get('description', 'A GitHub repository')}",
                "tags": repo_data.get("topics", [])[:8] or ["github", "open-source"],
                "category": "Other",
                "skill_level": "intermediate",
                "skill_level_numeric": 5,
                "project_health": "good",
                "project_health_score": 0.7,
                "use_cases": []
            }
    
    def generate_board_name(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate board name and description for a cluster."""
        prompt = BOARD_NAME_PROMPT.format(
            repo_names=", ".join(cluster_data.get("repo_names", [])[:10]),
            categories=", ".join(set(cluster_data.get("categories", []))),
            common_tags=", ".join(cluster_data.get("common_tags", [])[:15]),
            avg_stars=cluster_data.get("avg_stars", 0)
        )
        
        system_prompt = "You are an expert at creating concise, descriptive names for curated collections of repositories."
        
        try:
            response = self._call_llm(prompt, system_prompt)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            result = json.loads(response)
            return result
        except Exception as e:
            print(f"Error generating board name: {e}")
            return {
                "name": "Curated Collection",
                "description": "A collection of related repositories."
            }

