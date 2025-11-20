"""
Model Eğitim Scripti
Kendi makine parçası tanıma modelinizi eğitmek için kullanın
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from PIL import Image
import os
from pathlib import Path
import json


class MakineParcaDataset(Dataset):
    """Makine parçası veri seti"""
    
    def __init__(self, data_dir, transform=None):
        """
        Args:
            data_dir (str): Veri klasörü yolu
                Klasör yapısı:
                data_dir/
                    vida/
                        img1.jpg
                        img2.jpg
                    somun/
                        img1.jpg
                        img2.jpg
                    ...
            transform: Görüntü dönüşümleri
        """
        self.data_dir = Path(data_dir)
        self.transform = transform
        self.samples = []
        self.classes = []
        
        # Sınıfları topla
        for class_dir in self.data_dir.iterdir():
            if class_dir.is_dir():
                self.classes.append(class_dir.name)
                
                # Her sınıftaki görüntüleri ekle
                for img_path in class_dir.glob('*.jpg'):
                    self.samples.append((img_path, len(self.classes) - 1))
                for img_path in class_dir.glob('*.png'):
                    self.samples.append((img_path, len(self.classes) - 1))
        
        print(f"Toplam {len(self.samples)} görüntü yüklendi")
        print(f"Sınıflar: {self.classes}")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        
        return image, label


class MakineParcaModel(nn.Module):
    """Transfer Learning ile Makine Parçası Tanıma Modeli"""
    
    def __init__(self, num_classes, pretrained=True):
        super(MakineParcaModel, self).__init__()
        
        # ResNet50 modelini kullan
        self.base_model = models.resnet50(pretrained=pretrained)
        
        # Son katmanı değiştir
        num_features = self.base_model.fc.in_features
        self.base_model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        return self.base_model(x)


def train_model(data_dir, num_epochs=25, batch_size=32, learning_rate=0.001):
    """Model eğitimi"""
    
    # Cihazı belirle
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Kullanılan cihaz: {device}")
    
    # Veri dönüşümleri
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Veri setini yükle
    dataset = MakineParcaDataset(data_dir, transform=train_transform)
    
    # Train/Validation split
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        dataset, [train_size, val_size]
    )
    
    # Data loaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Model oluştur
    num_classes = len(dataset.classes)
    model = MakineParcaModel(num_classes=num_classes).to(device)
    
    # Loss ve optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=3)
    
    # Eğitim döngüsü
    best_val_loss = float('inf')
    
    for epoch in range(num_epochs):
        # Training
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = outputs.max(1)
            train_total += labels.size(0)
            train_correct += predicted.eq(labels).sum().item()
        
        train_loss /= len(train_loader)
        train_acc = 100. * train_correct / train_total
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()
        
        val_loss /= len(val_loader)
        val_acc = 100. * val_correct / val_total
        
        # Learning rate scheduler
        scheduler.step(val_loss)
        
        print(f'Epoch [{epoch+1}/{num_epochs}]')
        print(f'Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%')
        print(f'Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%')
        print('-' * 50)
        
        # En iyi modeli kaydet
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
                'val_acc': val_acc,
                'classes': dataset.classes,
            }, 'best_model.pth')
            print(f'✓ Model kaydedildi! (Val Loss: {val_loss:.4f})')
    
    print("\nEğitim tamamlandı!")
    print(f"En iyi validation loss: {best_val_loss:.4f}")
    
    return model, dataset.classes


def test_model(model_path, test_image_path):
    """Eğitilmiş modeli test et"""
    
    # Modeli yükle
    checkpoint = torch.load(model_path)
    classes = checkpoint['classes']
    num_classes = len(classes)
    
    model = MakineParcaModel(num_classes=num_classes, pretrained=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    # Görüntüyü işle
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    image = Image.open(test_image_path).convert('RGB')
    image_tensor = transform(image).unsqueeze(0)
    
    # Tahmin
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted = probabilities.max(1)
    
    predicted_class = classes[predicted.item()]
    confidence_score = confidence.item() * 100
    
    print(f"\nTahmin: {predicted_class}")
    print(f"Güven: {confidence_score:.2f}%")
    
    # Tüm olasılıkları göster
    print("\nTüm sınıf olasılıkları:")
    probs = probabilities[0].numpy()
    for i, (cls, prob) in enumerate(zip(classes, probs)):
        print(f"{cls}: {prob*100:.2f}%")
    
    return predicted_class, confidence_score


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Makine Parçası Tanıma Model Eğitimi')
    parser.add_argument('--mode', choices=['train', 'test'], required=True, help='Mod: train veya test')
    parser.add_argument('--data_dir', type=str, help='Eğitim verisi klasörü (train modu için)')
    parser.add_argument('--model_path', type=str, default='best_model.pth', help='Model dosyası yolu')
    parser.add_argument('--test_image', type=str, help='Test edilecek görüntü (test modu için)')
    parser.add_argument('--epochs', type=int, default=25, help='Epoch sayısı')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    
    args = parser.parse_args()
    
    if args.mode == 'train':
        if not args.data_dir:
            print("Hata: --data_dir parametresi gerekli!")
            exit(1)
        
        print("=" * 60)
        print("Makine Parçası Tanıma Modeli Eğitimi Başlıyor")
        print("=" * 60)
        
        model, classes = train_model(
            data_dir=args.data_dir,
            num_epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.lr
        )
        
    elif args.mode == 'test':
        if not args.test_image:
            print("Hata: --test_image parametresi gerekli!")
            exit(1)
        
        print("=" * 60)
        print("Model Test Ediliyor")
        print("=" * 60)
        
        test_model(args.model_path, args.test_image)
