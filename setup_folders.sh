#!/bin/bash
# Referans görüntüler klasör yapısını oluştur

echo "📁 Referans görüntüler için klasör yapısı oluşturuluyor..."

# Ana klasörü oluştur
mkdir -p referans_gorseller

# Her parça için alt klasör
parcalar=(
    "vida"
    "somun"
    "rulman"
    "kayis"
    "disli"
    "piston"
    "supap"
    "krank"
    "yay"
    "kaynak"
)

for parca in "${parcalar[@]}"; do
    mkdir -p "referans_gorseller/$parca"
    echo "  ✓ referans_gorseller/$parca/"
done

# Test görüntüleri klasörü
mkdir -p test_images
echo "  ✓ test_images/"

# Eğitim verileri klasörü
mkdir -p training_data
for parca in "${parcalar[@]}"; do
    mkdir -p "training_data/$parca"
    echo "  ✓ training_data/$parca/"
done

echo ""
echo "✅ Klasör yapısı oluşturuldu!"
echo ""
echo "📝 Şimdi ne yapmalısınız:"
echo "1. Her parça için 5-10 referans görüntü ekleyin:"
echo "   referans_gorseller/vida/vida1.jpg"
echo "   referans_gorseller/vida/vida2.jpg"
echo "   ..."
echo ""
echo "2. Test için örnek görüntüler ekleyin:"
echo "   test_images/test_vida.jpg"
echo ""
echo "3. Model eğitimi için daha fazla veri ekleyin (isteğe bağlı):"
echo "   training_data/vida/*.jpg (100+ görüntü)"
echo ""
echo "4. Sistemleri test edin:"
echo "   python feature_matcher.py"
echo "   python hybrid_detector.py"
