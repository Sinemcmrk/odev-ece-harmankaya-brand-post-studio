# Brand Post Studio — Çalıştırma

Python 3.10+ gerekir.

```bash
pip install -r requirements.txt
streamlit run app.py                 # arayüz (komut bulunamazsa: python -m streamlit run app.py)
python agent.py --brand all          # 4 marka x 3 = 12 örnek post (ornek_postlar/)
python agent.py --brand E4I --index 0 --output demo.png
python agent.py --brand ABA_Egitim --mode ai --topic "Üniversite başvurusu"
```

Streamlit arayüzü varsayılan olarak http://localhost:8501 adresinde açılır.

**Offline mod:** Brand Kit PDF'lerindeki renk, etiket, şerit ve düzen kurallarına göre, hazır kütüphane metniyle 1080x1350 PNG üretir. AI üretimi değildir.

**AI modu:** `OPENAI_API_KEY` gerekir (`.env.example` dosyasını `.env` olarak kopyalayıp anahtarı yazın). Marka tonuna ve dile (ABA: Türkçe; E4I ve Design House: İngilizce) göre başlık, alt metin ve caption üretir. Canlı API testi yapılmadı.

**Brand Kit uyumu:** Renkler, etiket/şerit rengi ve düzen (ABA Eğitim lacivert şerit, ABA Psikoloji bordo/adaçayı etiket + turuncu şerit, E4I lime şerit, Design House çizgi çerçeve + sol alt başlık) Brand Kit'lerden alındı. Instagram renkleri "~" ile yaklaşık değerlerdir.

**Sınırlar:**
- Logolar `logos/` klasöründen otomatik yapıştırılır: ABA Eğitim, ABA Psikoloji, E4I ve Design House Global (Instagram profil görseli, olduğu gibi) eklendi. Design House kitine göre postlarda yazısız beyaz çizgi kalkan kullanılıyor; bu dosya elimizde olmadığı için profil görseli kullanıldı.
- Resmî fontlar (Montserrat, Inter, Roboto, Archivo) pakete eklenmedi; `fonts/` klasörüne konursa kullanılır, yoksa DejaVu'ya düşer.
- Telefon/e-posta alanları teyit edilmediği için şeritte yalnızca web adresi var.
- ABA Psikoloji'de turuncu vurgu krem üstünde kontrast yetersiz olduğu için başlık koyu bırakıldı.
- Tüm çıktılar yayın öncesi insan onayı gerektirir.
