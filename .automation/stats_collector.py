# !/usr/bin/env python3
"""
Statistics collection and management functions for MegaLinter build system
"""
import json
import logging
import os
import re
import time
from datetime import datetime, timezone

import gitlab
import megalinter
import megalinter.linter_factory
import megalinter.config
import megalinter.utils
import requests
import yaml
from webpreview import web_preview
import webpreview.excepts

from build_constants import *


def collect_linter_previews():
    """Collect linter info from linter url, later used to build link preview card within linter documentation"""
    linters = megalinter.linter_factory.list_all_linters({"request_id": "build"})
    
    # Read file
    with open(LINKS_PREVIEW_FILE, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    
    updated = False
    
    # Collect info using web_preview
    for linter in linters:
        if (
            linter.linter_name not in data
            or megalinter.config.get(None, "REFRESH_LINTER_PREVIEWS", "false") == "true"
        ):
            logging.info(f"Collecting link preview info for {linter.linter_name} at {linter.linter_url}")
            title = None
            try:
                title, description, image = web_preview(
                    linter.linter_url, parser="html.parser", timeout=1000
                )
            except webpreview.excepts.URLUnreachable as e:
                logging.error("URLUnreachable: " + str(e))
            except Exception as e:
                logging.error(str(e))
            if title is not None:
                item = {
                    "title": megalinter.utils.clean_string(title),
                    "description": megalinter.utils.clean_string(description),
                    "image": image,
                }
                data[linter.linter_name] = item
                updated = True
    
    # Update file
    if updated is True:
        with open(LINKS_PREVIEW_FILE, "w", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=2, sort_keys=True)


def update_docker_pulls_counter():
    """Update docker pulls counter from Docker Hub API"""
    try:
        docker_pulls = 0
        # Get pulls for main image
        main_image_url = f"https://hub.docker.com/v2/repositories/{ML_DOCKER_IMAGE.replace('ghcr.io/', '')}"
        response = requests.get(main_image_url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            docker_pulls += data.get("pull_count", 0)
        
        # Get pulls for flavor images
        flavor_images = [
            "c_cpp", "cupcake", "dart", "documentation", "dotnet", "go", "java", 
            "javascript", "php", "python", "ruby", "rust", "salesforce", "scala", 
            "swift", "terraform"
        ]
        
        for flavor in flavor_images:
            flavor_image_url = f"https://hub.docker.com/v2/repositories/{ML_DOCKER_IMAGE.replace('ghcr.io/', '')}-{flavor}"
            try:
                response = requests.get(flavor_image_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    docker_pulls += data.get("pull_count", 0)
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                logging.debug(f"Error getting pulls for {flavor}: {e}")
        
        # Save to file
        stats_file = f"{REPO_HOME}/.automation/generated/docker_stats.json"
        os.makedirs(os.path.dirname(stats_file), exist_ok=True)
        stats_data = {
            "total_pulls": docker_pulls,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats_data, f, indent=2)
        
        logging.info(f"Docker pulls counter updated: {docker_pulls}")
        return docker_pulls
    except Exception as e:
        logging.warning(f"Error updating docker pulls counter: {e}")
        return 0


def manage_output_variables():
    if os.environ.get("UPGRADE_LINTERS_VERSION", "") == "true":
        updated_files = megalinter.utils.list_updated_files("..")
        updated_versions = 0
        for updated_file in updated_files:
            updated_file_clean = megalinter.utils.normalize_log_string(updated_file)
            if os.path.basename(updated_file_clean) == "linter-versions.json":
                updated_versions = 1
                break
        if updated_versions == 1:
            if "GITHUB_OUTPUT" in os.environ:
                github_output_file = os.environ["GITHUB_OUTPUT"]
                if not os.path.isfile(github_output_file):
                    github_output_file = github_output_file.replace(
                        "/home/runner/work/_temp/_runner_file_commands",
                        "/github/file_commands",
                    )
                with open(github_output_file, "a", encoding="utf-8") as output_stream:
                    output_stream.write("has_updated_versions=1\n")


def collect_usage_stats():
    """Collect usage statistics from various sources"""
    stats = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sources": {}
    }
    
    # GitHub stats
    try:
        github_api_url = f"https://api.github.com/repos/{ML_REPO.replace('https://github.com/', '')}"
        response = requests.get(github_api_url, timeout=30)
        if response.status_code == 200:
            repo_data = response.json()
            stats["sources"]["github"] = {
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "watchers": repo_data.get("watchers_count", 0),
                "open_issues": repo_data.get("open_issues_count", 0)
            }
    except Exception as e:
        logging.debug(f"Error collecting GitHub stats: {e}")
    
    # Docker Hub stats
    try:
        docker_stats_file = f"{REPO_HOME}/.automation/generated/docker_stats.json"
        if os.path.exists(docker_stats_file):
            with open(docker_stats_file, "r", encoding="utf-8") as f:
                docker_data = json.load(f)
                stats["sources"]["docker"] = docker_data
    except Exception as e:
        logging.debug(f"Error collecting Docker stats: {e}")
    
    # Save stats
    stats_file = f"{REPO_HOME}/.automation/generated/usage_stats.json"
    os.makedirs(os.path.dirname(stats_file), exist_ok=True)
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    
    logging.info("Usage statistics collected")
    return stats


def update_badge_values():
    """Update badge values in README and documentation"""
    try:
        # Update docker pulls badge
        docker_pulls = update_docker_pulls_counter()
        
        # Update GitHub stats
        usage_stats = collect_usage_stats()
        
        # Update version badges
        version_badge_files = [
            f"{REPO_HOME}/README.md",
            f"{REPO_HOME}/docs/index.md"
        ]
        
        for file_path in version_badge_files:
            if os.path.exists(file_path):
                # Update version references
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Replace version patterns
                content = re.sub(
                    r'@v\d+\.\d+\.\d+',
                    f'@{VERSION_V}',
                    content
                )
                content = re.sub(
                    r':\d+\.\d+\.\d+',
                    f':{VERSION_V}',
                    content
                )
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
        
        logging.info("Badge values updated successfully")
    except Exception as e:
        logging.warning(f"Error updating badge values: {e}")


def generate_stats_summary():
    """Generate a summary of all collected statistics"""
    summary = {
        "generation_time": datetime.now(timezone.utc).isoformat(),
        "megalinter_version": VERSION,
        "summary": {}
    }
    
    # Load various stats files
    stats_files = {
        "docker": f"{REPO_HOME}/.automation/generated/docker_stats.json",
        "usage": f"{REPO_HOME}/.automation/generated/usage_stats.json",
        "previews": f"{REPO_HOME}/.automation/generated/linter_previews.json"
    }
    
    for stat_type, file_path in stats_files.items():
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if stat_type == "docker":
                        summary["summary"]["docker_pulls"] = data.get("total_pulls", 0)
                    elif stat_type == "usage":
                        github_data = data.get("sources", {}).get("github", {})
                        summary["summary"]["github_stars"] = github_data.get("stars", 0)
                        summary["summary"]["github_forks"] = github_data.get("forks", 0)
                    elif stat_type == "previews":
                        summary["summary"]["linter_previews_count"] = len(data)
            except Exception as e:
                logging.debug(f"Error loading {stat_type} stats: {e}")
    
    # Save summary
    summary_file = f"{REPO_HOME}/.automation/generated/stats_summary.json"
    os.makedirs(os.path.dirname(summary_file), exist_ok=True)
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    
    logging.info("Statistics summary generated")
    return summary


def cleanup_generated_files():
    """Clean up old generated files"""
    generated_dir = f"{REPO_HOME}/.automation/generated"
    if os.path.exists(generated_dir):
        cutoff_time = time.time() - (7 * 24 * 60 * 60)  # 7 days ago
        for filename in os.listdir(generated_dir):
            file_path = os.path.join(generated_dir, filename)
            if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                    logging.info(f"Cleaned up old file: {filename}")
                except Exception as e:
                    logging.debug(f"Error cleaning up {filename}: {e}")


def validate_links_in_documentation():
    """Validate links in documentation files"""
    doc_files = []
    docs_dir = f"{REPO_HOME}/docs"
    
    # Collect all markdown files
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith(".md"):
                doc_files.append(os.path.join(root, file))
    
    broken_links = []
    
    for doc_file in doc_files:
        try:
            with open(doc_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Find markdown links
            links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', content)
            
            for link_text, link_url in links:
                if link_url.startswith("http"):
                    # Validate external links (basic check)
                    try:
                        response = requests.head(link_url, timeout=10)
                        if response.status_code >= 400:
                            broken_links.append({
                                "file": doc_file,
                                "url": link_url,
                                "status": response.status_code
                            })
                    except Exception as e:
                        broken_links.append({
                            "file": doc_file,
                            "url": link_url,
                            "error": str(e)
                        })
                    time.sleep(0.5)  # Rate limiting
        except Exception as e:
            logging.debug(f"Error validating links in {doc_file}: {e}")
    
    # Save broken links report
    if broken_links:
        report_file = f"{REPO_HOME}/.automation/generated/broken_links.json"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(broken_links, f, indent=2)
        logging.warning(f"Found {len(broken_links)} broken links")
    else:
        logging.info("No broken links found in documentation")
    
    return broken_links
