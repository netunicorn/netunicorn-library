from typing import Dict
from netunicorn.base import Task
from pprint import pprint
import subprocess
from ping3 import ping
import csv
import json

class AlexaWebsitesTask(Task):
    # Measure network metrics for a list of Alexa top websites.
    requirements = [
        "sudo apt-get install -y curl dnsutils traceroute",
        "pip install ping3"
    ]

    def __init__(self, domain: str = None, filepath: str = None, output_path: str = None, top_k: int = None):
        super().__init__()
        self.domain = domain
        self.filepath = filepath
        self.output_path = output_path
        self.top_k = top_k

    def get_traceroute(self) -> str:
        try:
            result = subprocess.run(["traceroute", "-m", "10", self.domain], capture_output=True, text=True, check=True)
            return result.stdout
        except Exception as e:
            return f"Traceroute failed: {e}"
        
    def measure_ping(self) -> Dict[str, float]:
        try:
            ping_value = ping(self.domain)
            if ping_value is None:
                return {"value": None, "unit": "ms"}
            return {"value": ping_value * 1000, "unit": "ms"}
        except Exception as e:
            return {"value": None, "unit": "ms", "error": str(e)}

    def measure_dns_time(self) -> Dict[str, float]:
        try:
            result = subprocess.run(["dig", self.domain], capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines():
                if "Query time" in line:
                    return {"value": float(line.split(":")[1].strip().split(" ")[0]), "unit": "ms"}
            return {"value": None, "unit": "ms"}
        except Exception as e:
            return f"DNS resolution failed: {e}"

    def measure_ttfb(self) -> Dict[str, float]:
        try:
            result = subprocess.run([
                "curl",
                "-o", "/dev/null",
                "-s",
                "-w", "%{time_starttransfer}",
                "-H", "Cache-Control: no-cache",
                f"http://{self.domain}",
            ], capture_output=True, text=True, check=True)
            ttfb = float(result.stdout.strip()) * 1000  # s to ms
            return {"value": ttfb, "unit": "ms"}
        except Exception as e:
            print(f"TTFB measurement failed for {self.domain}: {e}")
            return {"value": None, "unit": "ms", "error": str(e)}

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

    def run(self) -> Dict[str, Dict]:
        if self.domain:
            # Run for a single domain
            return {
                "domain": self.domain,
                "traceroute": self.get_traceroute(),
                "ping_time": self.measure_ping(),
                "dns_time": self.measure_dns_time(),
                "ttfb_time": self.measure_ttfb(),
            }

        elif self.filepath and self.output_path:
            # Run for all websites in the file
            websites = AlexaWebsitesTask.load_websites(self.filepath, self.top_k)
            print(f"Loaded {len(websites)} websites.")

            results = {}
            for website in websites:
                print(f"Processing: {website}")
                try:
                    self.domain = website
                    results[website] = self.run()
                except Exception as e:
                    results[website] = {"error": str(e)}

            # Save results to a JSON file
            with open(self.output_path, "w") as f:
                json.dump(results, f, indent=4)

            print(f"Results saved to {self.output_path}")
            return results

        else:
            raise ValueError("Either a domain or both a filepath and output_path must be provided.")
