import json
import os
import time
import redis
import csv
import statistics
from datetime import datetime
from edgeric_messenger import EdgericMessenger

edgeric_messenger = EdgericMessenger(socket_type="None")

def get_algorithm_name():
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        algo = r.get("scheduling_algorithm")
        if algo:
            return algo.decode("utf-8").replace(" ", "_")
        else:
            return "Unknown_Algorithm"
    except Exception as e:
        print(f"Warning: Could not read scheduling algorithm from Redis: {e}")
        return "Unknown_Algorithm"

# Setup Paths
algo_name = get_algorithm_name()
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
base_dir = os.path.join("logs", algo_name)
os.makedirs(base_dir, exist_ok=True)

# --- CHANGED: Single Master CSV Path ---
master_csv_path = os.path.join(base_dir, f"experiment_metrics_{timestamp}.csv")
json_path = os.path.join(base_dir, f"experiment_metrics_{timestamp}.json")

# State tracking
ue_history = {}
full_log = {}

def initialize_master_csv():
    """Create the single master CSV file with headers."""
    with open(master_csv_path, "w", newline="") as f:
        fieldnames = [
            "time_idx", "tti", "rnti",  # Added RNTI column
            "cqi", "snr", "tx_bytes", "rx_bytes",
            "ul_buffer", "ul_harq_ack", "ul_tx_attempt",
            "Z", "instantaneous_aoi", "average_aoi",
            "measured_throughput", "ptx", "sigma2"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

def append_to_master_csv(row_data):
    """Append a single row of data to the master CSV."""
    with open(master_csv_path, "a", newline="") as f:
        # We reuse the same fieldnames as initialize
        fieldnames = [
            "time_idx", "tti", "rnti",
            "cqi", "snr", "tx_bytes", "rx_bytes",
            "ul_buffer", "ul_harq_ack", "ul_tx_attempt",
            "Z", "instantaneous_aoi", "average_aoi",
            "measured_throughput", "ptx", "sigma2"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(row_data)

def main():
    print(f"Starting Consolidated UE Metrics Monitor...")
    print(f"Scheduling Algorithm: {algo_name}")
    print(f"Logging ALL UEs to: {master_csv_path}")
    print("Press Ctrl+C to stop.\n")

    # Initialize the single file
    initialize_master_csv()

    try:
        while True:
            tti_count, ue_data = edgeric_messenger.get_metrics(flag_print=False)
            snapshot = {"tti": tti_count, "ues": {}}

            # Process every UE present in this TTI
            for rnti, metrics in ue_data.items():
                
                # 1. Update History / Variance Stats
                if rnti not in ue_history:
                    ue_history[rnti] = {
                        "instantaneous_aoi": 1,
                        "average_aoi": 1.0,
                        "total_acks": 0,
                        "total_tx": 0,
                        "tti_seen": 0,
                        "sum_aoi": 0.0,
                        "Z_values": [] 
                    }
                
                hist = ue_history[rnti]
                hist["tti_seen"] += 1

                harq_ack = metrics.get("ul_harq_ack", False)
                tx_attempt = metrics.get("ul_tx_attempt", 0)
                hist["total_tx"] += tx_attempt

                # Compute Z and Variance
                Z = 1 if harq_ack and tx_attempt else 0
                hist["Z_values"].append(Z)
                
                # Keep Z history manageable (optional: sliding window)
                # if len(hist["Z_values"]) > 1000: hist["Z_values"].pop(0)

                sigma2 = statistics.pvariance(hist["Z_values"]) if len(hist["Z_values"]) > 1 else 0

                # AoI Calculation
                if harq_ack:
                    hist["instantaneous_aoi"] = 1
                    hist["total_acks"] += 1
                else:
                    hist["instantaneous_aoi"] += 1

                hist["sum_aoi"] += hist["instantaneous_aoi"]
                hist["average_aoi"] = hist["sum_aoi"] / hist["tti_seen"]

                measured_throughput = hist["total_acks"] / hist["tti_seen"] if hist["tti_seen"] > 0 else 0
                ptx = hist["total_acks"] / hist["total_tx"] if hist["total_tx"] > 0 else 0

                # 2. Prepare Data Row
                enriched_metrics = {
                    "time_idx": hist["tti_seen"], # Or use global time if preferred
                    "tti": tti_count,
                    "rnti": rnti, # KEY IDENTIFIER
                    "cqi": metrics.get("cqi", 0),
                    "snr": metrics.get("snr", 0),
                    "tx_bytes": metrics.get("tx_bytes", 0),
                    "rx_bytes": metrics.get("rx_bytes", 0),
                    "ul_buffer": metrics.get("ul_buffer", 0),
                    "ul_harq_ack": metrics.get("ul_harq_ack", False),
                    "ul_tx_attempt": metrics.get("ul_tx_attempt", 0),
                    "Z": Z,
                    "instantaneous_aoi": hist["instantaneous_aoi"],
                    "average_aoi": round(hist["average_aoi"], 4),
                    "measured_throughput": round(measured_throughput, 4),
                    "ptx": round(ptx, 4),
                    "sigma2": round(sigma2, 6)
                }

                # 3. Log to Master CSV
                append_to_master_csv(enriched_metrics)
                
                # 4. Save to JSON snapshot
                snapshot["ues"][rnti] = enriched_metrics

            full_log[tti_count] = snapshot

            # Periodic JSON Dump
            if tti_count % 500 == 0:
                with open(json_path, "w") as f:
                    json.dump(list(full_log.values()), f, indent=2)
                print(f"[TTI {tti_count}] Data appended. Active UEs: {list(ue_data.keys())}")

            # Sleep briefly to prevent CPU thrashing
            time.sleep(0.001)

    except KeyboardInterrupt:
        print("\nInterrupted. Saving final JSON...")
        with open(json_path, "w") as f:
            json.dump(list(full_log.values()), f, indent=2)
        print(f"Done. Data saved to {master_csv_path}")

if __name__ == "__main__":
    main()