import socket
import time
import docker
import threading
from queue import Queue

# --- Test Ayarları ---
TARGET_HOST = "127.0.0.1"
TARGET_PORT = 5060
CALLER_ID = "05548777858"
DESTINATION = "02124548590"

# --- Beklenen Log Mesajları ---
EXPECTED_SIP_LOG = f"Olay 'call.events' kuyruğuna yayınlandı"
EXPECTED_AGENT_LOG = "Yeni Olay Alındı!"

# --- Docker Konteyner Adları ---
SIP_CONTAINER_NAME = "sentiric_sip_signaling"
AGENT_CONTAINER_NAME = "sentiric_agent_service"

def log_listener(container_name, log_queue, stop_event):
    """Belirtilen konteynerin loglarını dinler ve bir kuyruğa yazar."""
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        print(f"👂 {container_name} konteyner logları dinleniyor...")
        for log in container.logs(stream=True, follow=True):
            if stop_event.is_set():
                break
            log_queue.put(log.decode('utf-8').strip())
    except docker.errors.NotFound:
        print(f"❌ HATA: '{container_name}' adında bir konteyner bulunamadı. Lütfen 'docker compose ps' ile kontrol edin.")
        log_queue.put(f"ERROR_CONTAINER_NOT_FOUND: {container_name}")
    except Exception as e:
        print(f"❌ Log dinleyicide hata: {e}")
        log_queue.put(f"ERROR_UNKNOWN: {e}")

def generate_sip_invite():
    """Test için temel bir SIP INVITE mesajı oluşturur."""
    call_id = f"{time.time()}@sentiric.cli"
    branch = f"z9hG4bK-{time.time()}"
    return (
        f"INVITE sip:{DESTINATION}@{TARGET_HOST} SIP/2.0\r\n"
        f"Via: SIP/2.0/UDP {TARGET_HOST}:5068;branch={branch}\r\n"
        f"Max-Forwards: 70\r\n"
        f"From: <sip:{CALLER_ID}@{TARGET_HOST}>;tag=cli-test-tag\r\n"
        f"To: <sip:{DESTINATION}@{TARGET_HOST}>\r\n"
        f"Call-ID: {call_id}\r\n"
        f"CSeq: 1 INVITE\r\n"
        f"Contact: <sip:{CALLER_ID}@{TARGET_HOST}:5068>\r\n"
        "Content-Type: application/sdp\r\n"
        "Content-Length: 0\r\n\r\n"
    )

def main():
    """Ana test fonksiyonu."""
    sip_log_queue = Queue()
    agent_log_queue = Queue()
    stop_event = threading.Event()

    # Log dinleyicilerini ayrı thread'lerde başlat
    sip_listener_thread = threading.Thread(target=log_listener, args=(SIP_CONTAINER_NAME, sip_log_queue, stop_event))
    agent_listener_thread = threading.Thread(target=log_listener, args=(AGENT_CONTAINER_NAME, agent_log_queue, stop_event))
    
    sip_listener_thread.start()
    agent_listener_thread.start()

    time.sleep(2) # Dinleyicilerin başlaması için kısa bir bekleme

    # SIP INVITE mesajını gönder
    sip_message = generate_sip_invite()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        print(f"\n📞 {DESTINATION} numarasına test çağrısı gönderiliyor...")
        sock.sendto(sip_message.encode(), (TARGET_HOST, TARGET_PORT))
    finally:
        sock.close()

    # Logları kontrol et
    sip_event_found = False
    agent_event_found = False
    start_time = time.time()
    timeout = 10 # saniye

    print("⏳ Loglarda beklenen olaylar kontrol ediliyor...")

    while time.time() - start_time < timeout:
        # SIP loglarını kontrol et
        while not sip_log_queue.empty():
            log_line = sip_log_queue.get()
            if EXPECTED_SIP_LOG in log_line:
                print(f"✅ [SIP-SIGNALING] Başarılı: Olay RabbitMQ'ya yayınlandı.")
                sip_event_found = True

        # Agent loglarını kontrol et
        while not agent_log_queue.empty():
            log_line = agent_log_queue.get()
            if EXPECTED_AGENT_LOG in log_line:
                print(f"✅ [AGENT-SERVICE] Başarılı: Olay RabbitMQ'dan tüketildi.")
                agent_event_found = True
        
        if sip_event_found and agent_event_found:
            break
        time.sleep(0.1)

    # Sonucu raporla
    stop_event.set() # Thread'leri durdur
    print("\n--- 🏁 Test Sonucu ---")
    if sip_event_found and agent_event_found:
        print("🏆🏆🏆 MILESTONE 4 TESTİ BAŞARILI! 🏆🏆🏆")
        print("Asenkron olay akışı (SIP -> RabbitMQ -> Agent) doğrulandı.")
    else:
        print("❌❌❌ TEST BAŞARISIZ! ❌❌❌")
        if not sip_event_found:
            print(f"- [HATA] '{SIP_CONTAINER_NAME}' loglarında beklenen '{EXPECTED_SIP_LOG}' mesajı bulunamadı.")
        if not agent_event_found:
            print(f"- [HATA] '{AGENT_CONTAINER_NAME}' loglarında beklenen '{EXPECTED_AGENT_LOG}' mesajı bulunamadı.")

if __name__ == "__main__":
    main()