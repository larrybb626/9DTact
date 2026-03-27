from torchvision import models
from torchvision.models import (
    ResNet18_Weights,
    ResNet34_Weights,
    ResNet50_Weights,
    ResNet101_Weights,
    DenseNet121_Weights,
    DenseNet161_Weights,
    DenseNet169_Weights,
    DenseNet201_Weights,
)
import torch
from torch import nn


def Resnet(layer=50, pretrained=True):
    weights = None
    if layer == 18:
        weights = ResNet18_Weights.DEFAULT if pretrained else None
        model = models.resnet18(weights=weights)
        print('use Resnet-18')
    elif layer == 34:
        weights = ResNet34_Weights.DEFAULT if pretrained else None
        model = models.resnet34(weights=weights)
        print('use Resnet-34')
    elif layer == 50:
        weights = ResNet50_Weights.DEFAULT if pretrained else None
        model = models.resnet50(weights=weights)
        print('use Resnet-50')
    else:
        weights = ResNet101_Weights.DEFAULT if pretrained else None
        model = models.resnet101(weights=weights)
        print('use Resnet-101')
    num_in_features = model.fc.in_features
    model.fc = nn.Linear(num_in_features, 6)
    return model


def Densenet(layer=169, pretrained=True):
    weights = None
    if layer == 121:
        weights = DenseNet121_Weights.DEFAULT if pretrained else None
        model = models.densenet121(weights=weights)
        print('use Densenet-121')
    elif layer == 161:
        print('use Densenet-161')
        weights = DenseNet161_Weights.DEFAULT if pretrained else None
        model = models.densenet161(weights=weights)
    elif layer == 169:
        weights = DenseNet169_Weights.DEFAULT if pretrained else None
        model = models.densenet169(weights=weights)
        print('use Densenet-169')
    else:
        weights = DenseNet201_Weights.DEFAULT if pretrained else None
        model = models.densenet201(weights=weights)
        print('use Densenet-201')
    num_in_features = model.classifier.in_features
    model.classifier = nn.Linear(num_in_features, 6)
    return model


if __name__ == '__main__':
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    densenet = Densenet(layer=201).to(device)

