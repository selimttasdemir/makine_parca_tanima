"""
Dataset Kontrol ve İstatistik Scripti
YOLO formatındaki veri setini kontrol eder ve istatistikleri gösterir
"""

import os
from pathlib import Path
import yaml
from collections import Counter
import matplotlib.pyplot as plt


def check_dataset(yaml_path='mech_parts_data.yaml'):
    """Dataset kontrolü ve istatistikler"""
    
    print("=" * 70)
    print("📊 Dataset Kontrol ve İstatistikler")
    print("=" * 70)
    print()
    
    # YAML dosyasını oku
    if not os.path.exists(yaml_path):
        print(f"❌ YAML dosyası bulunamadı: {yaml_path}")
        return
    
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Sınıf bilgileri
    nc = data.get('nc', 0)
    names = data.get('names', [])
    
    print(f"🏷️  Sınıf Bilgileri:")
    print(f"   Sınıf Sayısı: {nc}")
    print(f"   Sınıflar: {names}")
    print()
    
    # Her bir split için kontrol
    splits = ['train', 'val', 'test']
    stats = {}
    
    for split in splits:
        if split not in data:
            continue
            
        print(f"📁 {split.upper()} Seti:")
        print("-" * 70)
        
        # Yolları hazırla
        img_dir = Path(data[split])
        label_dir = img_dir.parent / 'labels'
        
        # Görüntüleri kontrol et
        img_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
        images = []
        for ext in img_extensions:
            images.extend(list(img_dir.glob(f'*{ext}')))
        
        # Etiketleri kontrol et
        labels = list(label_dir.glob('*.txt'))
        
        print(f"   📸 Görüntüler:")
        print(f"      Klasör: {img_dir}")
        print(f"      Toplam: {len(images)} dosya")
        
        print(f"   🏷️  Etiketler:")
        print(f"      Klasör: {label_dir}")
        print(f"      Toplam: {len(labels)} dosya")
        
        # Eşleşme kontrolü
        img_stems = set([img.stem for img in images])
        lbl_stems = set([lbl.stem for lbl in labels])
        
        matched = img_stems & lbl_stems
        only_img = img_stems - lbl_stems
        only_lbl = lbl_stems - img_stems
        
        print(f"   ✓ Eşleşen: {len(matched)} çift")
        if only_img:
            print(f"   ⚠ Etiketsiz görüntü: {len(only_img)} adet")
        if only_lbl:
            print(f"   ⚠ Görüntüsüz etiket: {len(only_lbl)} adet")
        
        # Sınıf dağılımı
        class_counts = Counter()
        bbox_counts = []
        
        for lbl_file in labels:
            if lbl_file.stem not in img_stems:
                continue
                
            with open(lbl_file, 'r') as f:
                lines = f.readlines()
                bbox_counts.append(len(lines))
                
                for line in lines:
                    parts = line.strip().split()
                    if parts:
                        cls = int(parts[0])
                        class_counts[cls] += 1
        
        print(f"   📊 Nesne İstatistikleri:")
        print(f"      Toplam nesne: {sum(class_counts.values())}")
        if bbox_counts:
            print(f"      Görüntü başına ortalama: {sum(bbox_counts)/len(bbox_counts):.2f}")
            print(f"      Min/Max: {min(bbox_counts)}/{max(bbox_counts)}")
        
        print(f"   📈 Sınıf Dağılımı:")
        for cls_id, count in sorted(class_counts.items()):
            cls_name = names[cls_id] if cls_id < len(names) else f"Class_{cls_id}"
            percentage = (count / sum(class_counts.values())) * 100
            print(f"      {cls_name:15s}: {count:5d} ({percentage:5.1f}%)")
        
        # İstatistikleri sakla
        stats[split] = {
            'images': len(images),
            'labels': len(labels),
            'matched': len(matched),
            'class_counts': class_counts,
            'bbox_counts': bbox_counts
        }
        
        print()
    
    # Özet
    print("=" * 70)
    print("📋 Özet")
    print("=" * 70)
    
    total_images = sum([s['images'] for s in stats.values()])
    total_objects = sum([sum(s['class_counts'].values()) for s in stats.values()])
    
    print(f"   Toplam görüntü: {total_images}")
    print(f"   Toplam nesne: {total_objects}")
    print()
    
    # Veri dengesizliği kontrolü
    all_class_counts = Counter()
    for split_stats in stats.values():
        all_class_counts.update(split_stats['class_counts'])
    
    if all_class_counts:
        max_count = max(all_class_counts.values())
        min_count = min(all_class_counts.values())
        imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
        
        print("⚖️  Veri Dengesi:")
        if imbalance_ratio < 2:
            print("   ✅ Dengeli (oran < 2)")
        elif imbalance_ratio < 5:
            print("   ⚠️  Hafif dengesiz (oran 2-5)")
        else:
            print(f"   ❌ Dengesiz (oran {imbalance_ratio:.1f})")
            print("      → Data augmentation veya sınıf ağırlıkları kullanmayı düşünün")
        print()
    
    # Grafikler
    try:
        create_plots(stats, names)
        print("📊 Grafikler oluşturuldu: dataset_statistics.png")
    except Exception as e:
        print(f"⚠️  Grafik oluşturulamadı: {e}")
    
    print()
    print("=" * 70)
    
    # Öneriler
    print("\n💡 Öneriler:")
    
    for split, split_stats in stats.items():
        if split_stats['images'] < 50:
            print(f"   ⚠️  {split} seti çok küçük ({split_stats['images']} görüntü)")
            print(f"      → En az 100+ görüntü önerilir")
    
    if 'train' in stats and 'val' in stats:
        train_count = stats['train']['images']
        val_count = stats['val']['images']
        if val_count < train_count * 0.1:
            print(f"   ⚠️  Validation seti çok küçük")
            print(f"      → Train'in ~10-20%'si kadar olmalı")
    
    print()


def create_plots(stats, class_names):
    """İstatistik grafikleri oluştur"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Dataset İstatistikleri', fontsize=16, fontweight='bold')
    
    # 1. Görüntü sayıları
    ax = axes[0, 0]
    splits = list(stats.keys())
    img_counts = [stats[s]['images'] for s in splits]
    
    colors = ['#3498db', '#2ecc71', '#e74c3c'][:len(splits)]
    bars = ax.bar(splits, img_counts, color=colors, alpha=0.7, edgecolor='black')
    ax.set_title('Görüntü Sayıları', fontsize=12, fontweight='bold')
    ax.set_ylabel('Görüntü Sayısı')
    ax.grid(axis='y', alpha=0.3)
    
    # Değerleri göster
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    # 2. Sınıf dağılımı (train)
    ax = axes[0, 1]
    if 'train' in stats:
        class_counts = stats['train']['class_counts']
        if class_counts:
            classes = [class_names[c] if c < len(class_names) else f'Class_{c}' 
                      for c in sorted(class_counts.keys())]
            counts = [class_counts[c] for c in sorted(class_counts.keys())]
            
            colors_classes = plt.cm.Set3(range(len(classes)))
            bars = ax.bar(classes, counts, color=colors_classes, alpha=0.7, edgecolor='black')
            ax.set_title('Sınıf Dağılımı (Train)', fontsize=12, fontweight='bold')
            ax.set_ylabel('Nesne Sayısı')
            ax.set_xlabel('Sınıf')
            ax.tick_params(axis='x', rotation=45)
            ax.grid(axis='y', alpha=0.3)
            
            # Değerleri göster
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom', fontweight='bold')
    
    # 3. Görüntü başına nesne sayısı
    ax = axes[1, 0]
    for split, color in zip(splits, colors):
        if stats[split]['bbox_counts']:
            ax.hist(stats[split]['bbox_counts'], bins=20, alpha=0.5, 
                   label=split, color=color, edgecolor='black')
    ax.set_title('Görüntü Başına Nesne Sayısı Dağılımı', fontsize=12, fontweight='bold')
    ax.set_xlabel('Nesne Sayısı')
    ax.set_ylabel('Görüntü Sayısı')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # 4. Split karşılaştırması (pasta)
    ax = axes[1, 1]
    total_objects = [sum(stats[s]['class_counts'].values()) for s in splits]
    
    ax.pie(total_objects, labels=splits, autopct='%1.1f%%',
           colors=colors, startangle=90, explode=[0.05]*len(splits))
    ax.set_title('Toplam Nesne Dağılımı', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('dataset_statistics.png', dpi=150, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Dataset Kontrol ve İstatistik')
    parser.add_argument('--data', type=str, default='mech_parts_data.yaml',
                       help='Dataset YAML dosyası')
    
    args = parser.parse_args()
    
    check_dataset(args.data)
