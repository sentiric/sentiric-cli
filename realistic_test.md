# Sentiric Media Service - Gerçekçi Stres Testi Raporu (Doğal Anatomi Simülasyonu)

Bu doküman, `sentiric-media-service`'in, bir çağrı merkezinin doğal davranışlarını taklit eden, değişken ve "patlamalı" (bursty) yükler altındaki performansını ölçmek için yapılan testlerin sonuçlarını içerir.

**Test Aracı:** `realistic_test_call.py`

## Test Metodolojisi

Testler, gerçek dünya senaryolarını daha iyi yansıtmak için aşağıdaki davranışları simüle eder:

1.  **Değişken Çağrı Süreleri:** Her çağrının süresi, belirtilen ortalama sürenin etrafında rastgele belirlenir. Bu, "sabırsız" kullanıcıları ve anonsu sonuna kadar dinleyenleri taklit eder.
2.  **Patlamalı Trafik (Poisson Dağılımı):** Yeni çağrılar, saniyede hedeflenen ortalama sayıya (`--cps`) ulaşacak şekilde, düzensiz ve "patlamalı" aralıklarla başlatılır.
3.  **Çeşitli Anons İstekleri:** Her çağrı, önceden tanımlanmış bir listeden rastgele bir anons dosyası talep eder. Bu liste, hata durumlarını test etmek için var olmayan bir dosya da içerir.

Bu metodoloji, sistemin kararlılığını, kaynak yönetimini (özellikle port karantina mekanizmasını) ve önbellekleme stratejisini daha zorlu ve gerçekçi koşullar altında test etmeyi amaçlar.

**Test Ortamı:**
- **Servis:** `sentiric-media-service` (Docker Konteyneri)
- **Donanım:** [Testin çalıştırıldığı makinenin CPU/RAM bilgilerini buraya yazın]
- **İşletim Sistemi:** [örn: Windows 11 Pro with Docker Desktop]

---

## Test Sonuçları

### Senaryo A: "Yoğun Pazartesi Sabahı"

- **Amaç:** Orta-yüksek yoğunluktaki, patlamalı bir trafiği sistemin nasıl karşıladığını görmek.
- **Servis Konfigürasyonu:**
  - `cpus: 0.5`
  - `mem_limit: 256m`
- **Test Komutu:** `python realistic_test_call.py --total-calls 500 --cps 50 --threads 100 --duration 4`
- **Rapor Özeti:**
  - **Test Zamanı:** 2025-07-30 17:58:46
  - **Toplam Süre:** 20.23 saniye
  - **Gerçekleşen Ortalama CPS:** 24.71
  - **Başarı Oranı:** %100.00
- **`docker stats` Gözlemleri:**
  - **Ortalama CPU Kullanımı:** ~70%
  - **Maksimum CPU Kullanımı (Patlama Anları):** ~90%
  - **Bellek Kullanımı:** ~35 MB (5 farklı anons önbelleğe alındıktan sonra)
- **Yorum:** Sistem, saniyede ortalama 25 çağrılık patlamalı bir yükü %100 başarı oranıyla ve CPU limitlerine dayanmadan rahatlıkla yönetmiştir. Bu konfigürasyon, bu trafik seviyesi için güvenli ve stabildir.

### Senaryo B: "Kara Cuma - Limit Testi"

- **Amaç:** Sistemin limitlerini zorlayarak, yüksek yoğunluktaki patlamalı trafikte "kırılma noktasını" bulmak.
- **Servis Konfigürasyonu:**
  - `cpus: 0.5`
- **Test Komutu:** `python realistic_test_call.py --total-calls 2000 --cps 150 --threads 300 --duration 4`
- **Rapor Özeti:**
  - **Test Zamanı:** 2025-07-30 17:59:35
  - **Toplam Süre:** 38.55 saniye
  - **Gerçekleşen Ortalama CPS:** 51.88
  - **Başarı Oranı:** %100.00
- **`docker stats` Gözlemleri:**
  - **Ortalama CPU Kullanımı:** ~98%
  - **Maksimum CPU Kullanımı (Patlama Anları):** %100 (Sürekli)
  - **Bellek Kullanımı:** ~35 MB
- **Yorum:** Hedeflenen 150 CPS'e ulaşılamamış, sistem saniyede yaklaşık 52 çağrıda stabilize olmuştur. Bu, 0.5 vCPU'nun bu servis için pratik üst limiti olduğunu göstermektedir. En önemlisi, sistem bu limite ulaştığında dahi **hiçbir çağrıyı düşürmemiş** ve gelen tüm istekleri %100 başarıyla tamamlamıştır. Bu, sistemin aşırı yük altında son derece kararlı olduğunu kanıtlamaktadır.
---

## Genel Değerlendirme ve Sonuçlar

[Tüm testler tamamlandıktan sonra buraya genel bir özet ve çıkarımlar yazılır. Örneğin: "Yapılan gerçekçi stres testleri, `sentiric-media-service`'in 1 vCPU ile saniyede ortalama 150 çağrılık patlamalı trafiği %99.5 başarı oranıyla yönetebildiğini göstermiştir. Bu, aynı anda ~600 aktif çağrıya denk gelmektedir..."]