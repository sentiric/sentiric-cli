import socket
import time

# Ayarlar
TARGET_HOST = "127.0.0.1"
TARGET_PORT = 5060
CALLER_ID = "1001"
DESTINATION = "902124548590"

# Çok temel bir SIP INVITE mesajı oluştur
# Not: Bu, gerçek bir SIP stack'inin yerini tutmaz ama test için yeterlidir.
# Call-ID ve branch gibi değerler her seferinde rastgele olmalıdır.
call_id = f"{time.time()}@sentiric.cli"
branch = f"z9hG4bK-{time.time()}"

sip_invite_message = f"""
INVITE sip:{DESTINATION}@{TARGET_HOST} SIP/2.0
Via: SIP/2.0/UDP 127.0.0.1:5068;branch={branch}
Max-Forwards: 70
From: <sip:{CALLER_ID}@{TARGET_HOST}>;tag=12345
To: <sip:{DESTINATION}@{TARGET_HOST}>
Call-ID: {call_id}
CSeq: 1 INVITE
Contact: <sip:{CALLER_ID}@127.0.0.1:5068>
Content-Type: application/sdp
Content-Length: 0

""".strip().replace('\n', '\r\n') + "\r\n\r\n"

# UDP soketi oluştur ve mesajı gönder
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    print(f"-> {DESTINATION} numarasına test çağrısı gönderiliyor...")
    sock.sendto(sip_invite_message.encode(), (TARGET_HOST, TARGET_PORT))

    # Sunucudan gelen yanıtı dinle
    print("<- Sunucudan yanıt bekleniyor...")
    data, addr = sock.recvfrom(1024)
    response = data.decode()
    print("\n--- Alınan Yanıt ---")
    print(response)
    print("--------------------")

    if "SIP/2.0 200 OK" in response:
        print("✅ TEST BAŞARILI: Çağrı başarıyla kuruldu!")
    else:
        print("❌ TEST BAŞARISIZ: Beklenen 200 OK yanıtı alınamadı.")

finally:
    sock.close()