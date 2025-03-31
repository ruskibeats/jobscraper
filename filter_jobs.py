#!/usr/bin/env python3
"""
Script to filter and rank job search results using an LLM.

This script takes a CSV file of job search results and uses an LLM to:
1. Filter out irrelevant jobs
2. Rank jobs by relevance to the search query
3. Save the filtered and ranked results to a new CSV file

Example usage:
    python filter_jobs.py --input jobs.csv --output filtered_jobs.csv --query "Project Manager" --api-key "your-openai-api-key"
"""

import os
import sys
import argparse
import pandas as pd
import json
import requests
from typing import List, Dict, Any, Optional

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Filter and rank job search results using an LLM.')
    
    # Required arguments
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    parser.add_argument('--query', required=True, help='Search query (e.g., "Project Manager")')
    
    # Optional arguments
    parser.add_argument('--api-key', help='OpenAI API key (if not provided, will use OPENAI_API_KEY environment variable)')
    parser.add_argument('--model', default='gpt-3.5-turbo', help='OpenAI model to use')
    parser.add_argument('--min-score', type=float, default=0.7, help='Minimum relevance score (0-1) to include a job')
    parser.add_argument('--limit', type=int, default=50, help='Maximum number of jobs to include in the output')
    
    return parser.parse_args()

def call_llm_api(api_key: str, model: str, messages: List[Dict[str, str]], temperature: float = 0.0) -> Dict[str, Any]:
    """
    Call either OpenAI API or OpenRouter API with the given messages.
    
    Args:
        api_key: API key (OpenAI or OpenRouter)
        model: Model to use
        messages: List of message dictionaries
        temperature: Temperature parameter for the API call
        
    Returns:
        API response as a dictionary
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature
    }
    
    # Determine which API to use based on the API key prefix
    if api_key.startswith("sk-or-"):
        # OpenRouter API
        url = "https://openrouter.ai/api/v1/chat/completions"
        # Add OpenRouter specific headers
        headers["HTTP-Referer"] = "https://jobspy.ai"
        headers["X-Title"] = "JobSpy"
    else:
        # OpenAI API
        url = "https://api.openai.com/v1/chat/completions"
    
    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(data)
    )
    
    if response.status_code != 200:
        raise Exception(f"API call failed with status code {response.status_code}: {response.text}")
    
    return response.json()

def evaluate_job_relevance(job: Dict[str, Any], query: str, api_key: str, model: str) -> Dict[str, Any]:
    """
    Evaluate the relevance of a job to the search query using an LLM.
    
    Args:
        job: Job data as a dictionary
        query: Search query
        api_key: OpenAI API key
        model: OpenAI model to use
        
    Returns:
        Dictionary with relevance score and explanation
    """
    # Prepare job data for the LLM
    job_description = f"""
    Title: {job.get('title', 'N/A')}
    Company: {job.get('company', 'N/A')}
    Location: {job.get('location', 'N/A')}
    Job Type: {job.get('job_type', 'N/A')}
    Description: {job.get('description', 'N/A')}
    """
    
    # Prepare the prompt
    messages = [
        {"role": "system", "content": f"""
        You are a job search assistant that evaluates the relevance of job postings to a user's search query.
        You will be given a job posting and a search query, and you need to:
        1. Evaluate how relevant the job is to the search query on a scale of 0 to 1 (where 1 is perfectly relevant)
        2. Provide a brief explanation for your score
        
        Return your response in the following JSON format:
        {{
            "score": 0.85,  # A float between 0 and 1
            "explanation": "This job is highly relevant because..."  # A brief explanation
        }}
        """},
        {"role": "user", "content": f"""
        Search Query: {query}
        
        Job Posting:
        {job_description}
        
        Evaluate the relevance of this job to the search query.
        """}
    ]
    
    # Call the LLM API
    response = call_llm_api(api_key, model, messages)
    
    # Parse the response
    try:
        content = response["choices"][0]["message"]["content"]
        # Extract the JSON part from the response
        json_str = content
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].strip()
        
        result = json.loads(json_str)
        return result
    except Exception as e:
        print(f"Error parsing API response: {e}")
        print(f"Response content: {response}")
        return {"score": 0.0, "explanation": f"Error: {e}"}

def filter_and_rank_jobs(input_file: str, output_file: str, query: str, api_key: str, model: str, min_score: float, limit: int):
    """
    Filter and rank jobs from the input CSV file and save the results to the output CSV file.
    
    Args:
        input_file: Input CSV file path
        output_file: Output CSV file path
        query: Search query
        api_key: OpenAI API key
        model: OpenAI model to use
        min_score: Minimum relevance score to include a job
        limit: Maximum number of jobs to include in the output
    """
    # Read the input CSV file
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    # Check if the dataframe is empty
    if df.empty:
        print("Input file is empty.")
        sys.exit(1)
    
    print(f"Read {len(df)} jobs from {input_file}")
    print(f"Filtering and ranking jobs for query: {query}")
    
    # Evaluate each job
    results = []
    for i, row in df.iterrows():
        print(f"Evaluating job {i+1}/{len(df)}: {row.get('title', 'N/A')}")
        
        # Convert row to dictionary
        job = row.to_dict()
        
        # Evaluate job relevance
        evaluation = evaluate_job_relevance(job, query, api_key, model)
        
        # Add evaluation to job data
        job["relevance_score"] = evaluation.get("score", 0.0)
        job["relevance_explanation"] = evaluation.get("explanation", "")
        
        # Add to results if score is above threshold
        if job["relevance_score"] >= min_score:
            results.append(job)
    
    # Sort results by relevance score (descending)
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    # Limit the number of results
    if limit > 0 and len(results) > limit:
        results = results[:limit]
    
    # Convert results to dataframe
    output_df = pd.DataFrame(results)
    
    # Save to output CSV file
    output_df.to_csv(output_file, index=False)
    
    print(f"Filtered {len(df)} jobs down to {len(results)} relevant jobs")
    print(f"Results saved to {output_file}")

def main():
    """Main function."""
    args = parse_arguments()
    
    # Get API key from arguments or environment variables
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: API key not provided. Use --api-key or set the OPENAI_API_KEY or OPENROUTER_API_KEY environment variable.")
        sys.exit(1)
    
    # Filter and rank jobs
    filter_and_rank_jobs(
        input_file=args.input,
        output_file=args.output,
        query=args.query,
        api_key=api_key,
        model=args.model,
        min_score=args.min_score,
        limit=args.limit
    )

if __name__ == "__main__":
    main()
