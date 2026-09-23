# Gable Steveson case-source bundle

Status: `review_only`  
Render eligibility: `false`  
Retrieved: 2026-09-20  
Scope: verify the public legal/news record behind the case reference in the
supplied UFC 331 Short. These sources do not establish whether the underlying
allegation occurred.

## Primary and authoritative sources

| ID | Authority and page | Published | Local copy | SHA-256 | What it establishes | Limits |
| --- | --- | --- | --- | --- | --- | --- |
| `HENNEPIN-2019-06-18` | [Hennepin County Attorney: No charges against UM wrestlers, investigation continues](https://www.hennepinattorney.org/news/news/2019/June/cao-wrestlers-charges-6-18-2019) | 2019-06-18 | `sources/hennepin-2019-06-18-no-charges-at-time.html` (17,078 bytes; retrieved 2026-09-20T20:57:08Z) | `9D957EB55E64D53348481FC89D5A7DA3C557049AA4441C00E82FCB1CE69D7EAE` | The office named criminal-sexual-conduct allegations against Gable Steveson and Dylan Martinez; it said no charges could be brought **at that time**, the investigation remained active, and prosecutors would review further evidence. | This is an interim June release, not the final prosecutorial decision. It does not describe the alleged conduct or decide its truth. |
| `HENNEPIN-2019-12-20` | [Hennepin County Attorney: No charges filed against University of Minnesota wrestlers following criminal sexual assault investigation](https://www.hennepinattorney.org/news/news/2019/December/university-wrestlers-12-20-2019) | 2019-12-20 | `sources/hennepin-2019-12-20-no-charges-filed.html` (18,432 bytes; retrieved 2026-09-20T20:57:09Z) | `2A25BCB5A471EBAA15311E35631B209CF410CBAEA633442E2A5119969C15D34D` | The Hennepin County Attorney's Office said the Minneapolis Police Department investigation was complete, the case had been reviewed by prosecutors and senior leadership, and **no charges were filed**. Mike Freeman cited conflicting versions and “inadequate evidence to fairly charge and prosecute this case.” | The statement does not adjudicate the allegation. It also says the office was constrained by the Minnesota intoxication/consent law then in force; do not turn that explanation into a claim that the outcome rested on one “loophole.” |
| `MN-STAT-2019-609344` | [Minnesota Revisor of Statutes: 2019 Minn. Stat. § 609.344](https://www.revisor.mn.gov/statutes/2019/cite/609.344/subd/609.344.1) | 2019 historical version | `sources/minnesota-statutes-2019-609-344.html` (75,346 bytes; retrieved 2026-09-20T20:57:09Z) | `8BC4D31D23A6BF4F4525EA8A636ADE57C40A5EA14E5A4BA89C688561D3834071` | Preserves the official 2019 statutory text for legal-context checking. | It is not evidence about this incident, the complainant, Steveson, or the charging decision. Do not use it to infer what happened. |
| `UFC-331-PRESSER` | [UFC: Pre-Fight Press Conference — Crypto.com UFC 331](https://www.ufc.com/video/160203) | 2026 event page | `sources/ufc-331-pre-fight-press-conference.html` (67,921 bytes; retrieved 2026-09-20T20:57:09Z) | `3A67312315CD26B71067C2E7725104C161A7236C0D706FB5FAAEE181D5C06E7F` | Officially identifies the public UFC 331 pre-fight press-conference page associated with the supplied news peg. | The page has no transcript of the accusation. Any quote must be checked against the recovered video; the speaker's words are not a legal finding. |

## Reading of the record

The two Hennepin releases form a clear sequence: June 18 was an interim
“no charges at this time” decision while the investigation remained active;
December 20 was the final public announcement that the office did not file
charges after review. The record supports “allegation/investigation” and
“no charges filed.” It does **not** support “convicted,” “acquitted,” “charges
dismissed,” “cleared,” “exonerated,” or a factual assertion that the alleged
conduct occurred.

The press-conference insult is newsworthy as an attributed public statement,
not as a verified description of Steveson's conduct. Keep the quote separate
from the official legal record and never use the quoted label as narrator voice.

## Retrieval and verification

All four files were fetched with `Invoke-WebRequest -UseBasicParsing` from the
public URLs above on 2026-09-20. Local bytes were checked with
`Get-FileHash -Algorithm SHA256`; the hashes in this file and `receipt.json`
are the verification values. No login, paywall bypass, credential, or private
record was used. No screenshot was needed because the authoritative HTML pages
were publicly accessible and preserved locally.
