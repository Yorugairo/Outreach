# Map places - sources

## `places.json`

| field | value |
|---|---|
| dataset | Natural Earth 1:10m Cultural Vectors - Populated Places (simple) |
| license | **public domain (Natural Earth terms of use)** |
| source | `https://raw.githubusercontent.com/nvkelso/natural-earth-vector/9380cca83db5f9aef52d5e762765100745f84b27/geojson/ne_10m_populated_places_simple.geojson` |
| commit | `9380cca83db5f9aef52d5e762765100745f84b27` (the commit `world-110m.paths.json` is pinned at) |
| raw bytes | 4932141 |
| raw blob SHA-1 | `534edbb72fee39f476239e24fd4b24acf6f965d5` (verified on every build: the bytes must hash to it) |
| point | the feature's own geometry |
| projection | build_world_map.project - x = (lon + 180) / 360 * 1000, y = (90 - lat) / 180 * 500 |

| id | label | Natural Earth class | adm0_a3 | ne_id | lon | lat | x | y |
|---|---|---|---|---|---|---|---|---|
| HKG | Hong Kong | Admin-0 region capital | HKG | 1159151629 | 114.183064 | 22.306927 | 817.175 | 188.036 |
| HSINCHU | Hsinchu | Admin-1 capital | TWN | 1159146175 | 120.976739 | 24.816791 | 836.046 | 181.064 |
| MAC | Macau | Admin-0 region capital | MAC | 1159149085 | 113.544375 | 22.189135 | 815.401 | 188.364 |
| SGP | Singapore | Admin-0 capital | SGP | 1159151627 | 103.853875 | 1.294979 | 788.483 | 246.403 |

Rebuild with

    python content/video_engine/scripts/build_map_places.py
