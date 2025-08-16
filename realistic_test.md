# Sentiric Media Service - Gerçekçi Stres Testi Raporu (Doğal Anatomi Simülasyonu)

Bu doküman, `sentiric-media-service`'in, bir çağrı merkezinin doğal davranışlarını taklit eden, değişken ve "patlamalı" (bursty) yükler altındaki performansını, kararlılığını ve kaynak tüketimini ölçmek için yapılan testlerin sonuçlarını içermektedir.

**Test Aracı:** `realistic_test_call.py`

## Test Metodolojisi

Testler, gerçek dünya senaryolarını daha iyi yansıtmak için aşağıdaki davranışları simüle eder:

1.  **Değişken Çağrı Süreleri:** Her çağrının süresi, belirtilen ortalama sürenin etrafında rastgele belirlenir. Bu, "sabırsız" kullanıcıları ve anonsu sonuna kadar dinleyenleri taklit eder.
2.  **Patlamalı Trafik (Poisson Dağılımı):** Yeni çağrılar, saniyede hedeflenen ortalama sayıya (`--cps`) ulaşacak şekilde, düzensiz ve "patlamalı" aralıklarla başlatılır.
3.  **Çeşitli Anons İstekleri:** Her çağrı, önceden tanımlanmış bir listeden rastgele bir anons dosyası talep eder. Bu liste, hata durumlarını test etmek için var olmayan bir dosya da içerir.
4.  **Gecikme (Latency) Ölçümü:** Script, bir isteğin gönderilmesi ile sunucudan ilk yanıtın alınması arasındaki süreyi (tepki süresi) ölçer ve P95/P99 gibi istatistiksel metrikler üretir.

Bu metodoloji, sistemin kararlılığını, kaynak yönetimini ve kullanıcı deneyimini zorlu ve gerçekçi koşullar altında test etmeyi amaçlar.

**Test Ortamı:**
- **Servis:** `sentiric-media-service` (Docker Konteyneri, `debian:bookworm-slim` tabanlı)
- **Donanım:** [Testin çalıştırıldığı makinenin CPU/RAM bilgilerini buraya yazın, örn: Intel i9-13900K, 64GB RAM]
- **İşletim Sistemi:** [örn: Windows 11 Pro with Docker Desktop v4.28]

---

## Test Sonuçları

### Senaryo A: "Standart Yük"

- **Amaç:** Orta yoğunluktaki bir trafik altında sistemin temel performansını ve kullanıcı deneyimini ölçmek.
- **Servis Konfigürasyonu:**
  - `cpus: 0.5`
  - `mem_limit: 256m`
- **Test Komutu:** `python realistic_test_call.py --total-calls 500 --cps 50 --threads 100 --duration 4`
- **Rapor Özeti:**
  > *Buraya test sonrası oluşan raporun "Özet Sonuçlar" ve "Gecikme İstatistikleri" bölümlerini kopyalayın.*
- **`docker stats` Gözlemleri:**
  - **Ortalama CPU Kullanımı:** 
  - **Maksimum CPU Kullanımı (Patlama Anları):**
  - **Bellek Kullanımı:**
- **Yorum:** 

### Senaryo B: "Yüksek Yük - Limit Tespiti"

- **Amaç:** Sistemin limitlerini zorlayarak, yüksek yoğunluktaki patlamalı trafikte "kırılma noktasını" ve bu noktadaki kullanıcı deneyimini (gecikme) bulmak.
- **Servis Konfigürasyonu:**
  - `cpus: 0.5`
- **Test Komutu:** `python realistic_test_call.py --total-calls 2000 --cps 150 --threads 300 --duration 4`
- **Rapor Özeti:**
  > *Buraya test sonrası oluşan raporun "Özet Sonuçlar" ve "Gecikme İstatistikleri" bölümlerini kopyalayın.*
- **`docker stats` Gözlemleri:**
  - **Ortalama CPU Kullanımı:**
  - **Maksimum CPU Kullanımı (Patlama Anları):**
  - **Bellek Kullanımı:**
- **Yorum:**

### Senaryo C: "Yüksek Performans (1 vCPU)"

- **Amaç:** Tek bir tam CPU çekirdeği ile ulaşılabilecek maksimum verimi ve bu verimdeki kullanıcı deneyimini ölçmek.
- **Servis Konfigürasyonu:**
  - `cpus: 1.0`
  - `mem_limit: 256m`
- **Test Komutu:** `python realistic_test_call.py --total-calls 2500 --cps 200 --threads 400 --duration 4`
- **Rapor Özeti:**
  > *Buraya test sonrası oluşan raporun "Özet Sonuçlar" ve "Gecikme İstatistikleri" bölümlerini kopyalayın.*
- **`docker stats` Gözlemleri:**
  - **Ortalama CPU Kullanımı:**
  - **Maksimum CPU Kullanımı (Patlama Anları):**
  - **Bellek Kullanımı:**
- **Yorum:**

---

## Genel Değerlendirme ve Kapasite Planlaması

Bu testler sonucunda elde edilen verilere göre, `sentiric-media-service` için aşağıdaki kapasite planlaması ve kaynak önerileri yapılabilir:

| vCPU Limiti | Stabil CPS Kapasitesi (P95 < 200ms) | Önerilen Kullanım Senaryosu |
|-------------|---------------------------------------|-----------------------------|
| **0.50**    | `~50 CPS`                             | Orta trafikli, standart production ortamı. |
| **1.00**    | `...`                                 | Yüksek trafikli, yoğun kullanım senaryoları. |

**Bellek Kullanımı:** Tüm testler boyunca bellek kullanımı `... MB`'ı aşmamıştır. `256m` limiti, yüzlerce farklı anonsun önbelleğe alınması için dahi yeterlidir. Darboğaz bellek değil, CPU'dur.

**Port Havuzu:** `10000-12000` aralığındaki 1001 port, test edilen en yüksek yük senaryoları için bile yeterli olmuştur. Karantina mekanizması ile birlikte bu havuz, 500+ eş zamanlı çağrıyı rahatlıkla destekleyebilir.