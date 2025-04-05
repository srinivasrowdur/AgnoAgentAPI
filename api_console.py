#!/usr/bin/env python3
import requests
import json
import sys
import os

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

API_URL = "http://localhost:8080"
MODEL_ID = "o3-mini"  # Default model ID

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    clear_screen()
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 50}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}  STANDARDS AGENTS API CONSOLE{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 50}{Colors.ENDC}")
    print()

def check_api_health():
    """Check if the API is accessible."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                return True, data.get("agents", [])
        return False, []
    except requests.RequestException:
        return False, []

def display_menu(agents):
    """Display the main menu with agent options."""
    print(f"{Colors.BOLD}Choose an agent to ask a question:{Colors.ENDC}")
    print(f"{Colors.BLUE}1. Safety Agent{Colors.ENDC}")
    print(f"{Colors.GREEN}2. Quality Agent{Colors.ENDC}")
    print(f"{Colors.YELLOW}3. Team Agent{Colors.ENDC}")
    print(f"{Colors.RED}4. Exit{Colors.ENDC}")
    print()
    return input(f"{Colors.BOLD}Select option (1-4): {Colors.ENDC}")

def ask_safety_agent(query):
    """Send a query to the safety agent."""
    payload = {
        "query": query,
        "model_id": MODEL_ID
    }
    response = requests.post(f"{API_URL}/safety/ask", json=payload)
    return response.json()

def ask_quality_agent(query):
    """Send a query to the quality agent."""
    payload = {
        "query": query,
        "model_id": MODEL_ID
    }
    response = requests.post(f"{API_URL}/quality/ask", json=payload)
    return response.json()

def ask_team_agent(query):
    """Send a query to the team agent."""
    # Ask for team mode
    print(f"\n{Colors.BOLD}Choose team mode:{Colors.ENDC}")
    print(f"{Colors.BLUE}1. Collaborate{Colors.ENDC}")
    print(f"{Colors.GREEN}2. Route{Colors.ENDC}")
    print(f"{Colors.YELLOW}3. Coordinate{Colors.ENDC}")
    mode_choice = input(f"{Colors.BOLD}Select mode (1-3, default is 1): {Colors.ENDC}")
    
    team_mode = "collaborate"
    if mode_choice == "2":
        team_mode = "route"
    elif mode_choice == "3":
        team_mode = "coordinate"
    
    payload = {
        "query": query,
        "model_id": MODEL_ID,
        "team_mode": team_mode
    }
    response = requests.post(f"{API_URL}/team/ask", json=payload)
    return response.json(), team_mode

def main():
    """Main application logic."""
    while True:
        print_header()
        
        # Check API health
        is_healthy, agents = check_api_health()
        if not is_healthy:
            print(f"{Colors.RED}Error: Cannot connect to the API. Make sure it's running at: {API_URL}{Colors.ENDC}")
            print(f"\nPress Enter to try again or 'q' to quit...")
            if input().lower() == 'q':
                sys.exit(0)
            continue
        
        print(f"{Colors.GREEN}✓ API is healthy. Available agents: {', '.join(agents)}{Colors.ENDC}\n")
        
        # Display menu and get user choice
        choice = display_menu(agents)
        
        if choice == "4":
            print(f"\n{Colors.YELLOW}Exiting. Goodbye!{Colors.ENDC}")
            break
        
        if choice not in ["1", "2", "3"]:
            input(f"\n{Colors.RED}Invalid choice. Press Enter to continue...{Colors.ENDC}")
            continue
        
        # Get user query
        print(f"\n{Colors.BOLD}Enter your question:{Colors.ENDC}")
        query = input(f"{Colors.BOLD}> {Colors.ENDC}")
        
        if not query.strip():
            input(f"\n{Colors.RED}Empty query. Press Enter to continue...{Colors.ENDC}")
            continue
        
        # Process the query based on chosen agent
        print(f"\n{Colors.BLUE}Sending request...{Colors.ENDC}")
        try:
            if choice == "1":
                result = ask_safety_agent(query)
                agent_name = "Safety Agent"
                color = Colors.BLUE
            elif choice == "2":
                result = ask_quality_agent(query)
                agent_name = "Quality Agent"
                color = Colors.GREEN
            else:
                result, team_mode = ask_team_agent(query)
                agent_name = f"Team Agent ({team_mode.capitalize()})"
                color = Colors.YELLOW
            
            # Display the result
            print(f"\n{color}{'=' * 50}{Colors.ENDC}")
            print(f"{color}{Colors.BOLD}{agent_name} Response:{Colors.ENDC}")
            print(f"{color}{'=' * 50}{Colors.ENDC}")
            print(result.get("response", "No response received"))
            print(f"{color}{'=' * 50}{Colors.ENDC}")
        except requests.RequestException as e:
            print(f"\n{Colors.RED}Error: Failed to get response from API: {str(e)}{Colors.ENDC}")
        
        input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Exiting. Goodbye!{Colors.ENDC}")
        sys.exit(0) 