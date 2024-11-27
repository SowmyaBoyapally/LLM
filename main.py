import os
import re
import openai
import subprocess
from typing import List, Dict, Any

class AICodeReviewer:
    def __init__(self, openai_api_key: str):
        openai.api_key = openai_api_key
        self.model = "gpt-4-turbo"
    
    def extract_code_changes(self, git_diff_output: str) -> List[Dict[str, Any]]:
        """
        Extract code changes from git diff output
        """
        changes = []
        current_file = None
        for line in git_diff_output.split('\n'):
            file_match = re.match(r'\+\+\+ b/(.+)', line)
            if file_match:
                current_file = file_match.group(1)
            
            if line.startswith('+') and not line.startswith('+++'):
                changes.append({
                    'file': current_file,
                    'line_content': line[1:].strip()
                })
        
        return changes
    
    def analyze_code_changes(self, changes: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Use OpenAI to analyze code changes and provide review suggestions
        """
        review_suggestions = []
        
        for change in changes:
            prompt = f"""
            Analyze the following code change in {change['file']}:
            ```
            {change['line_content']}
            ```
            
            Provide specific feedback on:
            1. Potential bugs or code quality issues
            2. Performance concerns
            3. Security vulnerabilities
            4. Best practices and improvements
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            suggestion = response.choices[0].message.content
            review_suggestions.append({
                'file': change['file'],
                'suggestion': suggestion
            })
        
        return review_suggestions
    
    def generate_review_report(self, suggestions: List[Dict[str, str]]) -> str:
        """
        Generate a comprehensive code review report
        """
        report = "# AI Code Review Report\n\n"
        
        for item in suggestions:
            report += f"## File: {item['file']}\n"
            report += f"{item['suggestion']}\n\n"
        
        return report
    
    def run_review(self, repo_path: str) -> str:
        """
        Orchestrate the entire code review process
        """
        # Change to repository directory
        os.chdir(repo_path)
        
        # Get git diff for uncommitted changes
        git_diff = subprocess.check_output(['git', 'diff']).decode('utf-8')
        
        # Extract and analyze changes
        code_changes = self.extract_code_changes(git_diff)
        review_suggestions = self.analyze_code_changes(code_changes)
        
        # Generate report
        review_report = self.generate_review_report(review_suggestions)
        
        return review_report

# Example usage
def main():
    openai_api_key = os.getenv('OPENAI_API_KEY')
    reviewer = AICodeReviewer(openai_api_key)
    
    repo_path = '/path/to/your/repository'
    review_report = reviewer.run_review(repo_path)
    
    print(review_report)
    
    # Optional: Save report to file
    with open('code_review_report.md', 'w') as f:
        f.write(review_report)

if __name__ == '__main__':
    main()