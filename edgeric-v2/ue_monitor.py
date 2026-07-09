#!/usr/bin/env python3
"""
Real-time UE Metrics Dashboard for AoI Analysis
Shows complete history from experiment start to observe convergence
"""

import sqlite3
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import argparse
import os

class LiveMetricsMonitor:
    def __init__(self, db_path, mode='full', window_size=500, downsample=10):
        self.db_path = db_path
        self.mode = mode  # 'full' or 'window'
        self.window_size = window_size
        self.downsample = downsample  # Plot every Nth point when data is large

        # --- NEW: CQI/SNR smoothing behavior ---
        # In your traces, CQI/SNR hit exactly 0 for many TTIs (very likely "no sample / not scheduled").
        # We treat 0 as missing and forward-fill for plotting so the curve stays connected.
        self.CQI_SNR_ZERO_IS_MISSING = True
        self.CQI_SNR_BRIDGE_WITH_FFILL = True  # if False, lines will break at missing samples

        # Setup plot
        self.fig, self.axes = plt.subplots(3, 2, figsize=(14, 10))
        self.fig.suptitle('Live UE Metrics Monitor - AoI Analysis (Full History)', fontsize=16)

        # Data storage
        self.rnti_colors = {}
        self.color_cycle = plt.cm.tab10(np.linspace(0, 1, 10))
        self.color_idx = 0

        # Performance tracking
        self.last_query_time = 0

        # Configure subplots
        self.setup_plots()

    def setup_plots(self):
        """Configure all subplots."""
        titles = [
            'CQI over Time',
            'SNR (dB) over Time',
            'Instantaneous Age of Information',
            'Average Age of Information',
            'Transmission Success Probability (p_tx)',
            'Throughput (packets/TTI)'
        ]

        for ax, title in zip(self.axes.flat, titles):
            ax.set_title(title)
            ax.set_xlabel('TTI')
            ax.grid(True, alpha=0.3)

    def get_color_for_rnti(self, rnti):
        """Assign consistent color to each RNTI."""
        if rnti not in self.rnti_colors:
            self.rnti_colors[rnti] = self.color_cycle[self.color_idx % len(self.color_cycle)]
            self.color_idx += 1
        return self.rnti_colors[rnti]

    # ---------------- NEW helper ----------------
    def _clean_for_connected_plot(self, y):
        """
        Convert a metric series to something plottable without sawtooth artifacts.

        Behavior:
        - If CQI_SNR_ZERO_IS_MISSING: replace exact zeros with NaN.
        - If CQI_SNR_BRIDGE_WITH_FFILL: forward-fill NaNs to keep the line connected.
          (This displays "hold-last" between valid reports.)
        """
        y = np.asarray(y, dtype=float)

        if self.CQI_SNR_ZERO_IS_MISSING:
            y[y == 0] = np.nan

        if not self.CQI_SNR_BRIDGE_WITH_FFILL:
            return y  # matplotlib breaks the line at NaNs

        if np.all(np.isnan(y)):
            return y

        idx = np.arange(len(y))
        valid = ~np.isnan(y)
        # last valid index at or before each point (prefix max)
        last_valid_idx = np.maximum.accumulate(np.where(valid, idx, -1))

        y_ffill = y.copy()
        mask = last_valid_idx >= 0
        y_ffill[mask] = y[last_valid_idx[mask]]
        # points before first valid remain NaN (no last-valid to fill)
        return y_ffill
    # --------------------------------------------

    def fetch_data(self):
        """Fetch data from database based on mode."""
        import time
        start_time = time.time()

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Get max TTI
        c.execute('SELECT MAX(tti) FROM ue_metrics')
        max_tti = c.fetchone()[0]

        if max_tti is None:
            conn.close()
            return {}, 0

        # Determine query range
        if self.mode == 'window':
            min_tti = max(0, max_tti - self.window_size)
        else:
            min_tti = 0

        # Adaptive downsampling for large datasets
        total_points = max_tti - min_tti
        if total_points > 5000:
            # Downsample: select every Nth row
            step = max(1, total_points // 5000)
            c.execute('''
                SELECT tti, rnti, cqi, snr, instantaneous_aoi, average_aoi, p_tx, throughput
                FROM ue_metrics
                WHERE tti >= ? AND (tti - ?) % ? = 0
                ORDER BY tti ASC
            ''', (min_tti, min_tti, step))
        else:
            c.execute('''
                SELECT tti, rnti, cqi, snr, instantaneous_aoi, average_aoi, p_tx, throughput
                FROM ue_metrics
                WHERE tti >= ?
                ORDER BY tti ASC
            ''', (min_tti,))

        rows = c.fetchall()
        conn.close()

        # Organize by RNTI
        data_by_rnti = {}
        for row in rows:
            tti, rnti, cqi, snr, inst_aoi, avg_aoi, p_tx, throughput = row

            if rnti not in data_by_rnti:
                data_by_rnti[rnti] = {
                    'tti': [], 'cqi': [], 'snr': [],
                    'instantaneous_aoi': [], 'average_aoi': [],
                    'p_tx': [], 'throughput': []
                }

            data_by_rnti[rnti]['tti'].append(tti)
            data_by_rnti[rnti]['cqi'].append(cqi)
            data_by_rnti[rnti]['snr'].append(snr)
            data_by_rnti[rnti]['instantaneous_aoi'].append(inst_aoi)
            data_by_rnti[rnti]['average_aoi'].append(avg_aoi)
            data_by_rnti[rnti]['p_tx'].append(p_tx)
            data_by_rnti[rnti]['throughput'].append(throughput)

        self.last_query_time = time.time() - start_time

        return data_by_rnti, max_tti

    def update_plot(self, frame):
        """Update all plots with latest data."""
        data_by_rnti, max_tti = self.fetch_data()

        if not data_by_rnti:
            return

        # Clear all axes
        for ax in self.axes.flat:
            ax.clear()

        # Reapply titles and grid
        self.setup_plots()

        # Update title with experiment progress
        mode_str = f"Full History (0-{max_tti} TTIs)" if self.mode == 'full' else f"Window ({max_tti-self.window_size}-{max_tti} TTIs)"
        self.fig.suptitle(
            f'Live UE Metrics Monitor - {mode_str} | Query: {self.last_query_time:.3f}s',
            fontsize=16
        )

        # Plot data for each RNTI
        for rnti, data in data_by_rnti.items():
            color = self.get_color_for_rnti(rnti)
            label = f'RNTI {rnti}'

            tti = np.array(data['tti'])

            # --- CQI (connected plot: treat 0 as missing, forward-fill) ---
            cqi_plot = self._clean_for_connected_plot(data['cqi'])
            self.axes[0, 0].plot(tti, cqi_plot, label=label, color=color, alpha=0.7, linewidth=1)
            self.axes[0, 0].set_ylabel('CQI')

            # --- SNR (connected plot: treat 0 as missing, forward-fill) ---
            snr_plot = self._clean_for_connected_plot(data['snr'])
            self.axes[0, 1].plot(tti, snr_plot, label=label, color=color, alpha=0.7, linewidth=1)
            self.axes[0, 1].set_ylabel('SNR (dB)')

            # Instantaneous AoI - shows sawtooth pattern with resets
            self.axes[1, 0].plot(tti, data['instantaneous_aoi'], label=label, color=color,
                                alpha=0.6, linewidth=0.8)
            self.axes[1, 0].set_ylabel('Instantaneous AoI (TTIs)')

            # Average AoI - shows convergence behavior
            self.axes[1, 1].plot(tti, data['average_aoi'], label=label, color=color,
                                alpha=0.7, linewidth=1.5)
            self.axes[1, 1].set_ylabel('Average AoI (TTIs)')

            # Add horizontal line at steady-state (last 10% of data)
            if len(data['average_aoi']) > 100:
                steady_state_start = int(len(data['average_aoi']) * 0.9)
                steady_state_aoi = np.mean(data['average_aoi'][steady_state_start:])
                self.axes[1, 1].axhline(y=steady_state_aoi, color=color, linestyle='--',
                                       alpha=0.3, linewidth=1)

            # p_tx
            self.axes[2, 0].plot(tti, data['p_tx'], label=label, color=color, alpha=0.7, linewidth=1)
            self.axes[2, 0].set_ylabel('p_tx')
            self.axes[2, 0].set_ylim([0, 1.05])

            # Throughput
            self.axes[2, 1].plot(tti, data['throughput'], label=label, color=color, alpha=0.7, linewidth=1)
            self.axes[2, 1].set_ylabel('Throughput (pkts/TTI)')

        # Add legend to first plot
        self.axes[0, 0].legend(loc='upper left', fontsize=8)

        plt.tight_layout()

    def run(self):
        """Start the live monitoring."""
        ani = FuncAnimation(self.fig, self.update_plot, interval=1000, cache_frame_data=False)
        plt.show()

def find_latest_db(base_dir="logs"):
    """Find the most recent database file."""
    db_files = []
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith('.db'):
                full_path = os.path.join(root, f)
                db_files.append((os.path.getmtime(full_path), full_path))

    if not db_files:
        return None

    db_files.sort(reverse=True)
    return db_files[0][1]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Live UE Metrics Monitor - AoI Analysis')
    parser.add_argument('--db', type=str, help='Path to SQLite database')
    parser.add_argument('--mode', type=str, default='full', choices=['full', 'window'],
                       help='Display mode: full history or moving window (default: full)')
    parser.add_argument('--window', type=int, default=500,
                       help='Window size in TTIs when using window mode (default: 500)')

    args = parser.parse_args()

    db_path = args.db
    if not db_path:
        db_path = find_latest_db()
        if db_path:
            print(f"Auto-detected database: {db_path}")
        else:
            print("No database found. Please specify --db path")
            exit(1)

    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        exit(1)

    monitor = LiveMetricsMonitor(db_path, mode=args.mode, window_size=args.window)
    print(f"Starting live monitor for {db_path}")
    print(f"Display mode: {args.mode}")
    if args.mode == 'window':
        print(f"Window size: {args.window} TTIs")
    monitor.run()
