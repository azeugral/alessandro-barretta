# Alessandro Barretta · prévia do site

Tatuador de japonés tradicional em Palma de Mallorca (@alessandrobarretta_tattoo, 16,3 mil seguidores), residente no Nero Art Tattoo. Prévia feita pela L R G Z, com `noindex`. O site está em espanhol.

**Conceito do hero, "sumi":** as pinturas dele (hannya, tigre solitário, Amaterasu, calavera y loto) se formam a pincel na tela, como num sumi-e. Primeiro uma aguada grande e mole (nijimi), depois pinceladas cada vez mais finas que seguem o fluxo da pintura, com pincel seco (kasure) no fim do traço, e por último o contorno em traços caligráficos. Tudo nasce em tinta preta diluída; a cor escorre por cima em manchas a partir de ~1,4 s, a pintura original assenta por baixo (~3,5 s) e depois a folha é lavada para a próxima peça (ciclo de 7,5 s). A folha fica sobre papel washi, com marcas de registro (kentō) nos cantos de baixo, e embaixo só o nome da peça. No PC (a partir de 1100 px) há colunas espelhadas nos dois lados. Paleta: papel #efe7d9, sumi #151311 e bermellón #c8321f. Fontes: Dela Gothic One e Zen Kaku Gothic New.

- A folha nasce em papel limpo (sem imagem estática antes). O MP4 abre com a hannya se pintando no papel (5,5 s) e, ao terminar, volta para 5,5 s (início do tigre, que começa com a hannya pronta), então a recarga nunca mostra a última peça.
- No PC roda em WebGL2 (`assets/js/sumi.js`, ~78 mil pinceladas nas 4 peças, em `assets/hero/<peça>.bin`). No celular toca o MP4 do mesmo renderizador (`assets/video/sumi.mp4`, 30 s em loop). Se o iPhone recusar o vídeo, o WebGL assume.
- `tools/laminas.py`: recorta as pinturas em 2:3 (`assets/hero/<peça>.webp`). `tools/pinceladas.py`: gera as pinceladas (campo de fluxo por tensor de estrutura, 5 camadas + contorno) e `assets/hero/pinceladas.json`.
- `tools/fotos.py`: portfólio (36), disponíveis (12), retrato e `assets/js/dados.js`.
- `tools/gerar_video.py`: MP4 do hero e capa. `tools/ver_sumi.py [peça] [tempos]`: tira de quadros. `tools/auditar.py`: 13 tamanhos de tela.
- O formulário e os botões "Lo quiero" abrem o WhatsApp +34 622 688 505 (o wa.link da bio) com a mensagem pronta.

## CONFIRMAR antes de publicar

- Se ele quer o site em espanhol (pela legenda "grazie", pode ser italiano) e se quer versão em italiano ou inglês.
- Se as 4 pinturas do hero e os 12 diseños disponibles ainda estão disponíveis, e o preço das pinturas originais à venda.
- Agenda de guests e convenções com datas (o site cita Mallorca Tattoo Convention, Bari Urban Fest, 1977 Tattoo Parlour em Madrid e Leipzig, sem datas).
- Se o horário de atendimento dele é o do estúdio (terça a sábado, 11h–19h).
- Retrato do Sobre: foto de @ras.isaac (pedir autorização ou trocar).
- Domínio (ex.: alessandrobarretta.com) e e-mail.
