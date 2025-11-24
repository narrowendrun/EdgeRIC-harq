#include "edgeric.h"
#include <cstdlib>
#include <sstream>
#include <unordered_set>

// -----------------------------------------------------------------------------
// Static member variable definitions
// -----------------------------------------------------------------------------
std::atomic<uint32_t> edgeric::tti_cnt{0};
uint32_t edgeric::er_ran_index_weights = 0;
uint32_t edgeric::er_ran_index_mcs = 0;

std::map<uint16_t, float>    edgeric::ue_cqis = {};
std::map<uint16_t, float>    edgeric::ue_snrs = {};
std::map<uint16_t, float>    edgeric::rx_bytes = {};
std::map<uint16_t, float>    edgeric::tx_bytes = {};
std::map<uint16_t, uint32_t> edgeric::ue_ul_buffers = {};
std::map<uint16_t, uint32_t> edgeric::ue_dl_buffers = {};
std::map<uint16_t, float>    edgeric::dl_tbs_ues = {};

std::map<uint16_t, bool> edgeric::ul_harq_ack = {};
std::map<uint16_t, bool> edgeric::ul_tx_attempt = {};

std::map<uint16_t, float>   edgeric::weights_recved = {};
std::map<uint16_t, uint8_t> edgeric::mcs_recved = {};

bool edgeric::enable_logging = false;
std::atomic<bool> edgeric::initialized{false};
bool edgeric::send_logging_enabled = false;
std::once_flag edgeric::init_once_flag;
std::mutex edgeric::metrics_mutex;

// -----------------------------------------------------------------------------
// ZeroMQ context and sockets
// -----------------------------------------------------------------------------
zmq::context_t context;
zmq::socket_t publisher(context, ZMQ_PUB);
zmq::socket_t subscriber_weights(context, ZMQ_SUB);
zmq::socket_t subscriber_mcs(context, ZMQ_SUB);

// -----------------------------------------------------------------------------
// Initialization and setup
// -----------------------------------------------------------------------------
void edgeric::init()
{
    const char* enable_log_env = std::getenv("EDGERIC_ENABLE_LOGGING");
    enable_logging = enable_log_env && enable_log_env[0] != '\0';

    const char* send_log_env = std::getenv("EDGERIC_LOG_SEND");
    send_logging_enabled = send_log_env && send_log_env[0] != '\0';
    if (send_logging_enabled) {
        enable_logging = true;
    }

    publisher.bind("tcp://10.53.2.4:5050");

    subscriber_weights.connect("tcp://10.53.2.5:5051");
    subscriber_weights.setsockopt(ZMQ_SUBSCRIBE, "", 0);
    int conflate = 1;
    subscriber_weights.setsockopt(ZMQ_CONFLATE, &conflate, sizeof(conflate));

    subscriber_mcs.connect("tcp://10.53.2.5:5052");
    subscriber_mcs.setsockopt(ZMQ_SUBSCRIBE, "", 0);
    subscriber_mcs.setsockopt(ZMQ_CONFLATE, &conflate, sizeof(conflate));

    initialized.store(true, std::memory_order_release);
}

void edgeric::ensure_initialized()
{
    std::call_once(init_once_flag, []() { init(); });
}

// -----------------------------------------------------------------------------
// HARQ and UL transmission tracking
// -----------------------------------------------------------------------------
void edgeric::set_ul_tx_attempt(uint16_t rnti, bool attempt)
{
    std::lock_guard<std::mutex> lock(metrics_mutex);
    bool& value = ul_tx_attempt[rnti];
    value = value || attempt;
}

void edgeric::set_ul_harq_ack(uint16_t rnti, bool ack)
{
    std::lock_guard<std::mutex> lock(metrics_mutex);
    bool& value = ul_harq_ack[rnti];
    value = value || ack;
}

void edgeric::set_rx_bytes(uint16_t rnti, float bytes)
{
    std::lock_guard<std::mutex> lock(metrics_mutex);
    rx_bytes[rnti] += bytes;
}

void edgeric::set_tx_bytes(uint16_t rnti, float bytes)
{
    std::lock_guard<std::mutex> lock(metrics_mutex);
    tx_bytes[rnti] += bytes;
}

// -----------------------------------------------------------------------------
// Send real-time UE metrics to EdgeRIC
// -----------------------------------------------------------------------------
void edgeric::send_to_er()
{
    ensure_initialized();

    const uint32_t tti_snapshot = tti_cnt.load(std::memory_order_relaxed);

    std::map<uint16_t, float>    ue_cqis_snapshot;
    std::map<uint16_t, float>    ue_snrs_snapshot;
    std::map<uint16_t, float>    rx_bytes_snapshot;
    std::map<uint16_t, float>    tx_bytes_snapshot;
    std::map<uint16_t, uint32_t> ue_ul_buffers_snapshot;
    std::map<uint16_t, uint32_t> ue_dl_buffers_snapshot;
    std::map<uint16_t, float>    dl_tbs_snapshot;
    std::map<uint16_t, bool>     ul_harq_ack_snapshot;
    std::map<uint16_t, bool>     ul_tx_attempt_snapshot;

    {
        std::lock_guard<std::mutex> lock(metrics_mutex);
        ue_cqis_snapshot.swap(ue_cqis);
        ue_snrs_snapshot.swap(ue_snrs);
        rx_bytes_snapshot.swap(rx_bytes);
        tx_bytes_snapshot.swap(tx_bytes);
        ue_ul_buffers_snapshot = ue_ul_buffers;
        ue_dl_buffers_snapshot = ue_dl_buffers;
        dl_tbs_snapshot.swap(dl_tbs_ues);
        ul_harq_ack_snapshot.swap(ul_harq_ack);
        ul_tx_attempt_snapshot.swap(ul_tx_attempt);
    }

    Metrics metrics_msg;
    metrics_msg.set_tti_cnt(tti_snapshot);

    std::unordered_set<uint16_t> rntis;
    auto collect_keys = [&rntis](const auto& m) {
        for (const auto& kv : m) {
            rntis.insert(kv.first);
        }
    };
    
    collect_keys(ue_cqis_snapshot);
    collect_keys(ue_snrs_snapshot);
    collect_keys(rx_bytes_snapshot);
    collect_keys(tx_bytes_snapshot);
    collect_keys(ue_ul_buffers_snapshot);
    collect_keys(ue_dl_buffers_snapshot);
    collect_keys(dl_tbs_snapshot);
    collect_keys(ul_harq_ack_snapshot);
    collect_keys(ul_tx_attempt_snapshot);

    std::ostringstream send_log;
    if (send_logging_enabled) {
        send_log << "[edgeric] send_to_er tti=" << tti_snapshot << " ue_count=" << rntis.size();
    }

    for (uint16_t rnti : rntis) {
        const float cqi      = ue_cqis_snapshot.count(rnti) ? ue_cqis_snapshot[rnti] : 0.0f;
        const float snr      = ue_snrs_snapshot.count(rnti) ? ue_snrs_snapshot[rnti] : 0.0f;
        const float tx_b     = tx_bytes_snapshot.count(rnti) ? tx_bytes_snapshot[rnti] : 0.0f;
        const float rx_b     = rx_bytes_snapshot.count(rnti) ? rx_bytes_snapshot[rnti] : 0.0f;
        const uint32_t dl_bo = ue_dl_buffers_snapshot.count(rnti) ? ue_dl_buffers_snapshot[rnti] : 0;
        const uint32_t ul_bo = ue_ul_buffers_snapshot.count(rnti) ? ue_ul_buffers_snapshot[rnti] : 0;
        const float dl_tbs   = dl_tbs_snapshot.count(rnti) ? dl_tbs_snapshot[rnti] : 0.0f;
        const bool ack       = ul_harq_ack_snapshot.count(rnti) ? ul_harq_ack_snapshot[rnti] : false;
        const bool attempt   = ul_tx_attempt_snapshot.count(rnti) ? ul_tx_attempt_snapshot[rnti] : false;

        UeMetrics* ue_metrics = metrics_msg.add_ue_metrics();
        ue_metrics->set_rnti(rnti);
        ue_metrics->set_cqi(static_cast<uint32_t>(cqi));
        ue_metrics->set_snr(snr);
        ue_metrics->set_tx_bytes(tx_b);
        ue_metrics->set_rx_bytes(rx_b);
        ue_metrics->set_dl_buffer(dl_bo);
        ue_metrics->set_ul_buffer(ul_bo);
        ue_metrics->set_dl_tbs(dl_tbs);
        ue_metrics->set_ul_harq_ack(ack);
        ue_metrics->set_ul_tx_attempt(attempt);

        if (send_logging_enabled) {
            send_log << " | rnti=" << rnti
                     << " cqi=" << cqi
                     << " snr=" << snr
                     << " tx_bytes=" << tx_b
                     << " rx_bytes=" << rx_b
                     << " dl_bo=" << dl_bo
                     << " ul_bo=" << ul_bo
                     << " dl_tbs=" << dl_tbs
                     << " ul_tx_attempt=" << attempt
                     << " ul_harq_ack=" << ack;
        }
    }

    std::string serialized_msg;
    if (!metrics_msg.SerializeToString(&serialized_msg)) {
        std::cerr << "[edgeric] Failed to serialize Metrics message.\n";
        return;
    }

    zmq::message_t zmq_msg(serialized_msg.size());
    memcpy(zmq_msg.data(), serialized_msg.data(), serialized_msg.size());
    publisher.send(zmq_msg, zmq::send_flags::dontwait);

    if (send_logging_enabled) {
        std::cout << send_log.str() << std::endl;
    }
}

// -----------------------------------------------------------------------------
// Receive policy (weights) from EdgeRIC
// -----------------------------------------------------------------------------
void edgeric::get_weights_from_er()
{
    ensure_initialized();
    zmq::message_t recv_message_er;
    zmq::recv_result_t size = subscriber_weights.recv(recv_message_er, zmq::recv_flags::dontwait);

    if (size) {
        SchedulingWeights weights_msg;
        if (weights_msg.ParseFromArray(recv_message_er.data(), recv_message_er.size())) {
            er_ran_index_weights = weights_msg.ran_index();

            float total_weight = 0.0f;
            weights_recved.clear();

            for (int i = 0; i < weights_msg.weights_size(); i += 2) {
                uint16_t rnti = static_cast<uint16_t>(weights_msg.weights(i));
                float weight = weights_msg.weights(i + 1);
                weights_recved[rnti] = weight;
                total_weight += weight;
            }

            if (total_weight > 0.0f) {
                for (auto& kv : weights_recved)
                    kv.second /= total_weight;
            }
        } else {
            std::cerr << "[edgeric] Failed to parse SchedulingWeights message.\n";
        }
    }
}

// -----------------------------------------------------------------------------
// Receive policy (MCS) from EdgeRIC
// -----------------------------------------------------------------------------
void edgeric::get_mcs_from_er()
{
    ensure_initialized();
    zmq::message_t recv_message_er;
    zmq::recv_result_t size = subscriber_mcs.recv(recv_message_er, zmq::recv_flags::dontwait);

    if (size) {
        mcs_control mcs_msg;
        if (mcs_msg.ParseFromArray(recv_message_er.data(), recv_message_er.size())) {
            er_ran_index_mcs = mcs_msg.ran_index();

            mcs_recved.clear();
            for (int i = 0; i < mcs_msg.mcs_size(); i += 2) {
                uint16_t rnti = static_cast<uint16_t>(mcs_msg.mcs(i));
                uint8_t mcs = mcs_msg.mcs(i + 1);
                mcs_recved[rnti] = mcs;
            }
        } else {
            std::cerr << "[edgeric] Failed to parse mcs_control message.\n";
        }
    }
}

// -----------------------------------------------------------------------------
// Policy getters
// -----------------------------------------------------------------------------
bool edgeric::get_weights(uint16_t rnti, float& value)
{
    auto it = weights_recved.find(rnti);
    if (it == weights_recved.end())
        return false;
    value = it->second;
    return true;
}

bool edgeric::get_mcs(uint16_t rnti, uint8_t& value)
{
    auto it = mcs_recved.find(rnti);
    if (it == mcs_recved.end())
        return false;
    value = it->second;
    return true;
}

// -----------------------------------------------------------------------------
// Logging helper (optional for debugging)
// -----------------------------------------------------------------------------
void edgeric::printmyvariables()
{
    if (!enable_logging)
        return;

    const uint32_t tti_snapshot = tti_cnt.load(std::memory_order_relaxed);

    std::map<uint16_t, float>    ue_cqis_snapshot;
    std::map<uint16_t, float>    ue_snrs_snapshot;
    std::map<uint16_t, float>    rx_bytes_snapshot;
    std::map<uint16_t, float>    tx_bytes_snapshot;
    std::map<uint16_t, uint32_t> ue_ul_buffers_snapshot;
    std::map<uint16_t, uint32_t> ue_dl_buffers_snapshot;
    std::map<uint16_t, float>    dl_tbs_snapshot;
    std::map<uint16_t, bool>     ul_tx_attempt_snapshot;
    std::map<uint16_t, bool>     ul_harq_ack_snapshot;

    {
        std::lock_guard<std::mutex> lock(metrics_mutex);
        ue_cqis_snapshot       = ue_cqis;
        ue_snrs_snapshot       = ue_snrs;
        rx_bytes_snapshot      = rx_bytes;
        tx_bytes_snapshot      = tx_bytes;
        ue_ul_buffers_snapshot = ue_ul_buffers;
        ue_dl_buffers_snapshot = ue_dl_buffers;
        dl_tbs_snapshot        = dl_tbs_ues;
        ul_tx_attempt_snapshot = ul_tx_attempt;
        ul_harq_ack_snapshot   = ul_harq_ack;
    }

    std::ofstream logfile("log.txt", std::ios_base::app);
    if (!logfile.is_open())
        return;

    logfile << "TTI: " << tti_snapshot
            << ", Weights Index: " << er_ran_index_weights
            << ", MCS Index: " << er_ran_index_mcs << "\n";

    for (const auto& cqi_pair : ue_cqis_snapshot) {
        uint16_t rnti = cqi_pair.first;
        logfile << "RNTI: " << rnti
                << " CQI: " << ue_cqis_snapshot[rnti]
                << " SNR: " << (ue_snrs_snapshot.count(rnti) ? ue_snrs_snapshot[rnti] : 0)
                << " TxBytes: " << (tx_bytes_snapshot.count(rnti) ? tx_bytes_snapshot[rnti] : 0)
                << " RxBytes: " << (rx_bytes_snapshot.count(rnti) ? rx_bytes_snapshot[rnti] : 0)
                << " ULBuf: " << (ue_ul_buffers_snapshot.count(rnti) ? ue_ul_buffers_snapshot[rnti] : 0)
                << " DLTBS: " << (dl_tbs_snapshot.count(rnti) ? dl_tbs_snapshot[rnti] : 0)
                << " UL_TX_ATTEMPT: " << (ul_tx_attempt_snapshot.count(rnti) ? ul_tx_attempt_snapshot[rnti] : 0)
                << " UL_HARQ_ACK: " << (ul_harq_ack_snapshot.count(rnti) ? ul_harq_ack_snapshot[rnti] : 0)
                << std::endl;
    }

    logfile.close();
}
