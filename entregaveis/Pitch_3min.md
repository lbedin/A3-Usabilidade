# Pitch A3 | Aurora Saúde (aprox. 2 min 35 s)

## Roteiro para gravação

**0:00-0:25 | Problema**

Olá. Nosso projeto é um sistema de agendamento online para clínicas médicas. Muitas clínicas ainda organizam horários por telefone, mensagens e planilhas. Isso pode gerar conflito de agenda, demora para confirmar uma consulta e dificuldade para o paciente marcar atendimento fora do horário comercial.

**0:25-0:55 | Solução**

A proposta reúne a agenda dos profissionais em uma aplicação web. O paciente consulta horários disponíveis, escolhe um médico e confirma a consulta. Também pode visualizar, reagendar ou cancelar o atendimento. A clínica cadastra profissionais e configura os dias e horários de atendimento.

**0:55-1:25 | Demonstração da interface**

Na tela inicial, a equipe acompanha os agendamentos e escolhe uma data. Na tela de nova consulta, selecionamos paciente, profissional e horário livre. O sistema considera a disponibilidade cadastrada e pede pelo menos 24 horas de antecedência. Depois da confirmação, a consulta aparece na agenda.

**1:25-2:05 | API e dados**

A interface conversa com uma API REST escrita em Python. A API oferece rotas para consultar profissionais e pacientes, listar a agenda, criar uma consulta, cancelar e reagendar. O banco SQLite mantém os cadastros e compromissos. Ao tentar reservar um horário já ocupado, o servidor rejeita a requisição. O relatório mostra respostas reais de sucesso e de conflito.

**2:05-2:35 | Processo e fechamento**

O desenvolvimento foi planejado em incrementos: começamos com cadastros, depois agenda e disponibilidade, em seguida os fluxos de consulta e por fim as notificações simuladas. A versão demonstra os requisitos centrais e pode evoluir com autenticação, envio de e-mail e SMS e hospedagem segura.

Essa é a proposta Aurora Saúde: facilitar o acesso dos pacientes e ajudar a clínica a manter os horários organizados. Obrigado.

## Sugestão de gravação

- Mostre a Visão geral durante a abertura.
- Abra Nova consulta e percorra paciente, profissional, data e horários livres.
- Mostre uma consulta confirmada na agenda.
- Abra `/api/docs` e execute `GET /api/health`, `POST /api/appointments` e a consulta filtrada por data.
- Encerre com o objetivo e os próximos passos.

O roteiro dura menos de três minutos em ritmo natural. O vídeo precisa ser gravado e publicado pelo aluno como não listado/aberto para gerar o link pedido pelo aviso.
