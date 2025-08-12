# 🛠️ Sentiric CLI (Command Line Interface)

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Language](https://img.shields.io/badge/language-Python-blue.svg)]()

**Sentiric CLI**, geliştiriciler ve yöneticiler için Sentiric platformunu komut satırından yönetmek, otomatize etmek ve test etmek için tasarlanmış bir araçtır.

## 🎯 Temel Sorumluluklar

*   **Platformla Etkileşim:** `sentiric-api-gateway-service` üzerinden çeşitli mikroservislerle etkileşim kurmak için uygun bir arayüz sağlar.
*   **Otomasyon:** Kullanıcı yönetimi, dialplan yapılandırması gibi yaygın görevleri otomatize eder.
*   **Test ve Hata Ayıklama:** Platformun işlevlerini, özellikle de telekomünikasyon akışlarını, test etmeyi ve hata ayıklamayı kolaylaştırır. Örnekler:
    *   `stress_test_call.py`: Basit bir SIP çağrı simülatörü.
    *   `concurrent_test_call.py`: Eş zamanlı SIP stres testi aracı.
    *   `realistic_test_call.py`: Gerçekçi, "patlamalı" trafik üreten gelişmiş bir stres testi aracı.

## 🛠️ Teknoloji Yığını

*   **Dil:** Python
*   **Kütüphaneler:** `argparse` (komut satırı argümanları için), `socket` (düşük seviye ağ iletişimi için).

## 🔌 API Etkileşimleri

*   **Protokol:** SIP (UDP üzerinden)
*   **Hedef Servis:** `sentiric-sip-gateway-service` (ve dolayısıyla tüm telekom altyapısı).
*   **Gelecek:** `sentiric-api-gateway-service`'e REST/JSON istekleri yapacak.

## 🚀 Kullanım

1.  **Bağımlılıkları Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Stres Testi Aracını Çalıştırın:**
    Script, komut satırı argümanları ile yapılandırılabilir. Yardım menüsünü görmek için:
    ```bash
    python concurrent_test_call.py --help
    ```
    **Örnek:** 10 thread kullanarak 50 çağrı başlatmak için:
    ```bash
    python concurrent_test_call.py --threads 10 --repeat 50
    ```

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen projenin ana [Sentiric Governance](https://github.com/sentiric/sentiric-governance) reposundaki kodlama standartlarına ve katkıda bulunma rehberine göz atın.

---
## 🏛️ Anayasal Konum

Bu servis, [Sentiric Anayasası'nın (v11.0)](https://github.com/sentiric/sentiric-governance/blob/main/docs/blueprint/Architecture-Overview.md) **Zeka & Orkestrasyon Katmanı**'nda yer alan merkezi bir bileşendir.