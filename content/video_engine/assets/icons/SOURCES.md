# Icon sources (A2a: sourced, with provenance, never generated)

Every glyph a `chip` species (P50 T2) can carry is a file in this folder, fetched from a named
icon set at a pinned version. Nothing here is drawn by us and nothing here is model-generated.
The compiler (`build_scene_timeline_f.py: icon_geometry`) reads the file, keeps only the
geometry elements, and embeds that geometry in the timeline's asset map under `icon:<name>`,
so the player stays one self-contained file.

## Set

| field | value |
|---|---|
| set | **Lucide** |
| version | **1.45.0** (released 2026-09-11) |
| release | https://github.com/lucide-icons/lucide/releases/tag/1.45.0 |
| license | **ISC** - full text in `LICENSE.lucide.txt` beside this file, upstream at https://github.com/lucide-icons/lucide/blob/1.45.0/LICENSE |
| fetched | 2026-09-11 (the first five, P50 T2) and 2026-09-26 (the supply chain, P73 T4), by `curl` from `raw.githubusercontent.com` at the tag (never `main`), with a generic User-Agent |

Lucide's ISC license permits use and redistribution with the copyright notice retained;
`LICENSE.lucide.txt` is that notice, committed beside the files it covers.

## Files

| file | upstream URL (pinned to 1.45.0) |
|---|---|
| `coins.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/coins.svg |
| `cpu.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/cpu.svg |
| `factory.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/factory.svg |
| `landmark.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/landmark.svg |
| `ship.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/ship.svg |
| `antenna.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/antenna.svg |
| `building.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/building.svg |
| `container.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/container.svg |
| `flag.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/flag.svg |
| `globe.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/globe.svg |
| `plane.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/plane.svg |
| `radar.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/radar.svg |
| `radio.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/radio.svg |
| `scale.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/scale.svg |
| `shield.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/shield.svg |
| `store.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/store.svg |
| `tag.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/tag.svg |
| `truck.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/truck.svg |
| `user.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/user.svg |
| `users.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/users.svg |
| `warehouse.svg` | https://raw.githubusercontent.com/lucide-icons/lucide/1.45.0/icons/warehouse.svg |

P73 T4 (2026-09-26) added the sixteen after `ship.svg` for the supply chain a flow diagram draws (a maker, a
distributor, a reseller, the carriers, the licence, the law, a price, a flag, a buyer): `building` a company,
`warehouse` a distributor, `store` a reseller or a storefront, `truck` / `container` / `plane` the carriers beside
`ship`, `shield` a licence or customs, `scale` the law, `tag` a price, `flag` a country, `globe` the world,
`radar` / `antenna` / `radio` what a radio part is for, `user` a buyer, `users` a crowd of them. Same tag as the
five (a re-fetched `coins.svg` came back byte-identical, so the method is the one the five used); `building-2`
is not at the tag (404) and was not taken. `tag.svg`'s dot carries `fill="currentColor"`, which the compiler's
geometry filter drops - its r .5 circle still paints as a dot under the chip's width-2 stroke.

Every file is byte-for-byte what the tag serves: a 24x24 viewBox, `fill="none"`,
`stroke="currentColor"`, stroke-width 2, round caps and joins. The chip paints the glyph in
chalk on the chip card and never rewrites the geometry.

## Adding one

1. `curl -sS -o content/video_engine/assets/icons/<name>.svg https://raw.githubusercontent.com/lucide-icons/lucide/<tag>/icons/<name>.svg`
2. add its row to the table above (and a new Set block if it comes from another set - Tabler is
   MIT and equally acceptable; name the set, the version and the license there too);
3. the compiler accepts only `path`, `circle`, `rect`, `line`, `polyline`, `polygon`, `ellipse`
   with geometry attributes - anything else in the file is dropped, and a file with no geometry
   left is a build error naming the icon.
