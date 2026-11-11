# Alessandro Barretta · prévia do site

Tatuador de japonés tradicional em Palma de Mallorca (@alessandrobarretta_tattoo, 16,3 mil seguidores), residente no Nero Art Tattoo. Prévia feita pela L R G Z, com `noindex`. O site está em espanhol.

**Conceito do hero, "grabado":** as pinturas dele (hannya, tigre solitário, Amaterasu, calavera y loto) são impressas na tela como um ukiyo-e, uma plancha de cor por vez. As cores saem da própria pintura por k-means. Cada cor entra chapada, com o veio da madeira e um leve deslize até o registro, do mais claro ao preto, que é a plancha-chave. Depois o detalhe a pincel da pintura original aparece, a tinta é lavada e vem a próxima peça. A folha fica sobre papel washi, com marcas de registro (kentō) nos cantos de baixo. As planchas se sobrepõem e a arte original se forma em ~3 s (ciclo de 7,5 s). Embaixo da folha, só o nome da peça. No PC (a partir de 1100 px) há colunas espelhadas nos dois lados. Paleta: papel #efe7d9, sumi #151311 e bermellón #c8321f. Fontes: Dela Gothic One e Zen Kaku Gothic New.

- No PC roda em WebGL (`assets/js/prensa.js`). No celular toca o MP4 do mesmo shader (`assets/video/grabado.mp4`, 30 s em loop). Se o iPhone recusar o vídeo, o shader assume.
- `tools/laminas.py`: recorta as pinturas em 2:3 e separa as planchas de cor (`assets/hero/<peça>.webp` e `-p.png`, mais `tools/laminas.json`).
- `tools/fotos.py`: portfólio (36), disponíveis (12), retrato e `assets/js/dados.js`.
- `tools/gerar_video.py`: MP4 do hero e capa. `tools/ver_prensa.py`: tira de quadros. `tools/auditar.py`: 13 tamanhos de tela.
- O formulário e os botões "Lo quiero" abrem o WhatsApp +34 622 688 505 (o wa.link da bio) com a mensagem pronta.

## CONFIRMAR antes de publicar

- Se ele quer o site em espanhol (pela legenda "grazie", pode ser italiano) e se quer versão em italiano ou inglês.
- Se as 4 pinturas do hero e os 12 diseños disponibles ainda estão disponíveis, e o preço das pinturas originais à venda.
- Agenda de guests e convenções com datas (o site cita Mallorca Tattoo Convention, Bari Urban Fest, 1977 Tattoo Parlour em Madrid e Leipzig, sem datas).
- Se o horário de atendimento dele é o do estúdio (terça a sábado, 11h–19h).
- Retrato do Sobre: foto de @ras.isaac (pedir autorização ou trocar).
- Domínio (ex.: alessandrobarretta.com) e e-mail.
