# Map sources

## `world-110m.paths.json`

| field | value |
|---|---|
| dataset | Natural Earth 1:110m Cultural Vectors - Admin 0 Countries |
| license | **public domain (Natural Earth terms of use)** - no attribution required, none withheld |
| source | `https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson` |
| commit | `9380cca83db5f9aef52d5e762765100745f84b27` |
| commit date | 2022-05-13T05:33:10Z |
| fetched | 2026-09-11 |
| raw bytes | 838726 |
| raw blob SHA-1 | `1e6ab74c7042f97013be69ceec798be8e1aff27d` (verified: the downloaded bytes hash to the blob SHA git records at that commit) |
| countries | 177 |
| projection | equirectangular (plate carree), x = (lon + 180) / 360 * 1000, y = (90 - lat) / 180 * 500 |
| box | 1000 x 500 units, 3 decimals |
| node budget | 450 nodes per country, all rings summed (the C4 seek envelope, P50 T5) |
| simplification | Douglas-Peucker, pure Python, epsilon raised per country until the budget fits; a ring is cut at its farthest point from the start so neither half collapses |
| ids | ISO_A3, falling back to ADM0_A3 where Natural Earth carries `-99` |

The raw GeoJSON is **not** in the repo: the builder caches it outside the tree
(`WORLD_MAP_CACHE`, else the system temp dir). Rebuild with

    python content/video_engine/scripts/build_world_map.py

Natural Earth's terms: "All versions of Natural Earth raster + vector map data found on
this website are in the public domain."

### ids that did not come from ISO_A3

- CYN (N. Cyprus): id taken from ADM0_A3 because ISO_A3 is -99 in Natural Earth 1:110m
- FRA (France): id taken from ADM0_A3 because ISO_A3 is -99 in Natural Earth 1:110m
- KOS (Kosovo): id taken from ADM0_A3 because ISO_A3 is -99 in Natural Earth 1:110m
- NOR (Norway): id taken from ADM0_A3 because ISO_A3 is -99 in Natural Earth 1:110m
- SOL (Somaliland): id taken from ADM0_A3 because ISO_A3 is -99 in Natural Earth 1:110m
