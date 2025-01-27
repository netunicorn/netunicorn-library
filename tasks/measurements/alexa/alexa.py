from typing import Dict, Union
from netunicorn.base import Task, Failure
import subprocess
import pprint
from ping3 import ping
import csv
import json

class AlexaWebsitesTask(Task):
    # Measure network metrics for a list of Alexa top websites.
    requirements = [
        "sudo apt-get install -y curl dnsutils traceroute",
        "pip install ping3"
    ]

    def __init__(self, domain: str = None, filepath: str = "alexa_websites.csv", output_path: str = None, top_k: int = 100, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain = domain
        self.filepath = filepath
        self.output_path = output_path
        self.top_k = top_k

    def get_traceroute(self) -> Union[str, Failure]:
        try:
            result = subprocess.run(["traceroute", "-m", "10", self.domain], capture_output=True, text=True, check=True)
            return result.stdout
        except Exception as e:
            return Failure(f"Traceroute failed: {e}")
        
    def measure_ping(self) -> Union[Dict[str, float], Failure]:
        try:
            ping_value = ping(self.domain)
            if ping_value is None:
                return Failure("Ping returned None.") 
            return {"value": ping_value * 1000, "unit": "ms"}
        except Exception as e:
            return Failure(f"Ping failed: {e}")

    def measure_dns_time(self) -> Union[Dict[str, float], Failure]:
        try:
            result = subprocess.run(["dig", self.domain], capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines():
                if "Query time" in line:
                    return {"value": float(line.split(":")[1].strip().split(" ")[0]), "unit": "ms"}
            return Failure("Query time not found in DNS response.")
        except Exception as e:
            return Failure(f"DNS resolution failed: {e}")

    def measure_timing(self) -> Union[Dict[str, Dict[str,float]], Failure]:
        try:
            result = subprocess.run([
                "curl",
                "-o", "/dev/null",
                "-s",
                "-w", 
                (
                    "time_appconnect: %{time_appconnect}\n"
                    "time_connect: %{time_connect}\n"
                    "time_namelookup: %{time_namelookup}\n"
                    "time_pretransfer: %{time_pretransfer}\n"
                    "time_redirect: %{time_redirect}\n"
                    "time_starttransfer: %{time_starttransfer}\n"
                    "time_total: %{time_total}\n"
                ),
                "-H", "Cache-Control: no-cache",
                f"https://{self.domain}",
            ], capture_output=True, text=True, check=True)
            metrics = {
                key.strip(): {"value": float(value.strip()) * 1000, "unit": "ms"}
                for line in result.stdout.splitlines()
                for key, value in [line.split(": ", 1)]
            }
            return metrics
        except Exception as e:
            return Failure(f"Network Timing measurement failed: {e}")

    @staticmethod
    def load_websites(filepath: str, top_k: int) -> list:
        # Load top k websites from a CSV file
        websites = []
        with open(filepath, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(websites) < top_k:
                    websites.append(row[1]) 
                else:
                    break
        return websites

    def run(self) -> Union[Dict[str, Dict], Failure]:
        if self.domain:
            # Run for a single domain
            return {
                "traceroute": self.get_traceroute(),
                "ping_time": self.measure_ping(),
                "dns_time": self.measure_dns_time(),
                "measure_timing": self.measure_timing(),
            }
        else:
            # Run for all websites in a file
            websites = self.load_websites(self.filepath, self.top_k)
            print(f"Loaded {len(websites)} websites.")

            results = {}
            for website in websites:
                print(f"Processing: {website}")
                try:
                    self.domain = website
                    results[website] = self.run()
                except Exception as e:
                    results[website] = Failure(f"Failed to process {website}: {e}")

            # Save results to a JSON file if output_path is provided
            if self.output_path:
                print(f"Saving results to {self.output_path}")
                try: 
                    with open(self.output_path, "w") as f:
                        json.dump(results, f, indent=4)
                except Exception as e:
                    return Failure(f"Failed to write results to file: {e}") 
            else:
                pprint.pp(results)
                
            return results
