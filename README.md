# A3-Usabilidade | Aurora Saúde

Sistema de agendamento de consultas com interface web e API REST local, feito como protótipo acadêmico.

## Iniciar

Requer Python 3, sem pacotes extras.

```powershell
python server.py
```

Abra `http://127.0.0.1:4173/` para acessar o site. A documentação interativa da API fica em `http://127.0.0.1:4173/api/docs`.

## Funcionalidades

- Cadastro de pacientes e profissionais, com disponibilidade semanal.
- Consulta da agenda e horários livres.
- Agendamento, reagendamento e cancelamento.
- Antecedência mínima de 24 horas e validação de conflito de horários no servidor.
- API REST em JSON e persistência SQLite no arquivo `aurora.sqlite3`.
- Notificações simuladas na interface.

## Rotas principais

- `GET /api/health` - estado do serviço.
- `GET /api/state` - estado completo da demonstração.
- `PUT /api/state` - sincroniza os dados da interface com o servidor.
- `GET /api/doctors` e `GET /api/patients` - listas de cadastros.
- `GET /api/appointments?date=AAAA-MM-DD` - lista consultas, com filtro opcional.
- `POST /api/appointments` - agenda uma consulta e valida disponibilidade e antecedência.
- `PATCH /api/appointments/{id}` - cancela ou reagenda uma consulta.

## Dados de demonstração

A primeira execução cria cadastros fictícios. Use apenas dados de exemplo: esta aplicação não possui autenticação, não envia e-mail/SMS e não foi projetada para guardar dados médicos reais. Para reiniciar, pare o servidor e apague `aurora.sqlite3`.
