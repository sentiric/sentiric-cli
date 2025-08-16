# 🛠️ Sentiric CLI - Görev Listesi

Bu belge, `sentiric-cli` aracının geliştirme yol haritasını ve önceliklerini tanımlar.

---

### Faz 1: Telekom Test Araçları (Mevcut Durum)

Bu faz, platformun telekomünikasyon katmanını test etmek için gerekli temel araçları oluşturmayı hedefler.

-   [x] **Tekli Çağrı Simülatörü (`stress_test_call.py`):** Basit bir SIP INVITE ve BYE paketi gönderen script.
-   [x] **Eş Zamanlı Stres Testi (`concurrent_test_call.py`):** Belirtilen sayıda thread kullanarak platforma eş zamanlı yük uygulayan ve rapor üreten script.
-   [x] **Gerçekçi Stres Testi (`realistic_test_call.py`):** Değişken çağrı süreleri ve "patlamalı" trafik desenleri (Poisson dağılımı) ile daha gerçekçi yük üreten gelişmiş test aracı.

---

### Faz 2: API Gateway Entegrasyonu ve Yönetim Komutları (Sıradaki Öncelik)

Bu faz, CLI'ı basit bir test aracından, platformu yönetebilen tam teşekküllü bir yönetim aracına dönüştürmeyi hedefler.

-   [ ] **Görev ID: CLI-001 - API İstemci Kütüphanesi**
    -   **Açıklama:** `sentiric-api-gateway-service` ile konuşmak için `httpx` veya `requests` tabanlı, yeniden kullanılabilir bir API istemci modülü oluştur.
    -   **Durum:** ⬜ Planlandı.

-   [ ] **Görev ID: CLI-002 - Kimlik Doğrulama (`auth`)**
    -   **Açıklama:** `sentiric-cli auth login` ve `sentiric-cli auth logout` gibi komutlar ekleyerek API Gateway'den JWT token almayı ve güvenli bir şekilde saklamayı sağla.
    -   **Durum:** ⬜ Planlandı.

-   [ ] **Görev ID: CLI-003 - Kullanıcı Yönetimi (`user`)**
    -   **Açıklama:** `sentiric-cli user create`, `sentiric-cli user list` gibi, `user-service`'i API Gateway üzerinden yöneten komutlar ekle.
    -   **Durum:** ⬜ Planlandı.

-   [ ] **Görev ID: CLI-004 - Raporlama (`cdr`)**
    -   **Açıklama:** `sentiric-cli cdr list --tenant-id=...` gibi, `cdr-service`'ten raporları çekip formatlayarak gösteren komutlar ekle.
    -   **Durum:** ⬜ Planlandı.