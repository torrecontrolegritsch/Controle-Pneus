-- Tabela de solicitações de pneus
-- Executar no SQL Editor do Supabase

CREATE TABLE IF NOT EXISTS gp_solicitacoes (
  id            bigserial PRIMARY KEY,
  filial_id     integer REFERENCES gp_filiais(id),
  filial_nome   text,
  medida        text NOT NULL,
  quantidade    integer NOT NULL DEFAULT 1,
  motivo        text NOT NULL,
  observacao    text,
  status        text NOT NULL DEFAULT 'pendente',
  observacao_admin text,
  usuario_nome  text,
  usuario_email text,
  criado_em     timestamptz DEFAULT now(),
  atualizado_em timestamptz DEFAULT now()
);

-- Índices para queries comuns
CREATE INDEX IF NOT EXISTS idx_gp_sol_filial  ON gp_solicitacoes(filial_id);
CREATE INDEX IF NOT EXISTS idx_gp_sol_status  ON gp_solicitacoes(status);
CREATE INDEX IF NOT EXISTS idx_gp_sol_criado  ON gp_solicitacoes(criado_em DESC);
