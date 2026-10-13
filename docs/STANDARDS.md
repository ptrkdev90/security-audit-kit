# Standards applicability and evidence

Public primary-source scope descriptions checked on 2026-10-12. Full copyrighted standard
texts were not audited. This is an applicability guide, not a conformity declaration.
Recheck editions and contractual requirements at the start of an actual engagement.

| Reference | Relevant scope | Toolkit treatment | Primary source |
|---|---|---|---|
| ISO/IEC/IEEE 26514:2022 | Design/development of information for software users | Audience, structure and maintenance guidance; a security report is a distinct document type | [ISO](https://www.iso.org/standard/77451.html) |
| IEC/IEEE 82079-1:2019 | Information for use of products | Editorial/process guidance where applicable, without claiming full conformity | [IEC](https://webstore.iec.ch/en/publication/29075) |
| ISO/IEC/IEEE 42010:2022 | Architecture descriptions, viewpoints and model kinds | Stakeholders, concerns, views, uncertainty and model references | [ISO](https://www.iso.org/standard/74393.html) |
| ASD-STE100 Issue 9 | Controlled English for technical documentation | Optional English style profile; requires full rules/vocabulary for conformance checking | [ASD](https://www.asd-ste100.org/STE_downloads.html) |
| OWASP ASVS v5.0.0 | Web application security verification requirements | Optional versioned requirement mapping; no level claim from partial coverage | [OWASP releases](https://github.com/OWASP/ASVS/releases) |
| iiRDS 1.2 | Documentation metadata and exchange specification | Possible integration profile; this toolkit's JSON/ZIP is not an iiRDS package | [iiRDS specification](https://www.iirds.org/materials/version-12) |
| VDI 2770 Blatt 1 | Digital manufacturer information for process-industry plants | Sector-specific; use only with an explicit industrial delivery requirement | [VDI](https://www.vdi.de/mitgliedschaft/vdi-richtlinien/details/vdi-2770-blatt-1-betrieb-verfahrenstechnischer-anlagen-mindestanforderungen-an-digitale-herstellerinformationen-fuer-die-prozessindustrie-grundlagen) |
| ISO 20607:2019 | Safety-relevant machinery instruction handbooks | Sector-specific; not automatically applicable to a software audit report | [ISO](https://www.iso.org/standard/68519.html) |

The Quanos article supplied by the user is a useful discovery overview. Primary publishers
own the actual requirements and edition status. Machinery warnings/symbols, US safety
notices and business-letter layout rules are not automatic software-audit requirements.
Record them as candidates only when product, market or contract makes them relevant.

## Engagement record

When documentation standards are requested, create `documentation-profile.json`:

- Name, edition, primary source and verification date.
- Applicable, reference-only, not-applicable or unknown, with a rationale.
- Whether the authorized full text was examined.
- Actual evidence IDs for any implemented or evaluated requirements.

The optional schema validates record structure and evidence references. It cannot decide
legal applicability or establish full normative conformity. Public abstracts support
scope selection only. Do not invent clause IDs, mandatory rules, legal obligations or
proof that a paid standard was reviewed. Escalate unresolved contractual requirements to
the responsible reviewer while continuing independently authorized technical work.

## Separate assurance categories

Security findings, documentation quality and SOC 2 readiness are separate dimensions.
A clear report does not attest operating effectiveness. A passed source check does not
satisfy organizational/period evidence. The default PDF exporter does not certify PDF/A
or PDF/UA, and its PDF is not tagged for accessibility. Request a capable export workflow
and independent format validation when those requirements actually apply.
