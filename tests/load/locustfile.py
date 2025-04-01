"""
Load testing script for the job search API.

This module contains a Locust load testing script for the job search API,
simulating various user behaviors and measuring performance.
"""

from locust import HttpUser, task, between
import json
import random

class JobSearchUser(HttpUser):
    """
    Simulated user for load testing the job search API.
    
    This class defines various tasks that simulate real user behavior,
    such as searching for jobs, checking task status, and viewing the dashboard.
    """
    
    # Wait between 1-5 seconds between tasks
    wait_time = between(1, 5)
    
    # Store task IDs for status checking
    task_ids = []
    
    # Job search parameters
    job_titles = [
        "Software Engineer",
        "Data Scientist",
        "Product Manager",
        "DevOps Engineer",
        "Frontend Developer",
        "Backend Developer",
        "Full Stack Developer",
        "Machine Learning Engineer",
        "UX Designer",
        "Business Analyst"
    ]
    
    locations = [
        "Remote",
        "New York",
        "San Francisco",
        "London",
        "Berlin",
        "Toronto",
        "Sydney",
        "Singapore",
        "Tokyo",
        "Paris"
    ]
    
    job_types = [
        "fulltime",
        "contract",
        "parttime",
        "internship"
    ]
    
    def on_start(self):
        """Initialize the user session."""
        self.task_ids = []
    
    @task(3)  # Higher weight for this common operation
    def search_jobs(self):
        """Simulate a job search request."""
        # Randomly select search parameters
        title = random.choice(self.job_titles)
        location = random.choice(self.locations)
        remote = random.choice([True, False])
        job_type = random.choice(self.job_types)
        
        # Send search request
        with self.client.get(
            "/search",
            params={
                "title": title,
                "location": location,
                "remote": remote,
                "job_type": job_type
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                # Check if response is valid JSON array
                try:
                    jobs = response.json()
                    if isinstance(jobs, list):
                        response.success()
                    else:
                        response.failure("Response is not a list")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(1)
    def async_search_and_check(self):
        """Simulate an async search with status checking."""
        # Randomly select search parameters
        title = random.choice(self.job_titles)
        location = random.choice(self.locations)
        remote = random.choice([True, False])
        job_type = random.choice(self.job_types)
        
        # Submit search
        with self.client.post(
            "/async/search",
            json={
                "title": title,
                "location": location,
                "remote": remote,
                "job_type": job_type
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "task_id" in data and "status" in data:
                        task_id = data["task_id"]
                        self.task_ids.append(task_id)
                        response.success()
                    else:
                        response.failure("Missing task_id or status in response")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(2)
    def check_task_status(self):
        """Simulate checking the status of a task."""
        if not self.task_ids:
            return
        
        # Select a random task ID
        task_id = random.choice(self.task_ids)
        
        # Check status
        with self.client.get(
            f"/async/search/{task_id}/status",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "status" in data:
                        response.success()
                    else:
                        response.failure("Missing status in response")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            elif response.status_code == 404:
                # Task not found, remove from list
                if task_id in self.task_ids:
                    self.task_ids.remove(task_id)
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(1)
    def get_task_results(self):
        """Simulate getting the results of a task."""
        if not self.task_ids:
            return
        
        # Select a random task ID
        task_id = random.choice(self.task_ids)
        
        # Get results
        with self.client.get(
            f"/async/search/{task_id}/results",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    jobs = response.json()
                    if isinstance(jobs, list):
                        response.success()
                    else:
                        response.failure("Response is not a list")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            elif response.status_code == 404:
                # Task not found or not completed, remove from list
                if task_id in self.task_ids:
                    self.task_ids.remove(task_id)
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(5)  # Most common operation
    def view_dashboard(self):
        """Simulate viewing the metrics dashboard."""
        with self.client.get(
            "/metrics/dashboard",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "queue" in data and "system" in data:
                        response.success()
                    else:
                        response.failure("Missing queue or system in response")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
