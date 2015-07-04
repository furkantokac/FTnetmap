FTnetmap Version 0.5

HATALAR:
Rapor edilen bir hata yok.

GELİŞTİRME SÜRECİNDEKİ ÖZELLİKLER:
-Host hakkında daha çok bilgi verilecek.

ŞİMDİKİ ÖZELLİKLER:
-2 IP arasındaki tüm IPlerin aktif olup olmadığını kontrol etmek.
-Cross-Platform.
-Aktif IPleri bir dosyaya yazdırmak.
-Hızlı.

GELECEK ÖZELLİKLER:
-Host hakkında daha çok bilgi verilecek.
-Daha gelişmiş ve yeni özellikler için soket kullanılacak.

KULLANIM:
Kullanım: python FTnetmap.py -e fileName.txt -r firstIP-lastIP
Yukarıdaki komut firstIP ve lastIP arasındaki IPlerin aktif olup olmadığını kontrol edip fileName.txt dosyasına aktaracak.

-r --range    - Kontrol edilecek IP aralığı.
-d --detailed - Çalışma esnasında program detayları gösterecek. (IPler sıralanmamış olabilir.)
-h --help     - Yardım
-e --export   - Aktif IPleri dosyaya yazdır.

Örnekler:
python FTnetmap.py -r 192.168.1.0-192.168.2.0
python FTnetmap.py -d -r 192.168.1.0-192.168.1.255
python FTnetmap.py -e fileName.txt -r 192.168.1.0-192.168.1.255
