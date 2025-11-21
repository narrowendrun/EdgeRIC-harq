import csv
import json
import os
import numpy as np
from collections import defaultdict
from newoptimizer import optimize_aoi_fixed_mu  # Assumes function with fixed mu=q, returns mu, sigma2, etc.

class VWDPolicy:
    def __init__(self, manual_q=None):
        self.p_history = defaultdict(list)   # RNTI: [p_i at each TTI]
        self.ack_history = defaultdict(list) # RNTI: [ul_harq_ack at each TTI]
        self.attempt_history = defaultdict(list) # RNTI: [ul_tx_attempt at each TTI]
        self.Z_history = defaultdict(list)   # RNTI: [Z_i(t), per-TTI ACK's sum]
        self.q = np.array(manual_q) if manual_q is not None else None
        self.optim_params = None             # Holds {'mu': ..., 'sigma2': ...}
        self.last_update_tti = 0
        self.log_file_path = os.path.join(os.path.dirname(__file__), "vwd_policy_decisions.csv")
        self._init_log_file()

    def step(self, rantti, uedata):
        """
        Main step function called at each TTI, matching the interface of other algorithms' multi functions.
        Returns weights array of shape (numUEs, 2): [RNTI, weight]
        """
        # Safety check: If no UEs are connected, return empty weights
        if not uedata:
            return []

        rntis = sorted(uedata.keys())
        numues = len(rntis)

        # --- Update histories and empirical reliabilities p_i ---
        for idx, rnti in enumerate(rntis):
            metrics = uedata[rnti]
            # Should be 0 or 1 for current TTI
            ul_harq_ack = int(metrics.get('ul_harq_ack', 0))
            ul_tx_attempt = int(metrics.get('ul_tx_attempt', 1))
            self.ack_history[rnti].append(ul_harq_ack)
            self.attempt_history[rnti].append(ul_tx_attempt)
            self.Z_history[rnti].append(ul_harq_ack) # Z_i(t) = ACK for time t

        # Calculate running p_i for each UE
        p_vec = np.array([
            sum(self.ack_history[rnti]) / max(sum(self.attempt_history[rnti]), 1)
            for rnti in rntis
        ])

        # Decide scheduling threshold for optimizer
        current_q = self.q
        if self.q is None:
            raise ValueError("q vector (manually specified) must be set.")
        
        # Handle dimension mismatch if num UEs != num manual_q entries
        if len(self.q) != numues:
            # If we have fewer UEs than config, slice q. If more, pad or error.
            # Here we slice for safety during startup/teardown
            if numues < len(self.q):
                current_q = self.q[:numues]
            else:
                # Fallback: repeat last q value or handle as error. 
                # For now, let's just resize roughly
                current_q = np.resize(self.q, numues)

        # --- Recompute mu (==q), sigma2 using the optimizer only if p has changed or periodically ---
        if (self.optim_params is None) or (rantti - self.last_update_tti > 100) or (len(self.optim_params['mu']) != numues):
            mu, sigma2, _, _ = optimize_aoi_fixed_mu(p_vec, current_q)
            self.optim_params = {'mu': mu, 'sigma2': sigma2}
            self.last_update_tti = rantti

        # --- Compute VWD Deficit for each UE ---
        d_vec = np.zeros(numues)
        for i, rnti in enumerate(rntis):
            t = len(self.Z_history[rnti])
            # Ensure we access params safely
            mu_i = self.optim_params['mu'][i]
            sigma2_i = self.optim_params['sigma2'][i]
            Z_sum = sum(self.Z_history[rnti])
            d_vec[i] = (t * mu_i - Z_sum) / (np.sqrt(sigma2_i) + 1e-9)

        # --- Schedule: one-hot with '1' for max-deficit UE ---
        weights = np.zeros((numues * 2)) # Corrected shape for flat array [RNTI, W, RNTI, W...]
        
        # Find index of max deficit
        max_i = np.argmax(d_vec)
        
        for i, rnti in enumerate(rntis):
            weights[i*2+0] = rnti
            if i == max_i:
                weights[i*2+1] = 1.0
            else:
                weights[i*2+1] = 0.0

        self._log_decision(rantti, rntis, uedata, weights)
        return weights

    def _init_log_file(self):
        """
        Ensure the CSV log file exists with the appropriate header for decision tracking.
        """
        if not os.path.exists(self.log_file_path):
            with open(self.log_file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['tti', 'rnti', 'weight', 'metrics'])

    def _log_decision(self, tti, rntis, uedata, weights):
        """
        Append UE metrics and scheduling decisions to the CSV log for traceability.
        """
        rows = []
        # weights is flat array [rnti, w, rnti, w]
        for idx, rnti in enumerate(rntis):
            metrics = dict(uedata.get(rnti, {}))
            w = weights[idx*2+1]
            rows.append([
                tti,
                rnti,
                float(w),
                json.dumps(metrics, sort_keys=True),
            ])

        with open(self.log_file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)