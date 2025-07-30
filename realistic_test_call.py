# realistic_test_call.py

import socket
import time
import uuid
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
from datetime import datetime
import statistics

class CallResult:
    """Her bir çağrının sonucunu tutmak için bir sınıf."""
    def __init__(self, caller_id, success=False, error=None, duration=0, anons_id=""):
        self.caller_id = caller_id
        self.success = success
        self.error = error
        self.duration = duration
        self.anons_id = anons_id

def generate_sip_packet(method: str, target_host: str, target_port: int,
                        caller_id: str, destination: str, local_ip: str, local_port: int,
                        call_id: str, from_tag: str, cseq: int) -> str:
    """
    Belirtilen metoda göre (INVITE, BYE) bir SIP paketi oluşturur.
    (Bu kısım semboliktir, asıl yük gRPC üzerinden media-service'e gider)
    """
    branch = f"z9hG4bK-{uuid.uuid4().hex}"
    sdp_body = ""
    if method == "INVITE":
        sdp_ip = local_ip if local_ip != '0.0.0.0' else get_routable_ip(target_host)
        sdp_body = (
            "v=0\r\n"
            f"o=- {int(time.time())} {int(time.time())} IN IP4 {sdp_ip}\r\n"
            "s=Realistic Stress Test Call\r\n"
            f"c=IN IP4 {sdp_ip}\r\n"
            "t=0 0\r\n"
            f"m=audio {local_port + 2} RTP/AVP 0\r\n"
            "a=rtpmap:0 PCMU/8000\r\n"
        )
    request_line = f"{method} sip:{destination}@{target_host}:{target_port} SIP/2.0"
    headers = [
        f"Via: SIP/2.0/UDP {local_ip}:{local_port};branch={branch};rport",
        "Max-Forwards: 70", f"From: \"Realistic Test\" <sip:{caller_id}@{local_ip}>;tag={from_tag}",
        f"To: <sip:{destination}@{target_host}>", f"Call-ID: {call_id}",
        f"CSeq: {cseq} {method}", f"Contact: <sip:{caller_id}@{local_ip}:{local_port}>",
        "User-Agent: Sentiric Realistic Test Agent", "Content-Type: application/sdp",
        f"Content-Length: {len(sdp_body)}",
    ]
    return "\r\n".join([request_line] + headers) + "\r\n\r\n" + sdp_body

def get_routable_ip(target_host='8.8.8.8'):
    """Hedefe ulaşmak için kullanılacak yerel IP'yi bulur."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((target_host, 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def run_realistic_call_flow(caller_id, destination_number, host, port, local_port, base_duration, anons_list):
    """
    Tek bir kullanıcının daha gerçekçi çağrı akışını simüle eder.
    """
    call_start_time = time.monotonic()
    
    call_id = f"{uuid.uuid4()}"
    from_tag = f"{random.randint(100000, 999999)}"
    anons_to_play = random.choice(anons_list)
    actual_duration = random.uniform(base_duration * 0.4, base_duration * 1.2)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    is_localhost_target = host in ['127.0.0.1', 'localhost']
    local_bind_ip = '127.0.0.1' if is_localhost_target else '0.0.0.0'
    sip_message_ip = '127.0.0.1' if is_localhost_target else get_routable_ip(host)

    try:
        sock.bind((local_bind_ip, local_port))
        sock.settimeout(10)

        # SIP-Signaling servisine giden INVITE (sembolik)
        # Gerçek senaryoda bu servis media-service'i tetikler.
        # Biz burada destination_number'ı kullanıyoruz.
        invite_packet = generate_sip_packet(
            "INVITE", host, port, caller_id, destination_number,
            sip_message_ip, local_port, call_id, from_tag, 1
        )
        sock.sendto(invite_packet.encode('utf-8'), (host, port))
        
        data, addr = sock.recvfrom(1024)

        time.sleep(actual_duration)

        bye_packet = generate_sip_packet(
            "BYE", host, port, caller_id, destination_number,
            sip_message_ip, local_port, call_id, from_tag, 2
        )
        sock.sendto(bye_packet.encode('utf-8'), (host, port))
        
        end_time = time.monotonic()
        return CallResult(caller_id, success=True, duration=end_time - call_start_time, anons_id=anons_to_play)

    except socket.timeout:
        end_time = time.monotonic()
        return CallResult(caller_id, success=False, error="Socket timeout", duration=end_time - call_start_time, anons_id=anons_to_play)
    except Exception as e:
        end_time = time.monotonic()
        return CallResult(caller_id, success=False, error=str(e), duration=end_time - call_start_time, anons_id=anons_to_play)
    finally:
        sock.close()

def generate_report(args, results, total_time):
    """Test sonuçlarından bir Markdown raporu oluşturur."""
    successful_calls = [r for r in results if r.success]
    failed_calls = [r for r in results if not r.success]
    
    success_rate = (len(successful_calls) / len(results)) * 100 if results else 0
    actual_cps = len(results) / total_time if total_time > 0 else 0
    
    report_filename = f"realistic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write("# Gerçekçi Stres Testi Raporu (Doğal Anatomi)\n\n")
        f.write(f"**Test Zamanı:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Test Parametreleri\n")
        f.write(f"- **Hedef Sunucu:** `{args.host}:{args.port}`\n")
        f.write(f"- **Toplam Çağrı Akışı:** `{args.total_calls}`\n")
        f.write(f"- **Maksimum Eş Zamanlılık (Thread):** `{args.threads}`\n")
        f.write(f"- **Ortalama Çağrı Süresi:** `{args.duration}` saniye (Rastgele dağılımlı)\n")
        f.write(f"- **Hedeflenen Ortalama CPS:** `{args.cps}` (Poisson dağılımlı)\n\n")
        
        f.write("## Özet Sonuçlar\n")
        f.write(f"- **Toplam Süre:** `{total_time:.2f}` saniye\n")
        f.write(f"- **Gerçekleşen Ortalama CPS:** `{actual_cps:.2f}`\n")
        f.write(f"- **Başarılı Çağrı:** `{len(successful_calls)}`\n")
        f.write(f"- **Başarısız Çağrı:** `{len(failed_calls)}`\n")
        f.write(f"- **Başarı Oranı:** `{success_rate:.2f}%`\n\n")
        
        if failed_calls:
            f.write("## Hata Detayları\n")
            error_summary = {}
            for call in failed_calls:
                error_summary[call.error] = error_summary.get(call.error, 0) + 1
            for error, count in sorted(error_summary.items()):
                f.write(f"- `{error}`: **{count}** kez\n")
    
    print(f"\nRapor oluşturuldu: {report_filename}")

def main():
    parser = argparse.ArgumentParser(description="Gerçekçi SIP Stres Testi Aracı (Doğal Anatomi Simülatörü)")
    parser.add_argument("--host", default="127.0.0.1", help="Hedef sunucu IP adresi")
    parser.add_argument("--port", type=int, default=5060, help="Hedef sunucu SIP portu")
    parser.add_argument("--destination", default="902124548590", help="Aranan numara (sembolik)")
    parser.add_argument("--duration", type=int, default=4, help="Ortalama çağrı süresi (saniye)")
    parser.add_argument("--total-calls", type=int, default=500, help="Toplam başlatılacak çağrı akışı sayısı")
    parser.add_argument("--cps", type=int, default=50, help="Saniyede hedeflenen ortalama yeni çağrı sayısı")
    parser.add_argument("--threads", type=int, default=100, help="Maksimum eş zamanlı çağrı yapacak thread sayısı")
    args = parser.parse_args()

    anons_list = [
        "audio/tr/welcome.wav",
        "audio/tr/welcome_guest.wav",
        "audio/tr/system_error.wav",
        "audio/tr/maintenance.wav",
        "audio/tr/non_existent_file.wav"
    ]

    caller_ids = [f"9055{str(100000000+i)[-8:]}" for i in range(args.total_calls)]

    print("Gerçekçi stres testi başlatılıyor...")
    print(f"Parametreler: {args.total_calls} çağrı akışı, {args.threads} max thread, hedef ~{args.cps} CPS")
    
    test_start_time = time.monotonic()
    results = []

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        future_to_caller = {}
        for i, caller_id in enumerate(caller_ids):
            local_port = 7000 + i
            future = executor.submit(
                run_realistic_call_flow,
                caller_id, args.destination, args.host, args.port,
                local_port, args.duration, anons_list
            )
            future_to_caller[future] = caller_id
            
            if args.cps > 0:
                delay = random.expovariate(args.cps)
                time.sleep(delay)

        for i, future in enumerate(as_completed(future_to_caller)):
            caller_id = future_to_caller[future]
            try:
                result = future.result()
                results.append(result)
                status = "BAŞARILI" if result.success else f"BAŞARISIZ ({result.error})"
                print(f"Akış {i+1}/{args.total_calls} tamamlandı: {caller_id} ({result.anons_id}) -> {status}")
            except Exception as exc:
                print(f'{caller_id} bir istisna oluşturdu: {exc}')
                results.append(CallResult(caller_id, success=False, error=str(exc)))

    test_end_time = time.monotonic()
    total_duration = test_end_time - test_start_time
    
    print("\nTest tamamlandı.")
    generate_report(args, results, total_duration)

if __name__ == "__main__":
    main()