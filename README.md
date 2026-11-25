# desk-layout

2D multi-monitor spatial layout solver (QR photo detections -> aspect-ratio-preserving snapped layout) and Deskflow v1.27+ INI/server config compiler.

## Features

- `solve_layout_from_photo(detections, nodes_by_code, existing_master_id=None)`
- `compute_links(items, names_by_id)` — non-overlapping integer percentage edge intervals `[0, 100]`
- `compile_server_conf(nodes_map, layout)` — emits Deskflow v1.27+ `section: links` and `section: options` (without deprecated `section: screens`)
- `compile_deskflow_ini(...)` — emits `Deskflow.conf` INI with `[core]`, `[server]`/`[client]`, `[security]`, and `[computer_N]` screen definitions for servers
