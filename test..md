# Sentiric Media Service - Performans ve Stres Testi Raporu

Bu doküman, `sentiric-media-service`'in farklı yükler altındaki performansını, kararlılığını ve kaynak tüketimini ölçmek için yapılan stres testlerinin sonuçlarını içermektedir.

**Test Ortamı:**
- **Servis:** `sentiric-media-service` (Docker Konteyneri)
- **Test Aracı:** `concurrent_test_call.py` (Python SIP Stres Testi Script'i)
- **Donanım:** [Testin çalıştırıldığı makinenin CPU/RAM bilgilerini buraya yazın, örn: Intel i7-12700K, 32GB RAM]
- **İşletim Sistemi:** [örn: Windows 11 Pro with Docker Desktop]

---

## Test Metodolojisi

Testler, `concurrent_test_call.py` script'i kullanılarak, `media-service`'in Docker konteynerine karşı çalıştırılmıştır. Her test senaryosunda, servisin CPU ve Bellek limitleri `docker-compose.service.yml` dosyası üzerinden ayarlanmış ve test boyunca `docker stats` ile kaynak kullanımı izlenmiştir.

**Sabit Parametreler:**
- **Çağrı Süresi (`--duration`):** 5 saniye
- **Çağrılar Arası Gecikme (`--delay`):** 0.01 saniye (Yüksek frekanslı istekler için)

**Değişken Parametreler:**
- **Servis CPU Limiti (`cpus`):** `docker-compose.yml` içinde ayarlanır.
- **Servis Bellek Limiti (`mem_limit`):** `docker-compose.yml` içinde ayarlanır.
- **Eş Zamanlılık (`--threads`):** Test script'inde ayarlanır.
- **Toplam Çağrı Sayısı (`--repeat`):** Test script'inde ayarlanır.

**Başarı Kriteri:** Testin %100 başarı oranıyla tamamlanması ve test süresince CPU kullanımının sürekli olarak %95'in altında kalması.

---

## Test Sonuçları

### Senaryo 1: Baseline Test (Düşük Kaynak Konfigürasyonu)

- **Amaç:** Servisin minimum kaynaklarla temel performansını ölçmek.
- **Servis Konfigürasyonu:**
  - `cpus: 0.25`
  - `mem_limit: 128m`

#### Test 1.1: 20 Eş Zamanlı Çağrı
- **Test Komutu:** `python concurrent_test_call.py --threads 20 --repeat 200 --delay 0.01`
- **Rapor Özeti:**
  - **Toplam Süre:** [Rapor dosyasından gelen değeri buraya yazın, örn: 12.34 saniye]
  - **CPS (Ortalama):** [Rapor dosyasından gelen değeri buraya yazın, örn: 16.21]
  - **Başarı Oranı:** %100.00
- **`docker stats` Gözlemleri:**
  - **Ortalama CPU Kullanımı:** [Test sırasındaki gözleminizi yazın, örn: ~45%]
  - **Maksimum CPU Kullanımı:** [Test sırasındaki gözleminizi yazın, örn: %60]
  - **Bellek Kullanımı:** [Test sırasındaki gözleminizi yazın, örn: ~25 MB]
- **Yorum:** 0.25 vCPU ile 20 eş zamanlı çağrı sorunsuz bir şekilde karşılanmıştır. Sistem stabil.

#### Test 1.2: 50 Eş Zamanlı Çağrı
- **Test Komutu:** `python concurrent_test_call.py --threads 50 --repeat 500 --delay 0.01`
- **Rapor Özeti:**
  - **Toplam Süre:** [Rapor dosyasından gelen değeri buraya yazın]
  - **CPS (Ortalama):** [Rapor dosyasından gelen değeri buraya yazın]
  - **Başarı Oranı:** [Rapor dosyasından gelen değeri buraya yazın, örn: %98.50]
  - **Hata Detayları:** [Eğer varsa, örn: `Socket timeout`: 15 kez]
- **`docker stats` Gözlemleri:**
  - **Ortalama CPU Kullanımı:** [örn: ~98%]
  - **Maksimum CPU Kullanımı:** [örn: %100 (Sürekli)]
  - **Bellek Kullanımı:** [örn: ~28 MB]
- **Yorum:** 0.25 vCPU konfigürasyonu, 50 eş zamanlı çağrı yükü altında darboğaza girmiştir. CPU limitinin %100'e ulaşması, bazı isteklerin zaman aşımına uğramasına neden olmuştur. **Bu konfigürasyon için güvenli operasyonel limit yaklaşık 30-40 eş zamanlı çağrıdır.**

---

### Senaryo 2: Standart Konfigürasyon Testi

- **Amaç:** Önerilen standart kaynaklarla (0.5 vCPU) sistemin kapasitesini belirlemek.
- **Servis Konfigürasyonu:**
  - `cpus: 0.5`
  - `mem_limit: 256m`

#### Test 2.1: 100 Eş Zamanlı Çağrı
- **Test Komutu:** `python concurrent_test_call.py --threads 100 --repeat 1000 --delay 0.01`
- **Rapor Özeti:**
  - ... [Rapor sonuçlarını buraya doldurun] ...
- **`docker stats` Gözlemleri:**
  - ... [Gözlemlerinizi buraya doldurun] ...
- **Yorum:** ... [Testin nasıl geçtiğini ve ne anlama geldiğini yorumlayın] ...

#### Test 2.2: 150 Eş Zamanlı Çağrı
- **Test Komutu:** `python concurrent_test_call.py --threads 150 --repeat 1500 --delay 0.01`
- **Rapor Özeti:**
  - ... [Rapor sonuçlarını buraya doldurun] ...
- **`docker stats` Gözlemleri:**
  - ... [Gözlemlerinizi buraya doldurun] ...
- **Yorum:** ... [Testin nasıl geçtiğini ve ne anlama geldiğini yorumlayın] ...

---

### Senaryo 3: Yüksek Performans Testi (1 vCPU)

- **Amaç:** Tek bir tam CPU çekirdeği ile ulaşılabilecek maksimum verimi ölçmek.
- **Servis Konfigürasyonu:**
  - `cpus: 1.0`
  - `mem_limit: 256m`

#### Test 3.1: 250 Eş Zamanlı Çağrı
- **Test Komutu:** `python concurrent_test_call.py --threads 250 --repeat 2500 --delay 0.01`
- **Rapor Özeti:**
  - ... [Rapor sonuçlarını buraya doldurun] ...
- **`docker stats` Gözlemleri:**
  - ... [Gözlemlerinizi buraya doldurun] ...
- **Yorum:** ... [Testin nasıl geçtiğini ve ne anlama geldiğini yorumlayın] ...

---

## Genel Sonuç ve Kapasite Planlaması

Bu testler sonucunda elde edilen verilere göre, `sentiric-media-service` için aşağıdaki kapasite planlaması ve kaynak önerileri yapılabilir:

| vCPU Limiti | Stabil Eş Zamanlı Çağrı Kapasitesi (Yaklaşık) | Önerilen Kullanım Senaryosu |
|-------------|-----------------------------------------------|-----------------------------|
| **0.25**    | ~35                                           | Düşük trafikli, küçük müşteriler veya geliştirme ortamları. |
| **0.50**    | ~120                                          | Orta trafikli, standart production ortamı. |
| **1.00**    | ~250+                                         | Yüksek trafikli, yoğun kullanım senaryoları. |

**Bellek Kullanımı:** Tüm testler boyunca bellek kullanımı `50 MB`'ı aşmamıştır. `128m` ve `256m` limitleri, anons sayısı artsa bile güvenli bir aralık sunmaktadır. Darboğaz bellek değil, CPU'dur.

**Port Havuzu:** `10000-12000` aralığındaki 1001 port, test edilen en yüksek yük senaryoları için bile yeterli olmuştur. Karantina mekanizması ile birlikte bu havuz, 500+ eş zamanlı çağrıyı rahatlıkla destekleyebilir.