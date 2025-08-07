#!/usr/bin/env python3
"""
PCD Dosya Görüntüleyici
Bu script PCD (Point Cloud Data) dosyalarını okuyup 3D olarak görselleştirir.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import plotly.express as px
import sys
import os
import argparse

class PCDViewer:
    def __init__(self):
        self.points = None
        self.colors = None
        self.filename = None
    
    def read_pcd_ascii(self, filename):
        """ASCII formatındaki PCD dosyasını okur"""
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            # Header bilgilerini parse et
            header_info = {}
            data_start = 0
            
            for i, line in enumerate(lines):
                line = line.strip()
                if line.startswith('VERSION'):
                    header_info['version'] = line.split()[1]
                elif line.startswith('FIELDS'):
                    header_info['fields'] = line.split()[1:]
                elif line.startswith('SIZE'):
                    header_info['size'] = [int(x) for x in line.split()[1:]]
                elif line.startswith('TYPE'):
                    header_info['type'] = line.split()[1:]
                elif line.startswith('COUNT'):
                    header_info['count'] = [int(x) for x in line.split()[1:]]
                elif line.startswith('WIDTH'):
                    header_info['width'] = int(line.split()[1])
                elif line.startswith('HEIGHT'):
                    header_info['height'] = int(line.split()[1])
                elif line.startswith('VIEWPOINT'):
                    header_info['viewpoint'] = [float(x) for x in line.split()[1:]]
                elif line.startswith('POINTS'):
                    header_info['points'] = int(line.split()[1])
                elif line.startswith('DATA'):
                    header_info['data_type'] = line.split()[1]
                    data_start = i + 1
                    break
            
            print(f"PCD Dosya Bilgileri:")
            print(f"  - Sürüm: {header_info.get('version', 'Bilinmiyor')}")
            print(f"  - Alanlar: {header_info.get('fields', [])}")
            print(f"  - Nokta sayısı: {header_info.get('points', 0)}")
            print(f"  - Veri tipi: {header_info.get('data_type', 'Bilinmiyor')}")
            
            # Data kısmını oku
            points_data = []
            for line in lines[data_start:]:
                line = line.strip()
                if line:
                    values = line.split()
                    if len(values) >= 3:  # En az x, y, z koordinatları olmalı
                        points_data.append([float(x) for x in values])
            
            points_array = np.array(points_data)
            
            # Koordinatları ayır
            if points_array.shape[1] >= 3:
                self.points = points_array[:, :3]  # x, y, z
                
                # RGB renk bilgisi varsa al
                if points_array.shape[1] >= 6:
                    self.colors = points_array[:, 3:6] / 255.0  # RGB değerlerini normalize et
                elif 'rgb' in header_info.get('fields', []):
                    # RGB packed format
                    rgb_idx = header_info['fields'].index('rgb')
                    if points_array.shape[1] > rgb_idx:
                        rgb_values = points_array[:, rgb_idx].astype(np.uint32)
                        r = ((rgb_values >> 16) & 0xFF) / 255.0
                        g = ((rgb_values >> 8) & 0xFF) / 255.0
                        b = (rgb_values & 0xFF) / 255.0
                        self.colors = np.column_stack([r, g, b])
                
                self.filename = filename
                return True
            else:
                print("Hata: Dosyada yeterli koordinat bilgisi bulunamadı")
                return False
                
        except Exception as e:
            print(f"Dosya okuma hatası: {e}")
            return False
    
    def read_pcd_binary(self, filename):
        """Binary formatındaki PCD dosyasını okur (temel implementasyon)"""
        print("Binary PCD dosyaları henüz tam desteklenmiyor. ASCII formatını kullanın.")
        return False
    
    def read_pcd(self, filename):
        """PCD dosyasını okur (format otomatik algılar)"""
        if not os.path.exists(filename):
            print(f"Hata: {filename} dosyası bulunamadı")
            return False
        
        # Dosya formatını kontrol et
        try:
            with open(filename, 'r') as f:
                first_line = f.readline().strip()
                if first_line.startswith('# .PCD'):
                    # ASCII format
                    return self.read_pcd_ascii(filename)
                else:
                    # Binary format deneme
                    return self.read_pcd_binary(filename)
        except:
            return self.read_pcd_binary(filename)
    
    def plot_matplotlib(self, sample_rate=1):
        """Matplotlib ile 3D görselleştirme"""
        if self.points is None:
            print("Önce bir PCD dosyası yükleyin")
            return
        
        # Çok fazla nokta varsa örnekleme yap
        if len(self.points) > 10000:
            indices = np.random.choice(len(self.points), 
                                     min(10000, len(self.points)), 
                                     replace=False)
            points = self.points[indices]
            colors = self.colors[indices] if self.colors is not None else None
        else:
            points = self.points[::sample_rate]
            colors = self.colors[::sample_rate] if self.colors is not None else None
        
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        
        if colors is not None:
            scatter = ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                               c=colors, s=1, alpha=0.6)
        else:
            scatter = ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                               c=points[:, 2], cmap='viridis', s=1, alpha=0.6)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'PCD Görselleştirme: {os.path.basename(self.filename)}')
        
        # Eşit ölçeklendirme
        max_range = np.array([points[:, 0].max()-points[:, 0].min(),
                             points[:, 1].max()-points[:, 1].min(),
                             points[:, 2].max()-points[:, 2].min()]).max() / 2.0
        mid_x = (points[:, 0].max()+points[:, 0].min()) * 0.5
        mid_y = (points[:, 1].max()+points[:, 1].min()) * 0.5
        mid_z = (points[:, 2].max()+points[:, 2].min()) * 0.5
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)
        
        plt.colorbar(scatter)
        plt.show()
    
    def plot_plotly(self, sample_rate=1):
        """Plotly ile interaktif 3D görselleştirme"""
        if self.points is None:
            print("Önce bir PCD dosyası yükleyin")
            return
        
        # Çok fazla nokta varsa örnekleme yap
        if len(self.points) > 50000:
            indices = np.random.choice(len(self.points), 
                                     min(50000, len(self.points)), 
                                     replace=False)
            points = self.points[indices]
            colors = self.colors[indices] if self.colors is not None else None
        else:
            points = self.points[::sample_rate]
            colors = self.colors[::sample_rate] if self.colors is not None else None
        
        if colors is not None:
            # RGB renkleri kullan
            color_values = ['rgb({},{},{})'.format(int(r*255), int(g*255), int(b*255)) 
                           for r, g, b in colors]
        else:
            # Z koordinatına göre renklendirme
            color_values = points[:, 2]
        
        fig = go.Figure(data=[go.Scatter3d(
            x=points[:, 0],
            y=points[:, 1],
            z=points[:, 2],
            mode='markers',
            marker=dict(
                size=2,
                color=color_values,
                colorscale='Viridis' if colors is None else None,
                opacity=0.6
            ),
            text=[f'X: {x:.2f}<br>Y: {y:.2f}<br>Z: {z:.2f}' 
                  for x, y, z in points[::max(1, len(points)//1000)]],
            hovertemplate='%{text}<extra></extra>'
        )])
        
        fig.update_layout(
            title=f'PCD Görselleştirme: {os.path.basename(self.filename)}',
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                aspectmode='cube'
            ),
            width=1000,
            height=700
        )
        
        fig.show()
    
    def print_stats(self):
        """Nokta bulutu istatistiklerini yazdır"""
        if self.points is None:
            print("Önce bir PCD dosyası yükleyin")
            return
        
        print(f"\n=== PCD İstatistikleri ===")
        print(f"Dosya: {self.filename}")
        print(f"Toplam nokta sayısı: {len(self.points):,}")
        print(f"Koordinat aralıkları:")
        print(f"  X: {self.points[:, 0].min():.3f} - {self.points[:, 0].max():.3f}")
        print(f"  Y: {self.points[:, 1].min():.3f} - {self.points[:, 1].max():.3f}")
        print(f"  Z: {self.points[:, 2].min():.3f} - {self.points[:, 2].max():.3f}")
        print(f"Renk bilgisi: {'Var' if self.colors is not None else 'Yok'}")

def create_sample_pcd(filename="sample_map.pcd", size=1000):
    """Test için örnek PCD dosyası oluşturur"""
    print(f"Örnek PCD dosyası oluşturuluyor: {filename}")
    
    # Rastgele 3D noktalar oluştur (bir oda/bina gibi)
    np.random.seed(42)
    
    # Zemin noktaları
    ground_points = []
    for x in np.linspace(-10, 10, 50):
        for y in np.linspace(-10, 10, 50):
            z = 0.0 + np.random.normal(0, 0.1)  # Biraz gürültü
            ground_points.append([x, y, z, 100, 100, 100])  # Gri renk
    
    # Duvar noktaları
    wall_points = []
    # Ön duvar
    for x in np.linspace(-10, 10, 30):
        for z in np.linspace(0, 3, 20):
            y = 10.0 + np.random.normal(0, 0.05)
            wall_points.append([x, y, z, 200, 150, 100])  # Kahverengi
    
    # Arka duvar
    for x in np.linspace(-10, 10, 30):
        for z in np.linspace(0, 3, 20):
            y = -10.0 + np.random.normal(0, 0.05)
            wall_points.append([x, y, z, 200, 150, 100])
    
    # Sol duvar
    for y in np.linspace(-10, 10, 30):
        for z in np.linspace(0, 3, 20):
            x = -10.0 + np.random.normal(0, 0.05)
            wall_points.append([x, y, z, 200, 150, 100])
    
    # Sağ duvar
    for y in np.linspace(-10, 10, 30):
        for z in np.linspace(0, 3, 20):
            x = 10.0 + np.random.normal(0, 0.05)
            wall_points.append([x, y, z, 200, 150, 100])
    
    # Tavan noktaları
    ceiling_points = []
    for x in np.linspace(-10, 10, 40):
        for y in np.linspace(-10, 10, 40):
            z = 3.0 + np.random.normal(0, 0.1)
            ceiling_points.append([x, y, z, 255, 255, 255])  # Beyaz
    
    # Bazı mobilya/engel noktaları
    furniture_points = []
    # Masa
    for x in np.linspace(-2, 2, 20):
        for y in np.linspace(-1, 1, 10):
            z = 1.0
            furniture_points.append([x, y, z, 139, 69, 19])  # Koyu kahve
    
    # Tüm noktaları birleştir
    all_points = ground_points + wall_points + ceiling_points + furniture_points
    
    # PCD dosyası yaz
    with open(filename, 'w') as f:
        f.write("# .PCD v0.7 - Point Cloud Data file format\n")
        f.write("VERSION 0.7\n")
        f.write("FIELDS x y z rgb\n")
        f.write("SIZE 4 4 4 4\n")
        f.write("TYPE F F F U\n")
        f.write("COUNT 1 1 1 1\n")
        f.write("WIDTH {}\n".format(len(all_points)))
        f.write("HEIGHT 1\n")
        f.write("VIEWPOINT 0 0 0 1 0 0 0\n")
        f.write("POINTS {}\n".format(len(all_points)))
        f.write("DATA ascii\n")
        
        for point in all_points:
            x, y, z, r, g, b = point
            # RGB değerlerini packed format'a dönüştür
            rgb_packed = (int(r) << 16) | (int(g) << 8) | int(b)
            f.write(f"{x:.6f} {y:.6f} {z:.6f} {rgb_packed}\n")
    
    print(f"Örnek PCD dosyası oluşturuldu: {len(all_points)} nokta")
    return filename

def main():
    parser = argparse.ArgumentParser(description='PCD Dosya Görüntüleyici')
    parser.add_argument('pcd_file', nargs='?', help='Görüntülenecek PCD dosyası')
    parser.add_argument('--create-sample', action='store_true', 
                       help='Örnek PCD dosyası oluştur')
    parser.add_argument('--viewer', choices=['matplotlib', 'plotly', 'both'], 
                       default='both', help='Kullanılacak görselleştirme aracı')
    parser.add_argument('--sample-rate', type=int, default=1,
                       help='Nokta örnekleme oranı (1=tümü, 2=yarısı, vs.)')
    
    args = parser.parse_args()
    
    viewer = PCDViewer()
    
    if args.create_sample:
        sample_file = create_sample_pcd()
        if not args.pcd_file:
            args.pcd_file = sample_file
    
    if not args.pcd_file:
        print("Hata: PCD dosyası belirtilmedi")
        print("Kullanım:")
        print("  python pcd_viewer.py dosya.pcd")
        print("  python pcd_viewer.py --create-sample")
        return
    
    # PCD dosyasını yükle
    if viewer.read_pcd(args.pcd_file):
        viewer.print_stats()
        
        # Görselleştir
        if args.viewer in ['matplotlib', 'both']:
            print("\nMatplotlib ile görselleştiriliyor...")
            viewer.plot_matplotlib(args.sample_rate)
        
        if args.viewer in ['plotly', 'both']:
            print("\nPlotly ile interaktif görselleştirme...")
            viewer.plot_plotly(args.sample_rate)
    else:
        print("PCD dosyası yüklenemedi")

if __name__ == "__main__":
    main()