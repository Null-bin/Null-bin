name: Gerar Animação de Contribuições (Tetris)

on:
  schedule:
    - cron: "0 */12 * * *" # roda a cada 12 horas
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout do repositório
        uses: actions/checkout@v4

      - name: Configurar Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Instalar gerador Tetris
        run: npm install -g github-contribution-graph

      - name: Gerar Tetris com paleta personalizada
        run: |
          github-contribution-graph \
            --mode tetris \
            --output tetris.gif \
            --duration 90 \
            --block-color "#006400" \
            --secondary-block-color "#000080" \
            --tertiary-block-color "#ff0000" \
            --quaternary-block-color "#1e90ff" \
            --background "#ebedf0" \
            --width 52 \
            --height 7

      - name: Configurar Git
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

      - name: Commitar e enviar GIF
        run: |
          git add tetris.gif
          git commit -m "Atualiza Tetris GIF (automatizado)" || echo "Nada para commitar"
          git push
