import catalog from './ibge_catalog.json';

export const IBGE_STATES = catalog.states ?? [];
export const IBGE_MUNICIPALITIES = [...(catalog.municipalities ?? [])].sort((a, b) =>
  (a.nome || '').localeCompare(b.nome || '', 'pt-BR')
);

const municipalityByCode = new Map(
  IBGE_MUNICIPALITIES.map((item) => [String(item.codigo_ibge).trim().padStart(7, '0'), item])
);

const municipalityByName = new Map(
  IBGE_MUNICIPALITIES.map((item) => [String(item.nome).trim().toLowerCase(), item])
);

export function getMunicipalityByCode(code) {
  if (!code) return null;
  return municipalityByCode.get(String(code).trim().padStart(7, '0')) ?? null;
}

export function getMunicipalityByName(name) {
  if (!name) return null;
  return municipalityByName.get(String(name).trim().toLowerCase()) ?? null;
}

export function getMunicipalityLabel(code) {
  const municipality = getMunicipalityByCode(code);
  if (!municipality) return String(code ?? '');
  return municipality.uf_abbr ? `${municipality.nome} - ${municipality.uf_abbr}` : municipality.nome;
}

export function getMunicipalityOption(code) {
  const municipality = getMunicipalityByCode(code);
  if (!municipality) return null;
  return {
    codigo: municipality.codigo_ibge,
    nome: getMunicipalityLabel(municipality.codigo_ibge),
    uf_abbr: municipality.uf_abbr ?? '',
    uf_nome: municipality.uf_nome ?? '',
  };
}

export function getMunicipalitiesByNames(names = []) {
  return names
    .map((name) => getMunicipalityByName(name))
    .filter(Boolean)
    .map((municipality) => ({
      codigo: municipality.codigo_ibge,
      nome: getMunicipalityLabel(municipality.codigo_ibge),
      uf_abbr: municipality.uf_abbr ?? '',
      uf_nome: municipality.uf_nome ?? '',
    }));
}
