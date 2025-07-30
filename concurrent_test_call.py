import socket
import time
import uuid
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
from datetime import datetime
import statistics

# --- (generate_sip_packet ve get_routable_ip fonksiyonları aynı kalacak) ---

def generate_sip_packet(method: str, target_host: str, target_port: int,
                        caller_id: str, destination: str, local_ip: str, local_port: int,
                        call_id: str, from_tag: str, cseq: int) -> str:
    branch = f"z9hG4bK-{uuid.uuid4().hex}"
    sdp_body = ""
    if method == "INVITE":
        sdp_ip = local_ip if local_ip != '0.0.0.0' else get_routable_ip(target_host)
        sdp_body = (
            "v=0\r\n"
            f"o=- {int(time.time())} {int(time.time())} IN IP4 {sdp_ip}\r\n"
            "s=Sentiric CLI Test Call\r\n"
            f"c=IN IP4 {sdp_ip}\r\n"
            "t=0 0\r\n"
            f"m=audio {local_port + 2} RTP/AVP 0\r\n"
            "a=rtpmap:0 PCMU/8000\r\n"
        )
    request_line = f"{method} sip:{destination}@{target_host}:{target_port} SIP/2.0"
    headers = [
        f"Via: SIP/2.0/UDP {local_ip}:{local_port};branch={branch};rport",
        "Max-Forwards: 70", f"From: \"Sentiric CLI\" <sip:{caller_id}@{local_ip}>;tag={from_tag}",
        f"To: <sip:{destination}@{target_host}>", f"Call-ID: {call_id}",
        f"CSeq: {cseq} {method}", f"Contact: <sip:{caller_id}@{local_ip}:{local_port}>",
        "User-Agent: Sentiric CLI Test Agent", "Content-Type: application/sdp",
        f"Content-Length: {len(sdp_body)}",
    ]
    return "\r\n".join([request_line] + headers) + "\r\n\r\n" + sdp_body

def get_routable_ip(target_host='8.8.8.8'):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((target_host, 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

# --- Değişiklikler Burada Başlıyor ---

class CallResult:
    """Her bir çağrının sonucunu tutmak için bir sınıf."""
    def __init__(self, caller_id, success=False, error=None, duration=0):
        self.caller_id = caller_id
        self.success = success
        self.error = error
        self.duration = duration

def run_single_call(caller_id, destination, host, port, local_port, duration):
    """
    Tek bir çağrı yapar ve sonucunu CallResult nesnesi olarak döndürür.
    """
    start_time = time.monotonic()
    
    call_id = str(uuid.uuid4())
    from_tag = str(random.randint(100000, 999999))

    is_localhost_target = host in ['127.0.0.1', 'localhost']
    local_bind_ip = '127.0.0.1' if is_localhost_target else '0.0.0.0'
    sip_message_ip = '127.0.0.1' if is_localhost_target else get_routable_ip(host)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        sock.bind((local_bind_ip, local_port))
        
        # Timeout ekleyerek sunucudan yanıt gelmemesi durumunu yönetelim
        sock.settimeout(duration + 2) # Çağrı süresinden 2 saniye fazla bekle

        # INVITE gönder
        invite_packet = generate_sip_packet(
            "INVITE", host, port, caller_id, destination,
            sip_message_ip, local_port, call_id, from_tag, 1
        )
        sock.sendto(invite_packet.encode('utf-8'), (host, port))
        
        # Basit bir yanıt bekleme (Gerçek bir SIP client'ı 200 OK bekler)
        # Bu, sunucunun canlı olup olmadığını anlamamıza yardımcı olur.
        # Bu kısım olmadan da çalışır, ama hata tespiti için faydalı.
        data, addr = sock.recvfrom(1024) 

        time.sleep(duration)

        # BYE gönder
        bye_packet = generate_sip_packet(
            "BYE", host, port, caller_id, destination,
            sip_message_ip, local_port, call_id, from_tag, 2
        )
        sock.sendto(bye_packet.encode('utf-8'), (host, port))
        
        end_time = time.monotonic()
        return CallResult(caller_id, success=True, duration=end_time - start_time)

    except socket.timeout:
        end_time = time.monotonic()
        return CallResult(caller_id, success=False, error="Socket timeout (sunucudan yanıt alınamadı)", duration=end_time - start_time)
    except Exception as e:
        end_time = time.monotonic()
        return CallResult(caller_id, success=False, error=str(e), duration=end_time - start_time)
    finally:
        sock.close()

# concurrent_test_call.py içindeki generate_report fonksiyonu

def generate_report(args, results, total_time):
    """
    Test sonuçlarından bir Markdown raporu oluşturur.
    """
    successful_calls = [r for r in results if r.success]
    failed_calls = [r for r in results if not r.success]
    
    success_rate = (len(successful_calls) / len(results)) * 100 if results else 0
    calls_per_second = len(results) / total_time if total_time > 0 else 0
    
    report_filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    # === DÜZELTME: encoding="utf-8" eklendi ===
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write("# Stres Testi Performans Raporu\n\n")
        f.write(f"**Test Zamanı:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Test Parametreleri\n")
        f.write(f"- **Hedef Sunucu:** `{args.host}:{args.port}`\n")
        f.write(f"- **Toplam Çağrı:** `{args.repeat}`\n")
        f.write(f"- **Eş Zamanlılık (Thread):** `{args.threads}`\n")
        f.write(f"- **Çağrı Süresi:** `{args.duration}` saniye\n")
        f.write(f"- **Çağrılar Arası Gecikme:** `{args.delay}` saniye\n\n")
        
        f.write("## Özet Sonuçlar\n")
        f.write(f"- **Toplam Süre:** `{total_time:.2f}` saniye\n")
        f.write(f"- **Saniyedeki Ortalama Çağrı (CPS):** `{calls_per_second:.2f}`\n")
        f.write(f"- **Başarılı Çağrı:** `{len(successful_calls)}`\n")
        f.write(f"- **Başarısız Çağrı:** `{len(failed_calls)}`\n")
        f.write(f"- **Başarı Oranı:** `{success_rate:.2f}%`\n\n")
        
        if failed_calls:
            f.write("## Hata Detayları\n")
            error_summary = {}
            for call in failed_calls:
                error_summary[call.error] = error_summary.get(call.error, 0) + 1
            
            for error, count in error_summary.items():
                f.write(f"- `{error}`: **{count}** kez\n")
    
    print(f"\nRapor oluşturuldu: {report_filename}")

def main():
    parser = argparse.ArgumentParser(description="SIP Stres Testi Aracı")
    parser.add_argument("--host", default="127.0.0.1", help="Hedef sunucu IP adresi")
    parser.add_argument("--port", type=int, default=5060, help="Hedef sunucu SIP portu")
    parser.add_argument("--destination", default="902124548590", help="Aranan numara")
    parser.add_argument("--duration", type=int, default=5, help="Her çağrının süresi (saniye)")
    parser.add_argument("--repeat", type=int, default=100, help="Toplam yapılacak çağrı sayısı")
    parser.add_argument("--delay", type=float, default=0.1, help="Yeni çağrı başlatmaları arasındaki gecikme (saniye)")
    parser.add_argument("--threads", type=int, default=20, help="Eş zamanlı çağrı yapacak thread sayısı")
    args = parser.parse_args()

    caller_ids = [f"9055{str(100000000+i)[-8:]}" for i in range(args.repeat)]

    print("Stres testi başlatılıyor...")
    print(f"Parametreler: {args.repeat} çağrı, {args.threads} thread, {args.duration}s süre, {args.delay}s gecikme")
    
    test_start_time = time.monotonic()
    results = []

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        future_to_caller = {}
        for i, caller_id in enumerate(caller_ids):
            local_port = 6000 + i  # Port çakışması olmaması için daha güvenli bir aralık
            future = executor.submit(
                run_single_call,
                caller_id, args.destination, args.host, args.port,
                local_port, args.duration
            )
            future_to_caller[future] = caller_id
            time.sleep(args.delay)

        for i, future in enumerate(as_completed(future_to_caller)):
            caller_id = future_to_caller[future]
            try:
                result = future.result()
                results.append(result)
                status = "BAŞARILI" if result.success else f"BAŞARISIZ ({result.error})"
                print(f"Çağrı {i+1}/{args.repeat} tamamlandı: {caller_id} -> {status}")
            except Exception as exc:
                print(f'{caller_id} bir istisna oluşturdu: {exc}')
                results.append(CallResult(caller_id, success=False, error=str(exc)))

    test_end_time = time.monotonic()
    total_duration = test_end_time - test_start_time
    
    print("\nTest tamamlandı.")
    generate_report(args, results, total_duration)

if __name__ == "__main__":
    main()

# python concurrent_test_call.py --threads 1 --repeat 1 --delay 1 --host 127.0.0.1 --port 5060