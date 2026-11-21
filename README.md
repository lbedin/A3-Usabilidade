# Aurora Saúde - sistema de agendamento

Protótipo local e independente para a atividade. Não precisa instalar pacotes.

## Como abrir

Abra `index.html` no navegador. Na primeira abertura, o programa cria exemplos fictícios para a clínica.

## Funcionalidades

- Painel com resumo, agenda do dia, calendário e atividade recente.
- Cadastro de pacientes e profissionais, incluindo horários, intervalo e dias de atendimento.
- Agendamento com horários livres e antecedência mínima de 24 horas.
- Reagendamento e cancelamento com confirmação; abaixo de 12 horas, avisa sobre a política de cancelamento.
- Busca de pacientes, filtros por data e situação e notificações simuladas.
- Dados persistidos no armazenamento local deste navegador.

## Limites da demonstração

Este é um protótipo acadêmico: não envia e-mail/SMS, não tem login real nem sincroniza entre dispositivos. Os dados ficam no navegador usado para abrir a página. Não insira dados médicos reais. Para reiniciar os exemplos, apague a chave `aurora-agenda-v1` no armazenamento local do navegador.
