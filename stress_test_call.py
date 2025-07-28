# DOSYA: sentiric-cli/stress_test_call.py (Windows Uyumluluk Düzeltmesi Eklendi)

import socket
import time
import uuid
import random
import argparse
import sys

# --- Test Ayarları ---
DEFAULT_TARGET_HOST = "127.0.0.1"
DEFAULT_TARGET_PORT = 5060
DEFAULT_CALLER_ID = "905548777858"
DEFAULT_DESTINATION = "902124548590"
DEFAULT_LOCAL_PORT = 5068


def generate_sip_packet(method: str, target_host: str, target_port: int,
                        caller_id: str, destination: str, local_ip: str, local_port: int,
                        call_id: str, from_tag: str, cseq: int) -> str:
    """
    Belirtilen metoda göre (INVITE, BYE) bir SIP paketi oluşturur.
    """
    branch = f"z9hG4bK-{uuid.uuid4().hex}"
    
    sdp_body = ""
    if method == "INVITE":
        # SDP'de kullanılacak IP adresinin, paketin gönderileceği arayüzün IP'si olması önemlidir.
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
        "Max-Forwards: 70",
        f"From: \"Sentiric CLI\" <sip:{caller_id}@{local_ip}>;tag={from_tag}",
        f"To: <sip:{destination}@{target_host}>",
        f"Call-ID: {call_id}",
        f"CSeq: {cseq} {method}",
        f"Contact: <sip:{caller_id}@{local_ip}:{local_port}>",
        "User-Agent: Sentiric CLI Test Agent",
        "Allow: INVITE, ACK, CANCEL, OPTIONS, BYE, REFER, SUBSCRIBE, NOTIFY, INFO, PUBLISH",
        f"Content-Length: {len(sdp_body)}",
    ]
    
    if sdp_body:
        headers.append("Content-Type: application/sdp")

    return "\r\n".join([request_line] + headers) + "\r\n\r\n" + sdp_body

def get_routable_ip(target_host='8.8.8.8'):
    """
    Belirtilen hedefe ulaşmak için kullanılacak en olası yerel IP adresini bulur.
    '0.0.0.0' veya '127.0.0.1' gibi adreslerden kaçınır.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((target_host, 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def run_single_call(args):
    """Tek bir arama yapar ve sonlandırır."""
    call_id = str(uuid.uuid4())
    from_tag = str(random.randint(100000, 999999))
    
    # --- KRİTİK DÜZELTME ---
    # Eğer hedef localhost ise, biz de localhost'tan (127.0.0.1) çıkış yapmalıyız.
    # Eğer hedef dış bir IP ise, dışarıya çıkan IP'mizi kullanmalıyız.
    # Windows'ta genellikle '0.0.0.0' (tüm arayüzler) daha stabil çalışır.
    is_localhost_target = args.host in ['127.0.0.1', 'localhost']
    local_bind_ip = '127.0.0.1' if is_localhost_target else '0.0.0.0'
    
    # SIP mesajlarının içine yazacağımız IP adresi '0.0.0.0' olamaz.
    # Bu yüzden, dışarıya yönlendirilebilir (routable) IP'mizi buluyoruz.
    sip_message_ip = '127.0.0.1' if is_localhost_target else get_routable_ip(args.host)
    
    # --- BİTTİ ---

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((local_bind_ip, args.local_port))

    print(f"📞 Arama Başlatılıyor...")
    print(f"   Call-ID: {call_id}")
    print(f"   Kimden: {args.caller_id} -> Kime: {args.destination}")
    print(f"   Hedef: {args.host}:{args.port}")
    print(f"   Yerel Arayüz (Binding): {local_bind_ip}:{args.local_port}")
    print(f"   SIP Mesaj IP'si: {sip_message_ip}")

    try:
        # 1. INVITE Gönder
        invite_packet = generate_sip_packet(
            "INVITE", args.host, args.port, args.caller_id, args.destination,
            sip_message_ip, args.local_port, call_id, from_tag, 1
        )
        sock.sendto(invite_packet.encode('utf-8'), (args.host, args.port))
        print("   -> INVITE gönderildi.")

        print(f"   ... {args.duration} saniye bekleniyor ...")
        time.sleep(args.duration)

        # 2. BYE Gönder
        bye_packet = generate_sip_packet(
            "BYE", args.host, args.port, args.caller_id, args.destination,
            sip_message_ip, args.local_port, call_id, from_tag, 2
        )
        sock.sendto(bye_packet.encode('utf-8'), (args.host, args.port))
        print("   <- BYE gönderildi.")
        print("✅ Arama başarıyla sonlandırıldı.")

    except Exception as e:
        print(f"❌ HATA: {e}", file=sys.stderr)
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser(
        description="Sentiric Platformu için SIP Stres Testi ve Arama Simülatörü.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--host", default=DEFAULT_TARGET_HOST, help="Hedef SIP sunucusunun (gateway) IP adresi.")
    parser.add_argument("--port", type=int, default=DEFAULT_TARGET_PORT, help="Hedef SIP sunucusunun portu.")
    parser.add_argument("--caller-id", default=DEFAULT_CALLER_ID, help="Arayan numara (veritabanında olmalı).")
    parser.add_argument("--destination", default=DEFAULT_DESTINATION, help="Aranan numara.")
    parser.add_argument("--local-port", type=int, default=DEFAULT_LOCAL_PORT, help="İstemcinin yanıtları dinleyeceği yerel port.")
    parser.add_argument("--duration", type=int, default=5, help="Her bir aramanın ne kadar süre açık kalacağı (saniye).")
    parser.add_argument("--repeat", type=int, default=1, help="Testin kaç defa tekrarlanacağı. Stres testi için yüksek bir değer girin (örn: 100).")
    parser.add_argument("--delay", type=int, default=1, help="Tekrarlanan aramalar arasındaki bekleme süresi (saniye).")

    args = parser.parse_args()

    print("--- Sentiric SIP Test Aracı Başlatıldı ---")

    for i in range(args.repeat):
        print(f"\n--- Test Döngüsü [{i + 1}/{args.repeat}] ---")
        try:
            # Her döngüde farklı bir yerel port kullanmak çakışmaları önleyebilir
            args.local_port = DEFAULT_LOCAL_PORT + i 
            run_single_call(args)
        except OSError as e:
            if "Only one usage of each socket address" in str(e):
                print(f"   ⚠️  UYARI: Port {args.local_port} hala kullanımda. Bir sonraki port denenecek.", file=sys.stderr)
                continue # Bir sonraki döngüye geç
            else:
                raise # Başka bir hataysa programı durdur
        
        if i + 1 < args.repeat:
            print(f"   ... Sonraki döngü için {args.delay} saniye bekleniyor ...")
            time.sleep(args.delay)
    
    print("\n--- Tüm Test Döngüleri Tamamlandı ---")

if __name__ == "__main__":
    main()