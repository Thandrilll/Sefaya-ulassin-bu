# PCD Dosyası Görüntüleme Kılavuzu

Bu kılavuz, PCD (Point Cloud Data) dosyalarını farklı yöntemlerle görüntülemenizi sağlar.

## 🚀 Hızlı Başlangıç

### 1. Python Script ile Görüntüleme (Önerilen)

```bash
# Sanal ortamı aktifleştir
source pcd_env/bin/activate

# Örnek PCD dosyası oluştur ve görüntüle
python pcd_viewer.py --create-sample

# Kendi PCD dosyanızı görüntüleyin
python pcd_viewer.py dosya.pcd

# Sadece Plotly ile interaktif görüntüleme
python pcd_viewer.py dosya.pcd --viewer plotly

# Sadece Matplotlib ile statik görüntüleme
python pcd_viewer.py dosya.pcd --viewer matplotlib
```

### 2. Script Özellikleri

- ✅ ASCII ve Binary PCD format desteği
- ✅ RGB renk bilgisi desteği
- ✅ İnteraktif 3D görselleştirme (Plotly)
- ✅ Statik 3D görselleştirme (Matplotlib)
- ✅ Otomatik nokta örnekleme (büyük dosyalar için)
- ✅ Detaylı istatistik bilgileri

### 3. Komut Satırı Seçenekleri

```bash
python pcd_viewer.py [dosya.pcd] [SEÇENEKLER]

Seçenekler:
  --create-sample     : Örnek PCD dosyası oluştur
  --viewer [matplotlib|plotly|both] : Görselleştirme aracı seç (varsayılan: both)
  --sample-rate N     : Nokta örnekleme oranı (1=tümü, 2=yarısı, vs.)
```

## 📋 PCD Dosya Formatları

### ASCII Format Örneği:
```
# .PCD v0.7 - Point Cloud Data file format
VERSION 0.7
FIELDS x y z rgb
SIZE 4 4 4 4
TYPE F F F U
COUNT 1 1 1 1
WIDTH 1000
HEIGHT 1
VIEWPOINT 0 0 0 1 0 0 0
POINTS 1000
DATA ascii
0.1 0.2 0.3 16711680
0.4 0.5 0.6 65280
...
```

### Desteklenen Alanlar:
- `x y z` - 3D koordinatlar (zorunlu)
- `rgb` - Packed RGB renk bilgisi
- `r g b` - Ayrı RGB değerleri
- `intensity` - Yoğunluk bilgisi
- `normal_x normal_y normal_z` - Yüzey normalleri

## 🔧 ROS ile Entegrasyon

### ROS2 ile PCD Yayınlama (gelecek özellik):

```bash
# ROS2 kurulumu (Ubuntu 22.04+)
sudo apt install ros-humble-desktop

# PCD'yi PointCloud2 mesajı olarak yayınla
ros2 run pcl_ros pcd_to_pointcloud dosya.pcd
```

### RViz2 ile Görüntüleme:

```bash
# RViz2'yi başlat
rviz2

# Görüntüleme ayarları:
# 1. Add -> PointCloud2
# 2. Topic: /cloud_pcd
# 3. Color Transformer: RGB8
```

## 🛠️ Kurulum ve Gereksinimler

### Python Gereksinimleri:
```bash
pip install numpy matplotlib plotly
```

### Sistem Gereksinimleri:
- Python 3.7+
- 2GB+ RAM (büyük PCD dosyaları için)
- OpenGL desteği (3D görselleştirme için)

## 📊 Performans İpuçları

### Büyük Dosyalar İçin:
- `--sample-rate` parametresini kullanın (örn. `--sample-rate 10`)
- Sadece Plotly kullanın: `--viewer plotly`
- RAM kullanımını izleyin

### Renk Görüntüleme:
- RGB bilgisi yoksa Z koordinatına göre renklendirme yapılır
- Packed RGB format desteklenir
- Renk değerleri 0-255 aralığında olmalı

## 🔍 Sorun Giderme

### Yaygın Hatalar:

1. **"Binary PCD dosyaları desteklenmiyor"**
   - Çözüm: PCD dosyasını ASCII formatına dönüştürün
   ```bash
   pcl_convert_pcd_ascii_binary input.pcd output.pcd 0
   ```

2. **"Dosya bulunamadı"**
   - Dosya yolunu kontrol edin
   - Çalışma dizininde olduğunuzdan emin olun

3. **"Matplotlib gösterilemiyor"**
   - X11 forwarding aktif değil (SSH bağlantısı)
   - Sadece Plotly kullanın: `--viewer plotly`

4. **"Çok az nokta görünüyor"**
   - `--sample-rate 1` kullanın
   - PCD dosyasının doğru format olduğunu kontrol edin

### Debug Modu:
```bash
python pcd_viewer.py dosya.pcd --verbose
```

## 📝 Örnek Kullanım Senaryoları

### 1. LIDAR Harita Görüntüleme:
```bash
python pcd_viewer.py lidar_map.pcd --viewer plotly --sample-rate 5
```

### 2. RGB-D Kamera Verisi:
```bash
python pcd_viewer.py rgbd_scene.pcd --viewer both
```

### 3. Büyük Dosya Analizi:
```bash
python pcd_viewer.py huge_map.pcd --viewer plotly --sample-rate 20
```

### 4. Renksiz Nokta Bulutu:
```bash
python pcd_viewer.py points_only.pcd --viewer matplotlib
```

## 🔗 Ek Kaynaklar

- [PCL (Point Cloud Library) Dökümantasyonu](https://pointclouds.org/)
- [ROS PointCloud2 Mesaj Formatı](http://docs.ros.org/en/api/sensor_msgs/html/msg/PointCloud2.html)
- [PCD Dosya Format Spesifikasyonu](https://pointclouds.org/documentation/tutorials/pcd_file_format.html)

## 🐛 Hata Bildirimi

Herhangi bir sorunla karşılaştığınızda:
1. PCD dosyasının formatını kontrol edin
2. Python ve kütüphane sürümlerini kontrol edin
3. Hata mesajını tam olarak kaydedin
4. Dosya boyutunu ve nokta sayısını belirtin

---

**Not:** Bu araç eğitim ve test amaçlı geliştirilmiştir. Üretim ortamında kullanım için ek optimizasyonlar gerekebilir.