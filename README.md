# Kairos Timer

Cronômetro de intervalos para treinos: blocos com rodadas, etapas de trabalho e descanso, descanso entre blocos (Tabata, EMOM, circuitos), bipes de início, contagem regressiva e fim. Funciona offline depois de instalado no celular.

- `app.html`: o app (fonte única), com as telas Treinos, Editor, Cronômetro, Configurações e Privacidade.
- `python montar.py`: gera `index.html`, `manifest.webmanifest`, `sw.js` e os ícones a partir de `app.html`. Troca o link do Google Fonts pelas fontes locais em `fonts/`.
- `fonts/`: Archivo e Fraunces (SIL Open Font License 1.1), servidas pelo próprio app para não haver pedido ao Google.

Configurações (guardadas só no aparelho): cores das fases (5 conjuntos prontos ou cor por fase), volume, tipo de som (bipe, suave, apito, sino, digital), quais avisos tocam, contagem de 0, 3 ou 5 s, vibração, voz e tela acesa.

Privacidade (RGPD/LGPD): o app não coleta dados. A política fica dentro do app (rodapé → Privacidade). Se o app passar a tratar algum dado, atualizar a política e a data em `PRIVACIDADE_DATA` antes de publicar.

Para atualizar: edite `app.html`, rode `python montar.py`, faça commit e push. O celular pega a versão nova na próxima vez que abrir o app com internet.
