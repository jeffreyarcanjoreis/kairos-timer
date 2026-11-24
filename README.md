# Kairos Timer

Cronômetro de intervalos para treinos: blocos com rodadas, etapas de trabalho e descanso, descanso entre blocos (Tabata, EMOM, circuitos), bipes de início, contagem 3-2-1 e fim. Funciona offline depois de instalado no celular.

- `app.html`: o app (fonte única).
- `python montar.py`: gera `index.html`, `manifest.webmanifest`, `sw.js` e os ícones a partir de `app.html`.

Para atualizar: edite `app.html`, rode `python montar.py`, faça commit e push. O celular pega a versão nova na próxima vez que abrir o app com internet.
