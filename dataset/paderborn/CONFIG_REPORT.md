# Relatório — Enriquecimento do `dataset/paderborn/config.csv`

## O que foi feito

O arquivo `dataset/paderborn/config.csv` foi expandido de **27 linhas** (uma por arquivo `.rar`, com 3 colunas) para **2240 linhas** (uma por arquivo `.mat` individual, com 13 colunas). Cada linha agora representa uma única aquisição de vibração de um rolamento específico, sob uma condição operacional específica, num ensaio específico — equivalente ao que o `dataset/cwru/config.csv` já fazia para o dataset CWRU.

O arquivo original de 27 linhas foi preservado como `dataset/paderborn/download_config.csv`.

---

## Colunas adicionadas e origem de cada parâmetro

| Coluna | Valores | Fonte |
|---|---|---|
| **condition** | `Normal`, `Inner Race`, `Outer Race` | Convenção do dataset Paderborn: prefixo `K` = saudável, `KA` = falha na pista externa (Außenring), `KI` = falha na pista interna (Innenring). Referência: Lessmeier et al. (2016), Tabela 1. |
| **base_url** | URL fixa do servidor KAt-DataCenter | Já existia no CSV original. Mantida por consistência com o padrão CWRU e por ser consumida por `download_file_from_register` em `dataset/utils.py:14`. |
| **filename** | Ex.: `K001/N15_M07_F10_K001_1.mat` | Extraído por varredura do diretório `raw_data/paderborn/` — o script listou todos os `.mat` dentro de cada subpasta de rolamento. O caminho relativo inclui a subpasta (`K001/`) porque os arquivos são extraídos nessa estrutura. |
| **bearing_code** | `K001`–`K006`, `KA01`–`KA30`, `KI01`–`KI21` | Extraído do nome do arquivo `.mat` via regex (`N\d{2}_M\d{2}_F\d{2}_{bearing_code}_{trial}.mat`). |
| **damage_type** | `None`, `Artificial`, `Real` | Classificação do paper Lessmeier et al. (2016), Seção 3: rolamentos K001–K006 são saudáveis (`None`); KA01/KA03/KA05–KA09 e KI01/KI03/KI05/KI07/KI08 receberam dano artificial em laboratório (`Artificial`); os demais KA/KI passaram por testes de vida acelerada (`Real`). |
| **damage_method** | `None`, `EDM`, `Drilling`, `Engraver`, `Fatigue Pitting`, `Plastic Deform` | Catálogo de rolamentos do Paderborn (Lessmeier et al. 2016, Tabela 1): EDM = eletroerosão, Drilling = furação, Engraver = gravação elétrica (todos artificiais); Fatigue Pitting = pitting por fadiga, Plastic Deform = indentações plásticas (ambos de degradação real). |
| **extent_level** | `None`, `1`, `2`, `3` | Nível de severidade conforme catálogo do Paderborn (Lessmeier et al. 2016, Tabela 1). `None` para saudáveis; 1 = dano leve, 2 = moderado, 3 = severo. |
| **rotational_speed** | `900`, `1500` | Decodificado do prefixo do nome do arquivo: `N09` = 900 RPM, `N15` = 1500 RPM. Documentado no paper do Paderborn, Seção 2 (setup experimental). |
| **load_torque** | `0.1`, `0.7` | Decodificado do nome do arquivo: `M01` = 0.1 Nm, `M07` = 0.7 Nm. Mesma fonte acima. |
| **radial_force** | `400`, `1000` | Decodificado do nome do arquivo: `F04` = 400 N, `F10` = 1000 N. Mesma fonte acima. |
| **trial** | `1`–`20` | Extraído do sufixo do nome do arquivo (`_1.mat` a `_20.mat`). Cada combinação rolamento + condição operacional possui 20 repetições. |
| **sample_rate** | `64000` | Especificação do dataset Paderborn: todos os sinais de vibração e corrente são amostrados a 64 kHz. Confirmado abrindo `raw_data/paderborn/K001/N09_M07_F10_K001_1.mat` com `scipy.io.loadmat` — o canal `vibration_1` contém 256.823 amostras (~4 segundos a 64 kHz). |
| **vibration** | `vibration_1` | Nome do canal dentro da struct do `.mat`. Confirmado por inspeção: cada arquivo contém 7 canais (`force`, `phase_current_1`, `phase_current_2`, `speed`, `temp_2_bearing_module`, `torque`, `vibration_1`), e `vibration_1` é o sinal primário de vibração do acelerômetro. |

---

## Distribuição final do CSV

| Critério | Valores |
|---|---|
| **condition** | Normal: 480 (6 rolamentos), Outer Race: 880 (11 rolamentos), Inner Race: 880 (11 rolamentos) |
| **damage_type** | None: 480, Artificial: 880 (6 OR + 5 IR), Real: 880 (5 OR + 6 IR) |
| **damage_method** | None: 480, EDM: 160, Drilling: 160, Engraver: 560, Fatigue Pitting: 720, Plastic Deform: 160 |
| **Condições operacionais** | 4 combinações × 20 trials × 28 rolamentos = 2240 linhas |

---

## Por que o `download_config.csv` ainda existe

O servidor do Paderborn disponibiliza os dados empacotados como **um arquivo `.rar` por rolamento** (ex.: `K001.rar` contém 80 `.mat`). Não é possível baixar um `.mat` individual diretamente pela URL.

O novo `config.csv` aponta para arquivos `.mat` individuais (ex.: `K001/N09_M07_F10_K001_1.mat`). Se a função `download_dataset` tentasse usar esse CSV, ela montaria URLs como `https://groups.uni-paderborn.de/.../K001/N09_M07_F10_K001_1.mat`, que **não existem** no servidor.

Por isso, o CSV original foi preservado como `download_config.csv` (27 linhas, apontando para `.rar`), mantendo o fluxo de download funcional separado do fluxo de carga/treino. São **responsabilidades distintas**:

- **`download_config.csv`** → responde "o que preciso baixar?" (27 `.rar`)
- **`config.csv`** → responde "o que tenho disponível e quais suas propriedades?" (2240 `.mat` com metadados completos)

---

## Referência bibliográfica

Lessmeier, C., Kimotho, J. K., Zimmer, D., & Sextro, W. (2016). *Condition Monitoring of Bearing Damage in Electromechanical Drive Systems by Using Motor Current Signals of Electric Motors: A Benchmark Data Set for Data-Driven Classification.* European Conference of the Prognostics and Health Management Society.
