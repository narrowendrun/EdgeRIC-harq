import json
import os
import time
import redis
import csv
import sqlite3
from datetime import datetime
from collections import deque
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

# Database for efficient querying and live monitoring
db_path = os.path.join(base_dir, f"metrics_{timestamp}.db")
csv_path = os.path.join(base_dir, f"metrics_{timestamp}.csv")

# Configuration
STALE_UL_TX_TIMEOUT_SEC = 5.0
BUFFER_SIZE = 100  # Write to disk every N samples
CSV_FLUSH_INTERVAL = 1000  # Flush CSV every N TTIs

# State tracking per RNTI
ue_last_ul_tx = {}  # Track last time ul_tx_attempt was True
active_ues = {}
ue_aoi_state = {}  # Track AoI state: {rnti: {'instantaneous_aoi': int, 'aoi_sum': int, 'count': int}}
ue_tx_stats = {}  # Track transmission stats: {rnti: {'harq_ack_count': int, 'tx_attempt_count': int}}

write_buffer = deque(maxlen=BUFFER_SIZE)

def initialize_database():
    """Create SQLite database with indexed tables for fast querying."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Main metrics table
    c.execute('''
        CREATE TABLE IF NOT EXISTS ue_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tti INTEGER NOT NULL,
            rnti INTEGER NOT NULL,
            timestamp REAL NOT NULL,
            cqi INTEGER,
            snr REAL,
            tx_bytes REAL,
            rx_bytes REAL,
            dl_buffer INTEGER,
            ul_buffer INTEGER,
            dl_tbs REAL,
            ul_harq_ack INTEGER,
            ul_tx_attempt INTEGER,
            Z INTEGER,
            instantaneous_aoi INTEGER,
            average_aoi REAL,
            p_tx REAL,
            throughput REAL
        )
    ''')
    
    # Indexes for fast queries
    c.execute('CREATE INDEX IF NOT EXISTS idx_tti ON ue_metrics(tti)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_rnti ON ue_metrics(rnti)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_rnti_tti ON ue_metrics(rnti, tti)')
    
    # Summary table for quick latest status
    c.execute('''
        CREATE TABLE IF NOT EXISTS ue_latest (
            rnti INTEGER PRIMARY KEY,
            last_tti INTEGER,
            last_timestamp REAL,
            last_ul_tx_attempt_time REAL,
            cqi INTEGER,
            snr REAL,
            tx_bytes REAL,
            rx_bytes REAL,
            dl_buffer INTEGER,
            ul_buffer INTEGER,
            dl_tbs REAL,
            ul_harq_ack INTEGER,
            ul_tx_attempt INTEGER,
            Z INTEGER,
            instantaneous_aoi INTEGER,
            average_aoi REAL,
            p_tx REAL,
            throughput REAL
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized: {db_path}")

def initialize_csv():
    """Create CSV file with headers."""
    with open(csv_path, "w", newline="") as f:
        fieldnames = [
            "tti", "rnti", "timestamp",
            "cqi", "snr", "tx_bytes", "rx_bytes",
            "dl_buffer", "ul_buffer", "dl_tbs",
            "ul_harq_ack", "ul_tx_attempt",
            "Z", "instantaneous_aoi", "average_aoi", "p_tx", "throughput"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

def flush_buffer_to_db(conn):
    """Batch write buffered data to database."""
    if not write_buffer:
        return
    
    c = conn.cursor()
    
    # Batch insert into main table
    c.executemany('''
        INSERT INTO ue_metrics 
        (tti, rnti, timestamp, cqi, snr, tx_bytes, rx_bytes, 
         dl_buffer, ul_buffer, dl_tbs, ul_harq_ack, ul_tx_attempt,
         Z, instantaneous_aoi, average_aoi, p_tx, throughput)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', [(
        row['tti'], row['rnti'], row['timestamp'],
        row['cqi'], row['snr'], row['tx_bytes'], row['rx_bytes'],
        row['dl_buffer'], row['ul_buffer'], row['dl_tbs'],
        row['ul_harq_ack'], row['ul_tx_attempt'],
        row['Z'], row['instantaneous_aoi'], row['average_aoi'], 
        row['p_tx'], row['throughput']
    ) for row in write_buffer])
    
    # Update latest table
    c.executemany('''
        INSERT OR REPLACE INTO ue_latest
        (rnti, last_tti, last_timestamp, last_ul_tx_attempt_time,
         cqi, snr, tx_bytes, rx_bytes, dl_buffer, ul_buffer, dl_tbs,
         ul_harq_ack, ul_tx_attempt, Z, instantaneous_aoi, average_aoi, 
         p_tx, throughput)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', [(
        row['rnti'], row['tti'], row['timestamp'], row['last_ul_tx_time'],
        row['cqi'], row['snr'], row['tx_bytes'], row['rx_bytes'],
        row['dl_buffer'], row['ul_buffer'], row['dl_tbs'],
        row['ul_harq_ack'], row['ul_tx_attempt'],
        row['Z'], row['instantaneous_aoi'], row['average_aoi'],
        row['p_tx'], row['throughput']
    ) for row in write_buffer])
    
    conn.commit()
    write_buffer.clear()

def append_to_csv_batch(rows):
    """Batch append rows to CSV."""
    if not rows:
        return
    
    with open(csv_path, "a", newline="") as f:
        fieldnames = [
            "tti", "rnti", "timestamp",
            "cqi", "snr", "tx_bytes", "rx_bytes",
            "dl_buffer", "ul_buffer", "dl_tbs",
            "ul_harq_ack", "ul_tx_attempt",
            "Z", "instantaneous_aoi", "average_aoi", "p_tx", "throughput"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        for row in rows:
            writer.writerow({k: row[k] for k in fieldnames})

def main():
    print(f"Starting Enhanced UE Metrics Monitor with AoI Tracking...")
    print(f"Scheduling Algorithm: {algo_name}")
    print(f"Database: {db_path}")
    print(f"CSV Backup: {csv_path}")
    print(f"Stale UL TX Timeout: {STALE_UL_TX_TIMEOUT_SEC}s")
    print("Press Ctrl+C to stop.\n")

    initialize_database()
    initialize_csv()
    
    conn = sqlite3.connect(db_path)
    csv_buffer = []
    
    try:
        while True:
            tti_count, ue_data = edgeric_messenger.get_metrics(flag_print=False)
            now = time.time()

            # Process each UE
            for rnti, metrics in ue_data.items():
                rnti_key = str(rnti)
                
                # Check if ul_tx_attempt is True
                ul_tx_attempt = metrics.get("ul_tx_attempt", False)
                ul_harq_ack = metrics.get("ul_harq_ack", False)
                
                # Update last ul_tx_attempt timestamp
                if ul_tx_attempt:
                    ue_last_ul_tx[rnti_key] = now
                
                # Skip this UE if it's been stale for too long
                if rnti_key in ue_last_ul_tx:
                    time_since_ul_tx = now - ue_last_ul_tx[rnti_key]
                    if time_since_ul_tx > STALE_UL_TX_TIMEOUT_SEC:
                        # Remove stale UE
                        print(f"[TTI {tti_count}] Removing stale RNTI {rnti} "
                              f"(no ul_tx_attempt for {time_since_ul_tx:.1f}s)")
                        ue_last_ul_tx.pop(rnti_key, None)
                        active_ues.pop(rnti_key, None)
                        ue_aoi_state.pop(rnti_key, None)
                        ue_tx_stats.pop(rnti_key, None)
                        continue
                elif not ul_tx_attempt:
                    # First time seeing this UE and ul_tx_attempt is False - skip
                    continue
                else:
                    # First time with ul_tx_attempt = True
                    ue_last_ul_tx[rnti_key] = now

                # Initialize AoI state for new RNTI
                if rnti_key not in ue_aoi_state:
                    ue_aoi_state[rnti_key] = {
                        'instantaneous_aoi': 1,
                        'aoi_sum': 0,
                        'count': 0
                    }
                    ue_tx_stats[rnti_key] = {
                        'harq_ack_count': 0,
                        'tx_attempt_count': 0
                    }

                # Calculate Z (successful transmission indicator)
                Z = 1 if ul_harq_ack else 0

                # Update instantaneous AoI
                if Z == 1:
                    ue_aoi_state[rnti_key]['instantaneous_aoi'] = 1
                else:
                    ue_aoi_state[rnti_key]['instantaneous_aoi'] += 1

                # Update AoI sum and count
                ue_aoi_state[rnti_key]['aoi_sum'] += ue_aoi_state[rnti_key]['instantaneous_aoi']
                ue_aoi_state[rnti_key]['count'] += 1

                # Calculate average AoI
                average_aoi = ue_aoi_state[rnti_key]['aoi_sum'] / ue_aoi_state[rnti_key]['count']

                # Update transmission statistics
                if ul_tx_attempt:
                    ue_tx_stats[rnti_key]['tx_attempt_count'] += 1
                    if ul_harq_ack:
                        ue_tx_stats[rnti_key]['harq_ack_count'] += 1

                # Calculate p_tx (probability of successful transmission)
                if ue_tx_stats[rnti_key]['tx_attempt_count'] > 0:
                    p_tx = ue_tx_stats[rnti_key]['harq_ack_count'] / ue_tx_stats[rnti_key]['tx_attempt_count']
                else:
                    p_tx = 0.0

                # Calculate throughput (successful transmissions per TTI)
                throughput = ue_tx_stats[rnti_key]['harq_ack_count'] / tti_count if tti_count > 0 else 0.0

                # Prepare data row
                enriched_metrics = {
                    "tti": tti_count,
                    "rnti": rnti,
                    "timestamp": now,
                    "last_ul_tx_time": ue_last_ul_tx[rnti_key],
                    "cqi": metrics.get("cqi", 0),
                    "snr": metrics.get("snr", 0),
                    "tx_bytes": metrics.get("tx_bytes", 0),
                    "rx_bytes": metrics.get("rx_bytes", 0),
                    "dl_buffer": metrics.get("dl_buffer", 0),
                    "ul_buffer": metrics.get("ul_buffer", 0),
                    "dl_tbs": metrics.get("dl_tbs", 0),
                    "ul_harq_ack": int(ul_harq_ack),
                    "ul_tx_attempt": int(ul_tx_attempt),
                    "Z": Z,
                    "instantaneous_aoi": ue_aoi_state[rnti_key]['instantaneous_aoi'],
                    "average_aoi": average_aoi,
                    "p_tx": p_tx,
                    "throughput": throughput
                }

                # Add to buffers
                write_buffer.append(enriched_metrics)
                csv_buffer.append(enriched_metrics)
                active_ues[rnti_key] = enriched_metrics

            # Flush to database when buffer is full
            if len(write_buffer) >= BUFFER_SIZE:
                flush_buffer_to_db(conn)

            # Flush to CSV periodically
            if tti_count % CSV_FLUSH_INTERVAL == 0 and csv_buffer:
                append_to_csv_batch(csv_buffer)
                csv_buffer.clear()

            # Status update
            if tti_count % 1000 == 0:
                print(f"[TTI {tti_count}] Active UEs: {list(active_ues.keys())}")

            time.sleep(0.001)

    except KeyboardInterrupt:
        print("\nInterrupted. Flushing final data...")
        flush_buffer_to_db(conn)
        if csv_buffer:
            append_to_csv_batch(csv_buffer)
        conn.close()
        print(f"Done. Data saved to {db_path} and {csv_path}")

if __name__ == "__main__":
    main()