import React from 'react';
import { Github, Linkedin, Mail, GraduationCap } from 'lucide-react';

const socialLinks = [
  { label: 'GitHub', Icon: Github, href: 'https://github.com/murilo-fmuniz' },
  { label: 'LinkedIn', Icon: Linkedin, href: 'https://www.linkedin.com/in/murilo-fontana-muniz-911003275/' },
  { label: 'Lattes', Icon: GraduationCap, href: 'http://lattes.cnpq.br/8927558763874917' },
  { label: 'E-mail', Icon: Mail, href: 'mailto:muri.fmuniz@gmail.com' },
];

function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-slate-50 text-gray-600">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-10 px-6 py-10 md:grid-cols-3 md:px-8">
        <section>
          <h2 className="text-xl font-bold tracking-tight text-slate-800">
            Urbix <span className="font-medium text-emerald-600">- Cidades Inteligentes</span>
          </h2>
          <p className="mt-3 max-w-md text-sm leading-6">
            Plataforma multicritério para avaliação e ranqueamento de maturidade urbana
            baseada nas normativas ISO 37120, ISO 37122 e ISO 37123.
          </p>
        </section>

        <section>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800">
            Pesquisa e Fomento
          </h2>
          <div className="mt-3 space-y-3 text-sm leading-6">
            <p>
              Desenvolvido como projeto de Iniciação Científica (IC) na{' '}
              <strong className="font-semibold text-slate-700">
                Universidade Tecnológica Federal do Paraná (UTFPR) - Campus Apucarana
              </strong>.
            </p>
            <p>
              Pesquisa realizada com o apoio e financiamento do{' '}
              <strong className="font-semibold text-slate-700">
                CNPq (Conselho Nacional de Desenvolvimento Científico e Tecnológico)
              </strong>.
            </p>
            <p>
              <span className="font-semibold text-slate-700">Orientação:</span>{' '}
              Prof. Me. Fábio Irigon e Profª. Dra. Daiane Chiroli.
            </p>
          </div>
        </section>

        <section>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800">
            Desenvolvedor e Contato
          </h2>
          <p className="mt-3 text-sm leading-6">
            Desenvolvido por <strong className="font-semibold text-slate-700">Murilo Fontana Muniz</strong>.
          </p>
          <nav aria-label="Links de contato" className="mt-5 flex flex-wrap gap-3">
            {socialLinks.map(({ label, Icon, href }) => (
              <a
                key={label}
                href={href}
                target={label === 'E-mail' ? undefined : '_blank'}
                rel={label === 'E-mail' ? undefined : 'noreferrer'}
                aria-label={label}
                className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 shadow-sm transition hover:border-emerald-300 hover:bg-emerald-50 hover:text-emerald-700"
              >
                <Icon size={17} strokeWidth={1.8} aria-hidden="true" />
                <span>{label}</span>
              </a>
            ))}
          </nav>
        </section>
      </div>

      <div className="border-t border-slate-200 px-6 py-4 text-center text-xs text-gray-500">
        © 2025-2026 Urbix. Código aberto e dados governamentais de domínio público.
      </div>
    </footer>
  );
}

export default Footer;
