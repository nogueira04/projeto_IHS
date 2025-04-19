# Projeto IHS – Jogo 2D com Integração Hardware-Software

Este projeto foi desenvolvido como parte da disciplina **Interface Hardware-Software (IF817)**. Consiste em um jogo 2D no estilo "pega-moedas", onde o jogador controla um drone utilizando recursos integrados de hardware e software. A implementação utiliza uma placa FPGA e um driver de controle escrito em C.

## 🎮 Visão Geral

- **Estilo do jogo**:2D "pega-moedas"
- **Controle**:Drone controlado via hardware (FPGA)
- **Integração**:Combinação de software em C com lógica programada na FPGA

## ⚙️ Tecnologias Utilizadas

- **Linguagens**:C, Python
- **Hardware**:Placa FPGA (Cyclone IV)
- **Outros**:Makefile para automação de build

## 📁 Estrutura do Projeto

```bash
projeto_IHS/
├── driver/         # Código-fonte do driver em C para comunicação com a FPGA
├── game/           # Lógica do jogo e interface gráfica
├── include/        # Arquivos de cabeçalho (.h) utilizados no projeto
├── example/        # Exemplos de uso e testes
├── README.md       # Este arquivo
```

## 🚀 Como Executar

1. **Pré-requisitos**:
  - Placa FPGA(Cyclone IV) configurada e conectada
  - Compilador C
  - Python 3.9 instalado.

2. **Compilação do Driver**:
   ```bash
   cd driver
   make
   ``


3. **Execução do Jogo**:
   ```bash
   cd game
   python3 main.py
   ``


