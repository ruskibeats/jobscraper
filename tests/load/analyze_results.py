"""
Analysis script for load test results.

This module provides functions to analyze load test results from Locust
and generate visualizations and reports.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
import argparse
from datetime import datetime

def analyze_load_test(csv_prefix):
    """
    Analyze load test results and generate visualizations.
    
    Args:
        csv_prefix: Prefix of the CSV files to analyze
    """
    # Check if the stats CSV file exists
    stats_file = f"{csv_prefix}_stats.csv"
    if not os.path.exists(stats_file):
        print(f"Error: Stats file {stats_file} not found")
        return
    
    # Load the stats CSV file
    stats = pd.read_csv(stats_file)
    
    # Create output directory
    output_dir = f"load_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Calculate key metrics
    avg_response_time = stats["Average Response Time"].mean()
    median_response_time = stats["Median Response Time"].mean()
    p95_response_time = stats["95%"].mean()
    failure_rate = stats["Failure Rate"].mean()
    
    # Print summary
    print(f"\nTest: {csv_prefix}")
    print(f"Average Response Time: {avg_response_time:.2f}ms")
    print(f"Median Response Time: {median_response_time:.2f}ms")
    print(f"95th Percentile: {p95_response_time:.2f}ms")
    print(f"Failure Rate: {failure_rate:.2f}%")
    
    # Save summary to file
    with open(f"{output_dir}/{csv_prefix}_summary.txt", "w") as f:
        f.write(f"Test: {csv_prefix}\n")
        f.write(f"Average Response Time: {avg_response_time:.2f}ms\n")
        f.write(f"Median Response Time: {median_response_time:.2f}ms\n")
        f.write(f"95th Percentile: {p95_response_time:.2f}ms\n")
        f.write(f"Failure Rate: {failure_rate:.2f}%\n")
    
    # Convert timestamp to datetime for better plotting
    stats["Timestamp"] = pd.to_datetime(stats["Timestamp"])
    
    # Group by name to analyze different endpoints
    endpoint_stats = stats.groupby("Name")
    
    # Plot response time distribution by endpoint
    plt.figure(figsize=(12, 8))
    for name, group in endpoint_stats:
        if name == "Aggregated":
            continue
        plt.plot(group["Timestamp"], group["Average Response Time"], label=name)
    
    plt.xlabel("Time")
    plt.ylabel("Response Time (ms)")
    plt.title(f"Response Time by Endpoint - {csv_prefix}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/{csv_prefix}_response_times_by_endpoint.png")
    
    # Plot aggregated response time distribution
    agg_stats = stats[stats["Name"] == "Aggregated"]
    
    plt.figure(figsize=(12, 8))
    plt.plot(agg_stats["Timestamp"], agg_stats["Average Response Time"], label="Average", color="blue")
    plt.plot(agg_stats["Timestamp"], agg_stats["Median Response Time"], label="Median", color="green")
    plt.plot(agg_stats["Timestamp"], agg_stats["95%"], label="95th Percentile", color="red")
    
    plt.xlabel("Time")
    plt.ylabel("Response Time (ms)")
    plt.title(f"Aggregated Response Time Distribution - {csv_prefix}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/{csv_prefix}_aggregated_response_times.png")
    
    # Plot request rate and failures
    plt.figure(figsize=(12, 8))
    plt.plot(agg_stats["Timestamp"], agg_stats["Requests/s"], label="Requests/s", color="blue")
    plt.plot(agg_stats["Timestamp"], agg_stats["Failures/s"], label="Failures/s", color="red")
    
    plt.xlabel("Time")
    plt.ylabel("Rate")
    plt.title(f"Request and Failure Rates - {csv_prefix}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/{csv_prefix}_request_rates.png")
    
    # Plot failure percentage
    plt.figure(figsize=(12, 8))
    plt.plot(agg_stats["Timestamp"], agg_stats["Failure Rate"], color="red")
    
    plt.xlabel("Time")
    plt.ylabel("Failure Rate (%)")
    plt.title(f"Failure Rate - {csv_prefix}")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/{csv_prefix}_failure_rate.png")
    
    # Analyze endpoint performance
    endpoint_summary = stats[stats["Name"] != "Aggregated"].groupby("Name").agg({
        "Average Response Time": "mean",
        "Median Response Time": "mean",
        "95%": "mean",
        "Failure Rate": "mean",
        "Requests/s": "mean"
    }).sort_values("Average Response Time", ascending=False)
    
    # Save endpoint summary to file
    endpoint_summary.to_csv(f"{output_dir}/{csv_prefix}_endpoint_summary.csv")
    
    # Plot endpoint performance comparison
    plt.figure(figsize=(12, 8))
    endpoint_summary["Average Response Time"].plot(kind="bar", color="skyblue")
    
    plt.xlabel("Endpoint")
    plt.ylabel("Average Response Time (ms)")
    plt.title(f"Endpoint Performance Comparison - {csv_prefix}")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/{csv_prefix}_endpoint_comparison.png")
    
    # If distribution file exists, analyze it
    dist_file = f"{csv_prefix}_distribution.csv"
    if os.path.exists(dist_file):
        dist = pd.read_csv(dist_file)
        
        # Plot response time distribution
        plt.figure(figsize=(12, 8))
        
        for name in dist["Name"].unique():
            if name == "Aggregated":
                continue
            
            group = dist[dist["Name"] == name]
            plt.plot(group["Response Time"], group["Count"], label=name)
        
        plt.xlabel("Response Time (ms)")
        plt.ylabel("Count")
        plt.title(f"Response Time Distribution - {csv_prefix}")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/{csv_prefix}_response_time_distribution.png")
    
    print(f"Analysis complete. Results saved to {output_dir}/")

def main():
    """Main function to run the analysis."""
    parser = argparse.ArgumentParser(description="Analyze load test results")
    parser.add_argument("--prefix", help="Prefix of the CSV files to analyze")
    parser.add_argument("--all", action="store_true", help="Analyze all CSV files in the current directory")
    
    args = parser.parse_args()
    
    if args.all:
        # Find all stats CSV files
        stats_files = glob.glob("*_stats.csv")
        prefixes = [f.replace("_stats.csv", "") for f in stats_files]
        
        for prefix in prefixes:
            analyze_load_test(prefix)
    elif args.prefix:
        analyze_load_test(args.prefix)
    else:
        # Default test prefixes
        for test in ["baseline", "steady_load", "peak_load", "endurance"]:
            if os.path.exists(f"{test}_stats.csv"):
                analyze_load_test(test)

if __name__ == "__main__":
    main()
